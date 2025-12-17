# 🚀 QUICK START GUIDE

## ⚡ 5 Menit Setup

### Step 1: Install Dependencies
```bash
pip install flask flask-sqlalchemy mysqlconnector-python
```

### Step 2: Setup Database
Buka MySQL Laragon dan jalankan:
```sql
CREATE DATABASE koperasi;
```

### Step 3: Seed Test Data
```bash
python seed_data.py
```

Output:
```
✅ DATABASE SEED COMPLETED!

📊 Test Accounts:
- admin / admin123
- budi / budi123
- siti / siti123
```

### Step 4: Run Application
```bash
python app.py
```

Output:
```
 * Running on http://127.0.0.1:5000/
```

### Step 5: Open Browser
```
http://127.0.0.1:5000/
```

---

## 📋 Test Scenarios (15 Menit)

### Scenario 1: Admin Approve Loan ✅

**Login sebagai: admin / admin123**

1. Klik menu: **📋 Daftar Pinjaman**
2. Cari pinjaman dengan status **⏳ Pending**
3. Klik tombol **Approve**
4. ✅ Status berubah menjadi **✅ Approved**

---

### Scenario 2: User Request Disbursement ✅

**Login sebagai: budi / budi123**

1. Klik menu: **📋 Pinjaman Saya**
2. Lihat pinjaman dengan status **✅ Approved**
3. Klik tombol **📤 Ajukan Pengambilan**
4. ✅ Status berubah menjadi **📤 Disbursement Requested**

---

### Scenario 3: Admin Disburse Loan ✅

**Login sebagai: admin / admin123**

1. Klik menu: **📋 Daftar Pinjaman**
2. Cari pinjaman dengan status **📤 Disbursement Requested**
3. Klik tombol **Disburse**
4. ✅ Status berubah menjadi **💰 Disbursed**

---

### Scenario 4: User Pay Installment ✅

**Login sebagai: budi / budi123**

1. Klik menu: **📋 Pinjaman Saya**
2. Lihat pinjaman dengan status **💰 Disbursed**
3. Klik tombol **💳 Bayar Cicilan**
4. Input:
   - Jumlah: **500000** (Rp 500,000)
   - Metode: **Transfer**
   - Bukti: **(optional)**
5. Klik **✅ Kirim Pembayaran**
6. ✅ Pembayaran status = **⏳ Pending**
7. Progress bar naik: **15%** (500k dari 3.18jt)

---

### Scenario 5: Admin Verify Payment ✅

**Login sebagai: admin / admin123**

1. Klik menu: **💰 Verifikasi Pembayaran**
2. Lihat pembayaran dengan status **⏳ Pending**
3. Klik tombol **Verify**
4. ✅ Pembayaran status = **✅ Verified**
5. Cek: Jika total verified ≥ total bayar → Pinjaman status = **🏁 Lunas**

---

## 🎯 Fitur yang Bisa Ditest

| Fitur | User | Admin | Path |
|-------|------|-------|------|
| Login/Register | ✅ | ✅ | `/login` |
| Dashboard | ✅ | ✅ | `/` |
| Pengajuan Pinjaman | ✅ | - | `/pengajuan` |
| Pinjaman Saya | ✅ | - | `/pinjaman_saya` |
| Pengambilan Pinjaman | ✅ | - | `/pengambilan_pinjaman` |
| Bayar Cicilan | ✅ | - | `/pinjaman/<id>/bayar` |
| Kelola Pinjaman | - | ✅ | `/daftar_pinjaman` |
| Verifikasi Pembayaran | - | ✅ | `/admin/pembayaran` |
| Admin Dashboard | - | ✅ | `/admin/dashboard` |
| Kelola User | - | ✅ | `/admin/users` |

---

## 🔍 Key Features to Check

### ✅ Status Pinjaman
```
Halaman: Pinjaman Saya (/pinjaman_saya)
Lihat: Status badge dengan warna berbeda
- ⏳ Pending (yellow)
- ✅ Approved (blue)
- 📤 Disbursement Requested (purple)
- 💰 Disbursed (green)
- 🏁 Lunas (indigo)
```

### ✅ Detail Angsuran
```
Halaman: Pinjaman Saya
Lihat: Grid dengan:
- Jumlah Pinjaman: Rp 5,000,000
- Tenor: 12 Bulan
- Total Bayar: Rp 5,600,000
- Cicilan/Bulan: Rp 466,667
```

### ✅ Progress Pembayaran
```
Halaman: Bayar Cicilan (/pinjaman/<id>/bayar)
Lihat: 
- Total Sudah Dibayar: Rp 500,000
- Sisa Pembayaran: Rp 2,680,000
- Progress Bar: [████░░░░░░░░░░░░░] 15%
```

### ✅ Admin Dashboard
```
Halaman: Admin Dashboard (/admin/dashboard)
Lihat:
- Total Pinjaman: 3
- Menunggu Persetujuan: 1
- Disetujui: 1
- Pembayaran Menunggu: 1
```

---

## 💾 Database Check

Untuk verify data di database, jalankan di MySQL:

```sql
-- Check users
SELECT * FROM users;

-- Check loans
SELECT id, peminjam, jumlah, tenor, total_bayar FROM pinjaman;

-- Check loan status
SELECT p.id, p.peminjam, ls.status FROM pinjaman p 
LEFT JOIN loan_status ls ON p.id = ls.pinjaman_id;

-- Check payments
SELECT id, pinjaman_id, jumlah, status FROM loan_payments;
```

---

## 🛑 Common Issues

### Issue: "Cannot connect to database"
**Solution:**
```bash
# 1. Cek MySQL running di Laragon
# 2. Jalankan di MySQL:
CREATE DATABASE koperasi;

# 3. Jalankan app lagi
python app.py
```

### Issue: "Static files not loading"
**Solution:**
```bash
# Pastikan folder ada:
# - static/style.css
# - static/uploads/ (buat jika belum ada)
mkdir static/uploads
```

### Issue: "Upload file error"
**Solution:**
```bash
# 1. Pastikan folder sudah ada
mkdir static/uploads

# 2. Pastikan file format: PNG, JPG, PDF (max 5MB)

# 3. Pastikan user punya write permission
```

### Issue: "Jinja2 UndefinedError"
**Solution:**
✅ Sudah fixed - context_processor ada di app.py

---

## 📞 Next Steps

### Untuk Testing
1. ✅ Follow scenarios di atas
2. ✅ Check database values
3. ✅ Test file upload
4. ✅ Test error handling

### Untuk Development
1. Buat admin user baru
2. Buat user accounts baru
3. Test semua workflow
4. Check validation messages
5. Verify calculations

### Untuk Production
1. Change `secret_key` di app.py
2. Set `debug=False`
3. Use production database
4. Setup backup system
5. Monitor logs

---

## 📚 Documentation Files

- **README.md** - Full documentation
- **FITUR_DOCUMENTATION.md** - Detailed feature specs
- **CHECKLIST.md** - Implementation checklist
- **seed_data.py** - Test data script

---

**🎉 Selamat! Setup sudah selesai.**

Silakan test aplikasi dan report jika ada issues.

**Status**: ✅ Ready to Test
