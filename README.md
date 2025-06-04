# Kullanıcı Yönetim Sistemi API
Bu proje, kullanıcı yönetimi için bir REST API'dir. SOLID prensiplerine uygun olarak geliştirilmiş ve FastAPI framework'ü kullanılmıştır.

## Özellikler
- Kullanıcı kaydı ve girişi
- JWT tabanlı kimlik doğrulaması
- Rol tabanlı yetkilendirme (Admin, User, Guest)
- RESTful API endpointleri
- SOLID prensiplerine uygun mimari
- MongoDB veritabanı

## Teknolojiler
- Python 3.8+
- FastAPI
- MongoDB (Motor ve PyMongo)
- Pydantic
- JWT (Python-jose)
- Passlib ve Bcrypt
- python-dotenv

## Kurulum
1. Sanal ortam oluşturun ve aktifleştirin:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # Linux/Mac için
   # veya
   myenv\Scripts\activate  # Windows için
   ```

2. Gereksinimleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. .env dosyasını oluşturun:
   ```bash
   # .env dosyası örneği
   JWT_SECRET_KEY="güvenli_ve_karmaşık_bir_anahtar"
   JWT_ALGORITHM="HS256"
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   MONGODB_URL="mongodb://localhost:27017"
   DATABASE_NAME="user_management"
   ```

4. MongoDB'yi kurun ve başlatın:
   ```bash
   # macOS için (Homebrew ile):
   brew tap mongodb/brew
   brew install mongodb-community
   brew services start mongodb-community
   
   # Linux için:
   sudo systemctl start mongod
   ```

5. Uygulamayı çalıştırın:
   ```bash
   uvicorn app.main:app --reload
   ```

6. API dökümanına erişin:
   ```
   http://localhost:8000/docs
   ```

## API Endpoints
### Kullanıcı İşlemleri
- `POST /api/register`: Yeni kullanıcı kaydı
- `POST /api/login`: Kullanıcı girişi
- `POST /api/token`: Token alma (OAuth2 uyumlu)
- `GET /api/me`: Mevcut kullanıcı bilgilerini getirme
- `GET /api/users`: Tüm kullanıcıları listeleme (sadece admin)
- `PUT /api/users/{user_id}`: Kullanıcı bilgilerini güncelleme
- `DELETE /api/users/{user_id}`: Kullanıcı silme (sadece admin)

## Çevre Değişkenleri
Proje, `.env` dosyasından yapılandırma ayarlarını okur. Aşağıdaki değişkenlerin tanımlanması gerekir:

| Değişken | Açıklama | Örnek Değer |
| --- | --- | --- |
| JWT_SECRET_KEY | JWT imzalama anahtarı | "güvenli_ve_karmaşık_bir_anahtar" |
| JWT_ALGORITHM | JWT algoritması | "HS256" |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Token geçerlilik süresi (dakika) | 30 |
| MONGODB_URL | MongoDB bağlantı URL'si | "mongodb://localhost:27017" |
| DATABASE_NAME | MongoDB veritabanı adı | "user_management" |

> **Not**: `.env` dosyası Git'e dahil edilmez. Güvenlik için her ortamda kendi `.env` dosyanızı oluşturmanız gerekir.

## Proje Yapısı
```
/app
  /api
    /endpoints
      user.py            # API rotaları
  /core
    security.py          # Güvenlik işlemleri (JWT, şifre hash'leme)
  /db
    base.py              # Veritabanı bağlantısı ve yönetimi
  /models
    user.py              # Veri modelleri ve enum'lar
  /schemas
    user.py              # Pydantic şemaları
  /services
    user_service.py      # İş mantığı servisleri
  /repositories
    user_repository.py   # Veritabanı işlemleri
  main.py                # Ana uygulama
requirements.txt
.env                     # Çevre değişkenleri 
.gitignore              
```

## SOLID Prensipleri
Bu projede uygulanan SOLID prensipleri:
1. **S**ingle Responsibility: Her sınıf tek bir sorumluluğa sahip
2. **O**pen/Closed: Sınıflar genişlemeye açık, değişime kapalı
3. **L**iskov Substitution: Alt sınıflar üst sınıfların yerine geçebilir
4. **I**nterface Segregation: Özel arayüzler genel arayüzlerden daha iyidir
5. **D**ependency Inversion: Soyutlamalara bağımlılık, somut implementasyonlara değil
