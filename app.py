from flask import Flask, render_template
from flask_pymongo import PyMongo


app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/manchester2021"
mongo = PyMongo(app)


@app.route('/')
def home():
    """Main home page for navigation"""
    return render_template('home.html')


@app.route('/single_upload')
def single_upload():
    """Page for uploading single variant via form to database"""
    return render_template('single_upload.html')


@app.route('/bulk_upload')
def bulk_upload():
    """Page for uploading bulk json data to database"""
    return render_template('bulk_upload.html')


@app.route('/search')
def search():
    """Page for searching database"""
    variant = mongo.db.variants.find().count()

    return render_template('search.html', variant=variant)
