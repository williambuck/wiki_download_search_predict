# Semantic Search

## Summary

The original prompt for this project is included after the section entitled "The Task". Below, I have detailed what the three .py files do with regards to the Wikipedia data.

**You can see a demonstration of each of this scripts in the Project_4-Final_Notebook_download-search-predict.ipynb file**

### download.py, search.py, and predict.py

The three .py files that are run in this notebook will do the following:
1. Download all of the page text, pageids, and titles from pages from a certain category.
    - This information is stored in a mongoDB set up on an AWS instance. The client connection is set in all three of the scripts as ```MongoClient('35.163.182.105', 27016)```
    - The way I have organized the data in mongo: 
        - Each category that is downloaded has its own database in mongo. 
        - Each collection is a subcategory of the orginally downloaded category.
        - Each document in a collection is a page that falls under the category in Wikipedia.
1. Search for any word or phrase in the contents of the downloaded Wikipedia pages.
    - When search.py is first run, it will merge all of the information in the mongo databases so that they can be searched.
1. Predict the category of a page from the wikipdia page title.
    - predict.py analyzes all of the page content related to a certain category, and when a page title is passed to the ```predict``` method, it uses the Wikipedia API to get all of the page text of the passed title, then predicts the category of the page based on that content.
    - The downloaded data must be stored in a pandas DataFrame in order for categorical predictions to be made.




-----------------------

## The Task
The objective of this assignment is to engineer a novel wikipedia search engine using what you've learned about data collection, infrastructure, and natural language processing.

The task has two **required sections:**
- Data collection
- Search algorithm development

And one **optional section:** 
  - Predictive modeling

![](http://interactive.blockdiag.com/image?compression=deflate&encoding=base64&src=eJxdjrsOwjAMRXe-wlsmRhaQkDoiMSDxBW5slahtHDmGCiH-nfQxtKy-59zruhPfUsAGPjsA56XvMdIRSIbYCZKD_RncENqQuGBQ3S7TidCwxsynjZUZ1T8m4HqvJlXZnhrBJMHBbWlTDHEeSFravYUXQy_E3TKrwbioMKb5z16UmRxfXZurVY_GjegbhqJIjaXm-wNmzE4W)

### Part 1 -- Collection (required)

We want you to query the wikipedia API and **collect all of the articles** under the following wikipedia categories:

* [Machine Learning](https://en.wikipedia.org/wiki/Category:Machine_learning)
* [Business Software](https://en.wikipedia.org/wiki/Category:Business_software)

The raw page text and its category information should be written to a collection on a Mongo server running on a dedicated AWS instance.

We want your code to be modular enough that any valid category from Wikipedia can be queried by your code. You are encouraged to exploit this modularity to pull additional wikipedia categories beyond ML and Business Software. As always, the more data the better. 

**Note:** Both "Machine Learning" and "Business Software" contain a heirarchy of nested sub-categories. Make sure that you pull every single page within each parent category, not just those directly beneath them. Take time to explore wikipedia's organization structure. It is up to you if you want to model this heirarchy anywhere within Mongo, otherwise flatten it by only recording the parent category associated with each page.

**optional**  
Make it so that your code can be run via a python script e.g.

```bash
$ docker run --rm -v $(pwd):/home/jovyan jupyter/scipy-notebook python download.py #SOME_CATEGORY#
```
This docker command starts a disposable scipy-notebook container for one-time use to run your script, `download.py`. Where `#SOME_CATEGORY#` is the wikipedia category to be downloaded. Read about passing arguments to python scripts here: https://docs.python.org/3/library/sys.html. 

**optional**  
Make it so that your code can query nested sub-categories e.g.

```bash
$ docker run --rm -v $(pwd):/home/jovyan jupyter/scipy-notebook python download.py #SOME_CATEGORY# #NESTING_LEVEL#
```

### Part 2 -- Search (required)

Use Latent Semantic Analysis to search your pages. Given a search query, find the top 5 related articles to the search query. SVD and cosine similarity are a good place to start. 

**optional**  
Make it so that your code can be run via a python script e.g.

```bash
$ docker run --rm -v $(pwd):/home/jovyan jupyter/scipy-notebook python search.py #SOME_TERM#
```

### Part 3 -- Predictive Model (optional)

In this part, we want you to build a predictive model from the data you've just indexed. Specifically, when a new article from wikipedia comes along, we would like to be able to predict what category the article should fall into. We expect a training script of some sort that is runnable and will estimate a model. 

Make it so that your code can be run via a python script e.g.

```bash
$ docker run --rm -v $(pwd):/home/jovyan jupyter/scipy-notebook python train.py
```

Finally, you should be able to pass the url of a wikipedia page and it will generate a prediction for the best category for that page, along with a probability of that being the correct category. 

Make it so that your code can be run via a python script e.g.

```bash
$ docker run --rm -v $(pwd):/home/jovyan jupyter/scipy-notebook python predict.py #URL#
```

## Infrastructure

We recommend that you run a MongDB server on a dedicated t2.micro instance. Feel free to run your Jupyter environment either on another instance or locally.


