from collections import defaultdict
import os
import json
import datetime

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

from config import SECRET_KEY, MONGO_URI

app = Flask(__name__)
# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = SECRET_KEY

# UPLOAD_FOLDER = "/home/fern/scripts/biol60860_variant_db/uploads"

UPLOAD_FOLDER = f"{os.getcwd()}/uploads"

ALLOWED_EXTENSIONS = {"json"}

app.config["MONGO_URI"] = MONGO_URI
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


# def get_id(source, name):
#     for row in source:
#         # lower() makes the string all lowercase
#         if name.lower() == row["name"].lower():
#             id = row["_id"]
#             # change number to string
#             id = str(id)
#             # return id if name is valid
#             return id
#     # return these if id is not valid - not a great solution, but simple
#     return "Unknown"

def bulk_variants(data):
    #there is an insert many function but it doesn't let you resolve individual uploads/failures
    result = []
    for j in data:
        
        qr = stop_duplicates(j['name'])
        if qr:
            result.append("Variant {0} already present in data with ID {1}".format(j['name'], qr['_id']))
        else:
            try:
                id=mongo.db.variants.insert_one(j)
                result.append("Variant {0} inserted as {1}".format(j['name'], id.inserted_id))
            except Exception as e:
                result.append("Variant {0} failed upload: {1}".format(j['name'], e))
                
    return result

def stop_duplicates(n):
    hit = mongo.db.variants.find_one({"name": n})
    return hit 

class VariantForm(FlaskForm):
    name = StringField('Variant Name?', validators=[validators.data_required()])
    build = SelectField(
        'Reference Build',
        choices=[
            (False, "------ SELECT BUILD ------"),
            ('GRCh37', 'GRCh37'), ('GRCh38', 'GRCh38')
        ], validators=[validators.data_required()]
    )
    typeChoices = mongo.db.variants.distinct("var_class")
    TYPE = [y for y in zip(typeChoices,typeChoices)]
    TYPE.insert(0,(False, "------ SELECT TYPE ------"))
    variantType = SelectField("Type of Variant", choices=TYPE, validators=[validators.data_required()])

    chromosome = SelectField(
        'Chromosome',
        choices=[
            (False, "------ SELECT CHROMOSOME ------"),
            ("1", "chr1"), ("2", "chr2"), ("3", "chr3"),
            ("4", "chr4"), ("5", "chr5"), ("6", "chr6"),
            ("7", "chr7"), ("8", "chr8"), ("9", "chr9"),
            ("10", "chr10"), ("11", "chr11"), ("12", "chr12"),
            ("13", "chr13"), ("14", "chr14"), ("15", "chr15"),
            ("16", "chr16"), ("17", "chr17"), ("18", "chr18"),
            ("19", "chr19"), ("20", "chr20"), ("21", "chr21"),
            ("22", "chr22"), ("X", "chrX"), ("Y", "chrY"),
        ], validators=[validators.data_required()]
    )
    start = IntegerField('Start Coord?', validators=[validators.data_required()])
    end = IntegerField('End Coord?', validators=[validators.data_required()])

    ancestralAllele = StringField('Wild Type', validators=[validators.data_required()])
    minorAllele = StringField('Variant', validators=[validators.data_required()])

    significance = SelectField("significance of Variant", choices = [
        (False, "------ SELECT SIGNIFICANCE ------"),
        ("Benign", "Benign"),
        ("Likely Benign", "Likely Benign"),
        ("Variant of Unknown Significance", "Variant of Unknown Significance"),
        ("Likely Pathogenic", "Likely Pathogenic"),
        ("Pathogenic", "Pathogenic"),
    ], validators=[validators.data_required()])
    
    submit = SubmitField('Submit')


@app.route('/')
def home():
    """Main home page for navigation"""
    total_vars = variants = mongo.db.variants.find({}).count()

    return render_template('home.html', total_vars=total_vars)



@app.route('/single_upload', methods=['GET', 'POST'])
def single_upload():
    currentDateTime = datetime.datetime.now().strftime("%m/%d/%Y_%H:%M")
    #DATA = list(mongo.db.variants.find({}))
    #names = get_names(DATA)
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = VariantForm()
    message = ""
    if form.validate_on_submit():
        name = form.name.data
        ds = stop_duplicates(name.lower())
        if ds:
            flash('{} is already in our database.'.format(name))
            return render_template('single_upload.html', form=form)
            # message = "That variant is already in our database."
            # return render_template('singleDuplicate.html', name=name, message=message)
        else:
            location = "{}:{}-{}".format(form.chromosome.data, str(form.start.data), str(form.end.data))
            mongo.db.variants.insert_one(
                {
                    
                    "source":"User Upload - Single Variant",
                    "name":form.name.data,
                    "var_class":form.variantType.data,
                    "mappings": [{
                        "assembly_name":form.build.data,
                        "seq_region_name":form.chromosome.data,
                        "start":form.start.data,
                        "end":form.end.data,
                        "location":location,
                    }],
                    "ancestral_allele":form.ancestralAllele.data,
                    "minor_allele":form.minorAllele.data,
                    "clinical_significance":form.significance.data,
                    "date_time_uploaded":currentDateTime,
                    }
            ).inserted_id
            variant = mongo.db.variants.find_one({"name":form.name.data})
            return render_template('singleSuccessful.html', name=name, variant=variant)
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
        else:
            flash('Please submit a json file')

    return render_template('bulk_upload.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


class SearchForm(FlaskForm):
    """Form fields for user searching database"""
    name = StringField('Variant Name', validators=[validators.Optional()])
    build = SelectField(
        'Reference Build',
        choices=[
            (False, "------ SELECT BUILD ------"),
            ('GRCh37', 'GRCh37'), ('GRCh38', 'GRCh38')
        ], validators=[validators.Optional()]
    )
    chromosome = SelectField(
        'Chromosome',
        choices=[
            (False, "------ SELECT CHROMOSOME ------"),
            ("1", "chr1"), ("2", "chr2"), ("3", "chr3"),
            ("4", "chr4"), ("5", "chr5"), ("6", "chr6"),
            ("7", "chr7"), ("8", "chr8"), ("9", "chr9"),
            ("10", "chr10"), ("11", "chr11"), ("12", "chr12"),
            ("13", "chr13"), ("14", "chr14"), ("15", "chr15"),
            ("16", "chr16"), ("17", "chr17"), ("18", "chr18"),
            ("19", "chr19"), ("20", "chr20"), ("21", "chr21"),
            ("22", "chr22"), ("X", "chrX"), ("Y", "chrY"),
        ], validators=[validators.Optional()]
    )
    start = IntegerField('Start Coordinate', validators=[validators.Optional()])
    end = IntegerField('End Coordinate', validators=[validators.Optional()])
    significance = SelectField("Significance of Variant", choices=[
        (False, "------ SELECT SIGNIFICANCE ------"),
        ("Benign", "Benign"),
        ("Likely Benign", "Likely Benign"),
        ("Variant of Unknown Significance", "Variant of Unknown Significance"),
        ("Likely Pathogenic", "Likely Pathogenic"),
        ("Pathogenic", "Pathogenic"),
    ], validators=[validators.Optional()])
    submit = SubmitField('Submit')


@app.route('/search', methods=['GET', 'POST'])
def search():
    """Page for searching database"""
    form = SearchForm()

    if form.submit.data:
        # form submitted

        if any([form.start.data, form.end.data, form.chromosome.data]):
            if '-' in form.chromosome.data:
                form.chromosome.data = None

            if not form.chromosome.data and (form.start.data or form.end.data):
                # missing chrom with start or end
                flash(u'Missing chromosome, start or end in form', 'error')
                return render_template('search.html', form=form)

        search_dict = {
            "name": {'$eq': form.name.data},
            "mappings.seq_region_name": {'$eq': form.chromosome.data},
            "mappings.start": {'$gte': form.start.data},
            "mappings.end": {'$lte': form.end.data},
            "clinical_significance": {'$eq': [form.significance.data.lower()]},
            "mappings.assembly_name": {'$eq': form.build.data}
        }
        query_dict = {}

        # human readable searches to display in template
        terms = []

        # build dict to search with from passed fields
        for key, val in search_dict.items():
            for k, v in val.items():
                if v is not None and '-' not in str(v) and v != '':
                    query_dict[key] = val
                    if isinstance(v, list):
                        # some are lists of 1 element
                        v = v[0]
                    terms.append(f"{key}: {v}")

        # gross mess to format nicely for viewing
        terms = [
            x.replace('_', ' ').replace(
                'mappings.', '').replace('seq region name', 'chromosome'
            ).replace('_', ' ') for x in terms
        ]

        print(terms)

        # query database
        result = list(
            mongo.db.variants.find(query_dict, {
                'name': 1, 'mappings': 1, 'MAF': 1, 'ambiguity': 1,
                'var_class': 1, 'synonyms': 1, 'evidence': 1,
                'ancestral_allele': 1, 'minor_allele': 1,
                'most_severe_consequence': 1, 'clinical_significance': 1
            })
        )

        variants = []

        for var in result:
            print(var)
            # build dict with formatting to pass to template
            var = defaultdict(str, var)
            var_dict = defaultdict(None)

            var_dict['name'] = var['name']
            var_dict['GRCh37'] = [
                x['location']
                for x in var['mappings']
                if x['assembly_name'] == 'GRCh37'
            ]
            var_dict['GRCh38'] = [
                x['location']
                for x in var['mappings']
                if x['assembly_name'] == 'GRCh38'
            ]
            var_dict['MAF'] = var['MAF']
            var_dict['ambiguity'] = var['ambiguity']
            var_dict['var_class'] = var['var_class']
            var_dict['synonyms'] = '; '.join([str(x) for x in var['synonyms']])
            var_dict['evidence'] = '; '.join(
                [str(x).replace('_', ' ') for x in var['evidence']]
            )
            var_dict['ancestral_allele'] = var['ancestral_allele']
            var_dict['minor_allele'] = var['minor_allele']
            var_dict['most_severe_consequence'] = var['most_severe_consequence'].replace('_', ' ')

            if 'clinical_significance' in var.keys():
                if isinstance(var['clinical_significance'], list):
                    var_dict['clinical_significance'] = "; ".join(
                            [str(x).capitalize() for x in var['clinical_significance']]
                    )
                else:
                    var_dict['clinical_significance'] = var['clinical_significance']
            else:
                var_dict['clinical_significance'] = None

            for k, v in var_dict.items():
                if isinstance(v, list) and len(v) == 0:
                    var_dict[k] = None
                if isinstance(v, list) and len(v) == 1:
                    var_dict[k] = v[0]

            variants.append(var_dict)

        total = len(variants)

        return render_template(
            'search_results.html', variants=variants, terms=terms, total=total
        )

    # render empty form
    return render_template('search.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)
