
import pandas as pd
from sklearn import datasets, linear_model
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords
import random
import urllib.request
import bs4 as bs
# Download stopwords list

import pickle

with open('real_data_training.pkl', 'rb') as f:
    real_url = pickle.load(f)
with open('fake_data_training.pkl', 'rb') as fh:
    fake_url=pickle.load(fh)

# print(real_url)
# print(fake_url)
# print(len(real_url))
# print(len(fake_url))


data_real=[]
real_label=[]
for i in real_url:
    data_real.append(i[0])
    real_label.append(i[1])

data_fake=[]
fake_label=[]
for k in fake_url:
    data_fake.append(k[0])
    fake_label.append(k[1])

train_real_x= data_real[:int((len(data_real)+1)*.80)]
test_real_x=data_real[int(len(data_real)*.80):]
train_real_y= real_label[:int((len(real_label)+1)*.80)]
test_real_y=real_label[int(len(real_label)*.80):]


train_fake_x= data_fake[:int((len(data_real)+1)*.80)]
test_fake_x=data_fake[int(len(data_real)*.80):]
train_fake_y= fake_label[:int((len(real_label)+1)*.80)]
test_fake_y=fake_label[int(len(real_label)*.80):]


#https://towardsdatascience.com/how-to-rank-text-content-by-semantic-similarity-4d2419a84c32

nltk.download('punkt')
stop_words = set(stopwords.words('english'))

# Interface lemma tokenizer from nltk with sklearn
class LemmaTokenizer:
    ignore_tokens = [',', '.', ';', ':', '"', '``', "''", '`']
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if t not in self.ignore_tokens]

# Lemmatize the stop words
tokenizer=LemmaTokenizer()
token_stop = tokenizer(' '.join(stop_words))


def get_cosine_sim(test):
    fake_list=[]
    fake_count=[]
    for i in range(len(test)):
        fake_indv_list=[]
        count_fake=0
        count_real=0
        search_terms=test[i]
        for k in range(len(train_fake_x)):
            documents=[train_fake_x[k], train_real_x[k]]
            # Create TF-idf model
            vectorizer = TfidfVectorizer(stop_words=token_stop,
                              tokenizer=tokenizer)
            doc_vectors = vectorizer.fit_transform([search_terms] + documents)

            # Calculate similarity
            cosine_similarities = linear_kernel(doc_vectors[0:1], doc_vectors).flatten()
            document_scores = [item.item() for item in cosine_similarities[1:]]
            fake_indv_list.append(document_scores)
            if(document_scores[0]>document_scores[1]):
                count_fake+=1
            else:
                count_real+=1
        if(count_real>count_fake):
            fake_count.append((count_real, count_fake, "credible"))
        else:
            fake_count.append((count_real, count_fake, "false"))

        fake_list.append(fake_indv_list)
    return(fake_list,fake_count)

def get_acc(list_count, real_fake):
    count=0
    for i in list_count:
        if i[2]==real_fake:
            count+=1
    return(count/len(list_count))

def get_text(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    source = urllib.request.urlopen(req).read()
    soup = bs.BeautifulSoup(source, 'lxml')

    string_website = ""
    for paragraph in soup.find_all('p'):
        string_website = ' '.join([string_website, str(paragraph.text)])

    url_list = list()
    for link in soup.find_all('a'):
        url_str = link.get('href')
        if url_str != None:
            if (url in url_str):
                url_list.append(url_str)
    if(len(url_list) > 7):
        url_list=url_list[1:7]

    for web_link in url_list:
        if ('location' not in url):
            sub_req = urllib.request.Request(web_link, headers={'User-Agent': 'Mozilla/5.0'})
            sub_source = urllib.request.urlopen(sub_req).read()
            sub_page = bs.BeautifulSoup(sub_source, 'lxml')
            for paragraph in sub_page.find_all('p'):
                string_website = ' '.join([string_website, str(paragraph.text)])
    return string_website


def get_user_sim_score(url):
    data_list=list()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    source = urllib.request.urlopen(req).read()
    soup = bs.BeautifulSoup(source, 'lxml')

    string_website = ""
    for paragraph in soup.find_all('p'):
        string_website = ' '.join([string_website, str(paragraph.text)])

    url_list = list()
    for link in soup.find_all('a'):
        url_str = link.get('href')
        if url_str != None:
            if (url in url_str):
                url_list.append(url_str)
    if(len(url_list) > 7):
        url_list=url_list[1:7]

    for web_link in url_list:
        if ('location' not in url):
            sub_req = urllib.request.Request(web_link, headers={'User-Agent': 'Mozilla/5.0'})
            sub_source = urllib.request.urlopen(sub_req).read()
            sub_page = bs.BeautifulSoup(sub_source, 'lxml')
            for paragraph in sub_page.find_all('p'):
                string_website = ' '.join([string_website, str(paragraph.text)])
    try: 
        if string_website !='':
            data_list.append(string_website)
    except:
        pass

    test_list,test_count=get_cosine_sim(data_list)
    if len(test_count) > 0: 
        return list(test_count[0])
    else:
        return test_count



# counts = get_user_sim_score("http://www.reallifecpc.org/")
# print(get_user_sim_score("http://chiltonwomenscenter.com/"))
# print(get_user_sim_score("https://www.plannedparenthood.org/"))

