import json
from flask import Flask,request
from pymongo import MongoClient
from bson import json_util
from dotenv import load_dotenv
import os #provides ways to access the Operating System and allows us to read the environment variables
import re

load_dotenv()
URI = os.getenv("MONGODB_STAGING_URI")
database = os.getenv("DATABASE")
port = os.getenv("PORT")

print("Target port: " + port)

#point the client at mongo URI
client = MongoClient(URI)

db = client[database]
#select the collection within the database
collection = db.mentorDetails
autocomplete_values = db.autocompleteValues

def remove_oid(string):
  # function that replace $oid to _id from collection.find() cursor
  while True:
      pattern = re.compile('{\s*"\$oid":\s*(\"[a-z0-9]{1,}\")\s*}')
      match = re.search(pattern, string)
      if match:
          string = string.replace(match.group(0), match.group(1))
      else:
          return string
    
def flatten(l):
    return [item for sublist in l for item in sublist]

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

@app.route("/mentors-search",methods=["GET"])
def search_without_parameters():

  input = (request.get_json(force=True))
  try: 
    query = input['query']
  except KeyError:
    query = "college guidance career guidance interview preparation job search guidance"
  
  try:
    page = input['page']
  except KeyError:
    page = 1

  try:
    perPage = input['perPage']
  except KeyError:
    perPage = 12

  try: 
    skip = input['skip']
  except KeyError:
    skip = 0

  try: 
    limit = input['limit']
  except KeyError:
    limit = page*perPage

  try: 
    sortBy = input['sortBy']
  except KeyError:
    sortBy = "score"

  try: 
    sortOrder = input['sortOrder']
  except KeyError:
    sortOrder = -1



  # @TODO: add OpenAPI documentation
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
  "$sort" : {sortBy : sortOrder}
  },
  {
    "$group":
    {
      "_id":"null",
      "count":{"$sum":1},
      "data":{"$push":"$$ROOT"}
    }
    
  },

  {
    "$project": {
      "_id":0,
      "count":1,
      "data":{
      "$slice": ['$data', skip, limit],
      }
    }
  },
 
])
  #print(list(result))
  #print(len(list_cur))
  
  json_data = json.loads(remove_oid(json_util.dumps(list(result))))
  print(json_data)
  obj = {'data' : json_data}
  return obj['data'][0]
  

@app.route("/weighted-search",methods=["GET"])
def weighted_search():
  
  input = (request.get_json(force=True))
  try: 
    query = input['query']
  except KeyError:
    query = {"corpus":"college guidance career guidance interview preparation job search guidance"}
  
  try:
    page = input['page']
  except KeyError:
    page = 1

  try:
    perPage = input['perPage']
  except KeyError:
    perPage = 12

  try: 
    skip = input['skip']
  except KeyError:
    skip = 0

  try: 
    limit = input['limit']
  except KeyError:
    limit = page*perPage

  try: 
    sortBy = input['sortBy']
  except KeyError:
    sortBy = "score"

  try: 
    sortOrder = input['sortOrder']
  except KeyError:
    sortOrder = -1

  pipelines = []
  querycorpus = ""

  # iterate through the json object of query
  for kv in query.items():
    
    # now our query is divided as kv={"path":"value"} in each iteration
    # kv[0] gives us path, kv[1] gives us value
    subpaths = get_subpath(kv[0])
    subgroups = get_subgroup(kv[0])
      
    condition = [
          {"text": {
            "query": kv[1],
            "path": kv[0],
            "score": { "boost": { "value": 10 } }
          }},
        
         {"text": {
            "query": kv[1],
            "path": subpaths, 
            "score": { "boost": { "value": 7 } }  
          }},
         
          {"text": {
            "query": kv[1],
            "path": subgroups,
            "score": { "boost": { "value": 5 } }  
          }}
    ]

    # in every iteration we add the above condition array to our pipelines array
    pipelines.append(condition)
    # also we create a querycorpus that contains all the query keywords
    querycorpus = querycorpus + kv[1] + " "
    
  # flatten lowers down the dimension of nested arrays ( just like spread in js )
  pipeline = (flatten(pipelines))
  
  # now that we have a flat array of dictionaries, we will push them into a new dictionary
  final_pipeline = {}
  for x in range(len(pipeline)):
    final_pipeline.update(pipeline[x])

  #print(new_pipeline)
  
  # and we define the corpus condition based on the query corpus
  corpus_condition = {
          "text": {
            "query": querycorpus,
            "path": "corpus"
          }
        }
  

  result = collection.aggregate([
  {
    "$search": {
      "index": "mentor_search",
      "highlight": {
         "path": "corpus"
         },
      "compound": {
        "should": [
        (corpus_condition), # documents should have some match in corpus based on entire query corpus 
        (final_pipeline) # documents will be ranked higher based on the search parameters (weighted)
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
    "$sort": {sortBy : sortOrder}
  },
  
  {
    "$group":
    {
      "_id":"null",
      "count":{"$sum":1},
      "data":{"$push":"$$ROOT"}
    }
  },

  {
    "$project": {
      "_id":0,
      "count":1,
      "data":{
      "$slice": ['$data', skip, limit],
      }
    }
  }
  ])
  
  list_cur = list(result)
  
  json_data = json.loads(remove_oid(json_util.dumps(list_cur)))
  
  try : 
    obj = {'data' : (json_data)}
    return obj['data'][0]
  
  except IndexError :
    obj = {'count':0, 'data':[]}
    return obj



@app.route("/autocomplete",methods=["GET"])
def autocomplete():
   args = request.args
  
   # query can be passed as an argument
   query = args.get("query", type=str)
   skip = args.get("skip",type=int)
   limit = args.get("limit",type=int)


   result = autocomplete_values.aggregate([
    { 
      "$search": {
                  "index": "autocomplete",
                  "autocomplete": {
                    "query": query,
                    "path": "value"
                    }
                }
    },
    {
      "$limit" : limit
    },
    {
      "$skip": skip
    }

  ])
   list_cur = list(result)
   json_data = json.loads(remove_oid(json_util.dumps(list_cur)))
   obj = {'data' : (json_data)}
   return  obj



if __name__ == '__main__':
    app.run(host='localhost', port=port)
