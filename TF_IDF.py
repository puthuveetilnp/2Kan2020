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
# Download stopwords list

import pickle

with open('real_data_training.pkl', 'rb') as f:
    real_url = pickle.load(f)
with open('fake_data_training.pkl', 'rb') as fh:
    fake_url=pickle.load(fh)

print(len(real_url))
print(len(fake_url))


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
            fake_count.append((count_real, count_fake,"real"))
        else:
            fake_count.append((count_real, count_fake, "fake"))

        fake_list.append(fake_indv_list)
    return(fake_list,fake_count)



def get_acc(list_count, real_fake):
    count=0
    for i in list_count:
        if i[2]==real_fake:
            count+=1
    return(count/len(list_count))


fake_list,fake_count=get_cosine_sim(test_fake_x)
real_list,real_count=get_cosine_sim(test_real_x)



print(get_acc(real_count,"real"), get_acc(fake_count,"fake"))


with open('fake_list.pkl', 'wb') as f:
    pickle.dump(fake_count, f)

with open('real_list.pkl', 'wb') as f:
    pickle.dump(real_count, f)

# print(len(train_real))
# print(len(test_real))


#
# train_real = real_url[:int((len(real_url)+1)*.80)]
# test_real=real_url[int((len(real_url)+1)*.80):]
# print(len(train_real))
# print(len(test_real))
# train_fake = fake_url[:int((len(real_url)+1)*.80)]
# test_fake=fake_url[int((len(real_url)+1)*.80):]
#
# print(len(train_fake))
# print(len(test_fake))
# with open('real_train.pkl', 'wb') as f:
#     pickle.dump(train_real, f)
#
# with open('real_test.pkl', 'wb') as f:
#     pickle.dump(test_real, f)
#
# with open('fake_train.pkl', 'wb') as f:
#     pickle.dump(train_fake, f)
#
# with open('fake_test.pkl', 'wb') as f:
#     pickle.dump(test_fake, f)


# X_train, X_test, y_train, y_test = train_test_split(real_url, y, test_size=0.2)
# print X_train.shape, y_train.shape
# print X_test.shape, y_test.shape

