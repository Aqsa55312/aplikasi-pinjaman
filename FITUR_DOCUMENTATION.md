# 📋 Dokumentasi Fitur Aplikasi Koperasi Simpan Pinjam

## ✅ Status Implementasi Fitur

### 1. **Status Pinjaman** ✅
Status pinjaman sudah terimplementasi dengan status-status berikut:
- **🟡 Pending**: Pinjaman baru, menunggu persetujuan admin
- **✅ Approved**: Pinjaman disetujui admin, siap untuk pengambilan
- **❌ Rejected**: Pinjaman ditolak admin
- **📤 Disbursement Requested**: User mengajukan pengambilan/pencairan
- **💰 Disbursed**: Pinjaman sudah dicairkan, pembayaran bisa dilakukan
- **🏁 Lunas**: Semua cicilan sudah lunas

**Lokasi kode**: `models.LoanStatus` di `app.py`
**Template**: Ditampilkan di `pinjaman_saya.html`, `pengambilan_pinjaman.html`, `bayar_pinjaman.html`

---

### 2. **Tindakan Lanjut untuk User** ✅

#### A. Pengambilan Pinjaman (Disbursement)
Jika status pinjaman = **"approved"**, user dapat:
- Mengakses halaman: `/pengambilan_pinjaman`
- Mengklik tombol **"📤 Ajukan Pengambilan Sekarang"**
- Status berubah menjadi **"disbursement_requested"** (menunggu verifikasi admin)

**Route**: `/pengambilan_pinjaman` (GET)
**Action**: `/pinjaman/<id>/ajukan-pengambilan` (POST)

#### B. Pembayaran Cicilan
Jika status pinjaman = **"disbursed"** atau **"lunas"**, user dapat:
- Mengakses halaman: `/pinjaman/<id>/bayar`
- Memasukkan jumlah pembayaran
- Memilih metode: Transfer, E-Wallet, atau Cash
- Upload bukti pembayaran (opsional, format PNG/JPG/PDF)
- Status pembayaran = **"pending"** (menunggu verifikasi admin)

**Route**: `/pinjaman/<id>/bayar` (GET/POST)
**Fitur**: Progress bar pembayaran, riwayat pembayaran

---

### 3. **Fitur Pembayaran** ✅

#### A. Input Pembayaran
User dapat membayar cicilan dengan:
- Jumlah pembayaran (validasi max = sisa)
- Metode pembayaran (transfer, e-wallet, cash)
- Bukti pembayaran (file upload)

#### B. Verifikasi Pembayaran (Admin)
Admin dapat:
- Melihat daftar pembayaran pending: `/admin/pembayaran`
- Verify pembayaran → status = **"verified"**
- Reject pembayaran → status = **"rejected"**
- Sistem otomatis cek: jika total verified ≥ total bayar → status pinjaman = **"lunas"**

**Template**: `bayar_pinjaman.html`, `admin_pembayaran.html`

---

### 4. **Fitur Pengambilan Pinjaman** ✅

#### A. User Side
- Halaman: `/pengambilan_pinjaman`
- Status pinjaman harus = **"approved"**
- Klik tombol "Ajukan Pengambilan" → status berubah menjadi **"disbursement_requested"**
- Tunggu admin verifikasi

#### B. Admin Side
- Kelola pinjaman: `/daftar_pinjaman`
- Tombol: **"Disburse"** → status = **"disbursed"**
- Pembayaran baru bisa diterima setelah status = **"disbursed"**

**Route**: `/pinjaman/<id>/ajukan-pengambilan` (POST)
**Admin Action**: `/admin/pinjaman/<id>/disburse` (POST)

---

### 5. **Detail Angsuran** ✅

Semua detail angsuran sudah terhitung dan ditampilkan:
- ✅ **Jumlah Pinjaman**: Input user saat pengajuan
- ✅ **Suku Bunga**: 12% per tahun (fixed)
- ✅ **Total Bunga**: `jumlah * bunga% * (tenor/12)`
- ✅ **Total Bayar**: `jumlah + total bunga`
- ✅ **Cicilan/Bulan**: `total bayar / tenor`

**Perhitungan**: Fungsi `calculate_loan_details()` di `app.py` (tidak ada, tapi logika sudah di pengajuan)
**Tampilan**: 
- `pengajuan.html` - preview
- `pinjaman_saya.html` - detail pinjaman
- `bayar_pinjaman.html` - detail lengkap + progress

---

## 📱 User Workflow

```
1. LOGIN / REGISTER
   ↓
2. PENGAJUAN PINJAMAN (Status: pending)
   ├─ Fill: Jumlah, Tenor, Keperluan
   ├─ System: Hitung bunga & angsuran
   └─ Submit → Status = "pending"
   ↓
3. ADMIN REVIEW
   ├─ Approve → Status = "approved"
   ├─ Reject → Status = "rejected"
   └─ Approved ✓
   ↓
4. PENGAMBILAN PINJAMAN (Status: approved → disbursement_requested)
   ├─ Click "Ajukan Pengambilan"
   ├─ Status = "disbursement_requested"
   └─ Wait for admin
   ↓
5. ADMIN DISBURSE
   ├─ Click "Disburse"
   └─ Status = "disbursed" ✓
   ↓
6. PEMBAYARAN CICILAN (Status: disbursed → verified/rejected/lunas)
   ├─ Input pembayaran
   ├─ Upload bukti
   ├─ Status = "pending"
   └─ Admin verify
   ↓
7. ADMIN VERIFY PEMBAYARAN
   ├─ Check pembayaran
   ├─ Verify → Status = "verified"
   ├─ System check: if total ≥ total_bayar → Lunas
   └─ Status = "lunas" ✓
```

---

## 🔗 Menu Navigation

### User Menu
- 🏠 Dashboard
- 📝 Pengajuan Pinjaman
- 📋 Pinjaman Saya (NEW: dengan status + aksi)
- 📤 Pengambilan Pinjaman (NEW)
- 💳 Pembayaran Cicilan (Accessible dari Pinjaman Saya)

### Admin Menu
- 🏠 Dashboard (NEW)
- 📋 Kelola Pinjaman (Approve/Reject/Disburse)
- 💰 Verifikasi Pembayaran
- 👥 Kelola User

---

## 🎨 Template yang Diupdate

1. **pinjaman_saya.html** ⭐
   - Cards layout dengan status badge
   - Action buttons (Ajukan Pengambilan, Bayar Cicilan, Hapus)
   - Grid detail pinjaman
   - Empty state dengan link ke pengajuan

2. **pengambilan_pinjaman.html** ⭐
   - Cards layout
   - Status filter untuk aksi
   - Detail pinjaman
   - Button "Ajukan Pengambilan Sekarang"

3. **bayar_pinjaman.html** ⭐
   - Info pinjaman + status
   - Detail angsuran (jumlah, bunga, total)
   - Progress bar pembayaran (visual%)
   - Form pembayaran (jumlah, metode, bukti)
   - Riwayat pembayaran (tabel)
   - Status badges untuk pembayaran

4. **admin_dashboard.html** (NEW)
   - Stat cards (total pinjaman, pending, approved, pembayaran pending)
   - Quick action buttons
   - System info

---

## 🔧 Technical Details

### Database Models
- `User` - Pengguna (admin/user)
- `Pinjaman` - Pinjaman
- `LoanStatus` - Status pinjaman
- `LoanPayment` - Pembayaran cicilan

### Helper Functions
- `login_required()` - Decorator untuk login
- `admin_required()` - Decorator untuk admin
- `user_required()` - Decorator untuk user
- `current_user()` - Get user dari session
- `ensure_loan_status()` - Ensure pinjaman punya status

### Validasi
- ✅ Jumlah pinjaman > 0
- ✅ Tenor 1-36 bulan (bisa disesuaikan)
- ✅ Pembayaran > 0 dan ≤ sisa
- ✅ User hanya lihat pinjaman milik sendiri
- ✅ File upload validasi (png/jpg/jpeg/pdf, max 5MB)

---

## 🐛 Catatan Penting

1. **Bunga Fixed 12% per tahun** - Bisa disesuaikan di route `/pengajuan`
2. **Pembayaran bisa parsial** - User bisa bayar lebih kecil dari sisa
3. **Auto-check lunas** - Saat admin verify pembayaran
4. **File upload** - Disimpan di `static/uploads/`
5. **Session-based** - Gunakan database session untuk production

---

## 📊 Status Pinjaman Flow

```
┌─────────────────┐
│     PENDING     │ ← Pinjaman baru
└────────┬────────┘
         │ Admin approve/reject
    ┌────▼────┬──────────┐
    │          │          │
    v          v          v
┌────────┐ ┌──────┐ ┌──────────┐
│APPROVED│ │REJECT│ (REJECTED)
└────┬───┘ └──────┘
     │ User ajukan pengambilan
     v
┌─────────────────────────────┐
│ DISBURSEMENT_REQUESTED      │
└────────┬────────────────────┘
         │ Admin disburse
         v
   ┌──────────────┐
   │  DISBURSED   │
   └────┬─────────┘
        │ User bayar cicilan
        │ (multiple times, status=pending/verified/rejected)
        │ System auto-check: if total ≥ total_bayar
        v
    ┌────────┐
    │ LUNAS  │ (Final)
    └────────┘
```

---

## ✨ Next Improvements (Optional)

1. Generate PDF struk pinjaman + bukti pembayaran
2. SMS/Email notification untuk pembayaran
3. Laporan keuangan (admin)
4. Auto reminder pembayaran
5. Setting bunga flexible per pinjaman
6. Support multiple currency

---

**Version**: 1.0
**Last Updated**: December 16, 2025
**Status**: ✅ All Major Features Implemented
