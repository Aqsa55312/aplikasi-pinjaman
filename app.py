import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ====== 1. KONFIGURASI ======
app = Flask(__name__)
app.secret_key = "KOPERASI_SUPER_RAHASIA_2025"

# Koneksi Database (Ganti 'koperasi' jika nama database Anda berbeda)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/koperasi"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Konfigurasi Upload
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads", "persyaratan")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

db = SQLAlchemy()
db.init_app(app)

# ====== 2. MODEL DATABASE ======
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telepon = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), default="user") # 'admin' atau 'user'
    
    # Dokumen Persyaratan
    ktp_npwp = db.Column(db.String(255))
    kk = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)

    pinjaman = db.relationship("Pinjaman", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Pinjaman(db.Model):
    __tablename__ = "pinjaman"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    peminjam = db.Column(db.String(100))
    jumlah = db.Column(db.Integer, nullable=False)
    tenor = db.Column(db.Integer, nullable=False)
    keperluan = db.Column(db.String(200))
    total_bayar = db.Column(db.Float)
    angsuran = db.Column(db.Float)
    status = db.Column(db.String(20), default="pending") # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ====== 3. DECORATORS & HELPERS ======
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session: return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Akses ditolak! Area khusus Admin.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

def current_user():
    return User.query.get(session.get("user_id"))

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ====== 4. ROUTES AUTH & UMUM ======
@app.route("/")
@login_required
def index():
    return render_template("index.html", user=current_user())

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = User.query.filter_by(username=request.form['username']).first()
        if u and u.check_password(request.form['password']):
            session.update({"user_id": u.id, "role": u.role, "nama": u.nama, "username": u.username})
            return redirect(url_for("index"))
        flash("Username atau password salah!", "error")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(username=request.form['username']).first():
            flash("Username sudah dipakai!", "error")
            return redirect(url_for("register"))
        u = User(nama=request.form['nama'], email=request.form['email'], 
                 telepon=request.form['telepon'], username=request.form['username'])
        u.set_password(request.form['password'])
        db.session.add(u)
        db.session.commit()
        flash("Berhasil daftar! Silakan login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ====== 5. ROUTES USER (PINJAMAN & DOKUMEN) ======
@app.route("/pengajuan", methods=["GET", "POST"])
@login_required
def pengajuan():
    user = current_user()
    if not user.is_verified:
        flash("Akun Anda belum diverifikasi Admin. Mohon lengkapi dokumen.", "warning")
        return redirect(url_for("halaman_dokumen"))
    
    if request.method == "POST":
        jml = int(request.form['jumlah'])
        tenor = int(request.form['tenor'])
        total = jml + (jml * 0.02 * tenor) # Bunga 2%
        new_loan = Pinjaman(user_id=user.id, peminjam=user.nama, jumlah=jml, 
                            tenor=tenor, keperluan=request.form['keperluan'],
                            total_bayar=total, angsuran=total/tenor)
        db.session.add(new_loan)
        db.session.commit()
        flash("Pengajuan pinjaman terkirim! Menunggu persetujuan admin.", "success")
        return redirect(url_for("pinjaman_saya"))
    return render_template("pengajuan.html", user=user)

@app.route("/pinjaman_saya")
@login_required
def pinjaman_saya():
    pinjaman_list = Pinjaman.query.filter_by(user_id=session['user_id']).all()
    return render_template("pinjaman_saya.html", pinjaman_list=pinjaman_list, user=current_user())

@app.route("/dokumen")
@login_required
def halaman_dokumen():
    return render_template("dokumen.html", user=current_user())

@app.route("/upload-dokumen", methods=["POST"])
@login_required
def upload_dokumen():
    user = current_user()
    for field in ['ktp_npwp', 'kk']:
        file = request.files.get(field)
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"u{user.id}_{field}.{ext}")
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            setattr(user, field, filename)
    db.session.commit()
    flash("Dokumen diupload. Admin akan segera memverifikasi.", "success")
    return redirect(url_for("index"))

# ====== 6. ROUTES ADMIN (USER & LOAN MANAGEMENT) ======

# --- Kelola User ---
@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@app.route("/admin/approve_user/<int:user_id>")
@login_required
@admin_required
def admin_approve_user(user_id):
    u = User.query.get_or_404(user_id)
    u.is_verified = True
    db.session.commit()
    flash(f"User {u.nama} telah diverifikasi.", "success")
    return redirect(url_for("admin_users"))

@app.route("/admin/reject_user/<int:user_id>")
@login_required
@admin_required
def admin_reject_user(user_id):
    u = User.query.get_or_404(user_id)
    u.is_verified = False
    db.session.commit()
    flash(f"Verifikasi {u.nama} dibatalkan.", "warning")
    return redirect(url_for("admin_users"))

@app.route("/admin/set_role/<int:user_id>/<string:role>")
@login_required
@admin_required
def admin_set_role(user_id, role):
    u = User.query.get_or_404(user_id)
    if u.id == session['user_id']:
        flash("Tidak bisa mengubah role sendiri!", "error")
    else:
        u.role = role
        db.session.commit()
        flash(f"Role {u.nama} sekarang adalah {role}.", "success")
    return redirect(url_for("admin_users"))

@app.route("/admin/delete_user/<int:user_id>")
@login_required
@admin_required
def admin_delete_user(user_id):
    u = User.query.get_or_404(user_id)
    if u.id == session['user_id']:
        flash("Tidak bisa hapus akun sendiri!", "error")
    else:
        db.session.delete(u)
        db.session.commit()
        flash(f"User {u.nama} dihapus selamanya.", "success")
    return redirect(url_for("admin_users"))

# --- Kelola Pinjaman ---
@app.route("/admin/pinjaman")
@login_required
@admin_required
def admin_pinjaman():
    pengajuan = Pinjaman.query.order_by(Pinjaman.created_at.desc()).all()
    return render_template("admin_pinjaman.html", pengajuan=pengajuan)

@app.route("/admin/pinjaman/approve/<int:id>")
@login_required
@admin_required
def approve_pinjaman(id):
    loan = Pinjaman.query.get_or_404(id)
    loan.status = "approved"
    db.session.commit()
    flash(f"Pinjaman {loan.peminjam} DISETUJUI.", "success")
    return redirect(url_for("admin_pinjaman"))

@app.route("/admin/pinjaman/reject/<int:id>")
@login_required
@admin_required
def reject_pinjaman(id):
    loan = Pinjaman.query.get_or_404(id)
    loan.status = "rejected"
    db.session.commit()
    flash(f"Pinjaman {loan.peminjam} DITOLAK.", "warning")
    return redirect(url_for("admin_pinjaman"))

# ====== 7. RUNNER ======
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)