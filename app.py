from flask import Flask, request, make_response, render_template, Response

app = Flask(__name__, template_folder='templates', static_folder='public', static_url_path='/')

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