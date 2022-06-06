import pandas as pd
import pickle
import numpy as np
from scipy import spatial
import sys

with open('./src/controllers/score/degree/degreevectors_final.pickle','rb') as handle:
  degreevectors = pickle.load(handle)

with open('./src/controllers/score/degree/degree_and_subjects.pickle','rb') as handle:
  degree_and_subjects = pickle.load(handle)

# with open('glove_degrees.pickle','rb') as handle:
#  glove_degrees = pickle.load(handle)


with open('./src/controllers/score/degree/softskill_vectors.pickle','rb') as handle:
  soft_skill_vectors = pickle.load(handle)

def degree_search(subject):
  ans = set()
  for i in degree_and_subjects:
    for j in degree_and_subjects[i]:
      if subject.lower() in j:
        ans.add(i)
  return ans

def subject_match(cv_degrees_list,subject):
  match = False
  for i in cv_degrees_list:
    if i in degree_search(subject):
      match=True
      break
  return int(match)		

def calculate_degrees_similarity(degree_1, degree_2):
  return 1-spatial.distance.cosine(degreevectors[degree_1],degreevectors[degree_2])

def get_top_softskills(degree):
  return sorted(soft_skill_vectors.keys(),key = lambda x:spatial.distance.cosine(soft_skill_vectors[x],degreevectors[degree]))[:10]

def calculate_degrees_list_similarity(l1,degree2):
  max_score = 0
  for i in l1:
    max_score = max(max_score,new_score(i,degree2))
  return max_score

def calculate_list_degrees(l1,l2):
  best_scores = [0]*len(l2)
  pos = 0
  while pos<=len(l2)-1:	
    for i in l1:
      best_scores[pos] = max(best_scores[pos],new_score(i,l2[pos]))
    pos+=1
  return sum(best_scores)/len(best_scores)
     
def new_score(degree1,degree2):
  score = calculate_degrees_similarity(degree1,degree2)
  return score  

def score_condition(l1,l2):
  len_l1 = len(l1)
  len_l2 = len(l2)
  if len_l1==1 and len_l2==1:
    return new_score(l1[0],l2[0])
  elif len_l1>1 and len_l2==1:
    return calculate_degrees_list_similarity(l1,l2[0])
  else:
    return calculate_list_degrees(l1,l2)

# The convention to be followed in all functions is:
# CV degree(s) as first argument, JD degree(s) as second argument


# 1. In order to get degree match score b/w degree1 and degree2:

# print(new_score(degree1,degree2))

# 2. In order to get degree match score b/w CV degrees and JD degree:

 #print(new_score([degree1,degree2,degree3],jd_degree))

# 3. In order to get degree match score if only subject/domain is given

 #print(subject_match(cv_degree_list,subject))

# 4. In order to get degree match score for multiple CV degrees and multiple JD degrees
# print(calculate_list_degrees(cv_degrees,jd_degrees))

print(score_condition(sys.argv[1].split(","), sys.argv[2].split(",")))