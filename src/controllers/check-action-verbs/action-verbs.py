import sys

def get_action_verbs_df():
    import pandas as pd
    df = pd.read_csv('src/controllers/check-action-verbs/all_action_verbs.csv')   
    words = list(df['action_verb'].values)
    return words
    
def action_words(text):
    tokens = text.split(" ")
    flag = 0
    words = get_action_verbs_df()
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
print(action_words(text))

