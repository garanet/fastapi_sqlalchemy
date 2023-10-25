import uvicorn, json
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List,Optional
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
        except:                
            raise HTTPException(status_code=404, detail=str("Error from the global function"))              
    else:
        raise HTTPException(status_code=404, detail=str("Google item_id empty or malformat"))  
    
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
                        added_result = await ItemRepo.create(db=db, item=item, name=result.id)
                    return {'Spreadsheet': "ADDED"}
        except:
            raise HTTPException(status_code=404, detail=str("Error from the global function"))             
    else:
       raise HTTPException(status_code=404, detail=str("Google item_id empty or malformat"))  
        
# QUERY THE DB BY ID AND SHOW THE RESULTS
@app.get('/query', tags=["Query the DB"],response_model=List[schemas.StoreBase])
def get_items_from_db_by_google_id(item_id: Optional[str] = None,db: Session = Depends(get_db)):    
    # Get all the Items stored in database    
    try:
        if item_id:       
        # Get the item_id from the TABLE data
            store_id = StoreRepo.fetch_by_name(db, name=item_id)                           
        # Get the items from the TABLE item related to the above store_id
            db_item = ItemRepo.fetch_all_by_name(db, name=store_id.id)            
            if db_item:                
                return jsonable_encoder(db_item)
            else:
                raise HTTPException(status_code=404, detail=str("Google item_id not found in the DB"))
        else:
            raise HTTPException(status_code=404, detail=str("Google item_id empty or malformat"))
    except:
        raise HTTPException(status_code=404, detail=str("Google item_id empty or not found in the DB"))
        
# Main Function, with or without SSL    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True, log_level="info")    
    # uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True, ssl_keyfile="./key.pem", ssl_certfile="./cert.pem",log_level="info")