from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
from datetime import datetime

@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}



# ====== KONFIGURASI APP & DATABASE (MySQL Laragon) ======
# Pastikan database "koperasi" sudah ada di MySQL Laragon
# Default Laragon biasanya: user=root, password="" (kosong), port=3306
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:@127.0.0.1:3306/koperasi"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "rahasia_koperasi_123"  # ganti kalau mau lebih aman

db = SQLAlchemy(app)


# ====== MODEL DATABASE ======
class User(db.Model):
    __tablename__ = "users"  # hindari nama tabel "user"
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telepon = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # role: admin / user
    role = db.Column(db.String(10), nullable=False, default="user")

    pinjaman = db.relationship("Pinjaman", backref="user", lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Pinjaman(db.Model):
    __tablename__ = "pinjaman"
    id = db.Column(db.Integer, primary_key=True)
    peminjam = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    jumlah = db.Column(db.Integer, nullable=False)
    tenor = db.Column(db.Integer, nullable=False)
    keperluan = db.Column(db.String(200), nullable=False)

    bunga = db.Column(db.Float, nullable=False)
    total_bunga = db.Column(db.Float, nullable=False)
    total_bayar = db.Column(db.Float, nullable=False)
    angsuran = db.Column(db.Float, nullable=False)


# ====== HELPER: LOGIN / ROLE REQUIRED ======
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("Akses ditolak: hanya admin.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "user":
            flash("Hanya user yang dapat mengajukan pinjaman.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


# ====== ROUTE LOGIN / REGISTER / LOGOUT ======
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["username"] = user.username
            session["nama"] = user.nama
            session["role"] = user.role
            flash("Berhasil login.", "success")
            return redirect(url_for("index"))
        else:
            flash("Username atau password salah.", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nama = request.form.get("nama", "").strip()
        email = request.form.get("email", "").strip()
        telepon = request.form.get("telepon", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not (nama and email and telepon and username and password):
            flash("Semua field wajib diisi.", "error")
        elif User.query.filter_by(username=username).first():
            flash("Username sudah digunakan.", "error")
        elif User.query.filter_by(email=email).first():
            flash("Email sudah digunakan.", "error")
        else:
            user = User(
                nama=nama,
                email=email,
                telepon=telepon,
                username=username,
                role="user"  # default role user
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash("Registrasi berhasil, silakan login.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Anda telah logout.", "success")
    return redirect(url_for("login"))


# ====== DASHBOARD ======
@app.route("/")
@login_required
def index():
    username = session.get("nama") or session.get("username")
    return render_template(
        "index.html",
        username=username,
        active="dashboard",
        role=session.get("role")
    )


# ====== USER: PENGAJUAN PINJAMAN (HANYA ROLE USER) ======
@app.route("/pengajuan", methods=["GET", "POST"])
@user_required
def pengajuan():
    if request.method == "POST":
        jumlah_str = request.form.get("jumlah", "0").strip()
        tenor_str = request.form.get("tenor", "0").strip()
        keperluan = request.form.get("keperluan", "").strip()

        try:
            jumlah = int(jumlah_str)
            tenor = int(tenor_str)
        except ValueError:
            flash("Jumlah dan tenor harus berupa angka.", "error")
            return redirect(url_for("pengajuan"))

        if jumlah <= 0 or tenor <= 0 or not keperluan:
            flash("Mohon isi data pinjaman dengan benar.", "error")
            return redirect(url_for("pengajuan"))

        user = User.query.filter_by(username=session["username"]).first()
        if not user:
            session.clear()
            flash("Session tidak valid, silakan login ulang.", "error")
            return redirect(url_for("login"))

        peminjam = user.nama or user.username

        bunga = 12.0  # % per tahun
        total_bunga = jumlah * (bunga / 100.0) * (tenor / 12.0)
        total_bayar = jumlah + total_bunga
        angsuran = total_bayar / tenor

        pinjaman = Pinjaman(
            peminjam=peminjam,
            user_id=user.id,
            jumlah=jumlah,
            tenor=tenor,
            keperluan=keperluan,
            bunga=bunga,
            total_bunga=total_bunga,
            total_bayar=total_bayar,
            angsuran=angsuran,
        )
        db.session.add(pinjaman)
        db.session.commit()

        flash("Pengajuan pinjaman berhasil disimpan.", "success")
        return redirect(url_for("daftar_pinjaman"))

    username = session.get("nama") or session.get("username")
    return render_template(
        "pengajuan.html",
        username=username,
        active="pengajuan",
        role=session.get("role")
    )


# ====== DAFTAR PINJAMAN (ADMIN: SEMUA, USER: MILIK SENDIRI) ======
@app.route("/daftar_pinjaman")
@login_required
def daftar_pinjaman():
    username = session.get("nama") or session.get("username")
    role = session.get("role")

    if role == "admin":
        pinjaman_list = Pinjaman.query.order_by(Pinjaman.id.desc()).all()
    else:
        user = User.query.filter_by(username=session["username"]).first()
        if not user:
            session.clear()
            flash("Session tidak valid, silakan login ulang.", "error")
            return redirect(url_for("login"))

        pinjaman_list = (
            Pinjaman.query
            .filter_by(user_id=user.id)
            .order_by(Pinjaman.id.desc())
            .all()
        )

    return render_template(
        "daftar_pinjaman.html",
        username=username,
        active="daftar",
        pinjaman_list=pinjaman_list,
        role=role
    )


# ====== USER: PINJAMAN SAYA (KHUSUS USER LOGIN) ======
@app.route("/pinjaman_saya")
@login_required
def pinjaman_saya():
    username = session.get("nama") or session.get("username")
    role = session.get("role")

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        session.clear()
        flash("Session tidak valid, silakan login ulang.", "error")
        return redirect(url_for("login"))

    pinjaman_list = (
        Pinjaman.query
        .filter_by(user_id=user.id)
        .order_by(Pinjaman.id.desc())
        .all()
    )

    return render_template(
        "pinjaman_saya.html",
        username=username,
        active="pinjaman_saya",
        pinjaman_list=pinjaman_list,
        role=role
    )


# ====== HAPUS PINJAMAN (ADMIN: BOLEH SEMUA, USER: HANYA MILIK SENDIRI) ======
@app.route("/hapus_pinjaman/<int:pinjaman_id>")
@login_required
def hapus_pinjaman(pinjaman_id):
    pinjaman = Pinjaman.query.get_or_404(pinjaman_id)
    role = session.get("role")

    if role != "admin":
        user = User.query.filter_by(username=session["username"]).first()
        if not user or pinjaman.user_id != user.id:
            flash("Akses ditolak: bukan pinjaman Anda.", "error")
            return redirect(url_for("daftar_pinjaman"))

    db.session.delete(pinjaman)
    db.session.commit()
    flash("Data pinjaman berhasil dihapus.", "success")
    return redirect(url_for("daftar_pinjaman"))


# ====== ADMIN AREA ======
@app.route("/admin/users")
@admin_required
def admin_users():
    users = User.query.order_by(User.id.desc()).all()
    return render_template("admin_users.html", users=users, active="admin_users")




@app.route("/admin/set-role/<int:user_id>/<string:role>")
@admin_required
def admin_set_role(user_id, role):
    if role not in ("admin", "user"):
        flash("Role tidak valid.", "error")
        return redirect(url_for("admin_users"))

    u = User.query.get_or_404(user_id)

    # Cegah admin menurunkan dirinya sendiri
    if u.username == session.get("username") and role != "admin":
        flash("Tidak bisa menurunkan role akun yang sedang login.", "error")
        return redirect(url_for("admin_users"))

    u.role = role
    db.session.commit()
    flash(f"Role user {u.username} berhasil diubah menjadi {role}.", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/delete-user/<int:user_id>")
@admin_required
def admin_delete_user(user_id):
    u = User.query.get_or_404(user_id)

    # Cegah admin hapus dirinya sendiri
    if u.username == session.get("username"):
        flash("Tidak bisa menghapus akun yang sedang login.", "error")
        return redirect(url_for("admin_users"))

    db.session.delete(u)
    db.session.commit()
    flash("User berhasil dihapus.", "success")
    return redirect(url_for("admin_users"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
