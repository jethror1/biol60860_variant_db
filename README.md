# BIOL60860 IT for Advanced Bioinformatics Variant Database
[![made-with-python][python-image]][python-url] [![flask-image]][flask-url] [![github-image]][github-url] 

Variant database created with MongoDB and Flask as part of BIOL60860 IT for Advanced Bioinformatics module.

### Developers

- Andrew Smith (Fyodir)
- Jethro Rainford (jethror1)
- Fern Johnson (FernJohnson)

![Variant Database](https://raw.githubusercontent.com/jethror1/biol60860_variant_db/dev/static/images/variantDb.png)

## Description

A MongoDB NoSQL database of genomic variants accompanied by a user interface designed within the flask micro web framework.

## Requirements

Python requirements are specified in `requirements.txt` and may be installed with `pip`.
A mongo database is also required, both secret key and uri need to be specified in `config.py`.

## Usage
Once the requirements have been set, the server may be started with:
```
export FLASK_APP=app.py
flask run
```

## Current Features

### Search

A form is presented for searching the database(shown below), this allows for searching for variants via name, reference build, position or clinical signficance.
On searching, the database is queried and matching variants presented in a table.

![search form](https://raw.githubusercontent.com/jethror1/biol60860_variant_db/dev/static/images/search_form_image.png)
![search results](https://raw.githubusercontent.com/jethror1/biol60860_variant_db/dev/static/images/search_results_image.png)

### Single Variant Upload

A form is presented in which users are able to enter data into set fields. This data is then saved to the databased upon the execution of the "Submit" button. 

If successful the user is redirected to a page notifying them of the successful upload which also displays the fields uploaded. If a variant with the given name is already present within the database an error will be returned to the user and the data will **NOT** be saved to the database. The user will instead be redirected to a page notifying them of this error.


![upload form](/static/images/uploadFormComplete.png)
![upload success](/static/images/uploadSuccessful.png)
![upload error](/static/images/uploadErrorDuplicate.png)
<!-- ![upload form](https://raw.githubusercontent.com/jethror1/biol60860_variant_db/dev/static/images/uploadFormComplete.png) -->
<!-- ![upload success](https://raw.githubusercontent.com/jethror1/biol60860_variant_db/dev/static/images/uploadSuccessful.png)
![upload error](https://raw.githubusercontent.com/jethror1/biol60860_variant_db/dev/static/images/uploadErrorDuplicate.png) -->


### Bulk Variant Upload (via JSON File)

Users can submit a JSON file of variants for bulk upload into the database.  Only JSON files will be accepted, otherwise the use will be prompted to upload a JSON file.
After upload the user is directed to a page with a list of results for the submitted variants, either the ID of the newly created document is given, or the error message returned by the database if the upload of the variant was unsuccessful. 

## Future Work

- Dynamic table of results from search query
- Option to review data before it is submitted
- Option to select different file types for bulk variant upload (.vcf, .json ...)

[python-image]: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
[python-url]: https://www.python.org/
[flask-image]: https://img.shields.io/static/v1?label=Made%20with&message=Flask&color=<green>
[flask-url]: https://github.com/pallets/flask
[github-image]: https://img.shields.io/static/v1?label=GitHub&message=Repo&color=blue
[github-url]: https://github.com/jethror1/biol60860_variant_db
