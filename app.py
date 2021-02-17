from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def home():
    """Main home page for navigation"""
    return render_template('home.html')


@app.route('/upload')
def upload():
    """Page for uploading new data to database"""
    return render_template('upload.html')


@app.route('/search')
def search():
    """Page for searching database"""
    return render_template('search.html')
