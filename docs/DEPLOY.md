# Urdu Education — Deploy Yo'riqnomasi

## Umumiy arxitektura
```
Frontend (Netlify) ←→ Backend API (Render) ←→ PostgreSQL (Render)
```

---

## 1. BACKEND — Render.com ga deploy qilish

### 1.1 Tayyorgarlik

```bash
# Loyiha papkasiga o'ting
cd urdu-education/backend

# Virtual muhit yarating
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Kutubxonalarni o'rnating
pip install -r requirements.txt

# .env fayl yarating
cp .env.example .env
# .env faylidagi qiymatlarni to'ldiring
```

### 1.2 Lokal test

```bash
# Migratsiyalar
python manage.py makemigrations
python manage.py migrate

# Superuser (birinchi Admin) yaratish
python manage.py createsuperuser

# Ishga tushirish
python manage.py runserver
```

### 1.3 Render.com da deploy

1. **render.com** ga kiring, yangi **Web Service** yarating
2. GitHub repozitoriyangizni ulang
3. Quyidagi sozlamalarni kiriting:

| Sozlama | Qiymat |
|---------|--------|
| **Name** | urdu-education-api |
| **Region** | Frankfurt (EU) yoki Singapore (Asia) |
| **Branch** | main |
| **Root Directory** | backend |
| **Runtime** | Python 3.11 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn urdu_platform.wsgi:application` |

4. **Environment Variables** bo'limida quyidagilarni qo'shing:

```
SECRET_KEY         = your-super-secret-key-min-50-chars
DEBUG              = False
ALLOWED_HOSTS      = your-service.onrender.com
DATABASE_URL       = (Render PostgreSQL dan avtomatik)
CORS_ALLOWED_ORIGINS = https://your-netlify.netlify.app
```

### 1.4 PostgreSQL yaratish (Render)

1. Render dashboard → **New** → **PostgreSQL**
2. Nom: `urdu-education-db`
3. Free tier tanlang
4. Yaratilgach, **Internal Database URL** ni nusxalang
5. Backend Web Service Environment Variables ga `DATABASE_URL` sifatida joylashtiring

### 1.5 Birinchi migratsiya va Admin yaratish

Render shell orqali:
```bash
python manage.py migrate
python manage.py createsuperuser
# Username, parol kiriting — bu platformaning birinchi Admin bo'ladi
```

### 1.6 Statik fayllar
```bash
python manage.py collectstatic --noinput
```
`whitenoise` orqali avtomatik xizmat ko'rsatiladi.

---

## 2. FRONTEND — Netlify ga deploy qilish

### 2.1 api.js ni yangilash

`frontend/assets/js/api.js` faylidagi API_BASE ni o'zgartiring:

```javascript
const API_BASE = 'https://urdu-education-api.onrender.com/api';
// Render URL ingiz bilan almashtiring
```

### 2.2 Netlify deploy

**Variant A — Drag & Drop (eng oson):**
1. netlify.com ga kiring
2. "Sites" → "Add new site" → "Deploy manually"
3. `frontend` papkasini drag & drop qiling

**Variant B — GitHub orqali:**
1. Netlify → "New site from Git"
2. GitHub repozitoriyangizni tanlang
3. Sozlamalar:
   - **Publish directory:** `frontend`
   - **Build command:** (bo'sh)

### 2.3 _redirects fayli (SPA uchun)

`frontend/_redirects` faylini yarating:
```
/*    /index.html    200
```

---

## 3. CORS SOZLAMALARI

Backend `.env` faylida frontend URL ni qo'shing:

```
CORS_ALLOWED_ORIGINS=https://your-app.netlify.app
```

Backend `settings.py` da allaqachon konfiguratsiya qilingan.

---

## 4. BIRINCHI FOYDALANISH

### 4.1 Admin (Superuser) bilan kirish

Render shell da yaratilgan superuser login/parol bilan:
- URL: `https://your-app.netlify.app`
- Login → Admin panelga yo'naltiriladi

### 4.2 Ketma-ketlik

```
1. Admin → Guruhlar yaratish (masalan: 22-DI-1, 23-KI-2)
2. Admin → O'qituvchi yaratish (login/parol berish)
3. Admin → Talabalar yaratish (login/parol berish)
4. Admin → Guruhga talabalar qo'shish
5. Admin → Guruhga o'qituvchi biriktirish

6. O'qituvchi → Mavzularni to'ldirish (M1-M12)
   - Dars matni
   - Psevdokod va C++/Python kod
   - Video URL (YouTube)
   - PDF/Slayd yuklash
   - Nashr qilish

7. O'qituvchi → Guruh uchun topshiriqlar yaratish
8. O'qituvchi → Guruh uchun testlar yaratish

9. Talaba → Login → Darslarni ko'rish (M1 → M2 → ... ketma-ket)
10. Talaba → Topshiriq topshirish
11. Talaba → Test yechish
```

---

## 5. MUHIM XAVFSIZLIK ESLATMALARI

```python
# Production uchun majburiy:
DEBUG = False
SECRET_KEY = "kamida-50-belgidan-iborat-tasodifiy-kalit"

# Parollar:
# - Talabalar: admin tomonidan berilgan login/parol
# - O'qituvchilar: admin tomonidan berilgan login/parol
# - Admin: manage.py createsuperuser orqali yaratilgan
```

---

## 6. LOKAL DEVELOPMENT

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env da DEBUG=True, DATABASE_URL bo'sh (SQLite ishlatiladi)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver  # http://localhost:8000

# Frontend
# api.js da:
# const API_BASE = 'http://localhost:8000/api';
# VS Code Live Server yoki:
cd frontend
python -m http.server 5500  # http://localhost:5500
```

---

## 7. API ENDPOINTLAR

| Endpoint | Metod | Tavsif |
|----------|-------|--------|
| `/api/auth/login/` | POST | Login (JWT token olish) |
| `/api/auth/refresh/` | POST | Token yangilash |
| `/api/users/me/` | GET | Joriy foydalanuvchi |
| `/api/users/` | GET/POST | Foydalanuvchilar (Admin) |
| `/api/groups/` | GET/POST | Guruhlar |
| `/api/groups/{id}/add_students/` | POST | Guruhga talaba qo'shish |
| `/api/groups/{id}/statistics/` | GET | Guruh statistikasi |
| `/api/courses/` | GET/POST | Mavzular (M1-M12) |
| `/api/courses/my_progress/` | GET | Talaba progressi |
| `/api/courses/{id}/mark_lesson_viewed/` | POST | Darsni ko'rildi belgilash |
| `/api/assessments/assignments/` | GET/POST | Topshiriqlar |
| `/api/assessments/assignments/{id}/submit/` | POST | Javob topshirish |
| `/api/assessments/assignments/grade/{id}/` | POST | Baholash |
| `/api/assessments/tests/` | GET/POST | Testlar |
| `/api/assessments/tests/{id}/start_attempt/` | POST | Test boshlash |
| `/api/assessments/tests/{id}/submit_attempt/` | POST | Test tugatish |
| `/api/assessments/progress/` | GET | O'zlashtirish |
| `/api/assessments/progress/summary/` | GET | Xulosa |

---

## 8. RENDER FREE TIER HAQIDA

⚠️ Render free tier 15 daqiqa faollik bo'lmasa "uyquga" ketadi.
Birinchi so'rov ~30 soniya kutishi mumkin.

Production uchun: Render Starter plan ($7/oy) tavsiya etiladi.
