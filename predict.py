from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

import pandas as pd
import numpy as np
import pymongo
import sys

import re
import requests

from string import punctuation
from bs4 import BeautifulSoup

import download

client = pymongo.MongoClient('35.163.182.105', 27016)


# NOTE: this keeps pages in all the categories they are found in. So, there is duplicate page content.
#       if we drop all duplicate titles, then pages that did appear in multiple categories will only be included
#       in one of the categories instead of all. 
merged_wiki_databases_df = pd.read_pickle('Data/merged_wiki_databases_df.p').drop_duplicates(['category','title'])
grouped_by_category = merged_wiki_databases_df.groupby('category').agg(lambda x: ';;;'.join(x))



def get_page_content_from_title(title):
    
    # replace spaces in category with '+' so can insert into search string
    title_re = re.sub('\s', '_', title) 
    
    query = 'https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&\
             format=json&titles={}'.format(title_re)
    
    QR = requests.get(query)
    
    [my_id] = [int(x) for x in QR.json()['query']['pages'].keys()]
    
    return download.get_page_contents(my_id)

def predict(title):
    
    # Getting page content of the input title
    page_content = get_page_content_from_title(title)
    
    # merged all content by category for TFIDF vectorization
    all_content = grouped_by_category['content']
    
    # Creating sparse matrices for the page contents and search phrase
    tfidf_vectorizer = TfidfVectorizer(min_df = 1, stop_words = 'english')
    document_term_matrix_sps = tfidf_vectorizer.fit_transform(all_content)   
    
    # SVD on the document_term_matrix_sps
    n_components = 100
    SVD = TruncatedSVD(n_components)
    latent_semantic_analysis = SVD.fit_transform(document_term_matrix_sps)
    
    # Getting vector for the page content from the input title and then SVDecomposing it
    page_content_vec = tfidf_vectorizer.transform([page_content])
    page_content_lsa = SVD.transform(page_content_vec)
    
    #SORTING BY VALUES IN COSINE SIMILARITIES... RETURNING LAST 5 INDICES
    cosine_similarities = latent_semantic_analysis.dot(page_content_lsa.T).ravel()
    predictions = cosine_similarities.argsort()[:-6:-1]
    
    top_list = []
    for x in grouped_by_category.T[predictions].T.index:
        top_list.append(x)
    
    return top_list