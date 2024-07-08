from flask import Flask, request, make_response, render_template, Response, redirect
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import csv
import time
import requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from bson import ObjectId
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity




load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='public', static_url_path='/')
app.secret_key = 'keroppi'

column_names = ['id', 'title', 'poster_url', 'year', 'duration', 'age_rating', 'star_rating', 'num_ratings', 'description']

# scrape movie info off imdb
def scrape_movies(url):
    soup = BeautifulSoup(requests.get(url, headers={'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"}).content, 'html.parser')
    entries = soup.find('div', attrs={'class': 'sc-e3ac1175-3 gJQFCa'}).text
    total_entries = int(entries.split(' ')[-1].replace(",", ""))
    print(total_entries)

    driver = webdriver.Chrome()
    driver.get(url)

    index = 1
    for i in tqdm(range(int(total_entries/50))):
        button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "ipc-see-more__button")))
        try:
            button.click()
        except:
            button.click()

    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')

    movie_elements = soup.find_all('li', attrs={'class': 'ipc-metadata-list-summary-item'})

    # print(movie_elements)



    i = 1
    with open('movies.csv', 'w', newline='', encoding='utf-8') as csv_file:
        
        writer = csv.DictWriter(csv_file, fieldnames=column_names, quoting=csv.QUOTE_ALL)
        writer.writeheader()

        for div_item in tqdm(movie_elements):
            title = ' '.join(div_item.find('h3', attrs={'class': 'ipc-title__text'}).text.split()[1:])
            poster_url = div_item.find('img', attrs={'class': 'ipc-image'}).get('srcset').split()[-2]
            info = div_item.find('div', attrs={'class': 'sc-b189961a-7 feoqjK dli-title-metadata'}).findChildren()
            if len(info) > 0:
                year = info[0].text
            if len(info) > 1:
                duration = info[1].text
            if len(info) > 2:
                age_rating = info[2].text
            rating_info = div_item.find('span', attrs={'class': 'ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating'}).text
            star_rating = rating_info.split()[0]
            num_ratings = rating_info.split()[1][1:-1]
            description = div_item.find('div', attrs={'class': 'ipc-html-content-inner-div'}).text

            # print(i)
            # print(title)
            # print(poster_url)
            # print(year)
            # print(duration)
            # print(age_rating)
            # print(star_rating)
            # print(num_ratings)
            # print(description)
            # print('\n')
            
            movie = {
                "id": i,
                "title": title,
                "poster_url": poster_url,
                "year": year,
                "duration": duration,
                "age_rating": age_rating,
                "star_rating": star_rating,
                "num_ratings": num_ratings,
                "description": description
            }
            writer.writerow(movie)
            i+=1
        

    print('Done writing to csv')
    
url = os.getenv('URL')

# scrape_movies(url)

# Create a new client and connect to the server
client = MongoClient(os.getenv('DSN'), server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['movie_rec']
users_collection = db['users']
movies_collection = db['movies']
movie_lists_collection = db['movie_lists']
rec_lists_collection = db['rec_lists']

# manage login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(uid):
    user = users_collection.find_one({"_id": ObjectId(uid)}) 
    return user

bcrypt = Bcrypt(app)
    
df = pd.read_csv('movies.csv')
# nlp = spacy.load("en_core_web_md") 

# nlp.vocab['not'].is_stop = False

# def preprocess(text):
#     doc = nlp(text)
#     no_stop_words = [token.text for token in doc if not token.is_stop]
#     return " ".join(no_stop_words) 

# df['preprocessed_description'] = df['description'].map(preprocess)

# df.to_csv('movies.csv', index=False)

tfidf = TfidfVectorizer()
matrix = tfidf.fit_transform(df['preprocessed_description'])

all_feature_names = tfidf.get_feature_names_out()
    
cos_sim = cosine_similarity(matrix)

from routes import register_routes
register_routes(app, db, bcrypt, cos_sim)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('PORT'), debug=False)