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