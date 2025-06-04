from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from app.core.security import get_password_hash
from app.db.base import users_collection
from app.models.user import UserRole

class UserRepository:
    async def create_user(self, db, email: str, username: str, password: str, role: UserRole = UserRole.USER):
        hashed_password = get_password_hash(password)
        now = datetime.utcnow()
        
        user_data = {
            "email": email,
            "username": username,
            "hashed_password": hashed_password,
            "is_active": True,
            "role": role,
            "created_at": now,
            "updated_at": now
        }
        
        result: InsertOneResult = await users_collection.insert_one(user_data)
        if result.inserted_id:
            return await self.get_user_by_id(db, result.inserted_id)
        return None
        
    async def get_user_by_username(self, db, username: str):
        user = await users_collection.find_one({"username": username})
        return user
        
    async def get_user_by_email(self, db, email: str):
        user = await users_collection.find_one({"email": email})
        return user
        
    async def get_user_by_id(self, db, user_id):
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except:
                return None
                
        user = await users_collection.find_one({"_id": user_id})
        return user
        
    async def get_all_users(self, db, skip: int = 0, limit: int = 100):
        cursor = users_collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
        
    async def update_user(self, db, user_id, user_data: dict):
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except:
                return None
        
        if "password" in user_data:
            user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
            
        user_data["updated_at"] = datetime.utcnow()
        
        result: UpdateResult = await users_collection.update_one(
            {"_id": user_id}, {"$set": user_data}
        )
        
        if result.modified_count:
            return await self.get_user_by_id(db, user_id)
        return None
        
    async def delete_user(self, db, user_id):
        """Kullanıcıyı sil"""
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except:
                return False
                
        result: DeleteResult = await users_collection.delete_one({"_id": user_id})
        return bool(result.deleted_count) 