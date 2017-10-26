import re

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import string

list_descriptions = []
list_labels = []
performance_issues = 0
nonperformance_issues = 0

def filterWords(text):
  try:
    text = re.sub(r'\d+', '', text)
  except TypeError:
    text = text.decode('utf-8')
  stop_words = set(stopwords.words("english"))
  text = word_tokenize(text)
  text = list(filter(lambda x: x not in string.punctuation, text))
  text =  list(filter(lambda x: x not in stop_words, text))
  lmtzr = WordNetLemmatizer()
  text = list(lmtzr.lemmatize(i) for i in text)
  stemmer = PorterStemmer()
  text = list(stemmer.stem(i) for i in text)
  return text
  
from openpyxl import load_workbook
wb = load_workbook('dataset.xlsx')

for sheet in wb:
  for i in range(2, len(sheet['AB'])):
    val = sheet[('AB' + str(i))].value
    if val == 1: #if it is a Performance issue
      summary = sheet[('N'+str(i))].value.encode('utf-8')
      description = sheet[('O'+str(i))].value.encode('utf-8')
      words = filterWords(summary)
      words += filterWords(description)
      list_descriptions.append(words)
      list_labels.append(1)  
      performance_issues += 1
   
for sheet in wb:
  if nonperformance_issues == performance_issues:
    break
  for i in range(2, len(sheet['AB'])):
    val = sheet[('AB' + str(i))].value
    if val == 0: #if it's not a Performance issue
      summary = sheet[('N'+str(i))].value.encode('utf-8')
      description = sheet[('O'+str(i))].value.encode('utf-8')
      words = filterWords(summary)
      words += filterWords(description)
      list_descriptions.append(words)
      list_labels.append(0)
      nonperformance_issues += 1
      if nonperformance_issues == performance_issues:
        break

import sys
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

print(len(list_descriptions))
print(len(list_labels))
print(performance_issues)
print(nonperformance_issues)

final_descriptions = []
for i in list_descriptions:
  str1 = ''.join(i)
  final_descriptions.append(str1)

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

count_vectorizer = TfidfVectorizer(min_df=2)
counts = count_vectorizer.fit_transform(final_descriptions)
classifier = MultinomialNB()

from sklearn.model_selection import StratifiedKFold, KFold, cross_val_score

k_fold = StratifiedKFold(n_splits=10, shuffle=True, random_state=1)
scores_recall = cross_val_score(classifier, counts, list_labels, cv=k_fold, scoring='recall')
print("Recall: %0.2f (+/- %0.2f)" % (scores_recall.mean(), scores_recall.std() * 2))
