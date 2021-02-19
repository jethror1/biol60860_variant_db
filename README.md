# BIOL60860 IT for Advanced Bioinformatics Variant Database
[![made-with-python][python-image]][python-url] [![flask-image]][flask-url] [![github-image]][github-url] 

Variant database created with MongoDB and Flask as part of BIOL60860 IT for Advanced Bioinformatics module.

### Developers

- Andrew Smith
- Jethro Rainford
- Fern Johnson

![Variant Database](/static/images/variantDb.png)

## Description

A MongoDB NoSQL database of genomic variants accompanied by a user interface designed within the flask micro web framework.

## Current Features

### Search

A search form is provided for searching for variants via name, chromosome, position(s), reference build and clinical significance.
On submitting the form the database is queried, and matching variants are returned and displayed in a table.

### Single Variant upload

A form is presented in which users are able to enter data into set fields. This data is then saved to the databased upon the execution of the "Submit" button. 

If successful the user is redirected to a page notifying them of the successful upload, and which also displays the fields uploaded

If a variant with the given name is already present within the database an error will be returned to the user and the data will **NOT** be saved to the database. The user will instead be redirected to a page notifying them of the error.

### Bulk Variant Upload (via JSON File)

Users can submit a JSON file of variants for bulk upload into the database.  Only JSON files will be accepted, otherwise the use will be prompted to upload a JSON file.
After upload the user is directed to a page with a list of results for the submitted variants, either the ID of the newly created document is given, or the error message returned by the database if the upload of the variant was unsuccessful. 

## Future Work



[python-image]: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
[python-url]: https://www.python.org/
[flask-image]: https://img.shields.io/static/v1?label=Made%20with&message=Flask&color=<green>
[flask-url]: https://github.com/pallets/flask
[github-image]: https://img.shields.io/static/v1?label=GitHub&message=Repo&color=blue
[github-url]: https://github.com/jethror1/biol60860_variant_db
