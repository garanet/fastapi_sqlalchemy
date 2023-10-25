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
    # title: Optional[str] = None
    # description: Optional[str] = None    
    # image: Optional[str] = None
    name: Optional[str] = None
    
    class Config:
        orm_mode = True