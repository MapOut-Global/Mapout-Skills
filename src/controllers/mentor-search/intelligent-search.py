import os

import marshmallow as ma
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask
from flask.views import MethodView
from flask_cors import CORS
from flask_smorest import Api, Blueprint
from pymongo import MongoClient

from mentor_search_utils import (
  get_subpath,
  get_subgroup,
  get,
  transform_pagination_params,
  is_empty,
  execute_query_with_params,
  get_filter_values
)
from schemas import (
  MentorsSearchRequestSchema,
  MentorProfilesSearchResponseSchema,
  MentorsWeightedSearchRequestSchema,
  MentorsAutocompleteRequestSchema,
  MentorsAutocompleteResponseSchema,
  MentorsFilterRequestSchema,
  MentorsFilterResponseSchema,
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
app.config['OPENAPI_URL_PREFIX'] = '/search/mentors/docs'
app.config['OPENAPI_JSON_PATH'] = 'openapi.json'
app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger'
app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.25.0/'
api = Api(app)
CORS(app)

blp = Blueprint(
  'mentors',
  'mentors',
  url_prefix='/search/mentors',
  description='Mentors search'
)

ma.Schema.TYPE_MAPPING[ObjectId] = ma.fields.UUID


@app.route("/")
def flask_app():
  return "Mapout Skills Flask Application"


# DEPRECATED
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


@blp.route('')
class WeightedSearch(MethodView):
  @blp.arguments(MentorsWeightedSearchRequestSchema, location='query')
  @blp.response(200, MentorProfilesSearchResponseSchema)
  def get(self, args: dict):
    """Mentors parameterised search

    Mapping of search params categories to the query params
    - Type of mentor - mentorType
    - Field of work - fieldOfWork
    - Field of education - educationSpecialization
    - University - educationUniversity
    - Company - experienceCompanyName
    - Industry - industry
    - Location - location
    - Languages - language

    "query" param is for arbitrary additional input of the user
    """

    #
    # A map of internal fields to the request fields
    # Transformation is necessary for the client-side convenience and ability to specify validation schema
    #
    query_fields_to_db_query_map = {
      'experience.designation': 'experienceDesignation', # seems to be missed
      'experience.company_name': 'experienceCompanyName',
      'education.university': 'educationUniversity',
      'education.degree': 'educationDegree', # seems to be missed
      'education.specialization': 'educationSpecialization',
      'industry': 'industry',
      'field_of_work': 'fieldOfWork',
      'language': 'languages',
      'mentorType': 'mentorType',
      'current_location': 'location',
      'corpus': 'query',
    }

    query = {}

    # transformation of the search request fields into the internal ones
    for target_path in query_fields_to_db_query_map:
      request_params_path = query_fields_to_db_query_map[target_path]
      if request_params_path in args:
        query[target_path] = args.pop(request_params_path)

    if is_empty(query):
      query['corpus'] = "college guidance career guidance interview preparation job search guidance"

    for search_param, search_value in query.items():
      if type(search_value) is list:
        query[search_param] = ' '.join(search_value)

    print(query, flush=True)

    pipelines = []
    query_corpus = query.pop('corpus', '')

    # Preparing MongoDB search conditions grounding on the passed field in the request
    for path, value in query.items():
      # contains a compound query that handles the widest  use-case
      query_corpus = query_corpus + value + " "

      subpaths = get_subpath(path)
      subgroups = get_subgroup(value)

      pipelines.append({
        "text": {
          "query": value,
          "path": path,
          "score": {"boost": {"value": 10}}
        },
      })

      if subpaths is not None:
        pipelines.append({
          "text": {
            "query": value,
            "path": subpaths,
            "score": {"boost": {"value": 7}}
          },
        })

      if subgroups is not None:
        pipelines.append({
          "text": {
            "query": value,
            "path": subgroups,
            "score": {"boost": {"value": 5}}
          },
        })

    print(pipelines, flush=True)

    search_stage = {
      "$search": {
        "index": "mentor_search",
        # "index": "mentor-search-production",
        "highlight": {
          "path": "corpus"
        },
        'compound': {
          'should': [
            *pipelines,

            {
              "text": {
                "query": query_corpus,
                "path": "corpus"
              }
            },
            {
              "text": {
                "query": query_corpus,
                "path": ['name', 'about', 'mentorFor', 'mentorTo', 'field_of_work', 'industry'],
                "score": {"boost": {"value": 5}}
              },
            },
            {
              "text": {
                "query": query_corpus,
                "path": ['tech_skill.name', 'soft_skill.name', 'experience.designation', 'experience.industry',
                         'education.degree', 'education.specialization'],
                "score": {"boost": {"value": 4}}
              },
            },
            {
              "text": {
                "query": query_corpus,
                "path": ['experience.company_name', 'education.university_name'],
                "score": {"boost": {"value": 3}}
              },
            },
            {
              "text": {
                "query": query_corpus,
                "path": ['languages', 'experiencecorpus', 'educationcorpus', 'talentboards'],
                "score": {"boost": {"value": 2}}
              },
            },
            {
              "text": {
                "query": query_corpus,
                "path": ['corpus'],
                "score": {"boost": {"value": 1}}
              }
            }
          ]
        }
      },
    }

    return execute_query_with_params(args, collection, [
      search_stage,

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

      {
        "$unwind": {
          "path": "$user",
          "preserveNullAndEmptyArrays": True
        }
      },

      {
        "$project": {
          "user_id": 1,
          "name": 1,
          'fieldOfWork': '$field_of_work',
          "experience.company_name": 1,
          "experience.designation": 1,
          "education": 1,
          'mentorType': 1,
          'industry': 1,
          "mentorFor": "$user.mentorFor.name",
          "mentorPrice": {"$toInt": "$user.mentorPrice"},
          "about": "$user.about",
          "current_location": "$user.current_location",
          "profilePic": "$user.profilePic",
          "talent_board": "$user.talent_board",
          "rating": "$user.rating",
          'language': 1
        }
      },
    ])


# TODO: when the query contains few fields the result might be empty - SOLVE IT
@blp.route('/autocomplete/search-params-and-values')
class MentorsAutocompleteSearchParamsAndValues(MethodView):
  @blp.arguments(MentorsAutocompleteRequestSchema, location='query')
  @blp.response(200, MentorsAutocompleteResponseSchema)
  def get(self, args: dict):
    """Autocompletes possible values and mentor profile fields where those values can be found"""
    query = args.pop("query")
    return execute_query_with_params(args, autocomplete_values, [
      {
        "$search": {
          "index": "autocomplete",
          "autocomplete": {
            "query": query,
            "path": "value"
          }
        },
      },
    ])


# TODO: add an appropriate index
@blp.route('/autocomplete/search-param-values')
class MentorsSearchAutocompleteSearchParameterValues(MethodView):
  @blp.arguments(MentorsAutocompleteRequestSchema, location='query')
  @blp.response(200, MentorsAutocompleteResponseSchema)
  def get(self, args: dict):
    """Autocompletes possible values for one search parameter"""
    query = args.pop('query')
    return execute_query_with_params(args, autocomplete_values, [
      {
        "$search": {
          "index": "autocomplete",
          "autocomplete": {
            "query": query,
            "path": "field_name"
          }
        },
      },
    ])


@blp.route('/filter-param-values')
class filter_parameters(MethodView):
  @blp.arguments(MentorsFilterRequestSchema, location='query')
  @blp.response(200, MentorsFilterResponseSchema)

  def get(self, args: dict):
    """Autocompletes possible values for one search parameter"""
    field_name = args.pop('field_name')
    filter_values = (get_filter_values(autocomplete_values, field_name))
    print(filter_values)
    return{"data": filter_values}

api.register_blueprint(blp)

if __name__ == '__main__':
  app.run(host='localhost', port=port)
