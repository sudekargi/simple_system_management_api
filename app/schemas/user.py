from typing import Optional, Dict, Any, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, field_serializer, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from app.models.user import UserRole

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(lambda x: ObjectId(x))
            ])
        ])
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_type, _handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"type": "string"}

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    is_active: bool = True
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_serializer('id')
    def serialize_id(self, id: ObjectId) -> str:
        return str(id)
    
    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True
    }

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

def user_doc_to_response(user_doc: Dict[str, Any]) -> Dict[str, Any]:
    if not user_doc:
        return None
    
    if "_id" in user_doc:
        user_doc["id"] = str(user_doc["_id"])
        
    return user_doc 