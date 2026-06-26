# 🎓 English Academy — Platform Guide

## Platform Overview
A complete platform for teaching English including:
- **Home Page**: Professional marketing interface
- **Teacher Dashboard**: Upload lectures, manage courses, live sessions, announcements, track students
- **Student Dashboard**: Track courses, watch videos, track progress
- **Database**: Built-in SQLite, no setup needed

---

## 🚀 Run Locally (On Your Machine)

### Requirements
- Python 3.10 or newer
- pip

### Steps
```bash
# 1. Extract folder and enter it
cd english-platform

# 2. Install libraries
pip install -r requirements.txt

# 3. Run the project
python app.py
```

### Open browser at:
```
http://localhost:5000
```

### Demo Login Credentials
| Role   | Email            | Password |
|---------|-------------------|-------------|
| Teacher | teacher@english.com | teacher123 |
| Student | Create new account | — |

---

## 🌐 Deploy Online

### Option 1: Railway (Easiest — Free)

1. Sign up at [railway.app](https://railway.app)
2. Click **New Project → Deploy from GitHub**
3. Upload project to GitHub first:
   ```bash
   git init
   git add .
   git commit -m "initial commit"
   git remote add origin https://github.com/USERNAME/english-platform.git
   git push -u origin main
   ```
4. In Railway: select the repo → Python will be detected automatically
5. Add environment variable:
   - `SECRET_KEY` = any long random text
6. Click **Deploy** — you'll get a URL like: `https://english-platform.up.railway.app`

---

### Option 2: Render (Free)

1. Sign up at [render.com](https://render.com)
2. **New → Web Service → Connect GitHub**
3. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Add environment variable `SECRET_KEY`
5. Click **Create Web Service**

---

### Option 3: VPS (Hostinger / DigitalOcean)

```bash
# On server
git clone https://github.com/USERNAME/english-platform.git
cd english-platform
pip install -r requirements.txt

# Run with gunicorn
gunicorn app:app --bind 0.0.0.0:8000 --workers 2 --daemon

# Nginx setup (optional for domain)
# /etc/nginx/sites-available/english
server {
    listen 80;
    server_name yourdomain.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    client_max_body_size 500M;  # Allow large video uploads
}
```

---

## 📁 Project Structure

```
english-platform/
├── app.py                    ← Main server and database
├── requirements.txt          ← Required libraries
├── railway.json              ← Railway deployment config
├── templates/
│   ├── base.html             ← Base shared template
│   ├── auth/
│   │   ├── login.html        ← Login page
│   │   └── register.html     ← Sign up page
│   ├── public/
│   │   ├── index.html        ← Home page
│   │   ├── courses.html      ← Course list
│   │   ├── course_detail.html← Course details
│   │   └── contact.html      ← Contact page
│   ├── teacher/
│   │   ├── dashboard.html    ← Teacher dashboard
│   │   ├── courses.html      ← Course management
│   │   ├── course_form.html  ← Create course
│   │   ├── course_edit.html  ← Edit course + upload lessons
│   │   ├── live.html         ← Live sessions
│   │   ├── announcements.html← Announcements
│   │   ├── students.html     ← Student management
│   │   └── profile.html      ← Profile
│   ├── student/
│   │   ├── dashboard.html    ← Student dashboard
│   │   ├── learn.html        ← Watch lessons
│   │   └── profile.html      ← Profile
│   ├── add_assistant.html    ← Add assistant
│   └── assistants.html       ← Assistants list
└── static/
    └── uploads/
        ├── videos/           ← Uploaded videos
        ├── thumbnails/       ← Course images
        ├── materials/        ← PDF and attachments
        ├── avatars/          ← User photos
        └── announcements/    ← Announcement images
```

---

## ⚙️ Important Environment Variables

```env
SECRET_KEY=your-very-secret-key-here-change-this
DATABASE_URL=sqlite:///english_platform.db   # Can be changed to PostgreSQL
```

---

## 🔧 Add New Teacher

To convert a student to teacher, run this in Python:

```python
from app import app, db, User
with app.app_context():
    user = User.query.filter_by(email='example@email.com').first()
    user.role = 'teacher'
    db.session.commit()
    print("Conversion successful")
```

---

## 🎯 Ready Features

✅ Login and registration
✅ Video uploads (local)
✅ YouTube/external link support
✅ PDF attachments upload
✅ Progress and completion system
✅ Approve/reject student enrollment
✅ Schedule live sessions
✅ Publish announcements
✅ Statistics dashboard
✅ Course filtering
✅ Blue & Gold theme design

---

**Development: English Academy © 2026**