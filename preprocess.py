import pandas as pd
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag

from tqdm import tqdm
from collections import OrderedDict
import re
nltk.download('all')

with open('./data/filtered_data.pickle', 'rb') as f:
    data = pickle.load(f)

text_df = data[['type', 'total']]

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def clean_str(string):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    string = re.sub(r'[^\.\?\!\w\d\s]', '', string)
    return string.strip().lower()

# To remove rare words
word_freq = {}

for doc_content in list(text_df['total']):
    temp = clean_str(doc_content)
    words = temp.split()
    for word in words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1

# To remove stop words
clean_docs = []

for doc_content in list(text_df['total']):
    temp = clean_str(doc_content)
    words = temp.split()
    doc_words = []
    for word in words:
        # word not in stop_words and word_freq[word] >= 5
        if word not in stop_words and word_freq[word] >= 5:
            doc_words.append(word)

    doc_str = ' '.join(doc_words).strip()
    clean_docs.append(doc_str)

# POS tagging
tokens_pos_list = []
for l in tqdm(clean_docs):
    pt = nltk.pos_tag(nltk.word_tokenize(l))
    tokens_pos_list.append(pt)

def get_wordnet_pos(postag):
    if postag.startswith('V'):
        return 'v'
    elif postag.startswith('N'):
        return 'n'
    elif postag.startswith('J'):
        return 'a'
    else:
        return None

words_pos_list_2 = []

for word_list in tqdm(tokens_pos_list):
    temp_list = []
    for token, postag in word_list:
        tag = get_wordnet_pos(postag)
        if tag!=None:
            temp_list.append((token, get_wordnet_pos(postag)))
    words_pos_list_2.append(temp_list)

# Lemmatize
lemm = WordNetLemmatizer()    
final_words = []
for token_pos in tqdm(words_pos_list_2):
    temp_list = []
    for token, tag in token_pos:
        temp_list.append(lemm.lemmatize(token, pos=tag))
        temp_list = list(OrderedDict.fromkeys(temp_list))
    final_words.append(temp_list)

final_df = pd.DataFrame({
    'total':data['total'],
    'words':final_words,
    'label':data['type']})


    


