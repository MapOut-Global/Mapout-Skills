import json
import os

import marshmallow as ma
from bson import json_util, ObjectId
from dotenv import load_dotenv
from flask import Flask, request
from flask.views import MethodView
from flask_cors import CORS
from flask_smorest import Api, Blueprint
from pymongo import MongoClient

from mentor_search_utils import (
  remove_oid,
  flatten,
  get_subpath,
  get_subgroup,
  get,
  transform_pagination_params,
)
from schemas import (
  MentorsSearchRequestSchema,
  MentorProfilesSearchResponseSchema,
)

load_dotenv()

URI = os.getenv("MONGODB_STAGING_URI")
database = os.getenv("DATABASE")
port = os.getenv("PORT")

client = MongoClient(URI)
db = client[database]

collection = db.mentorDetails
autocomplete_values = db.autocompleteValues

app = Flask(__name__)
app.config['API_TITLE'] = 'Mentors search'
app.config['API_VERSION'] = 'v1'
app.config['OPENAPI_VERSION'] = '3.0.0'
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config['OPENAPI_JSON_PATH'] = 'openapi.json'
app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.25.0/'
api = Api(app)
CORS(app)

blp = Blueprint(
  'mentors',
  'mentors',
  url_prefix='/',
  description='Mentors search'
)

ma.Schema.TYPE_MAPPING[ObjectId] = ma.fields.UUID


@app.route("/")
def flask_app():
  return "Mapout Skills Flask Application"


@blp.route('/mentors-search')
class MentorSearch(MethodView):
  @blp.arguments(MentorsSearchRequestSchema, location='query')
  @blp.response(200, MentorProfilesSearchResponseSchema)
  def get(self, args: dict):
    """Mentors search"""
    print(args, flush=True)

    query = args.pop('query', "college guidance career guidance interview preparation job search guidance")
    page = args.pop('page')
    per_page = args.pop('perPage')
    sort_by = args.pop('sortBy')
    sort_order = args.pop('sortOrder')

    skip, limit = transform_pagination_params(page, per_page)

    result = collection.aggregate([
      {
        "$search": {
          "index": "mentor_search",
          "highlight": {
            "path": "corpus"
          },
          "compound": {
            "should": [
              {
                "text": {
                  "query": query,
                  "path": "corpus"
                }
              },
              {
                "text": {
                  "query": query,
                  "path": ['name', 'about', 'mentorFor', 'mentorTo', 'field_of_work', 'industry'],
                  "score": {"boost": {"value": 5}}
                },
              },
              {
                "text": {
                  "query": query,
                  "path": ['tech_skill.name', 'soft_skill.name', 'experience.designation', 'experience.industry',
                           'education.degree', 'education.specialization'],
                  "score": {"boost": {"value": 4}}
                },
              },
              {
                "text": {
                  "query": query,
                  "path": ['experience.company_name', 'education.university_name'],
                  "score": {"boost": {"value": 3}}
                },
              },
              {
                "text": {
                  "query": query,
                  "path": ['languages', 'experiencecorpus', 'educationcorpus', 'talentboards'],
                  "score": {"boost": {"value": 2}}
                },
              },
              {
                "text": {
                  "query": query,
                  "path": ['corpus'],
                  "score": {"boost": {"value": 1}}
                }

              }
            ]
          }
        }
      },

      {
        "$lookup": {
          "from": "users",
          "localField": "user_id",
          "foreignField": "_id",
          "as": "user"
        }
      },

      {
        "$lookup": {
          "from": "experiences",
          "localField": "user.experience",
          "foreignField": "_id",
          "as": "experience"
        },
      },

      {"$unwind": "$user"},

      {
        "$project": {
          "user_id": 1,
          "name": 1,
          "experience.company_name": 1,
          "experience.designation": 1,
          "mentorFor": "$user.mentorFor.name",
          "mentorPrice": {
            "$toInt": "$user.mentorPrice"
          },
          "about": "$user.about",
          "current_location": "$user.current_location",
          "profilePic": "$user.profilePic",
          "talent_board": "$user.talent_board",
          "rating": "$user.rating",
          "score": {
            "$meta": "searchScore"
          },
        }
      },

      {
        "$sort": {sort_by: sort_order}
      },

      {
        "$group": {
          "_id": "null",
          "count": {"$sum": 1},
          "data": {"$push": "$$ROOT"}
        }
      },

      {
        "$project": {
          "_id": 0,
          "count": 1,
          "data": {
            "$slice": ['$data', skip, limit],
          }
        }
      },
    ])

    json_data = get(list(result), 0)

    print(json_data)

    return {
      'count': get(json_data, 'count', 0),
      'page': page,
      'perPage': per_page,
      'sortBy': sort_by,
      'sortOrder': sort_order,
      'data': get(json_data, 'data', []),
    }


@blp.route('/weighted-search')
class WeightedSearch(MethodView):
  # experience.designation : react developer, experience.company_name: Microsoft, education.university : IIT, education.degree : B.Tech, education.specialization : Web Development, industry : Software, field_of_work : Finance, corpus : experienced
  @blp.arguments(MentorsSearchRequestSchema, location='query')
  def get(self, args: dict):
    query = args.pop('query', 'college guidance career guidance interview preparation job search guidance')
    sort_by = args.pop('sortBy')
    sort_order = args.pop('sort_order')
    page = args.pop('page')
    per_page = args.pop('perPage')

    skip, limit = transform_pagination_params(page, per_page)

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
          "score": {"boost": {"value": 10}}
        }},

        {"text": {
          "query": kv[1],
          "path": subpaths,
          "score": {"boost": {"value": 7}}
        }},

        {"text": {
          "query": kv[1],
          "path": subgroups,
          "score": {"boost": {"value": 5}}
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

    # print(new_pipeline)

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
              (corpus_condition),  # documents should have some match in corpus based on entire query corpus
              (final_pipeline)  # documents will be ranked higher based on the search parameters (weighted)
            ]
          }
        }
      },

      {"$lookup": {
        "from": "users",
        "localField": "user_id",
        "foreignField": "_id",
        "as": "user"
      }
      },

      {"$lookup": {
        "from": "experiences",
        "localField": "user.experience",
        "foreignField": "_id",
        "as": "experience"
      },
      },

      {"$unwind": "$user"},

      {
        "$project": {
          "user_id": 1,
          "name": 1,
          "mentorPrice": 1,
          "experience.company_name": 1,
          "experience.designation": 1,
          "mentorFor": "$user.mentorFor.name",
          "mentorPrice": {"$toInt": "$user.mentorPrice"},
          "about": "$user.about",
          "current_location": "$user.current_location",
          "profilePic": "$user.profilePic",
          "talent_board": "$user.talent_board",
          "rating": "$user.rating",
          "score": {"$meta": "searchScore"},
        }
      },

      {
        "$sort": {sort_by: sort_order}
      },

      {
        "$group":
          {
            "_id": "null",
            "count": {"$sum": 1},
            "data": {"$push": "$$ROOT"}
          }
      },

      {
        "$project": {
          "_id": 0,
          "count": 1,
          "data": {
            "$slice": ['$data', skip, limit],
          }
        }
      }
    ])

    list_cur = list(result)
    # Find MongoDB object id serializer
    json_data = json.loads(remove_oid(json_util.dumps(list_cur)))

    try:
      obj = {'data': (json_data)}
      return obj['data'][0]

    except IndexError:
      obj = {'count': 0, 'data': []}
      return obj


@blp.route('/autocomplete')
class MentorsAutocomplete(MethodView):
  def get(self, args: dict):
    # query can be passed as an argument
    query = args.get("query")
    skip = args.get("skip")
    limit = args.get("limit")

    # TODO: add score sorting
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
        "$limit": limit
      },
      {
        "$skip": skip
      }

    ])
    list_cur = list(result)
    json_data = json.loads(remove_oid(json_util.dumps(list_cur)))
    obj = {'data': (json_data)}
    return obj


api.register_blueprint(blp)

if __name__ == '__main__':
  app.run(host='localhost', port=port)
