import pandas as pd
import sys
from nltk.corpus import stopwords
import spacy

# FIRST TIME INSTALLATION
#import nltk
#nltk.download('stopwords')

stopwords = set(stopwords.words('english'))


from spacy.lang.en import English

nlp=English()

# load pre-trained model
nlp = spacy.load('en_core_web_sm')

def action_words(nlp_text):
  
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    flag = 0
    
    df = pd.read_csv('src/controllers/check-action-verbs/all_action_verbs.csv')   
    words = list(df['0'].values)
  
    #action_words = []
    
    for token in tokens:
        token = token.strip()
        #print(token)
        if token.lower() in words:
            #action_words.append(token.lower())
            flag = 1
    
    return flag #, action_words

text = sys.argv[1]
#text = " Implemented xyz xyz xyz abc abc abc and performed xyz xyz xyz abc abc abc "

nlptext = nlp(text)
print(action_words(nlptext))

