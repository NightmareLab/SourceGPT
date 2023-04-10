## database schemas

MongoDB is used as the backend database.

Schemas:
 - Projects (file uploaded .zip) are saved on 'projects' schema
 - Results (metadata generated during code scan) are saved on 'results' schema
 - web app settings are saved on 'db_capa_settings' schema

Further information can be found on the file `./src/init_mongo.py` which does act as a wrapper to pymongo module.


