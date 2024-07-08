from flask_login import login_user, logout_user, current_user, login_required, UserMixin
from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import json
import time
import pandas as pd
from bson import json_util

class User(UserMixin):
    def __init__(self, user_json):
        self.user_json = user_json

    def get_id(self):
        object_id = self.user_json.get('_id')
        return str(object_id)
    
    def __repr__(self):
        return f'<User: {self.user_json.get('username')}>'


def register_routes(app, db, bcrypt, cos_sim):
    
    users_collection = db['users']
    movies_collection = db['movies']
    movie_lists_collection = db['movie_lists']

    
    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if isinstance(current_user, dict):
            return redirect(url_for('movielist'))
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            # Check if the username already exists
            if users_collection.find_one({'username': username}):
                flash('Username already exists. Choose a different one.', 'danger')
            else:
                hashed = bcrypt.generate_password_hash(password)
                new_user = users_collection.insert_one({'username': username, 'hashed': hashed})
                movie_lists_collection.insert_one({'user_id': new_user.inserted_id, 'movies': []})
                return redirect(url_for('movielist'))

        return render_template('register.html')
            
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if isinstance(current_user, dict):
            return redirect(url_for('movielist'))
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            user_json = users_collection.find_one({'username': username})
            if user_json:
                print(user_json)
                hashed = user_json['hashed']
                # Check if the username and password match
                if bcrypt.check_password_hash(hashed, password):
                    user = User(user_json)
                    login_user(user)
                    print(user)
                    return redirect(url_for('movielist'))
                else:
                    flash('Invalid password. Please try again.', 'danger')
            else:
                flash('User does not exist. Please try again.', 'danger')
        return render_template('login.html')
    
    @app.route('/logout', methods=['POST'])
    def logout():
        logout_user()
        return redirect(url_for('login'))
    
    @app.route('/movielist')
    def movielist():
        if not isinstance(current_user, dict):
            return redirect(url_for('login'))
        
        movie_list = movie_lists_collection.find_one({'user_id': current_user['_id']})
        
        # Insert Example
        # movie_list = {'movies': [{'title': 'john wick', 'date_added': 'today', 'rating': 3}]} 
        # movie_lists_collection.update_one({'user_id': current_user['_id']}, {'$set': movie_list})
        
        movie_list = movie_lists_collection.find_one({'user_id': current_user['_id']})
        movies = movie_list['movies']        
        if movie_list:
            return render_template('movielist.html', movies=movies)
        else:
            return render_template('movielist.html')
        
    @app.route('/rating_add', methods=['POST'])
    def rating_add():
        data = json.loads(request.data)
        
        if data['rating']: 
            rating = int(data['rating'])
        else:
            rating = None
        title = data['title']
        
        movie_list = movie_lists_collection.find_one({'user_id': current_user['_id']})
        
        movies = movie_list['movies']
        index_of_movie_to_be_updated = next((i for i, movie in enumerate(movies) if movie["title"] == title), None)
        movie_to_be_updated = movies[index_of_movie_to_be_updated]
        movie_to_be_updated['rating'] = rating
        movies[index_of_movie_to_be_updated] = movie_to_be_updated
        movie_lists_collection.update_one({'user_id': current_user['_id']}, {'$set': {"movies.$[elem].rating": rating }}, array_filters=[{ "elem.title": title } ])
        print(movies)
        
        return "OK"
    
    @app.route('/get_all_movies')
    def get_all_movies():
        movies = []
        with open('movies.csv') as file:
            csvFile = csv.reader(file)
            headers = next(csvFile)
            for lines in csvFile:
                movie = {}
                for i, header in enumerate(headers):
                    movie[header] = lines[i]
                movies.append(movie)
        return movies
    
    @app.route('/movie_add', methods=['POST'])
    def movie_add():
        data = json.loads(request.data)
        title = data['title']
        
        print('movie to add:',title)
        
        movie_list = movie_lists_collection.find_one({'user_id': current_user['_id']})
        movies = movie_list['movies']
        for movie in movies:
            print(movie)
            if movie['title'] == title:
                return {'error': "ERROR"}
		
        date = time.strftime('%B %d %-I:%M %p')
        print(date)
        
        new_movie = {'title': title, 'date_added': date, 'rating': None}
        movie_list = movie_lists_collection.update_one({'user_id': current_user['_id']}, {'$push': {'movies': new_movie}})
        print(movie_list)
        return {'ok': "OK"}

    
    def get_similar2(title):
        df = pd.read_csv('movies.csv')
        index_of_title = df[df['title']==title].index.values
        similar_shows = df[['id', 'title']].copy()
        
        similar_shows['similarity_score'] = [cos_sim[index_of_title, i][0] for i in range(len(similar_shows))]
        similar_shows['similar_to'] = title
        similar_shows = similar_shows.sort_values(by=['similarity_score'], ascending=False)
        similar_shows = similar_shows[similar_shows['similarity_score']>=0.1]
        return similar_shows[['title', 'similarity_score', 'similar_to']].drop(index_of_title, axis=0)

    @app.route('/reclist')
    def reclist():
        movie_list = movie_lists_collection.find_one({'user_id': current_user['_id']})
        movies = movie_list['movies']
        recs = []
        
        for movie in movies:
            multiplier = movie['rating']
            if multiplier:
                similar_shows = get_similar2(movie['title'])
                similar_shows['similarity_score'] = similar_shows['similarity_score'] * multiplier
                recs.extend(similar_shows.to_dict('records'))
                
        print(recs)
        sorted_recs = sorted(recs, key=lambda i: i['similarity_score'], reverse=True)
        print(sorted_recs)
        
        no_duplicate_recs = []
        read_ids = set()
        for movie in movies:
            read_ids.add(movie['title'])
        for sorted_rec in sorted_recs:
            if sorted_rec['title'] not in read_ids:
                read_ids.add(sorted_rec['title'])
                no_duplicate_recs.append(sorted_rec)
                    
        return render_template('reclist.html', recs=no_duplicate_recs)
    
    
    @app.route('/get_movie_info', methods=['POST'])
    def get_movie_info():
        data = json.loads(request.data)
        title = data['title']
        movies = movies_collection
        movie = movies.find_one({'title': title})
        print(movie)
        if movie:
            return {'ok': 'OK', 'movie': json.loads(json_util.dumps(movie))}
        else:
            return {'error': 'ERROR'}
        
    @app.route('/remove_movie', methods=['POST'])
    def remove_movie():
        data = json.loads(request.data)
        title = data['title']
        print(title)
        print(list(movie_lists_collection.find())[1])
        movie_lists_collection.update_one({'user_id': current_user['_id']}, {'$pull': {"movies": {'title': title} }})
        print(list(movie_lists_collection.find())[1])
        return {'ok': 'OK'}
