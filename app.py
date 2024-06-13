from flask import Flask, request, make_response, render_template, Response
from db import AtlasClient

app = Flask(__name__, template_folder='templates', static_folder='public', static_url_path='/')

ATLAS_URI = "mongodb+srv://jwangjy315:kkEQFR16wYGD95H3@cluster0.c4k5pnn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

DB_NAME = 'sample_mflix'
COLLECTION_NAME = 'embedded_movies'

atlas_client = AtlasClient (ATLAS_URI, DB_NAME)
atlas_client.ping()
print ('Connected to Atlas instance! We are good to go!')



# scrape movie info off imdb



@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=18686, debug=True)