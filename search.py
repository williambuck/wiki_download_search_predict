from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

import pandas as pd
import numpy as np
import pymongo
import sys

client = pymongo.MongoClient('35.163.182.105', 27016)

pickle_path = input('Pickle file to search: ')
try:
    merged_wiki_databases_df = pd.read_pickle(f'Data/{pickle_path}').drop_duplicates(['title'])
except:
    print('That pickle file does not exist in the "Data" directory. Please try again.\n')
    pickle_path = input('Pickle file to search: ')
    merged_wiki_databases_df = pd.read_pickle(f'Data/{pickle_path}').drop_duplicates(['title'])


def search_v2(phrase, with_SVD=False):

    # Making 'phrase' a list
    search_phrase = [phrase]

    content_from_df = merged_wiki_databases_df['content']
    titles_from_df = merged_wiki_databases_df['title']

    # Creating sparse matrices for the page contents and search phrase
    # NOTE: When I add an ngram_range to the TFIDF, it kills my kernel
    tfidf_vectorizer = TfidfVectorizer(min_df = 1, stop_words = 'english')
    document_term_matrix_sps = tfidf_vectorizer.fit_transform(content_from_df)
    search_phrase_matrix_sps = tfidf_vectorizer.transform(search_phrase)

    if with_SVD:
        # Singular Value Decomposition on the document_term_matrix
        # TruncatedSVD recommends 100 components for LSA
        n_components = 100
        SVD = TruncatedSVD(n_components)
        document_svd = SVD.fit_transform(document_term_matrix_sps)
        phrase_svd = SVD.transform(search_phrase_matrix_sps)

        cos_sim_df = pd.DataFrame(cosine_similarity(document_svd, phrase_svd),\
                                       index=titles_from_df, columns=['cosine_sim']).sort_values('cosine_sim', ascending=False)
    else:
        # Creating DataFrame of the top five page results for the search phrase.
        cos_sim_df = pd.DataFrame(cosine_similarity(document_term_matrix_sps, search_phrase_matrix_sps),\
                               index=titles_from_df, columns=['cosine_sim']).sort_values('cosine_sim', ascending=False)
    return cos_sim_df[:5]


with_svd = input('Use TruncatedSVD with search? [y/n] ')
phrase = input('Search: ')

if with_svd == 'y' or with_svd == 'yes':
    resluts_df = search_v2(phrase, with_SVD=True)
    display(resluts_df)
else:
    results_df = search_v2(phrase)
    display(results_df)
    
search_again = input('Make another search? [y/n] ')

while search_again == 'y' or search_again == 'yes':
    with_svd = input('Use TruncatedSVD with search? [y/n] ')
    phrase = input('Search: ')
    
    if with_svd == 'y' or with_svd == 'yes':
        resluts_df = search_v2(phrase, with_SVD=True)
        display(resluts_df)
    else:
        results_df = search_v2(phrase)
        display(results_df)
    
    search_again = input('Make another search? [y/n] ')