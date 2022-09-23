import json
from flask import Flask, request
from pymongo import MongoClient
from bson import json_util
from dotenv import load_dotenv
import os #provides ways to access the Operating System and allows us to read the environment variables

load_dotenv()
URI = os.getenv("MONGODB_STAGING_URI")
database = os.getenv("DATABASE")

#point the client at mongo URI
client = MongoClient(URI)

db = client[database]
#select the collection within the database
collection = db.mentorDetails

import re
def remove_oid(string):
  # function that replace $oid to _id from collection.find() cursor
  while True:
      pattern = re.compile('{\s*"\$oid":\s*(\"[a-z0-9]{1,}\")\s*}')
      match = re.search(pattern, string)
      if match:
          string = string.replace(match.group(0), match.group(1))
      else:
          return string

def get_subpath(paths):
  # function that returns subpaths where weights will be lower based on search parameteres
  subpaths = []

  for path in paths :
    if (path=='education.degree' or path=='education.specialization' or path=='education.university'):
      subpath1 = 'experiencecorpus'
      subpath2 = 'educationcorpus'
      subpaths.append(subpath1)
      subpaths.append(subpath2)
    
    if (path=='experience.designation' or path=='experience.company_name'):
      subpath = 'experiencecorpus'
      subpaths.append(subpath)

    if (path=='industry'):
      subpath1 = 'field_of_work'
      subpath2 = 'experience.industry'
      subpaths.append(subpath1)
      subpaths.append(subpath2)

    if (path=='field_of_work'):
      subpath1 = 'industry'
      subpath2 = 'experience.industry'
      subpaths.append(subpath1)
      subpaths.append(subpath2)


     
  if len(list(set(subpaths))):
    return(list(set(subpaths)))
  
  else :
    return paths


def get_subgroup(paths):
  # function that returns subgroup where weights will be even lower based on search parameteres
  subgroups = []

  for path in paths :
    if (path=='experience.designation' or path=='experience.company_name'):
      subgroup = 'about'
      subgroups.append(subgroup)

    if (path=='industry' or path=='field_of_work'):
      subgroup = 'experiencecorpus'
      subgroups.append(subgroup)

  if len(list(set(subgroups))):
    return(list(set(subgroups)))
  
  else :
    return paths

app = Flask(__name__)

@app.route("/")
def flask_app():
  return "Mapout Skills Flask Application"

@app.route("/search",methods=["GET"])
def search_without_parameters():
  args = request.args
  
  # query can be passed as an argument
  query = args.get("query", default="college guidance career guidance interview preparation job search guidance", type=str)
  
  # page(number) and perPage can be passed as arguments
  page = args.get("page",default=1,type=int)
  perPage = args.get("perPage",default=12,type=int)
  
  # based on the above arguments, the default value of skip and limit can be decided
  # or skip and limit can be separately passed as arguments
  skip = args.get("skip",default=((page-1)*perPage),type=int)
  limit = args.get("limit",default=page*perPage,type=int)
  
  # field name to sort by and the order of sorting can be passed as argument
  sortBy = args.get("sortBy",default="score", type=str)
  sortOrder = args.get("sortOrder",default=-1,type=int)

  result = collection.aggregate([
  {
    "$search": {
      "index": "mentor_search",
      "highlight": {
         "path": "corpus"
         },
      "compound": {
        "should": [{
          "text": {
            "query": query,
            "path": "corpus"
          }
        },

        {
          "text": {
            "query": query,
            "path": ['name','about','mentorFor','mentorTo','field_of_work','industry'],
            "score": { "boost": { "value": 5 } }
          },
        
         "text": {
            "query": query,
            "path": ['tech_skill.name','soft_skill.name','experience.designation','experience.industry','education.degree','education.specialization'],
            "score": { "boost": { "value": 4 } }  
          },
         
          "text": {
            "query": query,
            "path": ['experience.company_name','education.university_name'],
            "score": { "boost": { "value": 3 } }  
          },
         
         "text": {
            "query": query,
            "path": ['languages','experiencecorpus','educationcorpus','talentboards'],
            "score": { "boost": { "value": 2 } }  
         },
         
         "text": {
            "query": query,
            "path": ['corpus'],
            "score": { "boost": { "value": 1 } }  
         }

        }
        
        ]
      }
    }
  },

  {"$lookup" : {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user"
            }
  },

  { "$lookup": {
            "from": "experiences",
            "localField": "user.experience",
            "foreignField": "_id",
            "as": "experience"
            },
  },

  { "$unwind" :  "$user" },

  {
    "$project": {
      "user_id": 1,
      "name": 1,
      "mentorPrice":1,
      "experience.company_name":1,
      "experience.designation":1,
      "mentorFor":"$user.mentorFor.name",
      "mentorPrice":{"$toInt":"$user.mentorPrice"},
      "about":"$user.about",
      "current_location":"$user.current_location",
      "profilePic":"$user.profilePic",
      "talent_board":"$user.talent_board",
      "rating":"$user.rating",
      "score": { "$meta": "searchScore" },
      } 
  },

  {
    "$sort" : { sortBy : sortOrder }
  },

  {
    "$limit" : limit
  },

  {
    "$skip" : skip
  },
])
  #print(list(result))
  list_cur = list(result)
  #print(len(list_cur))
  json_data = json.loads(remove_oid(json_util.dumps(list_cur)))
  #print(json_data)
  obj = {'mentors' : (json_data)}
  return obj


@app.route("/weighted-search",methods=["GET"])
def weighted_search():
  args = request.args
  
  # query can be passed as an argument
  query = args.get("query", default="college guidance career guidance interview preparation job search guidance", type=str)
  
  # path can be specified as an argument for weighted search
  paths = args.get("paths",default=['corpus'],type=list)

  # page(number) and perPage can be passed as arguments
  page = args.get("page",default=1,type=int)
  perPage = args.get("perPage",default=12,type=int)
  
  # based on the above arguments, the default value of skip and limit can be decided
  # or skip and limit can be separately passed as arguments
  skip = args.get("skip",default=((page-1)*perPage),type=int)
  limit = args.get("limit",default=page*perPage,type=int)
  
  # field name to sort by and the order of sorting can be passed as argument
  sortBy = args.get("sortBy",default="score", type=str)
  sortOrder = args.get("sortOrder",default=-1,type=int)

  subpaths = get_subpath(paths)
  subgroups = get_subgroup(paths)

  result = collection.aggregate([
  {
    "$search": {
      "index": "mentor_search",
      "highlight": {
         "path": "corpus"
         },
      "compound": {
        "should": [{
          "text": {
            "query": query,
            "path": "corpus"
          }
        },

        {
          "text": {
            "query": query,
            "path": paths,
            "score": { "boost": { "value": 10 } }
          },
        
         "text": {
            "query": query,
            "path": subpaths, 
            "score": { "boost": { "value": 7 } }  
          },
         
          "text": {
            "query": query,
            "path": subgroups,
            "score": { "boost": { "value": 5 } }  
          },
         
         "text": {
            "query": query,
            "path": ['corpus'],
            "score": { "boost": { "value": 1 } }  
         }

        }
        
        ]
      }
    }
  },

  {"$lookup" : {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user"
            }
  },

  { "$lookup": {
            "from": "experiences",
            "localField": "user.experience",
            "foreignField": "_id",
            "as": "experience"
            },
  },

  { "$unwind" :  "$user" },

  {
    "$project": {
      "user_id": 1,
      "name": 1,
      "mentorPrice":1,
      "experience.company_name":1,
      "experience.designation":1,
      "mentorFor":"$user.mentorFor.name",
      "mentorPrice":{"$toInt":"$user.mentorPrice"},
      "about":"$user.about",
      "current_location":"$user.current_location",
      "profilePic":"$user.profilePic",
      "talent_board":"$user.talent_board",
      "rating":"$user.rating",
      "score": { "$meta": "searchScore" },
      } 
  },

  {
    "$sort" : { sortBy : sortOrder }
  },

  {
    "$limit" : limit
  },

  {
    "$skip" : skip
  },
])
  #print(list(result))
  list_cur = list(result)
  #print(len(list_cur))
  json_data = json.loads(remove_oid(json_util.dumps(list_cur)))
  #print(json_data)
  obj = {'mentors' : (json_data)}
  return obj


if __name__ == '__main__':
    app.run(host='localhost', port=5051)
