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

client = pymongo.MongoClient('35.163.182.105', 27016)


# NOTE: This dataframe loader keeps pages in all the categories they are found in. So, there is duplicate page content.
#       if we drop all duplicate titles, then pages that did appear in multiple categories will only be included
#       in one of the categories instead of all.

pickle_path = input('Pickle file to search: ')
try:
    merged_wiki_databases_df = pd.read_pickle(f'Data/{pickle_path}').drop_duplicates(['title'])
except:
    print('That pickle file does not exist. Please try again.\n')
    pickle_path = input('Pickle file to search: ')
    merged_wiki_databases_df = pd.read_pickle(f'Data/{pickle_path}').drop_duplicates(['title'])

grouped_by_category = merged_wiki_databases_df.groupby('category').agg(lambda x: ';;;'.join(x))

def request_category_pages(category):
    category_re = re.sub('\s', '+', category)
    query = 'http://en.wikipedia.org/w/api.php?action=query&format=json&list=categorymembers&cmtitle=\
           Category%3A+{}&cmlimit=max'.format(category_re)
    QR = requests.get(query)
    return QR.json()['query']['categorymembers']

def strip_punctuation(s):
    return ''.join(c for c in s if c not in punctuation)

def get_page_contents(pageid):
    '''Takes the pageid of a Wikipedia page and returns a string of all the text with HTML stripped out.'''
    
    query = 'http://en.wikipedia.org/w/api.php?action=query&prop=extracts&\
             rvprop=content&rvsection=0&format=json&pageids={}'.format(pageid)
    my_request = requests.get(query).json()['query']['pages'][str(pageid)]['extract']
    soup = BeautifulSoup(my_request, 'html.parser')
    clean_soup_text = strip_punctuation((soup.get_text()).replace('\n', ' '))
    return clean_soup_text

def get_page_content_from_title(title):

    # replace spaces in category with '+' so can insert into search string
    title_re = re.sub('\s', '_', title)
    query = 'https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&\
             format=json&titles={}'.format(title_re)
    QR = requests.get(query)
    [my_id] = [int(x) for x in QR.json()['query']['pages'].keys()]

    return get_page_contents(my_id)

def predict_v2(title, with_SVD=False):

    # Getting page content of the input title
    page_content = get_page_content_from_title(title)

    # merged all content by category for TFIDF vectorization
    all_content = grouped_by_category['content']
    titles_from_df = grouped_by_category.index

    # Creating sparse matrices for the page contents and search phrase
    tfidf_vectorizer = TfidfVectorizer(min_df = 1, stop_words = 'english')
    document_term_matrix_sps = tfidf_vectorizer.fit_transform(all_content)
    page_content_matrix_sps = tfidf_vectorizer.transform([page_content])


    if with_SVD:
        # SVD on the document_term_matrix_sps
        n_components = 100
        SVD = TruncatedSVD(n_components)
        document_svd = SVD.fit_transform(document_term_matrix_sps)
        page_content_svd = SVD.transform(page_content_matrix_sps)

        cos_sim_df = pd.DataFrame(cosine_similarity(document_svd, page_content_svd),\
                                   index=titles_from_df, columns=['cosine_sim']).sort_values('cosine_sim', ascending=False)
    else:
        cos_sim_df = pd.DataFrame(cosine_similarity(document_term_matrix_sps, page_content_matrix_sps),\
                                   index=titles_from_df, columns=['cosine_sim']).sort_values('cosine_sim', ascending=False)
    return cos_sim_df[:5]

with_svd = input('Use TruncatedSVD to predict? [y/n] ')
page_title = input('Page Title: ')

if with_svd == 'y' or with_svd == 'yes':
    resluts_df = predict_v2(page_title, with_SVD=True)
    display(resluts_df)
else:
    results_df = predict_v2(page_title)
    display(results_df)

predict_again = input('Make another category prediction from page title? [y/n] ')
while predict_again == 'y' or predict_again == 'yes':
    with_svd = input('Use TruncatedSVD to predict? [y/n] ')
    page_title = input('Page Title: ')

    if with_svd == 'y' or with_svd == 'yes':
        resluts_df = predict_v2(page_title, with_SVD=True)
        display(resluts_df)
    else:
        results_df = predict_v2(page_title)
        display(results_df)
    predict_again = input('Make another category prediction from page title? [y/n] ')
