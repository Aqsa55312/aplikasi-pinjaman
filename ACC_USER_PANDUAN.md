# 🎯 PANDUAN LENGKAP: FITUR ACC USER (APPROVE USER)

## 📌 Apa itu Fitur ACC User?

Fitur **ACC User** (Approve User) adalah fitur admin yang memungkinkan administrator untuk:
- ✅ **Menyetujui (Approve)** akun user baru yang mendaftar
- ⛔ **Menolak (Reject)** akun user
- 📊 **Melihat status verifikasi** setiap user
- 🔄 **Mengubah status** user kapan saja

---

## 🚀 Mulai Cepat

### 1. Setup Database

Buka terminal di folder aplikasi dan jalankan:

```bash
python init_db.py
```

Output akan menampilkan:
```
✅ DATABASE BERHASIL DIINISIALISASI!

TEST ACCOUNTS:
- admin / admin123
- budi / budi123 (Verified ✅)
- siti / siti123 (Pending ⏳)
- ahmad / ahmad123 (Pending ⏳)
```

### 2. Jalankan Server

```bash
python app.py
```

Buka: http://127.0.0.1:5000

### 3. Login sebagai Admin

```
Username: admin
Password: admin123
```

---

## 👥 Dashboard "Kelola User"

### Akses Menu

1. Login sebagai admin
2. Di sidebar kiri, klik **"🛡️ Kelola User"**
3. Anda akan melihat tabel semua user

---

## 📊 Tabel User - Kolom Penjelasan

| Kolom | Deskripsi |
|-------|-----------|
| **ID** | Nomor urut user di database |
| **Nama** | Nama lengkap user |
| **Username** | Username untuk login |
| **Email** | Email user |
| **Telepon** | No. telepon user |
| **Status** | ✅ Verified atau ⏳ Pending |
| **Role** | 👑 Admin atau 👤 User |
| **Action** | Tombol-tombol untuk manage user |

---

## 🎨 Status Badge

### ✅ Verified (Hijau)
```
Status: ✅ Verified
Artinya: User sudah diapprove, bisa akses semua fitur
Tombol: ⛔ Tolak (untuk reject kembali)
```

### ⏳ Pending (Kuning)
```
Status: ⏳ Pending
Artinya: User baru, menunggu approval dari admin
Tombol: ✅ Acc (untuk approve)
```

---

## 🔘 Tombol Action

### 1. **✅ Acc** (Approve User)

**Kapan muncul?**
- Hanya untuk user dengan status ⏳ Pending
- User bukan akun Anda sendiri

**Apa yang dilakukan?**
- Ubah status user menjadi ✅ Verified
- Catat siapa admin yang approve + tanggalnya
- User sekarang bisa akses semua fitur

**Cara click:**
1. Klik tombol **✅ Acc** pada baris user
2. Akan muncul confirmation: "Approve user [username]?"
3. Klik **OK** untuk confirm
4. Status berubah menjadi ✅ Verified

---

### 2. **⛔ Tolak** (Reject User)

**Kapan muncul?**
- Hanya untuk user dengan status ✅ Verified
- User bukan akun Anda sendiri

**Apa yang dilakukan?**
- Ubah status user kembali ke ⏳ Pending
- Clear data verification (siapa approve, kapan)
- User tidak bisa akses fitur (hanya view-only)

**Cara click:**
1. Klik tombol **⛔ Tolak** pada baris user
2. Confirmation: "Tolak user [username]?"
3. Klik **OK** untuk confirm
4. Status kembali ke ⏳ Pending

---

### 3. **Make Admin** (Ubah ke Admin)

**Kapan muncul?**
- Hanya untuk user dengan role 👤 User
- User bukan akun Anda sendiri

**Apa yang dilakukan?**
- Ubah role user menjadi 👑 Admin
- Admin bisa akses menu admin dan kelola user lain

**Cara click:**
1. Klik tombol **Make Admin** pada baris user
2. Confirmation: "Ubah role menjadi Admin?"
3. Klik **OK** untuk confirm
4. Role berubah menjadi 👑 Admin

---

### 4. **Make User** (Turunkan ke User)

**Kapan muncul?**
- Hanya untuk user dengan role 👑 Admin
- User bukan akun Anda sendiri

**Apa yang dilakukan?**
- Turunkan role admin menjadi 👤 User biasa
- User tidak lagi bisa akses menu admin

**Cara click:**
1. Klik tombol **Make User** pada baris user
2. Confirmation: "Turunkan role menjadi User?"
3. Klik **OK** untuk confirm
4. Role berubah menjadi 👤 User

---

### 5. **🗑️ Hapus** (Delete User)

**Kapan muncul?**
- Untuk semua user
- User bukan akun Anda sendiri

**Apa yang dilakukan?**
- Hapus user dari database (tidak bisa dibatalkan!)
- Hapus semua pinjaman user juga

**Cara click:**
1. Klik tombol **🗑️ Hapus** pada baris user
2. Confirmation: "Hapus user ini? Tidak bisa dibatalkan!"
3. Klik **OK** untuk confirm
4. User dihapus dari sistem

---

### 6. **(Akun Anda)** (Gray Button)

**Kapan muncul?**
- Untuk user yang sedang login (Anda sendiri)

**Artinya?**
- Anda tidak bisa approve/reject akun Anda sendiri
- Proteksi untuk mencegah kesalahan

**Bagaimana?**
- Tombol tidak bisa diklik (disabled)
- Hanya untuk informasi bahwa ini akun Anda

---

## 📋 Contoh Workflow

### Scenario: Admin Approve 2 User Baru

**Step 1: Login**
```
Username: admin
Password: admin123
```

**Step 2: Buka Kelola User**
- Sidebar → 🛡️ Kelola User

**Step 3: Lihat Daftar User**
```
ID | Nama            | Username | Email              | Status      | Action
1  | Administrator   | admin    | admin@...          | ✅ Verified | (Akun Anda)
2  | Budi Santoso    | budi     | budi@...           | ✅ Verified | ⛔ Tolak, ...
3  | Siti Nurhaliza  | siti     | siti@...           | ⏳ Pending  | ✅ Acc, ...
4  | Ahmad Wijaya    | ahmad    | ahmad@...          | ⏳ Pending  | ✅ Acc, ...
```

**Step 4: Approve Siti**
- Klik **✅ Acc** di baris Siti
- Confirm: "Approve user siti?" → OK
- Status berubah: ⏳ Pending → ✅ Verified
- Tombol berubah: ✅ Acc → ⛔ Tolak

**Step 5: Approve Ahmad**
- Klik **✅ Acc** di baris Ahmad
- Confirm: "Approve user ahmad?" → OK
- Status berubah: ⏳ Pending → ✅ Verified
- Tombol berubah: ✅ Acc → ⛔ Tolak

**Step 6: Hasil**
```
✅ Siti dan Ahmad sekarang bisa login dan akses semua fitur
✅ Mereka bisa buat pinjaman, bayar, dll
✅ Status approval tercatat di database (siapa approve, kapan)
```

---

## 🔒 Proteksi Keamanan

### 1. Self-Protection
❌ Anda tidak bisa:
- Approve/Reject akun Anda sendiri
- Turunkan role Anda sendiri
- Hapus akun Anda sendiri

✅ Ini mencegah: Akun admin kelihatan tidak valid/dihapus

---

### 2. Confirmation Dialog
Setiap action meminta konfirmasi:
```
Approve user ahmad?
[Cancel] [OK]
```

✅ Ini mencegah: Klik tombol salah/accidental

---

### 3. Admin-Only Routes
Hanya admin yang bisa akses:
- `/admin/approve-user/<id>`
- `/admin/reject-user/<id>`
- `/admin/delete-user/<id>`
- Decorator: `@admin_required`

✅ Ini mencegah: User biasa akses fitur admin

---

## 💾 Database Schema

### Kolom Baru di Tabel `users`

```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  nama VARCHAR(100),
  email VARCHAR(120) UNIQUE,
  telepon VARCHAR(30),
  username VARCHAR(50) UNIQUE,
  password_hash VARCHAR(255),
  role VARCHAR(10) DEFAULT 'user',
  
  -- Fitur ACC User:
  is_verified BOOLEAN DEFAULT FALSE,      -- Status approval
  verified_by INT FOREIGN KEY,             -- ID admin yang approve
  verified_at DATETIME                     -- Tanggal approval
);
```

### Contoh Data

```
User: siti
├─ is_verified: FALSE (belum diapprove)
├─ verified_by: NULL
└─ verified_at: NULL

User: budi (setelah diapprove)
├─ is_verified: TRUE (sudah diapprove)
├─ verified_by: 1 (Admin dengan ID 1)
└─ verified_at: 2025-12-17 10:30:00
```

---

## 🧪 Testing Checklist

- [ ] Setup database dengan `python init_db.py`
- [ ] Server jalan dengan `python app.py`
- [ ] Login sebagai admin berhasil
- [ ] Menu "Kelola User" muncul di sidebar
- [ ] Tabel user menampilkan 4 user (1 admin + 3 user)
- [ ] Status column menunjukkan badges yang benar
- [ ] Click "✅ Acc" untuk siti → status berubah ke ✅ Verified
- [ ] Click "⛔ Tolak" untuk siti → status kembali ke ⏳ Pending
- [ ] Tombol "(Akun Anda)" muncul untuk akun admin (tidak bisa click)
- [ ] Confirm dialog muncul sebelum action
- [ ] Flash message muncul setelah action (hijau = success)
- [ ] Role change buttons berfungsi (Make Admin, Make User)
- [ ] Delete button berfungsi (dengan warning)

---

## ❓ FAQ

### Q1: User baru bisa login meski belum diapprove?
**A:** Ya, tapi dia tidak bisa akses fitur-fitur tertentu (future implementation). Saat ini bisa, nanti bisa dikasih restriction.

### Q2: Berapa lama perlu tunggu approval?
**A:** Tergantung admin. Bisa langsung atau besoknya. Tidak ada time limit.

### Q3: Bagaimana cara buat user baru untuk test?
**A:** User baru mendaftar sendiri via halaman Register. Statusnya otomatis ⏳ Pending.

### Q4: Bisa batch approve (banyak sekaligus)?
**A:** Saat ini belum ada. Harus satu-satu. Bisa ditambah di future.

### Q5: Apakah ada email notification?
**A:** Saat ini belum. Hanya ada flash message di dashboard. Bisa ditambah email later.

### Q6: Bagaimana jika lupa siapa yang approve?
**A:** Lihat database field `verified_by` (ID admin) dan `verified_at` (tanggalnya).

---

## 📞 Troubleshooting

### Problem: Tombol Acc tidak muncul

**Solusi:**
1. Check apakah user sudah login sebagai admin
2. Refresh halaman (Ctrl+F5)
3. Cek database apakah field `is_verified` ada:
   ```sql
   DESCRIBE users;
   ```
4. Jika tidak ada, jalankan `python init_db.py`

---

### Problem: Error "admin_approve_user not found"

**Solusi:**
1. Restart server (`python app.py`)
2. Check apakah routes di app.py sudah disave
3. Cek error di terminal

---

### Problem: Tombol action tidak responsive

**Solusi:**
1. Clear browser cache (Ctrl+Shift+Del)
2. Restart browser
3. Cek console (F12) untuk JavaScript errors

---

### Problem: Status tidak berubah setelah click Acc

**Solusi:**
1. Refresh halaman (F5)
2. Check database:
   ```sql
   SELECT id, username, is_verified FROM users;
   ```
3. Jika masih pending, cek error di server terminal

---

## 📚 File Reference

### Backend
- `app.py`
  - Model: `class User` dengan field `is_verified`, `verified_by`, `verified_at`
  - Routes: `admin_approve_user()`, `admin_reject_user()`

### Frontend
- `templates/admin_users.html`
  - Status column dengan badges
  - Action buttons dengan approval logic

### Database
- `init_db.py` - Script untuk setup & seed data

### Documentation
- `FITUR_ACC_USER.md` - Detail teknis
- `ACC_USER_PANDUAN.md` - Panduan ini (user-friendly)

---

## 🎓 Kesimpulan

Fitur **ACC User** memberikan kontrol penuh kepada admin untuk:
1. ✅ **Approve** user baru
2. ⛔ **Reject** user yang tidak valid
3. 👑 **Manage** role dan permissions
4. 🗑️ **Delete** user jika perlu

Semuanya dengan **proteksi keamanan** dan **user-friendly interface**!

---

**Selamat! Anda sudah siap menggunakan fitur ACC User! 🎉**

Untuk detail teknis, baca: [FITUR_ACC_USER.md](./FITUR_ACC_USER.md)
