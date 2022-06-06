import sys
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
import spacy 
from io import BytesIO, StringIO
import urllib.request
import json

import pandas as pd

import re

from spacy.matcher import Matcher
import sys


import nltk
#nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('stopwords')
from nltk.corpus import stopwords

nlp = spacy.load('en_core_web_sm')


def pdf_from_url_to_txt(url):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    #codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec='utf-8', laparams=laparams)
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
 

#url = sys.argv[1]
url = "https://demo1-app-bucket.s3.ap-south-1.amazonaws.com/Nithin_Resume.pdf"
print(url)
text = pdf_from_url_to_txt(url)
nlp_text = nlp(text)
#print(nlp_text)
#print("hello")