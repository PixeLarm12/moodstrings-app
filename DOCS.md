# BACKEND

## DOCS

    To access api docs, access `localhost:8000/docs` and see Swagger docs native from FastAPI

## RULES

### Folders and how to use

1. `src`

    This folder store basically all of scripts

2. `src/dataset`

    To use as dataset folder storage. `.csv` accepted, for example

3. `src/controller`

    To create classes base on routes grouped. Controller must receive data from request, validate using any `validator/` and send it to any `services/`;

4. `src/util`

    Classes that are used to format and manipulate data with very specific purpose. For example, if need to format date everytime from `YYYY-mm-dd` into `dd/mm/YYYY`, create a `DateUtil` with `formatDate` function

5. `src/validators`

    Classes to validate data from request. Normally used into controller before the current data send to services,

6. `src/services`

    Group of functions that do something for someone. For example, if exists `MidiService.py` it is expected that the class has functions to manage midi files, for example.
