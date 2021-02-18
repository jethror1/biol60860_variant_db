import json

from bson.json_util import dumps
from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from mongo_datatables import DataTables
# from app import mongo


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
    variants = list(mongo.db.variants.find({}, {
        'name': 1, 'mappings': 1, 'MAF': 1, 'ambiguity': 1, 'var_class': 1,
        'synonyms': 1, 'evidence': 1, 'ancestral_allele': 1, 'minor_allele': 1,
        'most_severe_consequence': 1
    }))

    return render_template('search.html', variants=variants)
