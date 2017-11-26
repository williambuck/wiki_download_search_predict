from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

import pandas as pd
import numpy as np
import pymongo
import sys

client = pymongo.MongoClient('35.163.182.105', 27016)

class merge_all_mongo_content():
    
    content_list = []
    title_list = []
   
    def extract_all_collections_content_and_title(self, database):
        
        collection_list = [x for x in client[database].collection_names()]
        len_of_coll_list = len(collection_list)
        cnt = 1
        print('\n{} Categories in {}.\n'.format(len_of_coll_list, database))
        
        for col in collection_list:
            coll_dict = list(client[database][col].find())
            coll_content = [coll_dict[i]['content'] for i in range(len(coll_dict))]
            page_title = [coll_dict[i]['title'] for i in range(len(coll_dict))]
            
            self.content_list.extend(coll_content)
            self.title_list.extend(page_title)            
            sys.stdout.write('{}.'.format(cnt))
            cnt += 1
        
        print('\n\n')
        return
    
    def merge_databases(self, databases_list, pickle=False):
        
        for db in databases_list:
            self.extract_all_collections_content_and_title(db)
        
        return list(set(zip(self.title_list,self.content_list)))


# Will need to update this to 'wiki_db' once I'm done testing.
# Creating the searchable content
mamc = merge_all_mongo_content()
wiki_db_list = [x for x in client.database_names() if x[-len('_wiki_db'):] == '_wiki_db']
n_dbs = len(wiki_db_list)
print('Merging {} mongo databases for Wikipedia search.'.format(n_dbs))
title_content_zip = mamc.merge_databases(wiki_db_list)
title_list = [x for (x,y) in title_content_zip]
content_list = [y for (x,y) in title_content_zip]
print('Done merging databases.')

    
def search(phrase):
    
    # Making 'phrase' a list
    search_phrase = [phrase]
    
    # Creating sparse matrices for the page contents and search phrase
    tfidf_vectorizer = TfidfVectorizer(min_df = 1, stop_words = 'english')
    document_term_matrix_sps = tfidf_vectorizer.fit_transform(content_list)
    search_phrase_matrix_sps = tfidf_vectorizer.transform(search_phrase)
    
    # Singular Value Decomposition on the document_term_matrix
    # TruncatedSVD recommends 100 components for LSA
    n_components = 100
    SVD = TruncatedSVD(n_components)
    svd_matrix = SVD.fit_transform(document_term_matrix_sps)

    # Creating DataFrame of the top five page results for the search phrase.
    top_five_df = pd.DataFrame(cosine_similarity(document_term_matrix_sps, search_phrase_matrix_sps),\
                               index=title_list, columns=['cosine_sim']).sort_values('cosine_sim', ascending=False)[:5] 
    return top_five_df


def search_v2(phrase):
   
    # Making 'phrase' a list
    search_phrase = [phrase]
    
    # Creating sparse matrices for the page contents and search phrase
    tfidf_vectorizer = TfidfVectorizer(min_df = 1, stop_words = 'english')
    document_term_matrix_sps = tfidf_vectorizer.fit_transform(content_list)
    search_phrase_matrix_sps = tfidf_vectorizer.transform(search_phrase)
    
    # Singular Value Decomposition on the document_term_matrix
    # TruncatedSVD recommends 100 components for LSA
    n_components = 100
    SVD = TruncatedSVD(n_components)
    svd_matrix = SVD.fit_transform(document_term_matrix_sps)
    search_phrase_lsa = SVD.transform(search_phrase_matrix_sps)
    
    cos_sim = [x for x in cosine_similarity(document_term_matrix_sps, search_phrase_matrix_sps).tolist()]
    results = list(zip(title_list, [x for x in cos_sim]))
    results.sort(key=lambda tup: tup[1], reverse=True)
    
    return results[:5]