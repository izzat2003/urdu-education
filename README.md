# Urdu Education Platform

**Fan:** Ma'lumotlar tuzilmasi va algoritmlar (MTA1204)  
**Universitet:** Abu Rayhon Beruniy nomidagi Urganch davlat universiteti  
**O'qituvchi:** Madaminov Uktamjon | uktam9527@gmail.com  

---

## Platforma haqida

**Urdu Education** — real akademik foydalanish uchun mo'ljallangan to'liq veb ta'lim platformasi.

| Xususiyat | Ma'lumot |
|-----------|----------|
| Kurs | MTA — 12 ta mavzu (Sillabus asosida) |
| Foydalanuvchi rollari | Admin, O'qituvchi, Talaba |
| Frontend | HTML5, Tailwind CSS, Chart.js |
| Backend | Django 4.2 + DRF |
| Database | PostgreSQL |
| Deploy | Netlify + Render |

---

## Tez boshlash

```bash
# 1. Repozitoriyani klonlash
git clone https://github.com/yourname/urdu-education.git
cd urdu-education/backend

# 2. Muhit sozlash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env faylini tahrirlang

# 3. Bazani tayyorlash
python manage.py migrate
python manage.py createsuperuser

# 4. 12 ta MTA mavzusini seed qilish
python manage.py seed_topics

# 5. Ishga tushirish
python manage.py runserver
```

---

## Loyiha tuzilmasi

```
urdu-education/
├── backend/                  # Django backend
│   ├── apps/
│   │   ├── users/            # Foydalanuvchilar (RBAC)
│   │   ├── groups/           # Guruhlar
│   │   ├── courses/          # MTA mavzular (M1-M12)
│   │   └── assessments/      # Topshiriq, Test, Baho
│   └── urdu_platform/        # Django config
├── frontend/                 # Vanilla HTML/JS/CSS
│   ├── index.html            # Login
│   ├── pages/
│   │   ├── admin/            # Admin panel (3 sahifa)
│   │   ├── teacher/          # O'qituvchi (5 sahifa)
│   │   └── student/          # Talaba (4 sahifa)
│   ├── components/
│   │   └── layout.js         # Sidebar, toast, modal
│   └── assets/js/
│       └── api.js            # Barcha API so'rovlar
├── docs/
│   ├── ARXITEKTURA.md
│   └── DEPLOY.md
└── render.yaml
```

---

## Asosiy imkoniyatlar

### Admin
- Foydalanuvchi yaratish (login/parol berish)
- Guruh yaratish va talabalarni joylash
- O'qituvchi biriktirish
- Umumiy statistika

### O'qituvchi
- M1–M12 mavzularni to'ldirish:
  - 80 daqiqalik dars matni
  - Psevdokod + C++/Python kod (VSCode uchun)
  - YouTube video
  - PDF/Slayd yuklash
  - Vizualizatsiya (BST, BFS, DFS, Saralash)
- **Guruh uchun** topshiriqlar yaratish
- **Guruh uchun** testlar yaratish (to'g'ri/noto'g'ri javoblar)
- Amaliy ishlarni baholash (2, 3, 4, 5)
- Guruh va talaba statistikasi

### Talaba
- Ketma-ket darslar (M1→M2→...M12, oldingi yakunlanmasa keyingisi ochilmaydi)
- Dars matni, kod, video ko'rish
- Algoritm vizualizatsiyalari (BST, BFS, DFS, Sort)
- Topshiriq topshirish (fayl + matn)
- Test yechish (avtomatik baholash)
- Baholar va progress dashboard

---

## Baholash tizimi (Sillabus asosida)

| Baho | Daraja | Shart |
|------|--------|-------|
| 5 | A'lo | Fan to'liq o'zlashtirilgan |
| 4 | Yaxshi | Asosiy material o'zlashtirilgan |
| 3 | Qoniqarli | Umumiy tushuncha mavjud |
| 2 | Qoniqarsiz | Tayyorgarlik yo'q |

**Mavzu yakunlash shartlari:** Dars ko'rildi ✅ + Topshiriq baholangan ✅ + Test yechilgan ✅

---

## Deploy

`docs/DEPLOY.md` fayliga qarang.

**Qisqacha:**
- Backend → [Render.com](https://render.com) (Django + PostgreSQL)
- Frontend → [Netlify.com](https://netlify.com) (Static)
