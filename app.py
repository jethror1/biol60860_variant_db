import os
import json
from flask import Flask, flash, session, request, url_for, redirect, render_template, send_from_directory
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = b'_39jqjfg90qtqpj/'

UPLOAD_FOLDER = "/home/fern/scripts/biol60860_variant_db/uploads"
ALLOWED_EXTENSIONS = {"json"}

app.config["MONGO_URI"] = "mongodb://localhost:27017/manchester2021"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_json(filepath):
    try:
        print(filepath)
        data = [json.loads(line) for line in (open(filepath))]
        return data
    except ValueError as e:
         print('invalid json!')
         flash('json file is not valid')

@app.route('/')
def home():
    """Main home page for navigation"""
    return render_template('home.html')


@app.route('/single_upload')
def single_upload():
    """Page for uploading single variant via form to database"""
    return render_template('single_upload.html')


@app.route('/bulk_upload', methods=['GET', 'POST'])
def bulk_upload():
    """Page for uploading bulk json data to database"""
    
    if request.method == 'POST':
        if 'file' not in request.files: #check for a file
            flash('No file part')
            return redirect(request.url)
        file = request.files['file'] #check a file has been selected
        if file.filename == "":
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename): #save the file 
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data = parse_json(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #parse the json
            newgenes = mongo.db.variants.insert_many(data)
            flash('Upload successful!')
            return(redirect('/bulk_upload'))
            #print(newgenes.inserted_ids)
            #return redirect(url_for('uploaded_file', filename=filename))
    return render_template('bulk_upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/search')
def search():
    """Page for searching database"""
    variant = mongo.db.variants.find().count()

    return render_template('search.html', variant=variant)

if __name__ == "__main__":
    app.run(debug=True)