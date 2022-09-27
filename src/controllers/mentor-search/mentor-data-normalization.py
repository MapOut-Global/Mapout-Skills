from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import nltk

# run the below commands within the script to install libraries first time on local 
# on server no need to run these commands within the script
#nltk.download('stopwords')
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('omw-1.4')

from dotenv import load_dotenv

from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

lemmatizer = WordNetLemmatizer()

import os #provides ways to access the Operating System and allows us to read the environment variables

load_dotenv()
URI = os.getenv("MONGODB_STAGING_URI")
database = os.getenv("DATABASE")

#point the client at mongo URI
client = MongoClient(URI)

db = client[database]
#select the collection within the database
users = db.users

def flatten(l):
    return [item for sublist in l for item in sublist]

def text_preprocessing(text):
  # method to remove stop words and non alphanumeric characters from text
  text = re.sub('[^A-Za-z0-9]+', ' ',text)
  text = text.lower()
  words = nltk.word_tokenize(text)
  words = [lemmatizer.lemmatize(word) for word in words if word not in set(stopwords.words('english'))]
  sentence = ' '.join(words)
  return sentence

def get_values_from_list_of_dict(obj):
  # method to extract values from list of objects(or dictionary)
  try :
    values = [list(x.values()) for x in obj]
    #print(values)
    try: 
      values1 = " ".join(list(values))
      return (values1)
    except TypeError:
      try:
        values1 = " ".join(flatten(list(x.values() for x in obj)))
      except TypeError:
        industry = " ".join(list(x['industry'] for x in obj))
        resp = " ".join(flatten(list(x['responsibilities'] for x in obj)))
        try:
          company_name = " ".join(list(x['company_name'] for x in obj))
        except KeyError:
          company_name = " " 
        
        try:
          designation = " ".join(list(x['designation'] for x in obj))
        except:
          designation = " "
          
        values1 = industry + " " + resp + " " + company_name + " " + designation
      return values1
      
  except IndexError :
    return ''


def get_values(obj):
  # method to extract values from an object(or dictionary)
  try :
    values1 = " ".join(flatten(([list(x.values()) for x in obj])))
    return (values1)
  except IndexError :
    return ''

def get_values_from_list_of_list(obj,name):
  # method to extract values from a list of lists
  try :
    values = [x[name] for x in obj]
    values1 = " ".join(list(values))
    return (values1)
  except IndexError :
    return ''


def get_talent_board_details(x):
  # method to extract values from Talent Board
  try:
    values = get_values_from_list_of_dict(x['talent_boards'])
    return values
  except TypeError:
    return ''

def normalize_mentor_data():
    # main method to normalize data, generate corpus for individual fields and upload to mentorDetails collectionx
    try :
        res = users.aggregate([
            
            {"$match": {"mentor_status" : 2, "candidate_dashboard_visibility": True}},
    
                { "$lookup": {
            "from": "educations",
            "localField": "education",
            "foreignField": "_id",
            "as": "education"
            }},    
        
                { "$lookup": {
            "from": "experiences",
            "localField": "experience",
            "foreignField": "_id",
            "as": "experience"
            }},
            
                { "$lookup": {
            "from": "technicalSkills",
            "localField": "technical_skills.skill",
            "foreignField": "_id",
            "as": "tech_skill"
            }},

            { "$lookup": {
            "from": "softSkills",
            "localField": "soft_skills",
            "foreignField": "_id",
            "as": "soft_skill"
            }},

            { "$lookup": {
            "from": "languages",
            "localField": "languages.name",
            "foreignField": "_id",
            "as": "language"
            }},


            {
                "$project":{
                    "name":1,
                    "about":1,
                    "tech_skill.name":1,
                    "soft_skill.name":1,
                    "language.language":1,
                    "education.university_name":1,
                    "education.degree":1,
                    "education.description":1,
                    "education.specialization":1,
                    "experience.company_name":1,
                    "experience.designation":1,
                    "experience.industry":1,
                    "experience.responsibilities":1,
                    "mentorFor.name":1,
                    "mentorTo.name":1,
                    "field_of_work":1,
                    "industry":1,
                    "mentorType":1,
                    "talent_board.talent_boards.title":1,
                    "talent_board.talent_boards.description":1,

                
                }
            }
        
        ])

        # convert the res object into a dataframe to perform preprocessing
        df = pd.DataFrame(res)

        # create a corpus consisting education details
        df['educationcorpus'] = df['education'].apply(lambda x : get_values_from_list_of_dict(x))

        # create a corpus consisting experience details
        df['experiencecorpus'] = df['experience'].apply(lambda x : get_values_from_list_of_dict(x))

        # create a corpus consisting technical skills details
        df['techskillcorpus'] = df['tech_skill'].apply(lambda x : get_values_from_list_of_list(x,'name'))
        
        # create a corpus consisting soft skills details
        df['softskillcorpus'] = df['soft_skill'].apply(lambda x : get_values_from_list_of_list(x,'name'))

        # create a corpus consisting languages details
        df['languages'] = df['language'].apply(lambda x : get_values_from_list_of_list(x,'language'))

        # create a corpus consisting talent board details
        df['talentboards'] = df['talent_board'].apply(lambda x : get_talent_board_details(x))

        # pre-process the field mentorTo 
        df['mentorTo'].fillna("",inplace=True)
        df['mentorTo'] = df['mentorTo'].apply(lambda x : get_values_from_list_of_list(x,'name'))

        # pre-process the field mentorFor
        df['mentorFor'].fillna("",inplace=True)
        df['mentorFor'] = df['mentorFor'].apply(lambda x : get_values_from_list_of_list(x,'name'))

        # pre-process the about me section
        df['about'].fillna(' ', inplace=True)
        df['about'] = df['about'].apply(lambda x : text_preprocessing(x))

        # pre-process the corpus consisting education details
        df['educationcorpus'] = df['educationcorpus'].apply(lambda x : text_preprocessing(x))

        # pre-process the corpus consisting experience details
        df['experiencecorpus'] = df['experiencecorpus'].apply(lambda x : text_preprocessing(x))

        # pre-process the corpus consisting talent board details
        df['talentboards'] = df['talentboards'].apply(lambda x : text_preprocessing(x))

        # fill NaN with empty space so that it doesnt disturb the structure of dataframe 
        df.fillna(" ",inplace=True)

        # create a corpus consisting all the fields (overall features of a mentor profile)
        df['corpus'] = (df['name'] + ' ' + df['languages'] + ' ' + df['field_of_work'] + ' '  + df['industry'] + ' ' + df['techskillcorpus'] + ' ' + df['softskillcorpus'] + ' ' + df['educationcorpus'] + ' ' + df['experiencecorpus'] + ' ' + df['talentboards'] + ' ' + df['about']) + ' ' + df['mentorType'] + ' ' + df['mentorTo'] + ' ' + df['mentorFor']
        
        # rename the field _id taken from users collection to user_id in mentorDetails collection
        df.rename(columns={"_id":"user_id"},inplace=True)
        
        # convert the dataframe into a dictionary again (JSON format)
        profileData = df.to_dict(orient='records')
        
        # connect the new collection, remove previous data and insert new mentor data
        mentorDetailscollection = db['mentorDetails']
        mentorDetailscollection.remove()
        mentorDetailscollection.insert_many(profileData)
    
        status = 'success'
        return status

    except :
        status = 'failed'
        return status

print("Mentor Details normalization status : started at {}".format(datetime.now()))

normalization_status = normalize_mentor_data()

print("Mentor Details normalization status : {} at {}".format(normalization_status,datetime.now()))