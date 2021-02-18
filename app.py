from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired


app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/manchester2021"

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)

mongo = PyMongo(app)

DATA = list(mongo.db.variants.find({}))

def get_names(source):
    names = []
    for row in source:
        # lowercase all the names for better searching
        name = row["name"].lower()
        names.append(name)
    return sorted(names)

def get_id(source, name):
    for row in source:
        # lower() makes the string all lowercase
        if name.lower() == row["name"].lower():
            id = row["_id"]
            # change number to string
            id = str(id)
            # return id if name is valid
            return id
    # return these if id is not valid - not a great solution, but simple
    return "Unknown"


class VariantForm(FlaskForm):
    name = StringField('Variant Name?')
    chromosome = SelectField('Chromosome?',
    choices=[
        ("1","chr1"),
        ("2","chr2"),
        ("3","chr3"),
        ("4","chr4"),
        ("5","chr5"),
        ("6","chr6"),
        ("7","chr7"),
        ("8","chr8"),
        ("9","chr8"),
        ("10","chr10"),
        ("11","chr11"),
        ("12","chr12"),
        ("13","chr13"),
        ("14","chr14"),
        ("15","chr15"),
        ("16","chr16"),
        ("17","chr17"),
        ("18","chr18"),
        ("19","chr19"),
        ("20","chr20"),
        ("21","chr21"),
        ("22","chr22"),
        ("X","chrX"),
        ("Y","chrY"),
    ])
    # chromosome = StringField('Chromosome?')
    start = IntegerField('Start Coord?')
    end = IntegerField('End Coord?')
    significance = SelectField("significance of Variant", choices = [
        ("Benign", "Benign"),
        ("Likely Benign", "Likely Benign"),
        ("Variant of Unknown Significance", "Variant of Unknown Significance"),
        ("Likely Pathogenic", "Likely Pathogenic"),
        ("Pathogenic", "Pathogenic"),
    ])
    submit = SubmitField('Submit')
    


@app.route('/')
def home():
    """Main home page for navigation"""
    return render_template('home.html')


# @app.route('/single_upload')
# def single_upload():
#     """Page for uploading single variant via form to database"""
#     mongo.db.variants.insert_one({"name":"test", "MAF":"0.08969698"}).inserted_id
#     variant = mongo.db.variants.find_one({"name":"test"})

#     return render_template('single_upload.html', variant=variant)


	

@app.route('/single_upload', methods=['GET', 'POST'])
def single_upload():
    names = get_names(DATA)
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = VariantForm()
    message = ""
    if form.validate_on_submit():
        name = form.name.data
        if name.lower() in names:
            message = "That variant is already in our database."
            return render_template('singleDuplicate.html', message=message)
        else:
            mongo.db.variants.insert_one(
                {
                    "name":form.name.data, 
                    "chromosome":form.chromosome.data, 
                    "start":form.start.data, 
                    "end":form.end.data,
                    "clinical_significance":form.significance.data,
                    }
            ).inserted_id
            variant = mongo.db.variants.find_one({"name":form.name.data})
            return render_template('singleSuccessful.html', variant=variant, names=names)
    return render_template('single_upload.html', names=names, form=form, message=message)


@app.route('/bulk_upload')
def bulk_upload():
    """Page for uploading bulk json data to database"""
    return render_template('bulk_upload.html')


@app.route('/search')
def search():
    """Page for searching database"""
    variant = mongo.db.variants.find().count()

    return render_template('search.html', variant=variant)
