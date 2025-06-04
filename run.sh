#!/bin/bash

# Gerekli paketleri yükle
pip install -r requirements.txt

# Uygulamayı başlat
uvicorn app.main:app --reload 