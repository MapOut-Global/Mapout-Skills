from flask import Flask, request
from pymongo import MongoClient
import pandas as pd

from dotenv import load_dotenv
import os #provides ways to access the Operating System and allows us to read the environment variables

load_dotenv()
URL = os.getenv("MONGODB_STAGING_URL")


client = MongoClient()
#point the client at mongo URI
client = MongoClient(URL)

db = client['mapout-staging']
#select the collection within the database
collection = db.mentorDetails

app = Flask(__name__)

@app.route("/")
def flask_app():
  return "Mapout Skills Flask Application"

@app.route("/search",methods=["GET"])
def search_without_parameters():
  args = request.args
  query = args.get("query", default="college guidance career guidance interview preparation job search guidance", type=str)

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

        }]
      }
    }
  },
  
  {
    "$project": {
      "user_id": 1,
      "name": 1,
      "highlights": { "$meta": "searchHighlights" }

    }
  }
])
  
  df = pd.DataFrame(result)
  df['user_id'] = df['user_id'].apply(lambda x : str(x))
  mentors = (list(df['user_id']))
  paginated_mentors = [mentors[i:i+10] for i in range(0, len(mentors), 10)]
  obj = {'mentors' : (paginated_mentors)}
  return obj

if __name__ == '__main__':
    app.run(host='localhost', port=5051)
