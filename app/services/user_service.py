from datetime import timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId

from fastapi import Depends, HTTPException, status

from app.core.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.base import get_db
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, Token, user_doc_to_response

class IUserService:
    async def register_user(self, user_data: UserCreate, db) -> Dict[str, Any]:
        pass
        
    async def authenticate_user(self, username: str, password: str, db) -> Optional[Dict[str, Any]]:
        pass
        
    async def create_user_token(self, user: Dict[str, Any]) -> Dict[str, str]:
        pass
        
    async def get_current_active_user(self, username: str, db) -> Dict[str, Any]:
        pass
        
    async def get_all_users(self, skip: int, limit: int, db) -> List[Dict[str, Any]]:
        pass
        
    async def update_user(self, user_id, user_data: UserUpdate, db) -> Optional[Dict[str, Any]]:
        pass
        
    async def delete_user(self, user_id, db) -> bool:
        pass

class UserService(IUserService):
    def __init__(self, repository: UserRepository):
        self.repository = repository
        
    async def register_user(self, user_data: UserCreate, db) -> Dict[str, Any]:
        db_user = await self.repository.get_user_by_username(db, user_data.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten kullanımda")
            
        db_user = await self.repository.get_user_by_email(db, user_data.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Bu email zaten kullanımda")
            
        user = await self.repository.create_user(
            db=db,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            role=user_data.role
        )
        return user_doc_to_response(user)
        
    async def authenticate_user(self, username: str, password: str, db) -> Optional[Dict[str, Any]]:
        user = await self.repository.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user["hashed_password"]):
            return None
        return user
        
    async def create_user_token(self, user: Dict[str, Any]) -> Dict[str, str]:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
        
    async def get_current_active_user(self, username: str, db) -> Dict[str, Any]:
        user = await self.repository.get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        if not user["is_active"]:
            raise HTTPException(status_code=400, detail="Deaktif kullanıcı")
        return user_doc_to_response(user)
        
    async def get_user_by_id(self, user_id, db) -> Optional[Dict[str, Any]]:
        user = await self.repository.get_user_by_id(db, user_id)
        return user_doc_to_response(user)
        
    async def get_all_users(self, skip: int = 0, limit: int = 100, db = None) -> List[Dict[str, Any]]:
        users = await self.repository.get_all_users(db, skip=skip, limit=limit)
        return [user_doc_to_response(user) for user in users]
        
    async def update_user(self, user_id, user_data: UserUpdate, db) -> Optional[Dict[str, Any]]:
        user = await self.repository.update_user(db, user_id, user_data.model_dump(exclude_unset=True))
        return user_doc_to_response(user)
        
    async def delete_user(self, user_id, db) -> bool:
        return await self.repository.delete_user(db, user_id)

user_repository = UserRepository()
user_service = UserService(repository=user_repository)

def get_user_service() -> UserService:
    return user_service 