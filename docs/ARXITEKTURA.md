# Urdu Education Platform — To'liq Arxitektura

## Loyiha haqida
- **Platforma nomi:** Urdu Education
- **Fan:** Ma'lumotlar tuzilmasi va algoritmlar (MTA)
- **Universitet:** Abu Rayhon Beruniy nomidagi Urganch davlat universiteti
- **O'qituvchi:** Madaminov Uktamjon

---

## Texnologiyalar

| Qatlam     | Texnologiya               |
|------------|---------------------------|
| Frontend   | HTML5, Tailwind CSS, Vanilla JS, Chart.js |
| Backend    | Django 4.2 + Django REST Framework |
| Database   | PostgreSQL (production), SQLite (dev) |
| Auth       | Django sessions + JWT (DRF SimpleJWT) |
| Media      | Django media files → Render persistent disk |
| Deploy     | Frontend → Netlify, Backend → Render, DB → Render PostgreSQL |

---

## Papkalar tuzilmasi

```
urdu-education/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── urdu_platform/          # Asosiy Django config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── users/              # Foydalanuvchilar (Admin, O'qituvchi, Talaba)
│   │   ├── groups/             # Guruhlar va talabalar
│   │   ├── courses/            # Mavzular, darslar, videolar
│   │   └── assessments/        # Topshiriqlar, testlar, baholar
│   ├── static/
│   └── media/
├── frontend/
│   ├── index.html              # Login sahifa
│   ├── pages/
│   │   ├── admin/
│   │   │   ├── dashboard.html
│   │   │   ├── users.html
│   │   │   ├── groups.html
│   │   │   └── stats.html
│   │   ├── teacher/
│   │   │   ├── dashboard.html
│   │   │   ├── topics.html
│   │   │   ├── assignments.html
│   │   │   ├── grading.html
│   │   │   └── statistics.html
│   │   └── student/
│   │       ├── dashboard.html
│   │       ├── lesson.html
│   │       ├── assignment.html
│   │       └── grades.html
│   ├── components/
│   │   ├── navbar.js
│   │   ├── sidebar.js
│   │   └── theme.js
│   └── assets/
│       ├── css/
│       │   └── main.css
│       └── js/
│           ├── api.js          # API so'rovlar uchun
│           ├── auth.js         # Login/logout
│           └── charts.js       # Chart.js wrапper
└── docs/
    ├── ARXITEKTURA.md
    ├── API_DOCS.md
    └── DEPLOY.md
```

---

## Ma'lumotlar bazasi sxemasi

### Users (Foydalanuvchilar)
```
User
├── id (PK)
├── username (unique)
├── password (hashed)
├── role: ENUM(admin, teacher, student)
├── full_name
├── email
├── phone
├── is_active
├── created_at
└── created_by (FK → User)
```

### Groups (Guruhlar)
```
Group
├── id (PK)
├── name (e.g., "22-DI-1")
├── year
├── teacher (FK → User[teacher])
├── created_at
└── is_active

StudentGroup (Many-to-Many)
├── student (FK → User[student])
└── group (FK → Group)
```

### Topics (Mavzular — M1-M12)
```
Topic
├── id (PK)
├── code: ENUM(M1..M12)
├── title
├── description
├── lecture_content (HTML/Markdown)
├── pseudo_code
├── real_code (C/C++/Python)
├── video_url
├── pdf_file
├── order_number
└── is_published

TopicUnlock (Mavzu ochilishi)
├── student (FK → User)
├── topic (FK → Topic)
├── unlocked_at
└── completed_at
```

### Assignments (Topshiriqlar)
```
Assignment
├── id (PK)
├── topic (FK → Topic)
├── group (FK → Group)
├── title
├── description
├── deadline
├── type: ENUM(amaliy, mustaqil)
└── created_by (FK → User[teacher])

Submission (Topshiriq javobi)
├── id (PK)
├── assignment (FK → Assignment)
├── student (FK → User)
├── file (upload)
├── text_answer
├── submitted_at
├── grade: ENUM(2,3,4,5) nullable
├── feedback
└── graded_by (FK → User[teacher])
```

### Tests (Test savollari)
```
Test
├── id (PK)
├── topic (FK → Topic)
├── group (FK → Group)
└── created_by

Question
├── id (PK)
├── test (FK → Test)
├── text
└── order

Choice
├── id (PK)
├── question (FK → Question)
├── text
└── is_correct

TestAttempt (Test urinishi)
├── id (PK)
├── test (FK → Test)
├── student (FK → User)
├── score (0-100)
├── grade: ENUM(2,3,4,5)
└── completed_at

StudentAnswer
├── attempt (FK → TestAttempt)
├── question (FK → Question)
└── chosen (FK → Choice)
```

### Progress (O'zlashtirish)
```
StudentProgress
├── student (FK → User)
├── topic (FK → Topic)
├── lesson_done (bool)
├── assignment_grade
├── test_grade
└── overall_grade: ENUM(2,3,4,5)
```

---

## Rollar va ruxsatlar

| Amal                              | Admin | O'qituvchi | Talaba |
|-----------------------------------|-------|------------|--------|
| Foydalanuvchi yaratish            | ✅    | ❌         | ❌     |
| Guruh yaratish                    | ✅    | ❌         | ❌     |
| Talabani guruhga qo'shish         | ✅    | ❌         | ❌     |
| Mavzu qo'shish/tahrirlash         | ❌    | ✅         | ❌     |
| Guruh uchun topshiriq yaratish    | ❌    | ✅         | ❌     |
| Guruh uchun test yaratish         | ❌    | ✅         | ❌     |
| Topshiriqni baholash              | ❌    | ✅         | ❌     |
| Darsni ko'rish (ketma-ket)        | ❌    | ❌         | ✅     |
| Topshiriq topshirish              | ❌    | ❌         | ✅     |
| Test yechish                      | ❌    | ❌         | ✅     |
| O'z baholarini ko'rish            | ❌    | ❌         | ✅     |
| Guruh statistikasini ko'rish      | ❌    | ✅         | ❌     |
| Umumiy statistika                 | ✅    | ❌         | ❌     |

---

## MTA Kurs tuzilmasi (Sillabus asosida)

| Kod | Mavzu                                                    | Soat |
|-----|----------------------------------------------------------|------|
| M1  | Abstrakt tuzilmalar. Algoritmlar tahlili                | 2    |
| M2  | Rekursiv algoritmlar                                    | 2    |
| M3  | Qidiruv algoritmlari. Xeshlash                          | 4    |
| M4  | Saralash algoritmlari                                   | 4    |
| M5  | Statik/dinamik massivlar. Bog'langan ro'yxatlar         | 2    |
| M6  | Navbat, stek va dek                                     | 4    |
| M7  | Daraxtsimon ma'lumotlar tuzilmalari                     | 2    |
| M8  | Binar qidiruv daraxti. AVL daraxti                      | 2    |
| M9  | Heap tree                                               | 2    |
| M10 | Graflar bilan ishlash algoritmlari                      | 2    |
| M11 | BFS va DFS algoritmlar                                  | 2    |
| M12 | Eng qisqa yo'l: Floyd, Ford-Bellman, Dijkstra           | 2    |

**Ketma-ketlik qoidasi:** Har bir mavzu faqat oldingi mavzu to'liq yakunlangandan keyin ochiladi:
- Dars ko'rilgan ✅
- Topshiriq topshirilgan ✅  
- Test yechilgan ✅
