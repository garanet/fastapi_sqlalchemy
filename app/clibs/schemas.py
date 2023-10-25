from typing import Optional
from pydantic import BaseModel

class StoreBase(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None    
    image: Optional[str] = None
    name: int
    
class StoreCreate(StoreBase):
    pass

class Store(StoreBase):
    id: int    
    name: int
    
    class Config:
        orm_mode = True