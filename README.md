# PoC - FastAPI, SQLAlchemy & Uvicorn to fetch a Google Sheet

This PoC is using FastAPI with SQLAlchemy, to :
- Fetch items from a Google Sheets document (range A:C cells), based on the Google spreadsheet ID.
- Store the items into a database (SQLite,Postgres,Mysql,MSSQL,Oracle).
- Serve the items from the DB, via Restful API.

Helpful for a cronjob/task that triggers every 5 minutes the endpoint "/cronjob/{item_id}"
It will check if it's a new Spreadsheet or already exists. 
In the first case it will create a new RECORD inside the TABLE data, otherwise it will update the existing TABLE items with the new items.

- **There are improvements to apply, and they are written in TO-DO list.**
- **Tested on a Linux machine.**

###  REST API Endpoints Design
REST API access to items resources.

| Action | HTTPVerb | Endpoint | Description |
| ------ | ------ | ------ | ------ |
| Fetch | GET | /fetch/{item_id} | Fetch All Items in realtime from Google Sheet [for debug] |
| Cronjob | POST/PUT | /cronjob/{item_id} | Fetch All Items From Google And Store/Update DB |
| Query | GET | /query | Get items from the DB based on Google ID |

### Folders structure ###

+ Deploymeny.yml (Kubernetes)
+ Dockerfile (Docker)
+ README.md (This File)
+ app (Folder with the python APP)
    + clibs (Custom Libs folder)
        + db.py
        + gservices.py
        + models.py
        + repositories.py
        + schemas.py
    + config 
        + credentials.json (to download)
        + data.db (autogenerate)
    + main.py (main python APP)
    + requiremets.txt

### Prerequisites:

- A basic python and SQLite knowledge
- A basic knowledge of python libraries, classes like Pydantic, Pandas, URLRequests.
- Google Cloud Dev account, to enable the google API and download the credentials.
- A Google spreadsheet, with the above user/credentials allowed in read mode.
- Python 3.11 with Pipenv for local test with ENV.
- Docker to test with containers.
- Kubernetes with HelmChart/FluxCD for a cluster deployment.

### SETUP & RUN ###
There are 3 differents setup to run this project:
- Local Python env
- Docker 
- Kubernetes (microk8s)

**SETUP A LOCAL PYTHON ENV**

1. Clone the reposistory

```bash
$ git clone git@github.com:garanet/fastapi_sqlalchemy.git
$ cd fastapi_sqlalchemy
```

2. Activate Virtual Environment.

```bash
$ pipenv shell --python 3.11
```

3. Install all the required dependencies using Pipenv.

```bash
$ pipenv install google-api-python-client
$ pipenv install google-auth-httplib2
$ pipenv install google-auth-oauthlib
$ pipenv install fastapi
$ pipenv install uvicorn
$ pipenv install sqlalchemy
$ pipenv install pandas
```

or

```bash
$ pip install -r requiremets.txt
```

4. Copy the credentials.json file downloaded from google dev-api.
[Follow this docs to generate the credentials.json file](https://developers.google.com/sheets/api/quickstart/python "Cloud Console title")

```bash
$ cp ~/Download/credentials.json ./app/config/
```

5. Run the app

```bash
$ python main.py
```

**SETUP A DOCKER ENV**
1. Clone the reposistory

```bash
$ git clone git@github.com:garanet/fastapi_sqlalchemy.git
$ cd fastapi_sqlalchemy
```

2. Copy the credentials.json file downloaded from google dev-api.
[Follow this docs to generate the credentials.json file](https://developers.google.com/sheets/api/quickstart/python "Cloud Console title")

```bash
$ cp ~/Download/credentials.json ./app/config/
```

3. Build the docker Application.

```bash
$ docker build -t fastapi:latest .
```

4. Run the docker Application and expose the port

```bash
$ docker run -p 9000:9000  fastapi
```

**SETUP A K8s ENV with microk8s**

1. Clone the reposistory

```bash
$ git clone git@github.com:garanet/fastapi_sqlalchemy.git
$ cd fastapi_sqlalchemy
```

2. Copy the credentials.json file downloaded from google dev-api.

```bash
$ cp ~/Download/credentials.json ./app/config/
```

3. Build the docker Application.

```bash
$ docker build -t fastapi:latest .
```

4. Export the docker image.

```bash
$ docker save fastapi:latest > fastapi.tar
```

5. Import the docker tar file in microk8s

```bash
$ microk8s ctr image import fastapi.tar
```

6. Deploy the deployment.yml file into your helmcharts/orchestra tool

```bash
$ flux reconcile ks microservices
```

### Testing ###
- Swagger UI is used to test it via browser. Visit the [swagger at 127.0.0.1:9000 ](http://127.0.0.1:9000) 
- Use curl from your terminal to:

***GET /fetch/{item_id} -> "Get items from Google without store them"***
```bash
curl -X 'GET' \
  'http://127.0.0.1:9000/fetch/{google_spreadsheet_id}' \latest.tar
  -H 'accept: application/json'
 ```

***POST /cronjob/{item_id} -> "Get items and store or update them into the DB"***
```bash
curl -X 'POST' \
  'http://127.0.0.1:9000/cronjob?item_id=1LAvH4wPOXZSdfVRRHwDGaS5ensyQg2TNm_eoISNcnQg' \
  -H 'accept: application/json' \
  -d ''
 ```
 
 ***GET /querey/{item_id} -> "Get items from the DB"***
```bash
curl -X 'GET' \
  'http://127.0.0.1:9000/query?item_id=1LAvH4wPOXZSdfVRRHwDGaS5ensyQg2TNm_eoISNcnQg' \
  -H 'accept: application/json'
```

---

### How it works

- Google
- Database
- Database Models
- Schemas
- Repositories
- Main APP / EntryPoint

**Google Cloud Console**

[Follow this docs to generate the credentials.json file](https://developers.google.com/sheets/api/quickstart/python "Cloud Console title")

**Database**

This PoC is using SQLite, but FastAPI works with any database.
To integrate database with our application, there is a file db.py with the following content:
[]()

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# SIMPE SQLITE CONFIG
SQLALCHEMY_DATABASE_URL = "sqlite:///./config/data.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Database Models**

It will add all the database entities in models.py and it’s corresponding repository in repositories.py.
The are two database models, Item, Store and its repositories. The file db.py , is related to the SQLAlchemy models.
It provides a class called Base that is a declarative base, which can be used to declare our models.

```python
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from clibs.db import Base

# DATA DB - GOOGLE SHEET NAME
class Store(Base):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True)     
    name = Column(String(200), nullable=True) 
    items = relationship("Item",primaryjoin="Store.id == Item.name",cascade="all, delete-orphan")      
    def __repr__(self):        
        return 'Store(title=%s,description=%s,image=%s)' % (self.title, self.description, self.image)

# ITEMS DB - GOOGLE SHEET ITEMS
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)     
    title = Column(String(200), nullable=True)    
    description = Column(String(200), nullable=True)    
    image = Column(String(200), nullable=True)      
    name = Column(Integer,ForeignKey('data.id'),nullable=False) 
    def __repr__(self):
        return 'Item(title=%s, description=%s,image=%s)' % (self.title, self.description,self.image)         
```

**Repositories**

The repositories.py file contains functions to interact with the data in the database.

```python
from sqlalchemy.orm import Session
import clibs.models as models
import clibs.schemas as schemas

class ItemRepo:   
# CREATE ITEMS FROM PREVIOUS STORE
    async def create(db: Session, name, item):
        db_item = models.Item(title=item['title'],description=item['description'],image=item['image'],id=item['id'],name=name)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
# FETCH/QUERY ITEMS
    def fetch_by_id(db: Session,_id):
        return db.query(models.Item).filter(models.Item.id == _id).first()

    def fetch_by_name(db: Session,name):
        return db.query(models.Item).filter(models.Item.name == name).first()

    def fetch_all_by_name(db: Session, item_id, skip: int = 0, limit: int = 1000):
        return db.query(models.Item).filter(models.Item.name == item_id).offset(skip).limit(limit).all()    

    def fetch_all(db: Session, skip: int = 0, limit: int = 1000):
        return db.query(models.Item).offset(skip).limit(limit).all()  
# UPDATE ITEMS
    async def update(db: Session,item_data):        
        updated_item = db.merge(item_data)    
        db.commit()
        return updated_item
    
# # DELETE ITEMS (NOT USED/TESTED)
#     async def delete(db: Session,item_id):
#         db_item= db.query(models.Item).filter_by(id=item_id).first()
#         db.delete(db_item)
#         db.commit()          
#

class StoreRepo:    
# CREATE GOOGLE SHEET TABLE NAME    
    async def create(db: Session, name: schemas.StoreCreate):            
            db_store = models.Store(name=name)
            db.add(db_store)
            db.commit()
            db.refresh(db_store)
            return db_store
# FETCH/QUERY GOOGLE ID SHEET       
    def fetch_by_id(db: Session,_id:int):
        return db.query(models.Store).filter(models.Store.id == _id).first()
    
    def fetch_by_name(db: Session,name:str):
        return db.query(models.Store).filter(models.Store.name == name).first()
    
    def fetch_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Store).offset(skip).limit(limit).all()
    
# # DELETE GOOGLE SHEET TABLE NAME (NOT TESTED)
#     async def delete(db: Session,_id:int):
#         db_store= db.query(models.Store).filter_by(id=_id).first()
#         db.delete(db_store)
#         db.commit()
# # UPDATE GOOGLE SHEET TABLE NAME        
#     async def update(db: Session,store_data):
#         db.merge(store_data)
#         db.commit() 
```

**Schemas**

The file contains the Pydantic models for the SQLAlchemy models. 
These Pydantic models define more or less a schema (a valid data shape).

```python
from typing import Optional
from pydantic import BaseModel

class StoreBase(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None    
    image: Optional[str] = None
    name: Optional[str] = None
    
class StoreCreate(StoreBase):
    pass

class Store(StoreBase):
    id: int
    name: Optional[str] = None
    
    class Config:
        orm_mode = True
```



**Google Libs**

This is standard Google python lib to call the spreadsheet by it' ID and get value from the cell range A:C

```python
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
def google_fetch(item_id):
    try:
# Try the Google API connection and get values from the sheet        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        credentials = Credentials.from_service_account_file('./config/credentials.json', scopes=SCOPES) # TO DO (ENCRYPT OR LOAD IT IN ANOTHER WAY)
        service = build('sheets', 'v4', credentials=credentials)
        SPREADSHEET_ID = item_id
        CELL_RANGE = 'A:C'
    except Exception as error:
        return {"error": {"error_details": str(error)}}
# Sanitize result values to JSON format
    try:            
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=CELL_RANGE).execute()
        values = result.get('values', [])        
        cells = [dict(zip(values[0], row)) for row in values[1:]]
# Add incremental ID and sanitize empty values key.
        new_items = []
        x = 0
        for row in cells :
            x +=1
            row['name'] = item_id  
            row['id'] = x
            row.setdefault('title', '-')
            row.setdefault('image', '-')
            row.setdefault('description', '-')
            new_items.append(row)  
    except Exception as error:
        return {"error": error}
    return new_items
```

**MAIN APP**

The main python application entry point. 
In the root directory of the project, with the following content:

```python
import uvicorn, json
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
import pandas as pd
# IMPORT CUSTOM MODULES/LIBS
import clibs.models as models
import clibs.schemas as schemas
from clibs.db import get_db, engine
from clibs.repositories import ItemRepo,StoreRepo
from clibs.gservices import google_fetch

# DEFINE CONFIG APP
app = FastAPI(title="G-Sheets FastAPI Application",description="FastAPI Application with Swagger and Sqlalchemy to handle google sheets",version="1.0.0",)
models.Base.metadata.create_all(bind=engine)

# MANAGE ERRORS APP
@app.exception_handler(Exception)
def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(status_code=400, content={"message": f"{base_error_message}. Detail: {err}"})

# REAL TIME FETCH THE GOOGLE SHEET BY ID (FOR DEBUG)
@app.get('/fetch/{item_id}', tags=["RealTime data from google sheet - DEBUG"])
def realtime_fetch_all_items_from_google_sheet(item_id):      
    if item_id: 
    # Get all the Items stored in Google   
        try:
            values = jsonable_encoder(google_fetch(item_id))      
        # Check errors from the Google response and sanitize result
            if "error" in values:                                     
                return jsonable_encoder({'GOOGLE ERROR': str(values['error']['error_details'])})            
            else:  
        # Import the item into a Dataframe and dump to JSON format
                df = pd.DataFrame(values)
                result = json.loads(json.dumps(list(df.T.to_dict().values())))                        
        # Return the results
                return jsonable_encoder(result)
        except Exception as error:                
            return jsonable_encoder({'ERROR': str(error)})    
    else:
        return jsonable_encoder({'ERROR': "Google item_id empty or malformat"})  
    
# FETCH THE GOOGLE SHEET BY ID AND STORE ITEMS TO DB  
@app.post('/cronjob', tags=["CronJob to add or update the DB"],status_code=201)
async def fetch_all_items_from_google_and_store_update_to_db(item_id, db: Session = Depends(get_db)):
    if item_id: 
        # Get all the Items stored in Google Sheet  
        try:
            values = jsonable_encoder(google_fetch(item_id))
        # Check errors from the Google response and sanitize result
            if "error" in values:  
                return jsonable_encoder({'GOOGLE ERROR': str(values['error']['error_details'])})
            else:                        
        # Check if the Google sheet already exists in DB
                db_store = StoreRepo.fetch_by_name(db, name=item_id)            
        # If exists update the DB with the new Items            
                if db_store:                
        # Update the key value for each row
                    for item in values:                        
                        db_item = ItemRepo.fetch_by_id(db, item['id'])
                        update_item_encoded = jsonable_encoder(item)
                        db_item.title = update_item_encoded['title']
                        db_item.description = update_item_encoded['description']
                        db_item.image = update_item_encoded['image']                    
                        db_item.name = update_item_encoded['name']    
                        update_result = await ItemRepo.update(db=db, item_data=db_item)
                    return {'Spreadsheet': "UPDATED"}     
                else:
        # Create the new DB with the new Google sheet name with relationship                        
                    result = await StoreRepo.create(db=db, name=item_id)
                    for item in values:
                        added_result = await ItemRepo.create(db=db, item=item, name=item_id)
                    return {'Spreadsheet': "ADDED"}
        except Exception as error:        
            return jsonable_encoder({'ERROR': str(error)})     
    else:
        return jsonable_encoder({'ERROR': "Google item_id empty or malformat"})  
        
# QUERY THE DB BY ID AND SHOW THE RESULTS
@app.get('/query', tags=["Query the DB"],response_model=List[schemas.Store])
def get_items_from_db_by_google_id(item_id: Optional[str] = None,db: Session = Depends(get_db)):    
    # Get all the Items stored in database    
    try:
        if item_id:                    
            db_item = ItemRepo.fetch_all_by_name(db,item_id)               
            return jsonable_encoder(db_item)
        else:
            return jsonable_encoder({'ERROR': "Google item_id empty or malformat"})            
    except Exception as error:        
        return jsonable_encoder({'ERROR': str(error)})    
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True, log_level="info")
    # uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True, ssl_keyfile="./key.pem", ssl_certfile="./cert.pem",log_level="info")
```

### REFERENCES ###

- [FastAPI sql db](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [FastAPI errors message](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Google Quickstart](https://developers.google.com/sheets/api/quickstart/python)
- [Panda Dataframe](https://pandas.pydata.org/)

### TO DO ###

- [ ] Encrypt the Google Credentials file or use a keypass/password manager.
- [ ] Enable the https protocol in uvicorn, generating the key and the pem file.
- [ ] Improve the async and managing timeout session for big file.
