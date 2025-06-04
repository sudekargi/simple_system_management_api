from typing import List, Dict, Any
from bson import ObjectId

from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import get_current_user
from app.db.base import get_db
from app.models.user import UserRole
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin, UserUpdate
from app.services.user_service import UserService, get_user_service

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate, 
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    #Yeni kullanıcı kaydı ekliyoruz.
    db_user = await user_service.register_user(user, db)
    return db_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    #JWT token almak için
    user = await user_service.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz kullanıcı adı veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await user_service.create_user_token(user)

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    #Kullanıcı girişi içib
    user = await user_service.authenticate_user(user_data.username, user_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz kullanıcı adı veya şifre",
        )
    return await user_service.create_user_token(user)

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_username: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    #Kullanıcı bilgilerini görüntüleme
    user = await user_service.get_current_active_user(current_username, db)
    return user

@router.get("/users", response_model=List[UserResponse])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    current_username: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    #Tüm kullanıcıları listeleme (sadece admin)
    current_user = await user_service.get_current_active_user(current_username, db)
    
    # Yetki kontrolü
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Bu işlem için admin yetkisi gerekiyor"
        )
        
    users = await user_service.get_all_users(skip=skip, limit=limit, db=db)
    return users

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str = Path(..., title="Güncellenecek kullanıcı ID'si"),
    user_data: UserUpdate = None,
    current_username: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    #KULLANICI BİLGİLERİNİ GÜNCELLEME
    current_user = await user_service.get_current_active_user(current_username, db)
    
    target_user = await user_service.get_user_by_id(user_id, db)
    if not target_user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
    if str(current_user["_id"]) != user_id and current_user["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için yetkiniz yok"
        )
        
    updated_user = await user_service.update_user(user_id, user_data, db)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Kullanıcı güncellenemedi")
    return updated_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str = Path(..., title="Silinecek kullanıcı ID'si"),
    current_username: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    #BUNU SADECE ADMİN YAPABİLİYOR.
    current_user = await user_service.get_current_active_user(current_username, db)
    
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için admin yetkisi gerekiyor"
        )
        
    success = await user_service.delete_user(user_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı") 