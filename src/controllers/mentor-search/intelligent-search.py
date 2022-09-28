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


app = Flask(__name__)

@app.route("/")
def flask_app():
  return "Mapout Skills Flask Application"

@app.route("/mentors-search",methods=["GET"])
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
