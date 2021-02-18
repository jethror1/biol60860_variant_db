from flask import Flask, render_template
from flask_pymongo import PyMongo


app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/manchester2021"
mongo = PyMongo(app)


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
    variant = mongo.db.variants.find().count()

    return render_template('search.html', variant=variant)
