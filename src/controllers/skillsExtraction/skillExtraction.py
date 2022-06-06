# import required python function
from skills_ml.ontologies.onet import Onet
from skills_ml.datasets.onet_cache import OnetSiteCache
from skills_ml.storage import FSStore
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from skills_ml.algorithms.skill_extractors import FuzzyMatchSkillExtractor, ExactMatchSkillExtractor
from utils import extractInterest, removeStopwords
import sys
import os
from io import BytesIO, StringIO
import io
import urllib.request
# import libraries
from nltk.corpus import stopwords
import pandas as pd
import spacy

nlp = spacy.load('en_core_web_sm')

#from resume_parser import *

#from resume_parser 

# skill_data = pd.read_csv("./Database/skills_set", delimiter="\t")
# database_path = "./Database"
skill_data = pd.read_csv("./src/controllers/skillsExtraction/Database/skills_set", delimiter="\t")
database_path = "./src/controllers/skillsExtraction/Database"
onet_cache = OnetSiteCache(FSStore(database_path))
onet = Onet(onet_cache)
skill_extractors = [
    FuzzyMatchSkillExtractor(onet.competency_framework),
    ExactMatchSkillExtractor(onet.competency_framework),
]
competencies = onet.competencies
id_lookup = dict((competency.identifier, competency.categories) for competency in competencies)
extra_words = ["able", "self", "sr", "basic", "skill"]
extra_stop_words = set(stopwords.words("english") + extra_words)

def pdf_from_url_to_txt(url):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    f = urllib.request.urlopen(url).read()
    fp = BytesIO(f)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(fp,
                                  pagenos,
                                  maxpages=maxpages,
                                  password=password,
                                  caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str


def get_skills(text, flag=False):
    skills_category = {"Description": text}
    skills = {}
    for skill_extractor in skill_extractors:
        candidate_skills = list(
            skill_extractor.candidate_skills_raw(extractInterest(["NN", "JJ"], removeStopwords(str(text)), from_spacy=True))
        )
        if len(candidate_skills):
            for i in candidate_skills:
                if len(i.skill_name) > 1:
                    skills[i.skill_name] = {
                        "matched_skill_identifier": id_lookup[i.matched_skill_identifier],
                        "skill_extractor_name": i.skill_extractor_name,
                    }
    for word in skills:
        if word not in extra_stop_words:
            classes = skills[word]["matched_skill_identifier"]  # skills category
            # print(classes)
            for skilltype in classes:
                if flag:
                    if skilltype in skills_category.keys():
                        skills_category[skilltype].append(word)
                    else:
                        skills_category[skilltype] = []
                        skills_category[skilltype].append(word)
                else:
                    if skilltype in skills_category.keys():
                        skills_category[skilltype].append(word)
                    else:
                        skills_category[skilltype] = []
                        skills_category[skilltype].append(word)

    return skills_category


def skills_extraction(text):
    # print(text)
    # text = """JOB DESCRIPTION:  Local Business looking for a full-time SAFETY COORDINATOR.    Specific duties include but not limited to:  * Recommend & implement safety policies  * Responsible for Hazardous Communication response  * Responsible for training; Hazardous Communication and Hazardous Waste Management, Safety Orientation, Forklift, Scissor lift, JLG, Lock-out/Tag-out, Confined Space & misc. safety training  * Coordinate First Aid & CPR training   * Coordinate Safety Committee activities  * Arrange hazardous waste disposal   * Complete weekly facility checklist  * Other duties as assigned by management      JOB REQUIREMENTS:  SKILLS & EDUCATIONAL REQUIREMENTS   * 5 year minimum in the trades.  * GED/HS EQUIVALENCY  * Must have a current (Washington) driver license, to operate a company vehicle in the performance of job duties   * Industrial safety training & off-site.  * Must be able to speak (read, write) English to understand work and safety instructions, and/or training for the job.   * Hazardous Communication and Hazardous Waste Management training required.   * Proficient in Microsoft Office (Word, Excel, Outlook & Access).   * Ability to meet time constraints.   * Good communication skills.   * Employer will screen for work history that demonstrates ability to be punctual, dependable, and with a record of good attendance.    We are a Drug-Free company and a Foreign Trade Zone. All applicants must pass a U.S. Customs security background investigation (i.e. NCIC & local/state warrant check) prior to employment.    WORKING CONDITIONS   Extreme temperatures (hot, cold, humid, wet), working in confined spaces, tripping hazards (curbing, uneven surfaces), slippery floors, steam pipes accessible, climbing (ladders, stairs, etc.) ability to lift 65 lbs. or more.    HOURS / DAYS / SCHEDULE:  Position is hourly, full benefits, M-F 08:00-16:30 with potential overtime."""
    result = get_skills(text)
    print(result)

url = "https://demo1-app-bucket.s3.ap-south-1.amazonaws.com/Nithin_Resume.pdf"
text = pdf_from_url_to_txt(url)
nlp_text = nlp(text)

skills = skills_extraction(nlp_text)
print(skills)
# skills_extraction()
