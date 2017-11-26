import re
import requests
import pandas as pd
import numpy as np
import pymongo

from string import punctuation
from bs4 import BeautifulSoup

import sys

client = pymongo.MongoClient('35.163.182.105', 27016)

def request_category_pages(category):
    
    # replace spaces in category with '+' so can insert into search string
    category_re = re.sub('\s', '+', category) 
    
    query = 'http://en.wikipedia.org/w/api.php?action=query&format=json&list=categorymembers&cmtitle=\
           Category%3A+{}&cmlimit=max'.format(category_re)
    
    QR = requests.get(query)
    
    return QR.json()['query']['categorymembers']


def strip_punctuation(s):
    return ''.join(c for c in s if c not in punctuation)


# def striphtml(data):
#     p = re.compile(r'<.*?>')
#     return p.sub('', data)

def get_page_contents(pageid):
    '''Takes the pageid of a Wikipedia page and returns a string of all the text with HTML stripped out.'''
    
    query = 'http://en.wikipedia.org/w/api.php?action=query&prop=extracts&\
             rvprop=content&rvsection=0&format=json&pageids={}'.format(pageid)
    
    my_request = requests.get(query).json()['query']['pages'][str(pageid)]['extract']
    
    soup = BeautifulSoup(my_request, 'html.parser')
    clean_soup_text = strip_punctuation((soup.get_text()).replace('\n', ' '))
    
    return clean_soup_text


# This is using regex instead of BeautifulSoup, which is slightly faster but doesn't clean the text as well.
# def non_beautiful_soup_get_page_contents(pageid):
#     '''Takes the pageid of a Wikipedia page and returns a string of all the text with HTML stripped out.'''
    
#     query = 'http://en.wikipedia.org/w/api.php?action=query&prop=extracts&\
#              rvprop=content&rvsection=0&format=json&pageids={}'.format(pageid)
    
#     my_request = requests.get(query).json()
#     no_html_string = striphtml(my_request['query']['pages'][str(pageid)]['extract']).replace('\n', ' ')
    
#     return strip_punctuation(no_html_string)


class store_wiki_contents_in_mongo():
    
    database_name = ''
    all_subcategories_list = [] 
    countdown = 0
    
    def __init__(self, database_name):
        
        db_re = re.sub('\s', '_', database_name)
        self.database_name = '{}_wiki_db'.format(db_re)
    
    def get_all_page_contents_from_category(self, category, overwrite=False, second_run=False, nesting_level=0):
        '''Takes a Wikipedia category and creates a collection in the client.wiki_content_db that consists of the \
        page_id, page content (text), title, and parent category.

        WARNING: If overwrite=True, then the database that was previously created for the category will be dropped \
        before being created again. Overwrite is False by default.'''

        if second_run == False:
            self.all_subcategories_list = []
    
        category_re = re.sub('\s', '_', category)

        # Dropping the collection that was previously created for the category
        if overwrite:
            Q = input('About to delete database "{}". \nDo you want to continue [y/n]? '.format(self.database_name))
            if Q == 'y':
                client.drop_database(self.database_name)
            else:
                return 'Quitting without dropping database.'

        # Creating the collection and db
        wiki_content_db = client[self.database_name]
        wiki_coll_ref = wiki_content_db['{}_wiki_content_collection'.format(category_re)]

        # Getting a list of the json objects to be iterated through and inserted into the collection, page by page.
        my_pages_json_list = request_category_pages(category)

        for i, record in enumerate(my_pages_json_list):

            p_id = record['pageid']
            page_content = get_page_contents(p_id)
            page_title = my_pages_json_list[i]['title']

            # Inserting every pages information and inserting into collection
            wiki_coll_ref.insert_one({'page_id':p_id, 'content':page_content, \
                                      'category':category, 'title':page_title})
        
        if second_run == False:
            print('Finished updating "{}" with all page content from category "{}".\n'
                  .format(self.database_name, category))
        
        # Returning the function after the first layer of subpages have been added as collections
        if second_run:
            sys.stdout.write('{}.'.format(self.countdown))
            self.countdown -= 1
            return
        
        # Getting the nested subcategories
        these_subcats = self.get_all_nested_subcategories_from_parent(category, nesting_level=nesting_level)
        
        self.countdown = len(these_subcats)
        print('There are {} subcategories that need to be added to {}.\n'.format(self.countdown, self.database_name))
        self.countdown -= 1
              
        if these_subcats == []:
            print('There were no subcategory pages included in "{}".'.format(category))
            return
       
        # Getting all of the page content from the subcategories found using get_all_nested_subcategories_from_parent
        for subcat in these_subcats:
            self.get_all_page_contents_from_category(subcat, second_run=True)

        
    def get_all_nested_subcategories_from_parent(self, parent_category, nesting_level=0):
                
        # regex and API query for getting all subcategories of a parent
        category_re = re.sub('\s', '+', parent_category)
        query = 'https://en.wikipedia.org/w/api.php?action=query&format=json&cmlimit=max&list=categorymembers&\
                 cmtitle=Category:{}&cmtype=subcat'.format(category_re)

        QR = requests.get(query)
        
        # getting only the parts of the file that include 'title'
        subcat_dict = QR.json()['query']['categorymembers']
       
        # stripping out 'Category:' from title name
        subcat_list = []
        for i, item in enumerate(subcat_dict):
            subcat_list.append(subcat_dict[i]['title'][9:])

        # extending the self.pages list with all the subcategory titles
        self.all_subcategories_list.extend(subcat_list) 
        
        # iterating trough all subcategories contained in a parent and getting any potential nested categories     
        count = 0
        while count < nesting_level:

            for subcat in set(self.all_subcategories_list):
                self.get_all_nested_subcategories_from_parent(subcat, nesting_level=0)
            
            count += 1
        
        # returns a set of all the titles for subcategories of a parent category. 
        return sorted(set(self.all_subcategories_list))

    
class df_maker_merge_all_mongo_content():
    '''Merges all of the collections in the databases specified into one dataframe.'''
    my_df = pd.DataFrame()
   
    def make_collection_df(self, database, collection):
        return pd.DataFrame(list(client[database][collection].find()))

    def merge_collections(self, database):
        collection_list = [x for x in client[database].collection_names()]
        for col in collection_list:
            temp_df = self.make_collection_df(database, col)
            self.my_df = pd.concat([self.my_df, temp_df], ignore_index=True)
        return self.my_df
    
    def merge_databases(self, databases_list):
        for db in databases_list:
            self.merge_collections(db)
        return self.my_df
    