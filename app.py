import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func

app = Flask(__name__)

# ====== KONFIGURASI APP & DATABASE (MySQL Laragon) ======
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:@127.0.0.1:3306/koperasi"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "rahasia_koperasi_123"  # ganti kalau mau lebih aman

# ====== UPLOAD CONFIG (BUKTI PEMBAYARAN) ======
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


db = SQLAlchemy(app)


@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}


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
    
    # status verifikasi user
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    verified_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    verified_at = db.Column(db.DateTime)

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

    # relasi fitur baru
    loan_status = db.relationship(
        "LoanStatus",
        uselist=False,
        backref="pinjaman",
        cascade="all, delete-orphan",
        lazy=True,
    )
    payments = db.relationship(
        "LoanPayment",
        backref="pinjaman",
        cascade="all, delete-orphan",
        lazy=True,
    )


# ====== FITUR BARU: STATUS PINJAMAN & PEMBAYARAN ======
class LoanStatus(db.Model):
    __tablename__ = "loan_status"

    # 1-1: pinjaman_id = PK sekaligus FK
    pinjaman_id = db.Column(db.Integer, db.ForeignKey("pinjaman.id"), primary_key=True)

    # pending / approved / rejected / disbursement_requested / disbursed / lunas
    status = db.Column(db.String(30), nullable=False, default="pending")

    catatan = db.Column(db.String(255))

    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    approved_at = db.Column(db.DateTime)

    disbursed_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    disbursed_at = db.Column(db.DateTime)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LoanPayment(db.Model):
    __tablename__ = "loan_payments"

    id = db.Column(db.Integer, primary_key=True)

    pinjaman_id = db.Column(db.Integer, db.ForeignKey("pinjaman.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    jumlah = db.Column(db.Integer, nullable=False)
    metode = db.Column(db.String(30))  # cash/transfer/ewallet
    bukti_path = db.Column(db.String(255))  # relatif ke /static (contoh: uploads/xxx.pdf)

    # pending / verified / rejected
    status = db.Column(db.String(20), nullable=False, default="pending")

    catatan = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    verified_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    verified_at = db.Column(db.DateTime)


# ====== HELPER ======
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


def current_user():
    if "username" not in session:
        return None
    return User.query.filter_by(username=session["username"]).first()


def ensure_loan_status(pinjaman_id: int, default_status="pending"):
    st = LoanStatus.query.get(pinjaman_id)
    if not st:
        st = LoanStatus(pinjaman_id=pinjaman_id, status=default_status)
        db.session.add(st)
        db.session.commit()
    return st


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
                role="user",
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
        role=session.get("role"),
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

        user = current_user()
        if not user:
            session.clear()
            flash("Session tidak valid, silakan login ulang.", "error")
            return redirect(url_for("login"))

        peminjam = user.nama or user.username

        bunga = 1.0  # % per bulan (12% per tahun)
        total_bunga = jumlah * (bunga / 100.0) * tenor
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

        # status awal: pending (menunggu persetujuan admin)
        st = LoanStatus(pinjaman_id=pinjaman.id, status="pending")
        db.session.add(st)
        db.session.commit()

        flash("Pengajuan pinjaman berhasil dikirim. Menunggu persetujuan admin.", "success")
        return redirect(url_for("pengajuan"))

    # GET request: tampilkan form + riwayat + statistik
    user = current_user()
    if not user:
        session.clear()
        flash("Session tidak valid, silakan login ulang.", "error")
        return redirect(url_for("login"))

    # Ambil semua pinjaman user
    pinjaman_list = (
        Pinjaman.query.filter_by(user_id=user.id)
        .order_by(Pinjaman.id.desc())
        .all()
    )

    # Pastikan semua pinjaman punya status
    for p in pinjaman_list:
        if not p.loan_status:
            ensure_loan_status(p.id, default_status="pending")

    # Hitung statistik
    total_pengajuan = len(pinjaman_list)
    
    status_pending = sum(1 for p in pinjaman_list if p.loan_status and p.loan_status.status == "pending")
    status_approved = sum(1 for p in pinjaman_list if p.loan_status and p.loan_status.status == "approved")
    status_rejected = sum(1 for p in pinjaman_list if p.loan_status and p.loan_status.status == "rejected")
    status_disbursed = sum(1 for p in pinjaman_list if p.loan_status and p.loan_status.status == "disbursed")
    status_lunas = sum(1 for p in pinjaman_list if p.loan_status and p.loan_status.status == "lunas")
    
    total_pinjaman_nilai = sum(p.jumlah for p in pinjaman_list)
    total_harus_bayar = sum(p.total_bayar for p in pinjaman_list if p.loan_status and p.loan_status.status in ("disbursed", "lunas"))

    username = session.get("nama") or session.get("username")
    return render_template(
        "pengajuan.html",
        username=username,
        active="pengajuan",
        role=session.get("role"),
        pinjaman_list=pinjaman_list,
        total_pengajuan=total_pengajuan,
        status_pending=status_pending,
        status_approved=status_approved,
        status_rejected=status_rejected,
        status_disbursed=status_disbursed,
        status_lunas=status_lunas,
        total_pinjaman_nilai=total_pinjaman_nilai,
        total_harus_bayar=total_harus_bayar,
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
        user = current_user()
        if not user:
            session.clear()
            flash("Session tidak valid, silakan login ulang.", "error")
            return redirect(url_for("login"))

        pinjaman_list = (
            Pinjaman.query.filter_by(user_id=user.id).order_by(Pinjaman.id.desc()).all()
        )

    # pastikan pinjaman lama punya status juga
    for p in pinjaman_list:
        if not p.loan_status:
            ensure_loan_status(p.id, default_status="pending")

    return render_template(
        "daftar_pinjaman.html",
        username=username,
        active="daftar",
        pinjaman_list=pinjaman_list,
        role=role,
    )


# ====== USER: PINJAMAN SAYA (KHUSUS USER LOGIN) ======
@app.route("/pinjaman_saya")
@login_required
def pinjaman_saya():
    username = session.get("nama") or session.get("username")
    role = session.get("role")

    user = current_user()
    if not user:
        session.clear()
        flash("Session tidak valid, silakan login ulang.", "error")
        return redirect(url_for("login"))

    pinjaman_list = (
        Pinjaman.query.filter_by(user_id=user.id).order_by(Pinjaman.id.desc()).all()
    )

    for p in pinjaman_list:
        if not p.loan_status:
            ensure_loan_status(p.id, default_status="pending")

    return render_template(
        "pinjaman_saya.html",
        username=username,
        active="pinjaman_saya",
        pinjaman_list=pinjaman_list,
        role=role,
    )


# ====== HAPUS PINJAMAN (ADMIN: BOLEH SEMUA, USER: HANYA MILIK SENDIRI) ======
@app.route("/hapus_pinjaman/<int:pinjaman_id>")
@login_required
def hapus_pinjaman(pinjaman_id):
    pinjaman = Pinjaman.query.get_or_404(pinjaman_id)
    role = session.get("role")

    if role != "admin":
        user = current_user()
        if not user or pinjaman.user_id != user.id:
            flash("Akses ditolak: bukan pinjaman Anda.", "error")
            return redirect(url_for("daftar_pinjaman"))

    db.session.delete(pinjaman)
    db.session.commit()
    flash("Data pinjaman berhasil dihapus.", "success")
    return redirect(url_for("daftar_pinjaman"))


# =========================================================
# ===================== FITUR BARU =========================
# =========================================================

# ====== USER: HALAMAN PENGAMBILAN / PENCAIRAN PINJAMAN ======
@app.route("/pengambilan_pinjaman")
@user_required
def pengambilan_pinjaman():
    user = current_user()
    if not user:
        session.clear()
        return redirect(url_for("login"))

    pinjaman_list = (
        Pinjaman.query.filter_by(user_id=user.id).order_by(Pinjaman.id.desc()).all()
    )

    for p in pinjaman_list:
        if not p.loan_status:
            ensure_loan_status(p.id, default_status="pending")

    return render_template(
        "pengambilan_pinjaman.html",
        username=user.nama or user.username,
        active="pengambilan_pinjaman",
        pinjaman_list=pinjaman_list,
        role=session.get("role"),
    )


# ====== USER: AJUKAN PENGAMBILAN (APPROVED -> DISBURSEMENT_REQUESTED) ======
@app.route("/pinjaman/<int:pinjaman_id>/ajukan-pengambilan", methods=["POST"])
@user_required
def ajukan_pengambilan(pinjaman_id):
    user = current_user()
    p = Pinjaman.query.get_or_404(pinjaman_id)

    if not user or p.user_id != user.id:
        flash("Akses ditolak.", "error")
        return redirect(url_for("pengambilan_pinjaman"))

    st = p.loan_status or ensure_loan_status(p.id, default_status="pending")

    if st.status != "approved":
        flash("Pinjaman belum disetujui admin, belum bisa diajukan pencairan.", "error")
        return redirect(url_for("pengambilan_pinjaman"))

    st.status = "disbursement_requested"
    st.updated_at = datetime.utcnow()
    db.session.commit()

    flash("Pengambilan/pencairan diajukan. Menunggu verifikasi admin.", "success")
    return redirect(url_for("pengambilan_pinjaman"))


# ====== USER: BAYAR CICILAN PINJAMAN ======
@app.route("/pinjaman/<int:pinjaman_id>/bayar", methods=["GET", "POST"])
@user_required
def bayar_pinjaman(pinjaman_id):
    user = current_user()
    p = Pinjaman.query.get_or_404(pinjaman_id)

    if not user or p.user_id != user.id:
        flash("Akses ditolak.", "error")
        return redirect(url_for("pinjaman_saya"))

    st = p.loan_status or ensure_loan_status(p.id, default_status="pending")

    # hanya bisa bayar kalau sudah dicairkan atau sudah lunas (untuk lihat histori)
    if st.status not in ("disbursed", "lunas"):
        flash("Pinjaman belum dicairkan, pembayaran belum dibuka.", "error")
        return redirect(url_for("pinjaman_saya"))

    if request.method == "POST":
        jumlah = int(request.form.get("jumlah", "0"))
        metode = request.form.get("metode", "transfer")

        if jumlah <= 0:
            flash("Jumlah pembayaran harus > 0.", "error")
            return redirect(url_for("bayar_pinjaman", pinjaman_id=pinjaman_id))

        bukti_path = None
        bukti = request.files.get("bukti")
        if bukti and bukti.filename:
            if not allowed_file(bukti.filename):
                flash("Format bukti tidak didukung (png/jpg/jpeg/pdf).", "error")
                return redirect(url_for("bayar_pinjaman", pinjaman_id=pinjaman_id))

            fname = secure_filename(bukti.filename)
            fname = f"{user.id}_{pinjaman_id}_{int(datetime.utcnow().timestamp())}_{fname}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], fname)
            bukti.save(save_path)
            bukti_path = f"uploads/{fname}"  # relatif ke /static

        pay = LoanPayment(
            pinjaman_id=pinjaman_id,
            user_id=user.id,
            jumlah=jumlah,
            metode=metode,
            bukti_path=bukti_path,
            status="pending",
        )
        db.session.add(pay)
        db.session.commit()

        flash("Pembayaran dikirim. Menunggu verifikasi admin.", "success")
        return redirect(url_for("bayar_pinjaman", pinjaman_id=pinjaman_id))

    total_verified = (
        db.session.query(func.coalesce(func.sum(LoanPayment.jumlah), 0))
        .filter(LoanPayment.pinjaman_id == pinjaman_id, LoanPayment.status == "verified")
        .scalar()
    )
    sisa = float(p.total_bayar) - float(total_verified)

    payments = (
        LoanPayment.query.filter_by(pinjaman_id=pinjaman_id)
        .order_by(LoanPayment.id.desc())
        .all()
    )

    return render_template(
        "bayar_pinjaman.html",
        username=user.nama or user.username,
        active="bayar",
        role=session.get("role"),
        pinjaman=p,
        loan_status=st,
        total_verified=total_verified,
        sisa=sisa,
        payments=payments,
    )


# ====== ADMIN: APPROVE / REJECT PINJAMAN ======
@app.route("/admin/pinjaman/<int:pinjaman_id>/approve", methods=["POST"])
@admin_required
def admin_approve_pinjaman(pinjaman_id):
    admin = current_user()
    p = Pinjaman.query.get_or_404(pinjaman_id)
    st = p.loan_status or ensure_loan_status(p.id, default_status="pending")

    st.status = "approved"
    st.approved_by = admin.id if admin else None
    st.approved_at = datetime.utcnow()
    db.session.commit()

    flash("Pinjaman disetujui.", "success")
    return redirect(url_for("daftar_pinjaman"))


@app.route("/admin/pinjaman/<int:pinjaman_id>/reject", methods=["POST"])
@admin_required
def admin_reject_pinjaman(pinjaman_id):
    p = Pinjaman.query.get_or_404(pinjaman_id)
    st = p.loan_status or ensure_loan_status(p.id, default_status="pending")

    st.status = "rejected"
    db.session.commit()

    flash("Pinjaman ditolak.", "success")
    return redirect(url_for("daftar_pinjaman"))


# ====== ADMIN: TANDAI SUDAH DICAIRKAN ======
@app.route("/admin/pinjaman/<int:pinjaman_id>/disburse", methods=["POST"])
@admin_required
def admin_disburse_pinjaman(pinjaman_id):
    admin = current_user()
    p = Pinjaman.query.get_or_404(pinjaman_id)
    st = p.loan_status or ensure_loan_status(p.id, default_status="pending")

    if st.status != "disbursement_requested":
        flash("Status belum meminta pencairan.", "error")
        return redirect(url_for("daftar_pinjaman"))

    st.status = "disbursed"
    st.disbursed_by = admin.id if admin else None
    st.disbursed_at = datetime.utcnow()
    db.session.commit()

    flash("Pinjaman ditandai sudah dicairkan.", "success")
    return redirect(url_for("daftar_pinjaman"))


# ====== ADMIN: LIST PEMBAYARAN PENDING ======
@app.route("/admin/pembayaran")
@admin_required
def admin_pembayaran():
    payments = LoanPayment.query.filter_by(status="pending").order_by(LoanPayment.id.desc()).all()
    return render_template("admin_pembayaran.html", payments=payments, active="admin_pembayaran")


# ====== ADMIN: VERIFY / REJECT PEMBAYARAN ======
@app.route("/admin/pembayaran/<int:payment_id>/verify", methods=["POST"])
@admin_required
def admin_verify_payment(payment_id):
    admin = current_user()
    pay = LoanPayment.query.get_or_404(payment_id)

    pay.status = "verified"
    pay.verified_by = admin.id if admin else None
    pay.verified_at = datetime.utcnow()
    db.session.commit()

    # cek pelunasan
    p = Pinjaman.query.get(pay.pinjaman_id)
    if p:
        st = p.loan_status or ensure_loan_status(p.id, default_status="disbursed")

        total_verified = (
            db.session.query(func.coalesce(func.sum(LoanPayment.jumlah), 0))
            .filter(LoanPayment.pinjaman_id == p.id, LoanPayment.status == "verified")
            .scalar()
        )

        if float(total_verified) >= float(p.total_bayar):
            st.status = "lunas"
            db.session.commit()

    flash("Pembayaran diverifikasi.", "success")
    return redirect(url_for("admin_pembayaran"))


@app.route("/admin/pembayaran/<int:payment_id>/reject", methods=["POST"])
@admin_required
def admin_reject_payment(payment_id):
    pay = LoanPayment.query.get_or_404(payment_id)
    pay.status = "rejected"
    db.session.commit()

    flash("Pembayaran ditolak.", "success")
    return redirect(url_for("admin_pembayaran"))


# ====== ADMIN AREA (USERS) ======
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


@app.route("/admin/approve-user/<int:user_id>")
@admin_required
def admin_approve_user(user_id):
    """Approve/Verify user account"""
    admin = current_user()
    u = User.query.get_or_404(user_id)
    
    if u.username == session.get("username"):
        flash("Tidak bisa approve akun yang sedang login.", "error")
        return redirect(url_for("admin_users"))
    
    u.is_verified = True
    u.verified_by = admin.id if admin else None
    u.verified_at = datetime.utcnow()
    db.session.commit()
    
    flash(f"User {u.username} berhasil disetujui/diverifikasi.", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/reject-user/<int:user_id>")
@admin_required
def admin_reject_user(user_id):
    """Reject user account"""
    u = User.query.get_or_404(user_id)
    
    if u.username == session.get("username"):
        flash("Tidak bisa reject akun yang sedang login.", "error")
        return redirect(url_for("admin_users"))
    
    u.is_verified = False
    u.verified_by = None
    u.verified_at = None
    db.session.commit()
    
    flash(f"User {u.username} berhasil ditolak/tidak diverifikasi.", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/delete-user/<int:user_id>")
@admin_required
def admin_delete_user(user_id):
    u = User.query.get_or_404(user_id)

    # Cegah admin hapus dirinya sendiri
    if u.username == session.get("username"):
        flash("Tidak bisa menghapus akun yang sedang login.", "error")
        return redirect(url_for("admin_users"))

    try:
        # Hapus semua referensi user di loan_payments sebagai verified_by
        LoanPayment.query.filter_by(verified_by=user_id).update({"verified_by": None})
        
        # Hapus semua referensi user di loan_status sebagai approved_by/disbursed_by
        LoanStatus.query.filter_by(approved_by=user_id).update({"approved_by": None})
        LoanStatus.query.filter_by(disbursed_by=user_id).update({"disbursed_by": None})
        
        # Hapus semua pinjaman milik user (cascade akan menghapus loan_payments & loan_status)
        Pinjaman.query.filter_by(user_id=user_id).delete()
        
        # Hapus user
        db.session.delete(u)
        db.session.commit()
        
        flash("User berhasil dihapus.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Gagal menghapus user: {str(e)}", "error")
    
    return redirect(url_for("admin_users"))


# ====== ADMIN: DASHBOARD ======
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Dashboard statistik untuk admin"""
    total_users = User.query.count()
    total_loans = Pinjaman.query.count()
    
    pending_count = (
        db.session.query(func.count(LoanStatus.pinjaman_id))
        .filter(LoanStatus.status == "pending")
        .scalar()
    )
    
    approved_count = (
        db.session.query(func.count(LoanStatus.pinjaman_id))
        .filter(LoanStatus.status == "approved")
        .scalar()
    )
    
    pending_payments_count = (
        db.session.query(func.count(LoanPayment.id))
        .filter(LoanPayment.status == "pending")
        .scalar()
    )
    
    total_loan_amount = (
        db.session.query(func.coalesce(func.sum(Pinjaman.jumlah), 0))
        .scalar()
    )
    
    return render_template(
        "admin_dashboard.html",
        active="admin_dashboard",
        role=session.get("role"),
        total_users=total_users,
        total_loans=total_loans,
        pending_count=pending_count,
        approved_count=approved_count,
        pending_payments_count=pending_payments_count,
        total_loan_amount=int(total_loan_amount),
    )


# ====== OPTIONAL: HANDLE FILE TOO LARGE ======
@app.errorhandler(413)
def too_large(e):
    flash("Ukuran file terlalu besar. Maksimal 5MB.", "error")
    return redirect(request.referrer or url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
