# Requirements
Version: 1
Author: Fern Johnson 

## Goal 
Produce a large data that can be queried by Genomic Clinical Scientists via a front-end.

## User stories - Genomic Clinical Scientist
1. As a Clinical Scientist, I want to be able to find all the variants between two positions on a chromosome to see what variants are in the region of interest.
2. ..., I want to find all the pathogenic variants in the database to help with variant interpretation.
3. ..., I want to find all the missense variants in the database to test a missense prediction tool.
4. ..., I want to be able to see where the information has come from and when it was uploaded, so I know it is up to date and reliable.
5. ..., I want to easily navigate to other data sources, such as the dbSNP entry for a variant, to easily find more information.

## Non functional requirements
1. The database must be a NoSQL database.
2. The front end must be user friendly.
3. Queries shoudn't take a very long time.
4. Errors should be smoothly handled.
