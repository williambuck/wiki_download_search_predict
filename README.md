# Wikipedia Semantic Search

## You can see a demonstration of each of the scripts detailed below in the Download_Search_Predict_Demo.ipynb file

### Summary of download.py, search.py, and predict.py files
The three .py files that are run in this repository will do the following, demonstrated in three parts of the included .ipynb notebook:

**PART 1:** 
- Download all of the page text, pageids, and titles from pages from a certain category.
    - This information is stored in MongoDB which is set up on a dedicated AWS instance. The client connection is set in all three of the scripts as ```MongoClient('35.163.182.105', 27016)```
    - The way I have organized the data in MongoDB: 
        - Each category that is downloaded has its own collection in the Mongo database. 
        - A collection is also made for every subcategory of the orginally downloaded category if 'nesting_level' is specified when you run the download.py; there will be an input field.
        - Each document in a collection is a page that falls under the category in Wikipedia.

**PART 2:** 
- Search for any word or phrase in the contents of the downloaded Wikipedia pages.
    - A DataFrame must be created in the Data/ folder of the downloaded information to search it.

**PART 3:** 
- Predict the category of a page from the Wikipdia page title.
    - predict.py analyzes all of the page content related to a certain category, and when a page title is searched, it uses the Wikipedia API to get all of the page text of the passed title, then predicts the category of the page based on that content.
    - The downloaded data must be stored in a pandas DataFrame in order for categorical predictions to be made.

**Note about search/prediction accuracy and TruncatedSVD:**
<br>TruncatedSVD is included as an option before finding cosine similarity in both the predict.py and search.py scripts. It makes the results much slower, and it also is not always completely accurate becuase I'm not using an 'ngram_range' in the TFIDF transformation. I believe that doing this would increase the accuracy, but the the process keeps causing the kernel of my notebook to crash because its too intensive for my machine. An option if you would like to update the accuracy and/or search a larger number of Wikipedia articles would be to run these processes on an AWS EC2 instance.

-----------------------

## The Task

The objective of this project is to engineer a novel wikipedia search engine using NLP.

The task has three sections:
1. Data collection
1. Search algorithm development
1. Predictive modeling

### Part 1 -- Collection 

Using the download.py file, I started by querying the Wikipedia API and collecting all of the articles under the following Wikipedia categories:

* [Machine Learning](https://en.wikipedia.org/wiki/Category:Machine_learning)
* [Business Software](https://en.wikipedia.org/wiki/Category:Business_software)

The raw page text and its category information is written to a collection on a Mongo server running on a dedicated AWS instance.

The code is modular enough that any valid category from Wikipedia can be queried by the download.py script.

**Note:** Both "Machine Learning" and "Business Software" contain a heirarchy of nested sub-categories. I pulled every single page within each parent category, not just those directly beneath them, by specifying a nesting_level greater than 1. Depending on what the additional categories I downloaded where like in terms of quantity of subcategories, I would change the nesting level to be between 0-5. There is a flow chart that shows a simplified version of this in the 'Project_4-Final_Notebook.ipynb'.

### Part 2 -- Search 

The search.py file uses Latent Semantic Analysis to search the pages downloaded from Wikipdia. Given a search query, search.py will find the top 5 related articles to the search query. SVD is an option before cosine similarity, but as noted above, it is slower and less accurate without a sepecified 'ngram_range'.

### Part 3 -- Predictive Model

In this part, I built a predictive model from the data that was downloaded using the download.py script. Specifically, when a new article from Wikipedia is searched for by page title, predict.py will return what category the article should fall into based on the cosine similarity of the vectorized content of all pages included in the category of the page. 

### Infrastructure

This is all run a MongDB server on a dedicated AWS t2.micro instance. The client information is specified in all three of the download.py, search.py, and predict.py files.


