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
    