# 🚀 دليل النشر على Render (الأسهل والأفضل!)

## لماذا Render؟
- ✅ **الملفات تُحفظ دائماً** — لا تحتاج Firebase!
- ✅ **مجاني تماماً** — لا يحتاج بطاقة ائتمان
- ✅ **PostgreSQL مجاني** — قاعدة بيانات دائمة
- ✅ **سهل جداً** — نشر بنقرة واحدة

---

## الخطوة 1: رفع الكود إلى GitHub

افتح PowerShell في مجلد المشروع:

```powershell
# 1. دخل مجلد المشروع
cd english-platform

# 2. تهيئة Git
git init
git add .
git commit -m "Initial commit"

# 3. رفع إلى GitHub (استبدل YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/english-platform.git
git branch -M main
git push -u origin main
```

---

## الخطوة 2: إنشاء حساب Render

1. افتح https://render.com
2. سجل دخول بـ **GitHub**

---

## الخطوة 3: إنشاء قاعدة بيانات PostgreSQL

1. في Render dashboard، اضغط **New +**
2. اختر **PostgreSQL**
3. املأ:
   - **Name**: `english-platform-db`
   - **Region**: Frankfurt (EU) — الأقرب
   - **Plan**: Free
4. اضغط **Create Database**
5. انتظر حتى تصبح **Available**
6. اذهب إلى **Connections** وانسخ **Internal Database URL**
   - يبدو بالشكل: `postgresql://user:pass@host:5432/dbname`

---

## الخطوة 4: إنشاء Web Service

1. اضغط **New +** → **Web Service**
2. اربط بـ GitHub repo `english-platform`
3. املأ الإعدادات:

| الحقل | القيمة |
|-------|--------|
| **Name** | english-platform |
| **Region** | Frankfurt (EU) |
| **Branch** | main |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Plan** | Free |

4. في **Advanced** ← **Add Environment Variable**:
   - `SECRET_KEY` = اكتب أي نص عشوائي طويل (30+ حرف)
   - `DATABASE_URL` = Internal Database URL من الخطوة 3

5. في **Disk** (مهم جداً!):
   - **Name**: `uploads`
   - **Mount Path**: `/opt/render/project/src/static/uploads`
   - **Size**: 1 GB
   - **Plan**: Free

6. اضغط **Create Web Service**

---

## الخطوة 5: الانتظار

- Render سيبني المشروع تلقائياً (يستغرق 2-5 دقائق)
- ستظهر رسالة **"Your service is live"**
- اضغط على الرابط (مثلاً: `https://english-platform.onrender.com`)

---

## ✅ التحقق

1. افتح الرابط
2. سجل دخول كمعلم: `teacher@english.com` / `teacher123`
3. ارفع صورة — ستُحفظ دائماً!
4. أعد النشر — الصورة ستبقى!

---

## 🔄 تحديث الكود لاحقاً

```powershell
git add .
git commit -m "Update"
git push
```

Render سيعيد النشر تلقائياً!

---

## 📁 الملفات المعدلة للنشر على Render

| الملف | الوصف |
|-------|-------|
| `app_render.py` | المشروع بدون Firebase (الملفات تُحفظ محلياً) |
| `requirements.txt` | المتطلبات |
| `render.yaml` | إعدادات النشر السريع (Blueprints) |

**ملاحظة**: استخدم `app_render.py` بدلاً من `app.py` — هو نفس الكود بدون Firebase لأن Render يحتفظ بالملفات.

---

## 🆘 استكشاف الأخطاء

### "Build failed"
- تأكد من أن `requirements.txt` يحتوي على جميع المكتبات
- تأكد من أن `app.py` أو `app_render.py` موجود في root

### "Database connection error"
- تأكد من صحة `DATABASE_URL`
- تأكد من أن قاعدة البيانات **Available**

### "Files not persisting"
- تأكد من إضافة **Disk** في الإعدادات
- تأكد من أن **Mount Path** صحيح

---

**جاهز للنشر! 🎉**
