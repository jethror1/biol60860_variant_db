# BIOL60860 IT for Advanced Bioinformatics Variant Database
[![made-with-python][python-image]][python-url] [![flask-image]][flask-url] [![github-image]][github-url] 

Variant database created with MongoDB and Flask as part of BIOL60860 IT for Advanced Bioinformatics module.

### Developers

- Andrew Smith
- Jethro Rainford
- Fern Johnson

![Variant Database](static/variantDb.jpg)

## Description

A MongoDB NoSQL database of genomic variants accompanied by a user interface designed within the flask micro web framework.

## Current Features

### Search

### Single Variant upload

A form is presented in which users are able to enter data into set fields. This data is then saved to the databased upon the execution of the "Submit" button. 

If successful the user is redirected to a page notifying them of the successful upload, and which also displays the fields uploaded

If a variant with the given name is already present within the database an error will be returned to the user and the data will **NOT** be saved to the database. The user will instead be redirected to a page notifying them of theis error.

### Bulk Variant Upload (via JSON File)

## Future Work



[python-image]: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
[python-url]: https://www.python.org/
[flask-image]: https://img.shields.io/static/v1?label=Made%20with&message=Flask&color=<green>
[flask-url]: https://github.com/pallets/flask
[github-image]: https://img.shields.io/static/v1?label=GitHub&message=Repo&color=blue
[github-url]: https://github.com/jethror1/biol60860_variant_db