#import packages
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from termcolor import colored
import spacy
nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english')+['able','self','sr','basic','skill'])

#get text based on POS tags
def extractInterest(what, text,from_spacy=False):
    is_ofinterest = lambda pos: pos[:2] in what
    if from_spacy:
        doc = nlp(text)
        nouns = [token.text for token in doc if is_ofinterest(token.tag_)]
        return " ".join(nouns)                
    tokenized = word_tokenize(text) 
    nouns = [word for (word, pos) in pos_tag(tokenized) if is_ofinterest(pos) and len(word)>2]
    return " ".join(nouns)

#remove Punctuation from string
def removePunctuation(text):
    tokens = word_tokenize(text)
    return " ".join([word for word in tokens if word.isalpha()])
 
#stop words removing
def removeStopwords(text):
    word_tokens = word_tokenize(text.lower())
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return " ".join(filtered_sentence)

#add to colour to specific text
def coloredString(text,coloured_text,colour='red'):
    temp=[]
    for i in word_tokenize(text):
        if i.lower() in word_tokenize(coloured_text.lower()):
            temp.append(colored(i, colour))
        else:
            temp.append(i)
    return " ".join(temp)

#text cleaning 
def textPreprocess(text,removestopwords=True,removepunctuation=True):
    if removestopwords:
        text=removeStopwords(text)
    if removepunctuation:
        text=removePunctuation(text)
    return text