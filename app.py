from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os, uuid

app = Flask(__name__)

# ─── Secret Key ───────────────────────────────────────────
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'english-platform-secret-key-2024')

# ─── Database ─────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///english_platform.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# ─── Uploads ──────────────────────────────────────────────
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

ALLOWED_VIDEO = {'mp4', 'webm', 'mkv', 'avi', 'mov'}
ALLOWED_IMG = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
ALLOWED_FILE = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'zip'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ─── Models ───────────────────────────────────────────────
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')  # 'teacher' or 'student'
    avatar = db.Column(db.String(200), default='')
    bio = db.Column(db.Text, default='')
    phone = db.Column(db.String(30), default='')
    whatsapp = db.Column(db.String(50), default='')
    telegram = db.Column(db.String(100), default='')
    hero_photo = db.Column(db.String(200), default='')
    country = db.Column(db.String(60), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active_account = db.Column(db.Boolean, default=True)
    # Payment fields for teacher
    bank_account = db.Column(db.String(200), default='')
    bank_name = db.Column(db.String(100), default='')
    wallet_vodafone = db.Column(db.String(50), default='')
    wallet_instapay = db.Column(db.String(100), default='')
    wallet_stcpay = db.Column(db.String(50), default='')
    wallet_other = db.Column(db.String(200), default='')
    payment_notes = db.Column(db.Text, default='')
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    progress = db.relationship('Progress', backref='student', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    thumbnail = db.Column(db.String(200), default='')
    level = db.Column(db.String(30), default='Beginner')
    category = db.Column(db.String(60), default='Grammar')
    price = db.Column(db.Float, default=0.0)
    is_free = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher = db.relationship('User', backref='courses')
    lessons = db.relationship('Lesson', backref='course', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')

class Assistant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    specialty = db.Column(db.String(120), default='')
    bio = db.Column(db.Text, default='')
    image = db.Column(db.String(300), default='')
    phone = db.Column(db.String(50), default='')
    email = db.Column(db.String(120), default='')
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    can_upload_lessons = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    video_path = db.Column(db.String(300), default='')
    video_url = db.Column(db.String(500), default='')
    thumbnail = db.Column(db.String(200), default='')
    duration = db.Column(db.String(20), default='')
    order_num = db.Column(db.Integer, default=0)
    is_free_preview = db.Column(db.Boolean, default=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    materials = db.relationship('Material', backref='lesson', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('Progress', backref='lesson', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_live = db.Column(db.Boolean, default=False)
    live_link = db.Column(db.String(500), default='')

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    file_type = db.Column(db.String(20), default='pdf')
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    watched_at = db.Column(db.DateTime, default=datetime.utcnow)

class LiveSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    meeting_link = db.Column(db.String(500), default='')
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    is_active = db.Column(db.Boolean, default=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher = db.relationship('User', backref='live_sessions')
    max_students = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), default='')
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher = db.relationship('User', backref='announcements')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SiteContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, default='')
    value_ar = db.Column(db.Text, default='')  # Arabic value
    content_type = db.Column(db.String(20), default='text')  # text, html, markdown
    section = db.Column(db.String(50), default='general')  # hero, features, quote, footer
    description = db.Column(db.String(200), default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher = db.relationship('User', backref='site_contents')

# ─── Helpers ──────────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename, allowed):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def save_file(file, subfolder):
    ext = file.filename.rsplit('.', 1)[1].lower()
    fname = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder, fname)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file.save(path)
    return f"uploads/{subfolder}/{fname}"

def get_enrollment(course_id):
    if not current_user.is_authenticated:
        return None
    return Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()

def get_progress_pct(course_id, student_id):
    lessons = Lesson.query.filter_by(course_id=course_id).all()
    if not lessons:
        return 0
    done = Progress.query.filter(
        Progress.student_id == student_id,
        Progress.lesson_id.in_([l.id for l in lessons]),
        Progress.completed == True
    ).count()
    return round((done / len(lessons)) * 100)

app.jinja_env.globals['get_enrollment'] = get_enrollment
app.jinja_env.globals['get_progress_pct'] = get_progress_pct

CURRENCY_MAP = {
    'Egypt': ('Egyptian Pound', 'EGP', 'ج.م'),
    'Saudi Arabia': ('Saudi Riyal', 'SAR', 'SAR'),
    'UAE': ('Dirham', 'AED', 'AED'),
    'Kuwait': ('Kuwaiti Dinar', 'KWD', 'KWD'),
    'Bahrain': ('Bahraini Dinar', 'BHD', 'BHD'),
    'Qatar': ('Qatari Riyal', 'QAR', 'QAR'),
    'Oman': ('Omani Riyal', 'OMR', 'OMR'),
    'Jordan': ('Jordanian Dinar', 'JOD', 'JOD'),
    'Iraq': ('Iraqi Dinar', 'IQD', 'IQD'),
    'Syria': ('Syrian Pound', 'SYP', 'SYP'),
    'Lebanon': ('Lebanese Pound', 'LBP', 'LBP'),
    'Libya': ('Libyan Dinar', 'LYD', 'LYD'),
    'Tunisia': ('Tunisian Dinar', 'TND', 'TND'),
    'Algeria': ('Algerian Dinar', 'DZD', 'DZD'),
    'Morocco': ('Moroccan Dirham', 'MAD', 'MAD'),
    'Sudan': ('Sudanese Pound', 'SDG', 'SDG'),
    'Yemen': ('Yemeni Riyal', 'YER', 'YER'),
    'Palestine': ('Shekel', 'ILS', '₪'),
    'Mauritania': ('Ouguiya', 'MRU', 'MRU'),
    'Somalia': ('Somali Shilling', 'SOS', 'SOS'),
    'Djibouti': ('Djibouti Franc', 'DJF', 'DJF'),
    'Turkey': ('Turkish Lira', 'TRY', '₺'),
    'Pakistan': ('Pakistani Rupee', 'PKR', 'PKR'),
    'Malaysia': ('Ringgit', 'MYR', 'RM'),
    'Indonesia': ('Rupiah', 'IDR', 'Rp'),
    'Nigeria': ('Naira', 'NGN', '₦'),
    'United States': ('US Dollar', 'USD', '$'),
    'United Kingdom': ('British Pound', 'GBP', '£'),
    'Canada': ('Canadian Dollar', 'CAD', 'C$'),
    'Australia': ('Australian Dollar', 'AUD', 'A$'),
    'India': ('Indian Rupee', 'INR', '₹'),
    'Bangladesh': ('Taka', 'BDT', '৳'),
}

def get_currency(country):
    if country and country in CURRENCY_MAP:
        return CURRENCY_MAP[country][2]
    return 'ج.م'

app.jinja_env.globals['get_currency'] = get_currency
app.jinja_env.globals['CURRENCY_MAP'] = CURRENCY_MAP

def get_site_content(key, default='', lang='ar'):
    """Get site content by key, with fallback to default value"""
    content = SiteContent.query.filter_by(key=key).first()
    if content:
        if lang == 'ar' and content.value_ar:
            return content.value_ar
        return content.value or default
    return default

def get_all_site_content():
    """Get all site content as a dictionary"""
    contents = {}
    for item in SiteContent.query.all():
        contents[item.key] = {
            'value': item.value,
            'value_ar': item.value_ar,
            'section': item.section
        }
    return contents

app.jinja_env.globals['get_site_content'] = get_site_content
app.jinja_env.globals['get_all_site_content'] = get_all_site_content



# ─── Auth Routes ──────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        country = request.form.get('country', '')
        if User.query.filter_by(email=email).first():
            flash('This email is already registered', 'error')
            return render_template('auth/register.html')
        user = User(name=name, email=email,
                    password=generate_password_hash(password),
                    country=country, role='student')
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Welcome! Your account has been created successfully', 'success')
        return redirect(url_for('dashboard'))
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ─── Public Routes ────────────────────────────────────────
@app.route('/')
def index():
    courses = Course.query.filter_by(
        is_published=True
    ).order_by(
        Course.created_at.desc()
    ).limit(6).all()

    live_sessions = LiveSession.query.filter_by(
        is_active=True
    ).order_by(
        LiveSession.scheduled_at
    ).limit(3).all()

    announcements = Announcement.query.order_by(
        Announcement.created_at.desc()
    ).limit(3).all()

    teacher = User.query.filter_by(role='teacher').first()

    assistants = Assistant.query.all()

    stats = {
        'students': User.query.filter_by(role='student').count(),
        'courses': Course.query.filter_by(is_published=True).count(),
        'lessons': Lesson.query.count()
    }

    # Get site content
    site_contents = get_all_site_content()

    return render_template(
        'public/index.html',
        courses=courses,
        live_sessions=live_sessions,
        announcements=announcements,
        stats=stats,
        teacher=teacher,
        assistants=assistants,
        hero_photo=teacher.hero_photo if teacher else '',
        site_contents=site_contents
    )

@app.route('/courses')
def courses_list():
    category = request.args.get('category', '')
    level = request.args.get('level', '')
    q = Course.query.filter_by(is_published=True)
    if category:
        q = q.filter_by(category=category)
    if level:
        q = q.filter_by(level=level)
    courses = q.order_by(Course.created_at.desc()).all()
    return render_template('public/courses.html', courses=courses, category=category, level=level)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    if not course.is_published and (not current_user.is_authenticated or current_user.role != 'teacher'):
        return redirect(url_for('courses_list'))
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order_num).all()
    enrollment = get_enrollment(course_id)
    return render_template('public/course_detail.html', course=course, lessons=lessons, enrollment=enrollment)

@app.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    existing = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if existing:
        flash('You are already enrolled in this course', 'info')
        return redirect(url_for('course_detail', course_id=course_id))
    enrollment = Enrollment(student_id=current_user.id, course_id=course_id,
                            is_approved=course.is_free or course.price == 0)
    db.session.add(enrollment)
    db.session.commit()
    if course.is_free or course.price == 0:
        flash('Enrollment successful!', 'success')
        return redirect(url_for('learn', course_id=course_id))
    else:
        flash('Enrollment request sent, will be reviewed soon', 'info')
        return redirect(url_for('course_detail', course_id=course_id))

@app.route('/learn/<int:course_id>')
@app.route('/learn/<int:course_id>/lesson/<int:lesson_id>')
@login_required
def learn(course_id, lesson_id=None):
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if current_user.id != course.teacher_id:
        if not enrollment or not enrollment.is_approved:
            flash('Please enroll in the course first', 'error')
            return redirect(url_for('course_detail', course_id=course.id))
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order_num).all()
    if not lessons:
        flash('No lessons yet', 'info')
        return redirect(url_for('course_detail', course_id=course_id))
    current_lesson = Lesson.query.get(lesson_id) if lesson_id else lessons[0]
    progress_ids = [p.lesson_id for p in Progress.query.filter_by(
        student_id=current_user.id, completed=True).all()]
    return render_template('student/learn.html', course=course, lessons=lessons,
                           current_lesson=current_lesson, progress_ids=progress_ids)

@app.route('/mark_complete/<int:lesson_id>', methods=['POST'])
@login_required
def mark_complete(lesson_id):
    existing = Progress.query.filter_by(student_id=current_user.id, lesson_id=lesson_id).first()
    if not existing:
        p = Progress(student_id=current_user.id, lesson_id=lesson_id, completed=True)
        db.session.add(p)
        db.session.commit()
    return jsonify({'success': True})

# ─── Dashboard ────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    return redirect(url_for('student_dashboard'))

# ─── Student Routes ───────────────────────────────────────
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id, is_approved=True).all()
    live_sessions = LiveSession.query.filter_by(is_active=True).order_by(LiveSession.scheduled_at).all()
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()
    my_courses = []
    for e in enrollments:
        pct = get_progress_pct(e.course_id, current_user.id)
        my_courses.append({'course': e.course, 'progress': pct})
    return render_template('student/dashboard.html', my_courses=my_courses,
                           live_sessions=live_sessions, announcements=announcements)

@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
def student_profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.country = request.form.get('country', current_user.country)
        current_user.bio = request.form.get('bio', current_user.bio)
        if 'avatar' in request.files and request.files['avatar'].filename:
            f = request.files['avatar']
            if allowed_file(f.filename, ALLOWED_IMG):
                current_user.avatar = save_file(f, 'avatars')
        new_pw = request.form.get('new_password', '')
        if new_pw:
            current_user.password = generate_password_hash(new_pw)
        db.session.commit()
        flash('Changes saved', 'success')
    return render_template('student/profile.html')

# ─── Teacher Routes ────────────────────────────────────────
@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return redirect(url_for('student_dashboard'))
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    total_students = db.session.query(Enrollment).join(Course).filter(
        Course.teacher_id == current_user.id).count()
    total_lessons = db.session.query(Lesson).join(Course).filter(
        Course.teacher_id == current_user.id).count()
    live_sessions = LiveSession.query.filter_by(teacher_id=current_user.id).order_by(
        LiveSession.scheduled_at.desc()).limit(5).all()
    announcements = Announcement.query.filter_by(teacher_id=current_user.id).order_by(
        Announcement.created_at.desc()).limit(5).all()
    pending = Enrollment.query.join(Course).filter(
        Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
    pending = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
    return render_template('teacher/dashboard.html', courses=courses,
                           total_students=total_students, total_lessons=total_lessons,
                           live_sessions=live_sessions, announcements=announcements, pending=pending)

@app.route('/teacher/courses')
@login_required
def teacher_courses():
    if current_user.role != 'teacher':
        return redirect(url_for('dashboard'))
    courses = Course.query.filter_by(teacher_id=current_user.id).order_by(Course.created_at.desc()).all()
    pending = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
    return render_template('teacher/courses.html', courses=courses, pending=pending)

@app.route('/teacher/course/new', methods=['GET', 'POST'])
@login_required
def new_course():
    if current_user.role != 'teacher':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        thumb_path = ''
        if 'thumbnail' in request.files and request.files['thumbnail'].filename:
            f = request.files['thumbnail']
            if allowed_file(f.filename, ALLOWED_IMG):
                thumb_path = save_file(f, 'thumbnails')
        course = Course(
            title=request.form.get('title'),
            description=request.form.get('description', ''),
            level=request.form.get('level', 'Beginner'),
            category=request.form.get('category', 'Grammar'),
            price=float(request.form.get('price', 0)),
            is_free=request.form.get('is_free') == 'on',
            is_published=request.form.get('is_published') == 'on',
            thumbnail=thumb_path,
            teacher_id=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully', 'success')
        return redirect(url_for('teacher_course_edit', course_id=course.id))
    pending = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
    return render_template('teacher/course_form.html', course=None, pending=pending)

@app.route('/teacher/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def teacher_course_edit(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        return redirect(url_for('teacher_dashboard'))
    if request.method == 'POST':
        course.title = request.form.get('title', course.title)
        course.description = request.form.get('description', course.description)
        course.level = request.form.get('level', course.level)
        course.category = request.form.get('category', course.category)
        course.price = float(request.form.get('price', course.price))
        course.is_free = request.form.get('is_free') == 'on'
        course.is_published = request.form.get('is_published') == 'on'
        if 'thumbnail' in request.files and request.files['thumbnail'].filename:
            f = request.files['thumbnail']
            if allowed_file(f.filename, ALLOWED_IMG):
                course.thumbnail = save_file(f, 'thumbnails')
        db.session.commit()
        flash('Changes saved', 'success')
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order_num).all()
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    pending = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
    return render_template('teacher/course_edit.html', course=course, lessons=lessons, enrollments=enrollments, pending=pending)

@app.route('/teacher/course/<int:course_id>/lesson/new', methods=['POST'])
@login_required
def new_lesson(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        return redirect(url_for('teacher_dashboard'))
    video_path = ''
    if 'video' in request.files and request.files['video'].filename:
        f = request.files['video']
        if allowed_file(f.filename, ALLOWED_VIDEO):
            video_path = save_file(f, 'videos')
    lesson_thumb = ''
    if 'lesson_thumbnail' in request.files and request.files['lesson_thumbnail'].filename:
        f = request.files['lesson_thumbnail']
        if allowed_file(f.filename, ALLOWED_IMG):
            lesson_thumb = save_file(f, 'thumbnails')
    count = Lesson.query.filter_by(course_id=course_id).count()
    lesson_type = request.form.get('lesson_type')
    lesson = Lesson(
        title=request.form.get('title'),
        description=request.form.get('description', ''),
        video_path=video_path,
        video_url=request.form.get('video_url', ''),
        thumbnail=lesson_thumb,
        duration=request.form.get('duration', ''),
        order_num=count + 1,
        is_free_preview=request.form.get('is_free_preview') == 'on',
        course_id=course_id,
        is_live=(lesson_type == 'live'),
        live_link=request.form.get('video_url', '')
    )
    db.session.add(lesson)
    db.session.flush()
    if 'material' in request.files:
        for f in request.files.getlist('material'):
            if f.filename and allowed_file(f.filename, ALLOWED_FILE):
                mat_path = save_file(f, 'materials')
                mat = Material(title=f.filename, file_path=mat_path,
                               file_type=f.filename.rsplit('.', 1)[1].lower(),
                               lesson_id=lesson.id)
                db.session.add(mat)
    db.session.commit()
    flash('Lesson added successfully', 'success')
    return redirect(url_for('teacher_course_edit', course_id=course_id))

@app.route('/teacher/lesson/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course_id = lesson.course_id
    db.session.delete(lesson)
    db.session.commit()
    flash('Lesson deleted', 'success')
    return redirect(url_for('teacher_course_edit', course_id=course_id))

@app.route('/teacher/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        return redirect(url_for('teacher_dashboard'))
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted', 'success')
    return redirect(url_for('teacher_courses'))

@app.route('/teacher/live', methods=['GET', 'POST'])
@login_required
def teacher_live():
    if current_user.role != 'teacher':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            dt_str = request.form.get('scheduled_at')
            dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M')
            ls = LiveSession(
                title=request.form.get('title'),
                description=request.form.get('description', ''),
                meeting_link=request.form.get('meeting_link', ''),
                scheduled_at=dt,
                duration_minutes=int(request.form.get('duration_minutes', 60)),
                max_students=int(request.form.get('max_students', 50)),
                teacher_id=current_user.id
            )
            db.session.add(ls)
            db.session.commit()
            flash('Live session created', 'success')
        elif action == 'delete':
            ls_id = int(request.form.get('session_id'))
            ls = LiveSession.query.get(ls_id)
            if ls and ls.teacher_id == current_user.id:
                db.session.delete(ls)
                db.session.commit()
                flash('Session deleted', 'success')
        elif action == 'toggle':
            ls_id = int(request.form.get('session_id'))
            ls = LiveSession.query.get(ls_id)
            if ls and ls.teacher_id == current_user.id:
                ls.is_active = not ls.is_active
                db.session.commit()
    sessions = LiveSession.query.filter_by(teacher_id=current_user.id).order_by(
        LiveSession.scheduled_at.desc()).all()
    pending = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
    return render_template('teacher/live.html', sessions=sessions, pending=pending)

@app.route('/teacher/announcements', methods=['GET', 'POST'])
@login_required
def teacher_announcements():
    if current_user.role != 'teacher':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            ann_image = ''
            if 'ann_image' in request.files and request.files['ann_image'].filename:
                f = request.files['ann_image']
                if allowed_file(f.filename, ALLOWED_IMG):
                    ann_image = save_file(f, 'announcements')
            ann = Announcement(
                title=request.form.get('title'),
                content=request.form.get('content'),
                image=ann_image,
                teacher_id=current_user.id
            )
            db.session.add(ann)
            db.session.commit()
            flash('Announcement published', 'success')
        elif action == 'delete':
            ann_id = int(request.form.get('ann_id'))
            ann = Announcement.query.get(ann_id)
            if ann and ann.teacher_id == current_user.id:
                db.session.delete(ann)
                db.session.commit()
                flash('Announcement deleted', 'success')
    announcements = Announcement.query.filter_by(teacher_id=current_user.id).order_by(
        Announcement.created_at.desc()).all()
    pending = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
    return render_template('teacher/announcements.html', announcements=announcements, pending=pending)

@app.route('/teacher/students')
@login_required
def teacher_students():
    if current_user.role != 'teacher':
        return redirect(url_for('dashboard'))
    enrollments = db.session.query(Enrollment, User, Course).join(
        User, Enrollment.student_id == User.id).join(
        Course, Enrollment.course_id == Course.id).filter(
        Course.teacher_id == current_user.id).order_by(Enrollment.enrolled_at.desc()).all()
    pending = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
    return render_template('teacher/students.html', enrollments=enrollments, pending=pending)

@app.route('/teacher/enrollment/<int:enroll_id>/approve', methods=['POST'])
@login_required
def approve_enrollment(enroll_id):
    e = Enrollment.query.get_or_404(enroll_id)
    e.is_approved = True
    db.session.commit()
    flash('Student approved', 'success')
    return redirect(url_for('teacher_students'))

@app.route('/teacher/profile', methods=['GET', 'POST'])
@login_required
def teacher_profile():
    if current_user.role != 'teacher':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.whatsapp = request.form.get('whatsapp', current_user.whatsapp)
        current_user.telegram = request.form.get('telegram', current_user.telegram)
        current_user.bio = request.form.get('bio', current_user.bio)
        current_user.bank_account = request.form.get('bank_account', current_user.bank_account)
        current_user.bank_name = request.form.get('bank_name', current_user.bank_name)
        current_user.wallet_vodafone = request.form.get('wallet_vodafone', current_user.wallet_vodafone)
        current_user.wallet_instapay = request.form.get('wallet_instapay', current_user.wallet_instapay)
        current_user.wallet_stcpay = request.form.get('wallet_stcpay', current_user.wallet_stcpay)
        current_user.wallet_other = request.form.get('wallet_other', current_user.wallet_other)
        current_user.payment_notes = request.form.get('payment_notes', current_user.payment_notes)
        if 'avatar' in request.files and request.files['avatar'].filename:
            f = request.files['avatar']
            if allowed_file(f.filename, ALLOWED_IMG):
                current_user.avatar = save_file(f, 'avatars')
        if 'hero_photo' in request.files and request.files['hero_photo'].filename:
            f = request.files['hero_photo']
            if allowed_file(f.filename, ALLOWED_IMG):
                current_user.hero_photo = save_file(f, 'avatars')
        new_pw = request.form.get('new_password', '')
        if new_pw:
            current_user.password = generate_password_hash(new_pw)
        db.session.commit()
        flash('Profile saved successfully', 'success')
    pending = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
    return render_template('teacher/profile.html', pending=pending)

# ─── Contact Page ─────────────────────────────────────────
@app.route('/contact')
def contact():
    teacher = User.query.filter_by(role='teacher').first()
    return render_template('public/contact.html', teacher=teacher)

# ─── Site Content Management ──────────────────────────────
@app.route('/teacher/site-content', methods=['GET', 'POST'])
@login_required
def teacher_site_content():
    if current_user.role != 'teacher':
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update':
            key = request.form.get('key')
            value = request.form.get('value', '')
            value_ar = request.form.get('value_ar', '')
            content = SiteContent.query.filter_by(key=key, teacher_id=current_user.id).first()
            if content:
                content.value = value
                content.value_ar = value_ar
                content.updated_at = datetime.utcnow()
            else:
                content = SiteContent(
                    key=key,
                    value=value,
                    value_ar=value_ar,
                    section=request.form.get('section', 'general'),
                    description=request.form.get('description', ''),
                    teacher_id=current_user.id
                )
                db.session.add(content)
            db.session.commit()
            flash('Content updated successfully', 'success')
            return redirect(url_for('teacher_site_content'))

        elif action == 'bulk_update':
            # Handle bulk update from the form
            for key in request.form:
                if key.startswith('content_'):
                    content_key = key.replace('content_', '')
                    value = request.form.get(key, '')
                    value_ar_key = f'content_ar_{content_key}'
                    value_ar = request.form.get(value_ar_key, '')

                    content = SiteContent.query.filter_by(key=content_key, teacher_id=current_user.id).first()
                    if content:
                        content.value = value
                        content.value_ar = value_ar
                        content.updated_at = datetime.utcnow()
                    else:
                        # Determine section based on key prefix
                        section = 'general'
                        if content_key.startswith('hero_'): section = 'hero'
                        elif content_key.startswith('feature_'): section = 'features'
                        elif content_key.startswith('quote_'): section = 'quote'
                        elif content_key.startswith('section_'): section = 'sections'
                        elif content_key.startswith('footer_'): section = 'footer'
                        elif content_key.startswith('nav_'): section = 'nav'

                        content = SiteContent(
                            key=content_key,
                            value=value,
                            value_ar=value_ar,
                            section=section,
                            teacher_id=current_user.id
                        )
                        db.session.add(content)
            db.session.commit()
            flash('All content updated successfully', 'success')
            return redirect(url_for('teacher_site_content'))

    # Get all content for the form
    contents = SiteContent.query.filter_by(teacher_id=current_user.id).all()
    content_dict = {c.key: c for c in contents}

    # Default content structure
    default_keys = [
        # Hero Section
        ('hero_tag', 'hero', 'Hero tag text (e.g., منصة تعليمية احترافية)'),
        ('hero_title_en', 'hero', 'Hero English title'),
        ('hero_title_ar', 'hero', 'Hero Arabic title'),
        ('hero_subtitle', 'hero', 'Hero subtitle/description'),
        ('hero_cta_primary', 'hero', 'Primary CTA button text'),
        ('hero_cta_secondary', 'hero', 'Secondary CTA button text'),

        # Features Section
        ('features_title', 'sections', 'Features section title'),
        ('features_title_full', 'sections', 'Features section full title (e.g., خدماتنا المميزة)'),
        ('features_subtitle', 'sections', 'Features section subtitle'),
        ('feature_1_title', 'features', 'Feature 1 title'),
        ('feature_1_desc', 'features', 'Feature 1 description'),
        ('feature_2_title', 'features', 'Feature 2 title'),
        ('feature_2_desc', 'features', 'Feature 2 description'),
        ('feature_3_title', 'features', 'Feature 3 title'),
        ('feature_3_desc', 'features', 'Feature 3 description'),
        ('feature_4_title', 'features', 'Feature 4 title'),
        ('feature_4_desc', 'features', 'Feature 4 description'),
        ('feature_5_title', 'features', 'Feature 5 title'),
        ('feature_5_desc', 'features', 'Feature 5 description'),
        ('feature_6_title', 'features', 'Feature 6 title'),
        ('feature_6_desc', 'features', 'Feature 6 description'),

        # Quote Section
        ('quote_text', 'quote', 'Quote text'),
        ('quote_author', 'quote', 'Quote author'),

        # Courses Section
        ('courses_title', 'sections', 'Courses section title'),
        ('courses_subtitle', 'sections', 'Courses section subtitle'),

        # Live Sessions Section
        ('live_title', 'sections', 'Live sessions section title'),
        ('live_subtitle', 'sections', 'Live sessions section subtitle'),

        # Announcements Section
        ('announcements_title', 'sections', 'Announcements section title'),

        # Footer
        ('footer_brand_name', 'footer', 'Footer brand name'),
        ('footer_brand_desc', 'footer', 'Footer brand description'),
        ('footer_copyright', 'footer', 'Footer copyright text'),

        # Navigation
        ('nav_courses', 'nav', 'Navigation - Courses'),
        ('nav_live', 'nav', 'Navigation - Live Sessions'),
        ('nav_announcements', 'nav', 'Navigation - Announcements'),
    ]

    # Initialize default content if not exists
    for key, section, desc in default_keys:
        if key not in content_dict:
            default_content = SiteContent(
                key=key,
                value='',
                value_ar='',
                section=section,
                description=desc,
                teacher_id=current_user.id
            )
            db.session.add(default_content)
            content_dict[key] = default_content

    db.session.commit()

    pending = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
    return render_template('teacher/site_content.html', content_dict=content_dict, pending=pending)


# ─── Assistant Routes ───────────────────────────────────
@app.route('/add-assistant', methods=['GET', 'POST'])
@login_required
def add_assistant():
    if current_user.role != 'teacher':
        abort(403)
    if request.method == 'POST':
        image_file = request.files.get('image')
        image_path = ''
        if image_file and image_file.filename:
            if allowed_file(image_file.filename, ALLOWED_IMG):
                image_path = save_file(image_file, 'avatars')
        can_upload = request.form.get('can_upload_lessons') == 'on'
        assistant = Assistant(
            name=request.form.get('name'),
            specialty=request.form.get('specialty'),
            bio=request.form.get('bio'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            image=image_path,
            teacher_id=current_user.id,
            can_upload_lessons=can_upload
        )
        db.session.add(assistant)
        db.session.commit()
        flash('Assistant added successfully', 'success')
        return redirect(url_for('assistants'))
    pending = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
    return render_template('add_assistant.html', pending=pending)

@app.route('/assistant/<int:assistant_id>/delete', methods=['POST'])
@login_required
def delete_assistant(assistant_id):
    if current_user.role != 'teacher':
        abort(403)
    assistant = Assistant.query.get_or_404(assistant_id)
    if assistant.teacher_id != current_user.id:
        abort(403)
    db.session.delete(assistant)
    db.session.commit()
    flash('Assistant deleted', 'success')
    return redirect(url_for('assistants'))

@app.route('/assistant/<int:assistant_id>/toggle-permissions', methods=['POST'])
@login_required
def toggle_assistant_permissions(assistant_id):
    if current_user.role != 'teacher':
        abort(403)
    assistant = Assistant.query.get_or_404(assistant_id)
    if assistant.teacher_id != current_user.id:
        abort(403)
    assistant.can_upload_lessons = not assistant.can_upload_lessons
    db.session.commit()
    status = 'Enabled' if assistant.can_upload_lessons else 'Disabled'
    flash(f'Permissions updated - Upload: {status}', 'success')
    return redirect(url_for('assistants'))

@app.route('/assistants')
def assistants():
    if current_user.is_authenticated and current_user.role == 'teacher':
        assistants = Assistant.query.filter_by(teacher_id=current_user.id).all()
        pending = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
        return render_template('assistants.html', assistants=assistants, is_teacher=True, pending=pending)
    else:
        assistants = Assistant.query.all()
        pending = Enrollment.query.join(Course).filter(Course.teacher_id == current_user.id, Enrollment.is_approved == False).count()
        return render_template('assistants.html', assistants=assistants, is_teacher=False, pending=pending)

# ─── Init DB & seed ───────────────────────────────────────
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='teacher@english.com').first():
            teacher = User(
                name='Mr. Alaa Elsaadany',
                email='teacher@english.com',
                password=generate_password_hash('teacher123'),
                role='teacher',
                bio='Certified TEFL instructor with 10+ years of experience teaching English to non-native speakers.',
                country='United Kingdom'
            )
            db.session.add(teacher)
            db.session.commit()
            course = Course(
                title='English Grammar Fundamentals',
                description='A comprehensive course to learn English grammar from scratch with practical exercises',
                level='Beginner', category='Grammar',
                price=0, is_free=True, is_published=True,
                teacher_id=teacher.id
            )
            db.session.add(course)
            db.session.flush()
            for i, t in enumerate(['Introduction to Grammar', 'Present Tenses', 'Past Tenses'], 1):
                lesson = Lesson(title=t, order_num=i,
                                video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
                                duration='45 min', course_id=course.id,
                                is_free_preview=(i == 1))
                db.session.add(lesson)
            db.session.commit()
            print("✅ Database initialized with demo data")
            print("👤 Teacher login: teacher@english.com / teacher123")

for _sub in ['thumbnails', 'videos', 'avatars', 'materials', 'announcements']:
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], _sub), exist_ok=True)

init_db()

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'true').lower() == 'true',
            host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
