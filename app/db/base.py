import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from fastapi import Depends
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGODB_URL or not DATABASE_NAME:
    raise ValueError("MONGODB_URL ve DATABASE_NAME .env dosyasında tanımlanmalıdır!")

try:
    client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))
    db = client[DATABASE_NAME]
    print("MongoDB bağlantısı başarılı!")
except Exception as e:
    print(f"MongoDB bağlantı hatası: {e}")
    client = None
    db = None

users_collection = None if db is None else db.users

async def get_db():
    if db is None:
        raise Exception("MongoDB bağlantısı yok!")
    try:
        yield db
    finally:
        pass

async def init_db():
    if db is None:
        print("MongoDB bağlantısı yok, indeksler oluşturulamadı.")
        return
    
    try:
        await client.admin.command('ping')
        print("MongoDB bağlantısı başarılı!")
        
        await db.users.create_index("username", unique=True)
        await db.users.create_index("email", unique=True)
        print("MongoDB indeksleri oluşturuldu.")
    except Exception as e:
        print(f"MongoDB bağlantı veya indeks hatası: {e}")
        raise 