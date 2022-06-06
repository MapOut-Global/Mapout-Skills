import email
from tkinter import N
from tracemalloc import stop
from unicodedata import name
from unittest import TextTestResult
from itsdangerous import json
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
from scipy.misc import face
import spacy 
from io import BytesIO, StringIO
import urllib.request
from urllib.parse import quote
import json

import pathlib

import pandas as pd

import re

from spacy.matcher import Matcher
import sys

import docx2txt

import nltk
#nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('stopwords')
from nltk.corpus import stopwords

#nltk.download('omw-1.4')

stopwords = set(stopwords.words('english'))


from spacy.lang.en import English

nlp=English()

# load pre-trained model
nlp = spacy.load('en_core_web_sm')

database_path = "./src/controllers/resumeParser/Database"

titles = {
    "headline": ["Headline"],
    "personal": [
      "personal info",
      "personal",
      "details",
      "personal information",
      "personal details",
      "Personal summary",
    ],
    "summary": [
      "summary",
      "About",
      "abstract",
      "profile",
      "brief",
      "About Me",
      "overview",
      "objective",
      "Personal Profile",
      "objectives",
      "WHO AM I",
      "Career Objective",
      "PROFESSIONAL SUMMARY",
      "PROFESSIONAL PROFILE",
      "Seeking position as a",
      "Seeking position as an",
      "PROFESSIONAL BIO",
      "Personal summary",
      "Personal bio",
      "Career summary",
      "Professional History",
      "Background",
      "Personal statement",
      "Profili",
      "Profil",
      "Introduction",
    ],
    "experience": [
      "E X P E R I E N C E",
      "Relevant Work Experience",
      "work experience",
      "W O R K",
      "work exp",
      "experience",
      "career progression",
      "employment record",
      "employment history",
      "Employment Experience",
      "professional experience",
      "Work History",
      "Professional bio",
      "Professional biography",
      "teaching experience",
      "Relevant Experience",
      "Selected Experience",
      "Professional Background",
      "EMPLOYMENT",
      "Career Highlights",
      "Experience highlights",
      "EDUCATION AND TRAINING",
      "Military experience"
    ],
    "positions":[
      "positions of responsibility"
      "positions held",
      "positions",
      "position held",
      "positions of responsibilties"
    ],
    "education": [
      "E D U C A T I O N",
      "education",
      "certification and awards",
      "certificates & awards",
      "certificates/awards",
      "certification & awards",
      "certification/ awards",
      "licenses & certifications",
      "Certificates and Clearances",
      "other certificates",
      "education and training",
      "education & training",
      "higher education",
      "Educational qualifications",
      "Education highlights",
      "ACADEMICS",
      "ACADEMIC PURSUIT",
      "ACADEMIC QUALIFICATIONS",
      "QUALIFIED UNIVERSITY",
      "QUALIFIED UNIVERSITIES",
      "ACADEMIC BACKGROUND",
      "EDUCATIONAL BACKGROUND",
      "ACADEMIC DETAILS",
      "ACADEMIC  RECORD",
      "PROFESSIONAL & ACADEMIC QUALIFICATIONS",
      "Education and Qualifications",
      "Education & Qualifications",
      "Education, Honors, and Certifications",
      "Auxiliary Education",
      "DEGREE",
      "certification",
      "certificates"
    ],
    "skills": [
      "skills",
      "technical skills & languages",
      "Skills & Expertise",
      "A R E A O F E X P E R T I S E",
      "AREAS OF EXPERTISE",
      "skills summary",
      "KEY SKILLS AND COMPETENCIES",
      "Skills & Competencies",
      "Skills and Competencies",
      "Skills/Competencies",
      "SKILLS / IT SKILLS",
      "competencies",
      "competency",
      "strengths",
      "strength",
      "Key Skills",
      "Primary Skills",
      "professional skills",
      "professional",
      "related skills",
      "language and computer skills",
      "summary of qualifications",
      "summary of skills",
      "Qualifications summary",
      "SKILLS AND ABILITIES",
      "special skills",
      "SPECIAL SKILLS AND ABILITIES",
      "Core Competencies/Skills",
      "Core Skills",
      "Core Competencies",
      "Core Competencies and Skills",
      "Core Competencies & Skills",
      "KEY SKILLS & COMPETENCIES",
      "KEY SKILLS/COMPETENCIES",
      "HARD & SOFT SKILLS",
      "HARD AND SOFT SKILLS",
      "Core Competencies/Areas of Expertise",
      "Relevant skills",
      "Experience & Skills",
      "specialties",
      "specialties, capabilities",
      "specialties & capabilities",
      "specialties and capabilities",
      "specialties/capabilities",
      "lists of skills",
      "Skills/Training",
      "Digital skills",
      "tech skills",
      "technical skills",
      "personal skills",
      "personality skills",
      "soft skills",
      "computer skills",
      "software skills",
      "IT Skills",
      "Relevant IT skills",
      "Relevant Software skills",
      "Interpersonal and Teamwork Skills",
      "Quantitative Skills",
      "Programming skills",
      "Coding skills",
      "Other skills",
    ],
    "languages": ["languages", "language skills", "foreign languages", "linguistic","linguistic proficiency", "linguistic skills"],
    "courses": [
      "PROFESSIONAL TRAINING",
      "Training",
      "Personal development",
      "Courses",
      "Seminars",
      "Courses attended",
      "Training & Seminars",
      "Personal development courses",
      "Workshops",
      "Training, Seminars, Workshops",
      "training course",
      "training courses",
      "Training/ Seminars/Workshops",
      "Career development courses",
      "Personal development courses",
      "Seminars & Conferences",
      "Seminars and Conferences",
      "Conferences and Seminars",
      "Conferences & Seminars",
      "Conferences",
      "Professional development",
      "Continuing Education",
    ],
    "projects": [
      "PROJECT",
      "PROJECTS",
      "Projects",
      "portfolio",
      "my portfolio",
      "RESEARCH INTERESTS",
      "RESEARCHES",
      "portfolio",
      "PERSONAL PROJECTS",
      "Projects implemented",
      "Implemented projects",
      "Ongoing projects",
      "Projects authored",
      "Authored projects",
      "Projects & Programs",
    ],
    "contacts": ["Contact Information", "Contact details", "Contact info"],
    "awards": [
      "awards",
      "honors",
      "HONORS/AWARDS",
      "HONORS & AWARDS",
      "HONORS and AWARDS",
      "Patents",
      "Patent",
      "Selected projects",
      "academic projects"
      "achievements"
      "OTHER ACHIEVEMENTS",
      "KEY ACHIEVEMENTS",
      "ACHIEVEMENTS",
      "a c h i e v e m e n t s"
    ],
    "additional": [
      "Other (additional specialties, capabilities)",
      "Additional info",
      "Additional details",
      "Additional information",
      "Additional details",
      "Other details",
    ],
    "interests": ["interests", "INTEREST & HOBBIES"],
    "references": [
      "R E F E R E N C E S",
      "references",
      "professional references",
      "Testimonials",
      "Recommendations",
    ],
  "profiles": [
    "github.com",
    "linkedin.com",
    "facebook.com",
    "fb.com",
    "bitbucket.org",
    "stackoverflow.com",
  ]
}

RESUME_SECTIONS =  [
                    'summary',
                    'experience',
                    'education',
                    'languages',
                    'projects',
                    'awards',
                    'interests',
                    'profiles',
                    'skills',
                    'courses',
                    'positions'
                ]

    
qualification = [
            'BE','B.E.', 'B.E', 'BS', 'B.S', 
            'Bachelor','Bachelors','M.E', 'M.E.', 'MS', 'M.S', 
            'BTECH', 'B.TECH','B.TECH ' ,'M.TECH', 'MTECH', 
            'SSC', 'HSC', 'X', 'XII','B. TECH', '10TH','12TH',
            '12 TH','10 TH','BTECH '  
        ]

awards = ("|".join(list(titles['awards'])))
awards = awards.lower()
awardsregex ="r'" + awards + "'"

skillregex = ("|".join(list(titles['skills'])))
skillregex = skillregex.lower()
skillsregex ="r'" + skillregex + "'"

profiles = ("|".join(list(titles['profiles'])))
profiles = profiles.lower()
profilesregex ="r'" + profiles + "'"

positions = ("|".join(list(titles['positions'])))
positions = positions.lower()
positionsregex ="r'" + positions + "'"

projects = ("|".join(list(titles['projects'])))
projects = projects.lower()
projectsregex ="r'" + projects + "'"

education = ("|".join(list(titles['education'])))
education = education.lower()
educationregex ="r'" + education + "'"

summary = ("|".join(list(titles['summary'])))
summary = summary.lower()
summaryregex ="r'" + summary + "'"

experience = ("|".join(list(titles['experience'])))
experience = experience.lower()
experienceregex ="r'" + experience + "'"

languages = ("|".join(list(titles['languages'])))
languages = languages.lower()
languagesregex ="r'" + awards + "'"

interests = ("|".join(list(titles['interests'])))
interests = interests.lower()
interestsregex ="r'" + interests + "'"

courses = ("|".join(list(titles['courses'])))
courses = courses.lower()
coursesregex ="r'" + courses + "'"

resume_sections = ("|".join(list(RESUME_SECTIONS)))
resume_sections = resume_sections.lower()
rsregex ="r'" + resume_sections + "'"

# reading the csv file
#data = pd.read_excel("./src/controllers/resumeParser/Database/job_titles.xlsx") 
data = pd.read_excel("E:/mapout-resume-parser/mapout-skills/src/controllers/resume-parser/Database/job_titles.xlsx")
#skills_data = skills_data.applymap(lambda x: x.lower() if pd.notnull(x) else x)
data = data.apply(lambda x: x.astype(str).str.lower())
jobtitles = list(data['name'].values)

titles = ("|".join(list(jobtitles)))
titles = titles.lower()
#titles = re.sub(',',' ',titles)
titlesregex ="r'" + titles + "'"

degrees = ("|".join(list(qualification)))
degrees = degrees.lower()
#titles = re.sub(',',' ',titles)
degreesregex ="r" + degrees + ""

#uni = pd.read_excel('./src/controllers/resumeParser/Database/mapout_universities.xlsx')
uni = pd.read_excel('E:/mapout-resume-parser/mapout-skills/src/controllers/resume-parser/Database/mapout_universities.xlsx')
uni.drop(['Unnamed: 0'],axis=1,inplace=True)
uni = uni.applymap(str.lower)
uni['University'] = uni['University'].str.replace(",","")
universities = list(uni['University'].values)
unis = ("|".join(list(universities)))
uniregex ="r'" + unis + "'"

""""
def pdf_reader(url):
    req = urllib.request.Request(url)#, headers={'User-Agent' : "Magic Browser"})
    remote_file = urllib.request.urlopen(req).read()
    remote_file_bytes = io.BytesIO(remote_file)
    pdfdoc_remote = PyPDF2.PdfFileReader(remote_file_bytes)

    for i in range(pdfdoc_remote.numPages):
        text = ' '
        current_page = pdfdoc_remote.getPage(i)
        text = text + (current_page.extractText())

    return text
"""

def text_extraction(url):
  text = ''
  file_extension = pathlib.Path(url).suffix
  
  if file_extension == '.pdf':
    text = pdf_from_url_to_txt(url)
  
  elif file_extension == '.doc':
    text = extract_text_from_doc(url)

  elif file_extension == '.docx':
    text = extract_text_from_docx(url)

  else :
    print("invalid file format")
  
  return text

def pdf_from_url_to_txt(url):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    #url = url.replace(" ","")
    
    f = urllib.request.urlopen((url)).read()
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

def extract_text_from_docx(url):
    
    try:
        f = urllib.request.urlopen(url).read()
        fp = BytesIO(f)
        temp = docx2txt.process(fp)
        text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
        return ' '.join(text)
    except KeyError:
        return ' '


def extract_text_from_doc(url):
    
    try:
        try:
            import textract
        except ImportError:
            return ' '
        f = urllib.request.urlopen(url).read()
        fp = BytesIO(f)
        text = textract.process(fp).decode('utf-8')
        return text
    except KeyError:
        return ' '

def extract_email(text):

    # regular expression for email address
    email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", str(text))
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None


def extract_mobile_number(text):
     
      mob_num_regex = r'((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))'
      
      phone = re.findall(re.compile(mob_num_regex), str(text))

      if phone:
        primary_number = ''.join(phone[0])
        if len(primary_number)<9:
          primary_number = ''
        
        try:
          secondary_number = ''.join(phone[1])
          if len(secondary_number)<9:
            secondary_number = ''
          if primary_number == '':
            primary_number = secondary_number
            secondary_number = ''
        except IndexError:
          secondary_number=''

        return primary_number

def titles_sub(text1):
  new_text = text1
  new_text = re.sub(skillsregex,'skills',text1.lower(),flags=re.MULTILINE)
  new_text = re.sub(summaryregex,'summary',new_text.lower(),flags=re.MULTILINE)
  new_text = re.sub(educationregex,'education',new_text.lower(),flags=re.MULTILINE)
  #print(re.findall(experienceregex,new_text.lower()))
  new_text = re.sub(experienceregex,'experience',new_text.lower(),flags=re.MULTILINE)
  new_text = re.sub(projectsregex,'projects',new_text.lower(),flags=re.MULTILINE)
  new_text = re.sub(languagesregex,'languages',new_text.lower(),flags=re.MULTILINE)
  new_text = re.sub(interestsregex,'interests',new_text.lower(),flags=re.MULTILINE)
  new_text = re.sub(profilesregex,'profiles',new_text.lower(),flags=re.MULTILINE)
  new_text = re.sub(awardsregex,'awards',new_text.lower(),flags=re.MULTILINE)
  new_text = re.sub(coursesregex,'courses',new_text.lower(),flags=re.MULTILINE)
  new_text = re.sub(positionsregex,'positions',new_text.lower(),flags=re.MULTILINE)

  return new_text

def find_dates(resume_text):

    month1 = ''
    year1 = ''
    month2 = ''
    year2 = ''


    resume_text = resume_text.replace(" to ", " - ")
    resume_text = resume_text.replace(" till ", " - ")
    resume_text = resume_text.replace(" until ", " - ")
    #resume_text = resume_text.replace("till date"," - now ")
    #print(resume_text)
    not_alpha_numeric = r'[^a-zA-Z\d]'

    # Various month format definitions
    months_short = r'(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)|(aug)|(sep)|(oct)|(nov)|(dec)'
    months_long = r'(january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december)'
    months_numeric = r'(?<![\d])\d{1,2}(?![\d])'
    month_alphabetic = r'(' + months_short + r'|' + months_long + r')'
    month_numeric_long = r'([\d]{1,2})(?=[^A-Za-z]{1}[\d]{4})'
    month = r'(' + months_short + r'|'+ months_long + r'|' + months_numeric + r'|' + month_alphabetic + r'|' + month_numeric_long + r')'
    #print(month)
    year = r'((20|19)(\d{2}))'
    # Double (normal) year range (e.g.: 2020 - 2022)
    double_year_range = year + not_alpha_numeric + r"{1,3}" + year

    # Multi year range (e.g.: 2013 - 2018 - 2022)
    multi_year_range = r'(' + year + '(' + not_alpha_numeric + r'{1,3}' + year + '){1,5})|(' + year +\
                        not_alpha_numeric + r'{1,3}' + r')'

    # Start Date definitions in various formats
    start_date_alphabetic = month_alphabetic + not_alpha_numeric + r"{1,3}" + year
    start_date_numeric = months_numeric + not_alpha_numeric + r'{1,3}' + year
    start_date_numeric_long = r'[\d]{1,2}[^a-zA-Z\d]?' + months_numeric + not_alpha_numeric + r'?' + year
    start_date_alphabetic_long = r'[\d]{1,2}[^a-zA-Z\d]?' + month_alphabetic + not_alpha_numeric + r'?' + year

    # End Date definitions in various formats
    end_date_alphabetic = r'((' + month_alphabetic + not_alpha_numeric + r"{1,3}" + year + r')|(present)|(now)|(today))'
    end_date_numeric = r'((' + months_numeric + not_alpha_numeric + r"{1,3}" + year + r')|(present)|(now)|(today))'
    end_date_numeric_long = r'(([\d]{1,2}[^a-zA-Z\d]?' + months_numeric + not_alpha_numeric + r"?" + year + r')|(present)|(now)|(today))'
    end_date_alphabetic_long = r'(([\d]{1,2}[^a-zA-Z\d]?' + month_alphabetic + not_alpha_numeric + r"?" + year + r')|(present)|(now)|(today))'

    # Date Range alphabetic (e.g.: April 2019 - May 2022)
    date_range_alphabetic = r"(" + start_date_alphabetic + not_alpha_numeric + r"{1,3}" + end_date_alphabetic + r")|(" + double_year_range + r")"

    # Date Range numberic (e.g.: 01.2020 - 12.2021)
    date_range_numeric = r"(" + start_date_numeric + not_alpha_numeric + r"{1,3}" + end_date_numeric + r")"
    # Date Range numeric long format (e.g.: 15.01.2019- 31.07.2020)
    date_range_numeric_long = r"(" + start_date_numeric_long + not_alpha_numeric + r"{1,3}" + end_date_numeric_long + r")"
    #print(date_range_numeric_long)
    # Date Range alphabetic long format (e.g.: 15. May 2021 - 16. July 2022)
    date_range_alphabetic_long = r"(" + start_date_alphabetic_long + not_alpha_numeric + r"{1,3}" + end_date_alphabetic_long + r")"

    # DD.MM.YYYY - DD.MM.YYYY Date range in numeric format
    date_range_long_numeric = r'(' + date_range_numeric_long + r')' + not_alpha_numeric + r'{1,4}'
    # DD.MM.YYYY - DD.MM.YYYY Date range in alphabetic format
    date_range_long_alphabetic = r'(' + date_range_numeric_long + r')' + not_alpha_numeric + r'{1,4}'

    
    # MM.YYYY-MM.YYYY Date range in either alphabetic or numeric format
    date_range = r'(' + date_range_alphabetic + r'|' + date_range_numeric + r'|' + date_range_numeric_long + r')'  + r'(' + not_alpha_numeric + r'{1,4}|$)'

    # Open-ended durations, where only start date is present (e.g: 2.2015 - )
    start_date_only = r'(?<![^A-Za-z]{5})' + r'(' + start_date_numeric + r'|' + start_date_alphabetic + r')' + r'(?![^A-Za-z]{5})'

    # Month range (e.g.: From 02-04 2014 finds 02-04)
    month_range = r'(' + month_alphabetic + r'|' + months_numeric + r')' + not_alpha_numeric + r"{1,4}" + r'(' + \
                  month_alphabetic + r'|' + months_numeric + r')' + not_alpha_numeric + r"{1,2}" + year

    range = (re.search(date_range,resume_text.lower()))
    #print(range)


    try:
      range = resume_text[range.start():range.end()]
      range = str(range)
      starting = (range.split("-")[0])
      start_month = (re.search(re.compile(month),starting.lower()))
      start_year = (re.search(re.compile(year),starting.lower()))
      #print(start_month)
      month1 = starting[start_month.start():start_month.end()]
      year1 = starting[start_year.start():start_year.end()]
      
      try:
        end = (range.split("-")[1])
        end_month = (re.search(re.compile(month),end.lower()))
        end_year = (re.search(re.compile(year),end.lower()))
        month2 = end[end_month.start():end_month.end()]
        year2 = end[end_year.start():end_year.end()]

      except AttributeError:
        month2 = "Present"
        year2 = "Present"

    except :
      start_year = (re.findall(re.compile(year),resume_text.lower()))
      start_month = (re.search(re.compile(month),resume_text.lower()))
      #print(start_month)
      if start_month:
        month1 = start_month.group()

      if start_year:
        year1 = start_year[0][0]
        
        try:
          year2 = start_year[1][0]
        
        except:
          if year2 == '':
            year2 = year1
            month2 = month1
            year1 = ''
            month1 = ''
      else:
        ''

    return (month1, year1, month2, year2)

"""
def extract_experience(text):
    
    wordnet_lemmatizer = WordNetLemmatizer()

    # word tokenization
    word_tokens = nltk.word_tokenize(str(text))

    # remove stop words and lemmatize
    filtered_sentence = [
            w for w in word_tokens if w not
            in stopwords and wordnet_lemmatizer.lemmatize(w)
            not in stopwords
        ]
    sent = nltk.pos_tag(filtered_sentence)

    # parse regex
    cp = nltk.RegexpParser('P: {<NNP>+}')
    cs = cp.parse(sent)

    # for i in cs.subtrees(filter=lambda x: x.label() == 'P'):
    #     print(i)

    test = []

    for vp in list(
        cs.subtrees(filter=lambda x: x.label() == 'P')
    ):
        test.append(" ".join([
            i[0] for i in vp.leaves()
            if len(vp.leaves()) >= 2])
        )

    # Search the word 'experience' in the chunk and
    # then print out the text after it
    x = [
        x[x.lower().index('experience') + 10:]
        for i, x in enumerate(test)
        if x and 'experience' in x.lower()
    ]
    return x

"""

"""
def extract_education(text):
    
    nlp_text = nlp(str(text))

    # Sentence Tokenizer
    nlp_text = [sent.text.strip() for sent in nlp_text.sents]

    edu = {}
    # Extract education degree
    for index, text in enumerate(nlp_text):
        for tex in text.split():
            # Replace all special symbols
            tex = tex.strip()
            tex = re.sub(r'[?|$|.|!|,|-]', r'', tex)
            if tex.upper() in qualification and tex not in stopwords:
                edu[tex] = text + nlp_text[index + 1]

    # Extract year
    education = []
    for key in edu.keys():
        year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
        if year:
            education.append((key, ''.join(year[0])))
        else:
            education.append(key)
    
    return education
"""

def extract_skills(resume_text):
    
    nlp_text = nlp(resume_text)
    #print(nlp_text)
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]

    # reading the csv file
    #skills_data = pd.read_csv("./src/controllers/resumeParser/Database/mapout_technical_skills.csv") 
    skills_data = pd.read_csv('E:/mapout-resume-parser/mapout-skills/src/controllers/resume-parser/Database/mapout_technical_skills.csv')

    #skills_data = skills_data.apply(lambda x: x.astype(str).str.upper())
    # extract values
    #skills = list(skills_data['Element Name'].values)
    skills = list(skills_data['name'].values)
    #skills = list(skills_data.columns.values)
    #print(skills)
    #print(skills)
    
    skillset = []
    
    # check for 1-word skills (example: python)
    for token in tokens:
        token = token.strip()
        #print(token)
        if token.lower() in skills:
            skillset.append(token)
    
    # check for multiple-word skills (example: machine learning)
    for token in nlp_text.noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    
    return [i.capitalize() for i in set([i.lower() for i in skillset])]


def soft_skills(resume_text):
    
    resume_text = re.sub('/n', ' ', str(resume_text))
    nlp_text = nlp(resume_text)
    #print(nlp_text)
    #print(nlp_text)
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]

    # reading the csv file
    #skills_data = pd.read_csv("./src/controllers/resumeParser/Database/mapout_soft_skills.csv") 
    skills_data = pd.read_csv('E:/mapout-resume-parser/mapout-skills/src/controllers/resume-parser/Database/mapout_soft_skills.csv')

    #skills_data = skills_data.applymap(lambda x: x.lower() if pd.notnull(x) else x)
    #skills_data = skills_data.apply(lambda x: x.astype(str).str.upper())
    # extract values
    #skills = list(skills_data['Element Name'].values)
    skills = list(skills_data['name'].values)
    #skills = list(skills_data.columns.values)
    #print(skills)
    #print(skills)
    
    skillset = []
    
    # check for 1-word skills (example: python)
    for token in tokens:
        token = token.strip()
        #print(token)
        if token.lower() in skills:
            skillset.append(token)
    
    # check for multiple-word skills (example: machine learning)
    for token in nlp_text.noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    
    return [i.capitalize() for i in set([i.lower() for i in skillset])]


def extract_languages(resume_text):
    
    resume_text = re.sub('/n', ' ', str(resume_text))
    nlp_text = nlp(resume_text)
    #print(nlp_text)
    #print(nlp_text)
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]

    # reading the csv file
    #data = pd.read_csv("./src/controllers/resumeParser/Database/languages.csv") 
    data = pd.read_csv('E:/mapout-resume-parser/mapout-skills/src/controllers/resume-parser/Database/languages.csv')

    #skills_data = skills_data.applymap(lambda x: x.lower() if pd.notnull(x) else x)
    data = data.apply(lambda x: x.astype(str).str.lower())
    # extract values
    #skills = list(skills_data['Element Name'].values)
    languages = list(data['language'].values)
    #print(languages)
    #skills = list(skills_data.columns.values)
    #print(skills)
    #print(skills)
    
    langset = []
    
    # check for 1-word skills (example: python)
    for token in tokens:
        token = token.strip()
        #print(token)
        if token.lower() in languages:
            langset.append(token)
    
    # check for multiple-word skills (example: machine learning)
    for token in nlp_text.noun_chunks:
        token = token.text.lower().strip()
        if token in languages:
            langset.append(token)
    
    return [i.capitalize() for i in set([i.lower() for i in langset])]

def extract_hobbies(resume_text):
    
    resume_text = re.sub('/n', ' ', str(resume_text))
    nlp_text = nlp(resume_text)
    #print(nlp_text)
    #print(nlp_text)
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]

    # reading the csv file
    #data = pd.read_csv("./src/controllers/resumeParser/Database/hobbies.csv")
    data = pd.read_csv('E:/mapout-resume-parser/mapout-skills/src/controllers/resume-parser/Database/hobbies.csv')
 
    #skills_data = skills_data.applymap(lambda x: x.lower() if pd.notnull(x) else x)
    data = data.apply(lambda x: x.astype(str).str.lower())
    # extract values
    #skills = list(skills_data['Element Name'].values)
    hobbies = list(data['name'].values)
    #print(languages)
    #skills = list(skills_data.columns.values)
    #print(skills)
    #print(skills)
    
    hobbiesset = []
    
    # check for 1-word skills (example: python)
    for token in tokens:
        token = token.strip()
        #print(token)
        if token.lower() in hobbies:
            hobbiesset.append(token)
    
    # check for multiple-word skills (example: machine learning)
    for token in nlp_text.noun_chunks:
        token = token.text.lower().strip()
        if token in hobbies:
            hobbiesset.append(token)
    
    return [i.capitalize() for i in set([i.lower() for i in hobbiesset])]


def social_links(text) :
  social = {}
  try:
    github = (re.search(re.compile('(?:www\.)?github\.com\/(?P<login>[A-z0-9_-]+)\/?'),text)).group()
  except AttributeError:
    github = ''
  try:
    linkedin = (re.search(re.compile('(?:[\w]+\.)?linkedin\.com\/in\/(?P<permalink>[\w\-\_À-ÿ%]+)\/?'),text)).group()
  except AttributeError:
    linkedin = ''
  try:
    twitter = (re.search(re.compile('(?:[A-z]+\.)?twitter\.com\/@?(?!home|share|privacy|tos)(?P<username>[A-z0-9_]+)\/?'),text)).group()
  except AttributeError:
    twitter = ''
  try:
    youtube = (re.search(re.compile('(?:[A-z]+\.)?youtube.com\/channel\/(?P<id>[A-z0-9-\_]+)\/?|(?:[A-z]+\.)?youtube.com\/user\/(?P<username>[A-z0-9]+)\/?'),text)).group()
  except AttributeError:
    youtube = ''
  try:  
    reddit = (re.search(re.compile('(?:[a-z]+\.)?reddit\.com\/(?:u(?:ser)?)\/(?P<username>[A-z0-9\-\_]*)\/?'),text)).group()
  except AttributeError:
    reddit = ''
  try:
    facebook = (re.search(re.compile('(?:www\.)?(?:facebook|fb)\.com\/(?P<profile>(?![A-z]+\.php)(?!marketplace|gaming|watch|me|messages|help|search|groups)[A-z0-9_\-\.]+)\/?|(?:www\.)facebook.com/(?:profile.php\?id=)?(?P<id>[0-9]+)'),text)).group()
  except AttributeError:
    facebook = ''
  try:
    instagram = (re.search(re.compile('(?:www\.)?(?:instagram\.com|instagr\.am)\/(?P<username>[A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)'),text)).group()
  except AttributeError:
    instagram = ''
  try:
    medium = (re.search(re.compile('medium\.com\/@(?P<username>[A-z0-9]+)(?:\?.*)?|medium\.com\/u\/(?P<user_id>[A-z0-9]+)(?:\?.*)'),text)).group()
  except AttributeError:
    medium = ''

  social['github'] = github
  social['linkedin'] = linkedin
  social['twitter'] = twitter
  social['youtube'] = youtube
  social['reddit'] = reddit
  social['facebook'] = facebook
  social['instagram'] = instagram
  social['medium'] = medium
  
  return social
  #return github, linkedin, twitter, youtube, reddit, facebook, instagram, medium


def extract_entity_sections(text):
    
    #text = re.sub('/n', ' ', str(text))
    text = text.lower()
    text_split = [i.strip() for i in text.split('\n')]
    #text_split = re.sub('/n', ' ', str(text_split))
    #print(text_split)
    # sections_in_resume = [i for i in text_split if i.lower() in sections]
    entities = {}
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
        else:
            p_key = set(phrase.lower().split()) & set(RESUME_SECTIONS)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass
        if p_key in RESUME_SECTIONS:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
            entities[key].append(phrase)

    return entities


def extract_experience(text) :
  text = titles_sub(text)
  experiences = {}
  group=[]
  try:
    exp = extract_entity_sections(text)['experience']
    #print(exp)
  
    experience = ''.join(exp)
    #print(experience)
    #experience = titles_sub(text)

    matches = (re.finditer(titlesregex, experience,re.MULTILINE))
    experiences = {}
    group=[]
    i = 0
    for match in matches:
      #print(match)
      experiences[i] = {}
      group.append(match.group())
      experiences[i]['role']=(match.group())
      try:
        desc = ((experience.split(group[0]))[1].split(group[1])[0])

        month1,year1,month2,year2 = find_dates(desc)

        #print(desc.split(year2)[1])
        try:
          experiences[i]['description']= desc.split(str(year2))[2]
        except IndexError:
          experiences[i]['description']= desc.split(str(year2))[1]

      except IndexError:
        desc=((experience.split(group[0]))[1])
        #print(desc)

        month1,year1,month2,year2 = find_dates(desc)
        #print(desc.split(year2)[1])
        try:
          experiences[i]['description']= desc.split(str(year2))[2]
        except:
          try:
            experiences[i]['description']= desc.split(str(year2))[1]
          except:
            experiences[i]['description']=''

      try:
        experiences[i]['dates'] = find_dates(desc)
        
      except:
        ''

      i = i+1
  except KeyError:
    ''

  return experiences

def find_university(text):
    text1 = re.sub('/n', ' ', str(text))
    text1 = text.lower()
    try:
        university = re.search(uniregex, text1).group()
    except AttributeError:
        university = ''
    return university

def extract_education(nlp_text):
    
    # Sentence Tokenizer
    nlp_text = [sent.text.strip() for sent in nlp_text.sents]
    #print(nlp_text)
    edu = {}
    degree = []
    # Extract education degree
    for index, text in enumerate(nlp_text):
        for tex in text.split():
            # Replace all special symbols
            tex = tex.strip()
            tex = re.sub(r'[?|$|.|!|,|-]', r'', tex)
            #print(tex)
            try:
              if tex.upper() in qualification and tex not in stopwords:
                  edu[tex] = text + nlp_text[index + 1]
                  #print(edu[tex])
                  #degree.append(tex)
            except IndexError:
              ''
    # Extract year
    
    education = {}
    i = 0
    for key in edu.keys():
      #print(edu[key])
      education[i] = {}
      education[i]['degree'] = key
      education[i]['university'] = find_university(edu[key])    
      #i = 0
      #print(degree[i])
      #print(edu[key])
      #desc = edu[key].split(str(degree[i]))
      #print(desc)
      #print("----------")
      month1, year1, month2, year2 = find_dates(edu[key])

      #print(month1, year1, month2, year2)
      education[i]['dates'] = year1,year2

      i = i+1
      #list1 = list(month1,year1,month2,year2)
      #i = i+1
      #dates = list(dates)
      #print(dates[0])
      #print(dates)
      #education.append((key, ''.join(list1)))

    return education



def parse_resume(text):
  #nlp_text = nlp(text)
  #name = extract_name(nlp_text)
  parsed_info = {}
  email = extract_email(nlp_text)
  parsed_info['email'] = email
  number = extract_mobile_number(nlp_text)
  parsed_info['contact'] = number
  coreskills = extract_skills(text)
  parsed_info['core skills'] = coreskills
  softskills = soft_skills(text)
  parsed_info['soft skills'] = softskills
  languages = extract_languages(text)
  parsed_info['languages'] = languages
  hobbies = extract_hobbies(text)
  parsed_info['hobbies'] = hobbies
  #education = extract_entity_sections(text)['education']
  edu = extract_education(nlp_text)
  parsed_info['education'] = edu
  #experience = extract_entity_sections(text)['experience']
  #experience_str = ''.join(experience)
  exp = extract_experience(text)
  parsed_info['experience'] = exp
  socials = social_links(text)
  parsed_info['social links'] = socials   
  try:
    project = extract_entity_sections(text)['projects']
    projects = ''.join(project)
  except KeyError:
    projects = {}
  
  return parsed_info
  #return email, number, coreskills, softskills, languages, hobbies, edu, exp, socials, projects

#nlp_text = extract_text(r'C:\Users\Zeeshan\Downloads\Nithin_Resume (1).pdf')
#nlp_text = extract_text(r'C:\Users\Zeeshan\Downloads\ANJU GOEL CV (1).pdf')

#url = "https://demo1-app-bucket.s3.ap-south-1.amazonaws.com/Nithin_Resume.pdf"
#url = "https://demo1-app-bucket.s3.ap-south-1.amazonaws.com/1628785743136_Javed+Akhtar+Ansari+Resume.pdf"

#url = input("Enter url : ")

url = sys.argv[1]
url = url.replace(" ", "%20")
#url = "https://demo1-app-bucket.s3.ap-south-1.amazonaws.com/0-21149832792.pdf"

#url = "hi"
#print(url) 
#url = url.apply(str)
#print("URL : " +url)

#text = pdf_from_url_to_txt(url)

text = text_extraction(url)

nlp_text = nlp(text)
print(parse_resume(text))

"""

name = extract_name(nlp_text)
print("Name : " +name)

email = extract_email(nlp_text)
print("Email : " +email)

number = extract_mobile_number(nlp_text)
print("Contact : " +number)

education_details = extract_education(nlp_text)
print("Education : ")
print(education_details)

experience = extract_experience(nlp_text)
print("Experience : ") 
print(experience)
"""
