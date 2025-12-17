# 🚀 QUICK START - FITUR ACC USER

## 5 Menit Setup

### 1️⃣ Initialize Database (1 min)
```bash
cd "c:\laragon\www\aplikasi pinjaman"
python init_db.py
```

Expected output:
```
✅ DATABASE BERHASIL DIINISIALISASI!
✅ Admin: admin (verified=True)
✅ User: budi (verified=True)
⏳ User: siti (verified=False)
⏳ User: ahmad (verified=False)
```

---

### 2️⃣ Run Server (1 min)
```bash
python app.py
```

Expected output:
```
WARNING: This is a development server. Do not use it in production.
Running on http://127.0.0.1:5000
```

---

### 3️⃣ Test di Browser (3 min)

#### Login sebagai Admin
```
URL: http://127.0.0.1:5000/login
Username: admin
Password: admin123
```

#### Akses Kelola User
```
Klik: 🛡️ Kelola User (di sidebar)
```

#### Test Approve User
```
Lihat: Tabel dengan 4 user
─────────────────────────────
siti (⏳ Pending)
  └─ Klik: ✅ Acc
  └─ Confirm: OK
  └─ Result: Status → ✅ Verified ✅
```

#### Test Reject User
```
siti (✅ Verified)
  └─ Klik: ⛔ Tolak
  └─ Confirm: OK
  └─ Result: Status → ⏳ Pending ✅
```

---

## 📊 Tabel User

| ID | Nama | Username | Status | Role | Action |
|----|------|----------|--------|------|--------|
| 1 | Administrator | admin | ✅ Verified | 👑 Admin | (Akun Anda) |
| 2 | Budi Santoso | budi | ✅ Verified | 👤 User | ⛔ Tolak, Make Admin, 🗑️ Hapus |
| 3 | Siti Nurhaliza | siti | ⏳ Pending | 👤 User | ✅ Acc, Make Admin, 🗑️ Hapus |
| 4 | Ahmad Wijaya | ahmad | ⏳ Pending | 👤 User | ✅ Acc, Make Admin, 🗑️ Hapus |

---

## 🔘 Tombol Penjelasan

| Tombol | Warna | Status | Fungsi |
|--------|-------|--------|--------|
| **✅ Acc** | Hijau | Pending | Approve user |
| **⛔ Tolak** | Kuning | Verified | Reject user |
| **Make Admin** | Merah | User | Naik ke Admin |
| **Make User** | Biru | Admin | Turun ke User |
| **🗑️ Hapus** | Merah Gelap | Any | Delete user |
| **(Akun Anda)** | Abu | Own | Disabled (self) |

---

## 🎯 Workflow

```
Admin Dashboard
    ↓
Kelola User
    ↓
Lihat tabel user dengan Status
    ↓
Klik "✅ Acc" untuk approve
    ↓
Confirm dialog
    ↓
Status berubah ✅ Verified
    ↓
Flash message: User berhasil disetujui
```

---

## ✨ Key Features

✅ **Status Tracking**
- ✅ Verified (hijau)
- ⏳ Pending (kuning)

✅ **User Management**
- Approve user baru
- Reject user
- Change role (Admin ↔ User)
- Delete user

✅ **Security**
- Self-protection (tidak bisa approve diri sendiri)
- Confirmation dialogs
- Admin-only routes

✅ **User Experience**
- Clear badges
- Intuitive buttons
- Flash messages
- Responsive design

---

## 📁 Files

**Backend:**
- `app.py` - Routes & Database model

**Frontend:**
- `templates/admin_users.html` - UI

**Database:**
- `init_db.py` - Setup script

**Documentation:**
- `ACC_USER_PANDUAN.md` - User guide (detail)
- `FITUR_ACC_USER.md` - Technical docs
- `IMPLEMENTASI_ACC_USER_SUMMARY.md` - Implementation summary

---

## 🆘 Troubleshooting

### Error: "admin_users.html not found"
→ Semua file sudah ada, refresh halaman

### Error: "is_verified not found"
→ Jalankan: `python init_db.py`

### Tombol tidak muncul
→ Refresh cache: Ctrl+Shift+Del, lalu F5

### Status tidak berubah
→ Refresh: F5, atau restart server

---

## 🎓 Learning Path

1. **User Level** → Baca: `ACC_USER_PANDUAN.md`
2. **Developer Level** → Baca: `FITUR_ACC_USER.md`
3. **Quick Test** → Ikuti: Quick Start ini

---

## 📝 Test Accounts

```
Username: admin
Password: admin123
Role: Admin
Status: ✅ Verified

---

Username: budi
Password: budi123
Role: User
Status: ✅ Verified

---

Username: siti
Password: siti123
Role: User
Status: ⏳ Pending (Ready for testing!)

---

Username: ahmad
Password: ahmad123
Role: User
Status: ⏳ Pending (Ready for testing!)
```

---

## ✅ Success Criteria

Jika semua ini terpenuhi, setup berhasil:

- [x] `python init_db.py` runs successfully
- [x] `python app.py` runs successfully
- [x] Login berhasil dengan admin/admin123
- [x] Menu "Kelola User" muncul di sidebar
- [x] Tabel menampilkan 4 user dengan Status column
- [x] Badges muncul benar (✅ Verified, ⏳ Pending)
- [x] Click "✅ Acc" untuk siti → status berubah
- [x] Click "⛔ Tolak" untuk siti → status kembali
- [x] "(Akun Anda)" muncul untuk admin (disabled)
- [x] Confirmation dialog muncul sebelum action
- [x] Flash message berhasil ditampilkan

---

**🎉 Setup Complete!**

Anda sudah siap menggunakan fitur ACC User!

Untuk detail lebih, baca file dokumentasi lengkapnya.
