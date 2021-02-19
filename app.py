import os
import json

from flask import (
    Flask, flash, session, request, url_for, redirect,
    render_template, send_from_directory
)
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from mongo_datatables import DataTables
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, SelectField, IntegerField
import wtforms.validators as validators


app = Flask(__name__)
# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# UPLOAD_FOLDER = "/home/fern/scripts/biol60860_variant_db/uploads"

UPLOAD_FOLDER = f"{os.getcwd()}/uploads"

ALLOWED_EXTENSIONS = {"json"}

app.config["MONGO_URI"] = "mongodb://localhost:27017/manchester2021"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)
Bootstrap(app)



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

def bulk_variants(data):
    #there is an insert many function but it doesn't let you resolve individual uploads/failures
    result = []
    for j in data: 
        try:
            id=mongo.db.variants.insert_one(j)
            result.append("Variant {0} inserted as {1} \n".format(j['name'], id.inserted_id))
        except Exception as e:
            result.append("Variant {0} failed upload: {1} \n".format(j['name'], e))
            continue
    return result


class VariantForm(FlaskForm):
    name = StringField('Variant Name?', validators=[validators.data_required()])

    typeChoices = mongo.db.variants.distinct("var_class")
    TYPE = [y for y in zip(typeChoices,typeChoices)]
    TYPE.insert(0,(False, "------ SELECT TYPE ------"))
    variantType = SelectField("Type of Variant", choices=TYPE)

    # chromosomeChoices = mongo.db.variants.distinct("mappings.seq_region_name")
    # CHROMOSOMES = [y for y in zip(chromosomeChoices,chromosomeChoices)]
    # CHROMOSOMES.insert(0,(False, "------ SELECT CHROMOSOME ------"))
    # chromosome = SelectField("Chromosome", choices=CHROMOSOMES)

    chromosome = SelectField(
        'Chromosome?',
        choices=[
            (False, "------ SELECT CHROMOSOME ------"),
            ("1", "chr1"),
            ("2", "chr2"),
            ("3", "chr3"),
            ("4", "chr4"),
            ("5", "chr5"),
            ("6", "chr6"),
            ("7", "chr7"),
            ("8", "chr8"),
            ("9", "chr8"),
            ("10", "chr10"),
            ("11", "chr11"),
            ("12", "chr12"),
            ("13", "chr13"),
            ("14", "chr14"),
            ("15", "chr15"),
            ("16", "chr16"),
            ("17", "chr17"),
            ("18", "chr18"),
            ("19", "chr19"),
            ("20", "chr20"),
            ("21", "chr21"),
            ("22", "chr22"),
            ("X", "chrX"),
            ("Y", "chrY"),
        ]
    )
    # chromosome = StringField('Chromosome?')

    start = IntegerField('Start Coord?', validators=[validators.data_required()])
    end = IntegerField('End Coord?', validators=[validators.data_required()])

    # NUCLEOTIDES = [
    #     (False, "------ SELECT NUCLEOTIDE ------"),
    #     ("Null", "Null"),
    #     ("G","G"),
    #     ("A","A"),
    #     ("C","C"),
    #     ("T","T"),
    # ]
    # nucleotideChoices = mongo.db.variants.distinct("minor_allele")
    # NUCLEOTIDES = [y for y in zip(nucleotideChoices,nucleotideChoices)]
    # NUCLEOTIDES.insert(0,(False, "------ SELECT NUCLEOTIDE ------"))
    ancestralAllele = StringField('Wild Type', validators=[validators.data_required()])
    minorAllele = StringField('Variant Allele', validators=[validators.data_required()])
    # minorAllele = SelectField("Variant", choices = NUCLEOTIDES)

    significance = SelectField("significance of Variant", choices = [
        (False, "------ SELECT SIGNIFICANCE ------"),
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
    total_vars = variants = mongo.db.variants.find({}).count()

    return render_template('home.html', total_vars=total_vars)



@app.route('/single_upload', methods=['GET', 'POST'])
def single_upload():
    DATA = list(mongo.db.variants.find({}))
    names = get_names(DATA)
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = VariantForm()
    message = ""
    if form.validate_on_submit():
        name = form.name.data
        if name.lower() in names:
            message = "That variant is already in our database."
            return render_template('singleDuplicate.html', name=name, message=message)
        else:
            mongo.db.variants.insert_one(
                {
                    "name":form.name.data,
                    "variantType":form.variantType.data,
                    "chromosome":form.chromosome.data,
                    "start":form.start.data,
                    "end":form.end.data,
                    "ancestral_allele":form.ancestralAllele.data,
                    "minor_allele":form.minorAllele.data,
                    "clinical_significance":form.significance.data,
                    }
            ).inserted_id
            variant = mongo.db.variants.find_one({"name":form.name.data})
            return render_template('singleSuccessful.html',  variant=variant, names=names, name=name)
    return render_template('single_upload.html', form=form)


@app.route('/bulk_upload', methods=['GET', 'POST'])
def bulk_upload():
    """Page for uploading bulk json data to database"""

    if request.method == 'POST':
        if 'file' not in request.files:  # check for a file
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']  # check a file has been selected
        if file.filename == "":
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):  # save the file
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data = parse_json(
                os.path.join(app.config['UPLOAD_FOLDER'], filename)
            )  # parse the json
            newgenes = bulk_variants(data)

            return render_template('bulk_result.html', result = newgenes)
            # print(newgenes.inserted_ids)
            # return redirect(url_for('uploaded_file', filename=filename))
        else:
            flash('Please submit a json file')

    return render_template('bulk_upload.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


class SearchForm(FlaskForm):
    """Form fields for user searching database"""
    name = StringField('Variant Name')
    build = SelectField(
        'Reference Build',
        choices=[
            (False, "------ SELECT BUILD ------"),
            ('GRCh37', 'GRCh37'), ('GRCh38', 'GRCh38')
        ]
    )
    chromosome = SelectField(
        'Chromosome',
        choices=[
            (False, "------ SELECT CHROMOSOME ------"),
            ("1", "chr1"), ("2", "chr2"), ("3", "chr3"),
            ("4", "chr4"), ("5", "chr5"), ("6", "chr6"),
            ("7", "chr7"), ("8", "chr8"), ("9", "chr8"),
            ("10", "chr10"), ("11", "chr11"), ("12", "chr12"),
            ("13", "chr13"), ("14", "chr14"), ("15", "chr15"),
            ("16", "chr16"), ("17", "chr17"), ("18", "chr18"),
            ("19", "chr19"), ("20", "chr20"), ("21", "chr21"),
            ("22", "chr22"), ("X", "chrX"), ("Y", "chrY"),
        ]
    )
    start = IntegerField('Start Coordinate')
    end = IntegerField('End Coordinate')
    significance = SelectField("Significance of Variant", choices=[
        (False, "------ SELECT SIGNIFICANCE ------"),
        ("Benign", "Benign"),
        ("Likely Benign", "Likely Benign"),
        ("Variant of Unknown Significance", "Variant of Unknown Significance"),
        ("Likely Pathogenic", "Likely Pathogenic"),
        ("Pathogenic", "Pathogenic"),
    ])
    submit = SubmitField('Submit')


@app.route('/search')
def search():
    """Page for searching database"""
    form = SearchForm()

    # Need to check form, do some validation somehow then query db with this
    # then return results to search_results template

    variants = list(mongo.db.variants.find({}, {
        'name': 1, 'mappings': 1, 'MAF': 1, 'ambiguity': 1, 'var_class': 1,
        'synonyms': 1, 'evidence': 1, 'ancestral_allele': 1, 'minor_allele': 1,
        'most_severe_consequence': 1, 'clinical_significance': 1
    }))

    return render_template('search.html', variants=variants, form=form)


if __name__ == "__main__":
    app.run(debug=True)
