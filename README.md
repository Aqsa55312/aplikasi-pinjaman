# 🏦 Aplikasi Koperasi Simpan Pinjam

Sistem manajemen pinjaman untuk koperasi dengan fitur pengajuan, persetujuan, pengambilan, dan pembayaran cicilan yang lengkap.

## ✨ Fitur Utama

### 👤 User Features
- ✅ **Pendaftaran & Login** - Sistem autentikasi aman
- ✅ **Pengajuan Pinjaman** - Form pengajuan dengan perhitungan bunga otomatis
- ✅ **Pinjaman Saya** - Dashboard pinjaman dengan status real-time
- ✅ **Pengambilan Pinjaman** - Ajukan pencairan untuk pinjaman yang disetujui
- ✅ **Pembayaran Cicilan** - Input pembayaran dengan upload bukti
- ✅ **Riwayat Pembayaran** - Track semua transaksi pembayaran

### 👨‍💼 Admin Features
- ✅ **Admin Dashboard** - Statistik pinjaman & pembayaran
- ✅ **Kelola Pinjaman** - Approve/Reject pengajuan & Disburse pinjaman
- ✅ **Verifikasi Pembayaran** - Review & verify pembayaran cicilan
- ✅ **Kelola User** - Atur role dan kelola account user

## 🔄 Workflow Pinjaman

```
┌─────────────────────────────────────────────────────────┐
│ 1. USER PENGAJUAN PINJAMAN                              │
│    Status: PENDING ⏳                                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ 2. ADMIN REVIEW                                         │
│    Approve ✅ / Reject ❌                                 │
└────────────────────┬────────────────────────────────────┘
                     │ (if approved)
┌────────────────────▼────────────────────────────────────┐
│ 3. USER AJUKAN PENGAMBILAN                              │
│    Status: DISBURSEMENT_REQUESTED 📤                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ 4. ADMIN DISBURSE (CAIRKAN)                             │
│    Status: DISBURSED 💰                                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ 5. USER BAYAR CICILAN (Multiple Times)                  │
│    Status Payment: PENDING ⏳                            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ 6. ADMIN VERIFY PEMBAYARAN                              │
│    Status Payment: VERIFIED ✅ / REJECTED ❌             │
│    if total verified ≥ total bayar → Status Pinjaman: LUNAS
└─────────────────────────────────────────────────────────┘
```

## 📋 Status Pinjaman

| Status | Icon | Keterangan |
|--------|------|-----------|
| Pending | ⏳ | Menunggu persetujuan admin |
| Approved | ✅ | Disetujui admin |
| Rejected | ❌ | Ditolak admin |
| Disbursement Requested | 📤 | Pengambilan sedang diajukan |
| Disbursed | 💰 | Sudah dicairkan |
| Lunas | 🏁 | Semua cicilan sudah terbayar |

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- MySQL (Laragon recommended)
- pip

### Installation Steps

```bash
# 1. Clone repository (atau download source)
cd "c:\laragon\www\aplikasi pinjaman"

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
.venv\Scripts\activate

# 4. Install dependencies
pip install flask flask-sqlalchemy mysqlconnector-python werkzeug

# 5. Create database
# Buka MySQL dan jalankan:
# CREATE DATABASE koperasi;

# 6. Seed test data (optional, untuk testing)
python seed_data.py

# 7. Run application
python app.py
```

### Access Application
```
URL: http://127.0.0.1:5000/
```

## 📝 Test Accounts (dari seed_data.py)

### Admin
```
Username: admin
Password: admin123
Email: admin@koperasi.com
```

### User 1
```
Username: budi
Password: budi123
Email: budi@email.com
```

### User 2
```
Username: siti
Password: siti123
Email: siti@email.com
```

## 📱 Menu Navigation

### User Menu
- 🏠 Dashboard
- 📝 Pengajuan Pinjaman
- 📋 Pinjaman Saya ⭐ **[NEW]**
  - Status pinjaman
  - Aksi: Ajukan Pengambilan, Bayar Cicilan
- 📤 Pengambilan Pinjaman ⭐ **[NEW]**
  - Ajukan pengambilan untuk pinjaman approved
- 💳 Pembayaran Cicilan ⭐ **[NEW]**
  - Input pembayaran cicilan
  - Progress bar & riwayat
- 🚪 Logout

### Admin Menu
- 🏠 Dashboard ⭐ **[NEW]**
  - Statistik & quick actions
- 📋 Kelola Pinjaman
  - Approve/Reject/Disburse
- 💰 Verifikasi Pembayaran ⭐ **[NEW]**
  - Verify/Reject pembayaran
- 👥 Kelola User

## 💾 Database Schema

### users
```sql
id (PK)
nama
email (UNIQUE)
telepon
username (UNIQUE)
password_hash
role (admin/user)
```

### pinjaman
```sql
id (PK)
peminjam
user_id (FK to users)
jumlah
tenor (bulan)
keperluan
bunga
total_bunga
total_bayar
angsuran
```

### loan_status
```sql
pinjaman_id (PK, FK to pinjaman)
status (pending/approved/rejected/disbursement_requested/disbursed/lunas)
catatan
approved_by (FK to users)
approved_at
disbursed_by (FK to users)
disbursed_at
updated_at
```

### loan_payments
```sql
id (PK)
pinjaman_id (FK to pinjaman)
user_id (FK to users)
jumlah
metode (cash/transfer/ewallet)
bukti_path
status (pending/verified/rejected)
catatan
created_at
verified_by (FK to users)
verified_at
```

## 📊 Perhitungan Bunga

```
Bunga per tahun: 12%
Total Bunga = Jumlah × 12% × (Tenor / 12)
Total Bayar = Jumlah + Total Bunga
Angsuran/Bulan = Total Bayar / Tenor

Contoh:
- Jumlah: Rp 5,000,000
- Tenor: 12 bulan
- Total Bunga = 5,000,000 × 12% × (12/12) = Rp 600,000
- Total Bayar = 5,000,000 + 600,000 = Rp 5,600,000
- Angsuran = 5,600,000 / 12 = Rp 466,667
```

## 🎨 UI Features

- ✅ Modern gradient backgrounds dengan parallax effect
- ✅ Responsive design (mobile-friendly)
- ✅ Cards layout untuk semua halaman
- ✅ Status badges dengan emoji dan color coding
- ✅ Progress bar untuk pembayaran
- ✅ Empty states dengan call-to-action
- ✅ Form validation client & server side
- ✅ Flash messages untuk feedback user
- ✅ Tailwind CSS styling

## 📂 Project Structure

```
aplikasi-pinjaman/
├── app.py                          # Main Flask app
├── seed_data.py                    # Test data seeder
├── FITUR_DOCUMENTATION.md          # Detailed feature docs
├── CHECKLIST.md                    # Implementation checklist
├── README.md                       # This file
├── templates/
│   ├── base.html                   # Base layout
│   ├── base_app.html               # App layout
│   ├── base_auth.html              # Auth layout
│   ├── login.html                  # Login page
│   ├── register.html               # Register page
│   ├── index.html                  # Dashboard
│   ├── pengajuan.html              # Loan application
│   ├── pinjaman_saya.html          # My loans ⭐
│   ├── pengambilan_pinjaman.html   # Disbursement request ⭐
│   ├── bayar_pinjaman.html         # Payment page ⭐
│   ├── daftar_pinjaman.html        # All loans (admin)
│   ├── admin_dashboard.html        # Admin dashboard ⭐
│   ├── admin_pembayaran.html       # Payment verification
│   └── admin_users.html            # User management
├── static/
│   ├── style.css                   # Styling
│   └── uploads/                    # Payment proof storage
└── .gitignore
```

## 🔐 Security Features

- ✅ Password hashing (Werkzeug)
- ✅ Session management
- ✅ Login required decorators
- ✅ Role-based access control (admin/user)
- ✅ File upload validation (extension, size)
- ✅ CSRF protection via Flask
- ✅ SQL injection prevention (SQLAlchemy ORM)

## 🚀 Deployment Notes

Sebelum production:

1. Ganti `secret_key` dengan random string yang aman
2. Set `debug=False` di `app.py`
3. Gunakan production database (bukan in-memory)
4. Setup HTTPS/SSL
5. Configure file upload path
6. Setup email notifications (optional)
7. Monitor log files
8. Regular database backup

## 🐛 Troubleshooting

### Error: ModuleNotFoundError
```bash
pip install flask flask-sqlalchemy mysqlconnector-python
```

### Error: Database connection
```bash
# Pastikan MySQL running di Laragon
# Pastikan database "koperasi" sudah dibuat
```

### Error: 'now' is undefined
✅ **FIXED** - context_processor sudah ditambahkan

### File upload tidak bekerja
```bash
# Buat folder: static/uploads/
mkdir static/uploads
```

## 📞 Support

Jika ada pertanyaan atau bug report, silakan hubungi tim development.

---

**Version**: 1.0
**Last Updated**: December 16, 2025
**Status**: ✅ Production Ready

**⭐ Features Baru:**
- Pinjaman Saya dengan status & action buttons
- Pengambilan Pinjaman (Disbursement Request)
- Pembayaran Cicilan dengan verification
- Admin Dashboard
- Modern UI dengan cards layout
- Progress bar pembayaran
- Riwayat pembayaran lengkap
