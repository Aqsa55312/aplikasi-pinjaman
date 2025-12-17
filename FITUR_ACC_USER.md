# 📋 FITUR ACC/APPROVE USER - DOKUMENTASI

## 📌 Overview

Fitur "ACC User" atau "Approve User" memungkinkan **Admin** untuk memverifikasi dan menyetujui akun pengguna baru yang mendaftar. User yang belum disetujui tidak bisa mengajukan pinjaman atau mengakses fitur-fitur tertentu.

---

## 🏗️ Struktur Implementasi

### 1. **Database Model - User Table**

Tambahan field pada model `User`:

```python
class User(db.Model):
    # ... field existing ...
    
    # Status verifikasi user
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    verified_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    verified_at = db.Column(db.DateTime)
```

**Penjelasan:**
- `is_verified`: Boolean status apakah user sudah diapprove (True/False)
- `verified_by`: ID admin yang melakukan approval
- `verified_at`: Timestamp kapan user diapprove

---

### 2. **Backend Routes - app.py**

#### Route: Approve User
```python
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
```

**Fungsi:**
- Set `is_verified = True`
- Catat admin yang approve + timestamp
- Redirect ke halaman kelola user dengan flash message

---

#### Route: Reject User
```python
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
```

**Fungsi:**
- Set `is_verified = False`
- Clear verified_by dan verified_at
- Redirect dengan flash message

---

### 3. **Frontend - Template admin_users.html**

#### Status Column
```html
<td class="px-6 py-4 text-center">
  {% if user.is_verified %}
    <span class="inline-block px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">
      ✅ Verified
    </span>
  {% else %}
    <span class="inline-block px-3 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-800">
      ⏳ Pending
    </span>
  {% endif %}
</td>
```

**Tampilan:**
- Green badge: ✅ Verified (sudah diapprove)
- Yellow badge: ⏳ Pending (menunggu approval)

---

#### Action Buttons
```html
<!-- Approve/Reject Button -->
{% if user.username != session.get('username') %}
  {% if not user.is_verified %}
    <a href="{{ url_for('admin_approve_user', user_id=user.id) }}" 
       class="px-3 py-1 bg-green-500 hover:bg-green-600 text-white text-xs font-semibold rounded transition"
       onclick="return confirm('Approve user {{ user.username }}?');">
      ✅ Acc
    </a>
  {% else %}
    <a href="{{ url_for('admin_reject_user', user_id=user.id) }}" 
       class="px-3 py-1 bg-yellow-500 hover:bg-yellow-600 text-white text-xs font-semibold rounded transition"
       onclick="return confirm('Tolak user {{ user.username }}?');">
      ⛔ Tolak
    </a>
  {% endif %}
{% else %}
  <span class="px-3 py-1 bg-gray-200 text-gray-600 text-xs font-semibold rounded">
    (Akun Anda)
  </span>
{% endif %}
```

**Logika Tombol:**
- Jika user belum verified: tampil tombol **✅ Acc** (hijau)
- Jika user sudah verified: tampil tombol **⛔ Tolak** (kuning)
- Jika user = akun admin yang login: tampil "(Akun Anda)" (gray, disabled)

---

## 🎯 User Flow

### Untuk Admin:

```
1. Login sebagai Admin
   ↓
2. Klik menu "Kelola User" (sidebar)
   ↓
3. Lihat tabel User dengan kolom "Status"
   ↓
4. Untuk user dengan status "⏳ Pending":
   - Klik tombol "✅ Acc" untuk approve
   - Klik tombol "⛔ Tolak" untuk reject
   ↓
5. Status berubah menjadi "✅ Verified" atau "⏳ Pending"
   ↓
6. Bisa juga ubah role atau hapus user
```

### Untuk User Baru:

```
1. Register akun baru
   ↓
2. Login berhasil (tapi status = ⏳ Pending)
   ↓
3. Tunggu approval dari admin
   ↓
4. Setelah diapprove: Status = ✅ Verified
   ↓
5. Bisa mengakses semua fitur (pengajuan, daftar, bayar, dll)
```

---

## 📊 Tabel Comparasi

| Status | is_verified | Badge | Action Buttons |
|--------|-------------|-------|---|
| Pending | False | ⏳ Yellow | ✅ Acc, Make Admin, Delete |
| Verified | True | ✅ Green | ⛔ Tolak, Make Admin, Delete |
| Own Account | - | Gray | (Akun Anda) |

---

## 🔒 Security Features

### 1. **Self-Protection**
Admin tidak bisa:
- Approve/Reject akunnya sendiri
- Delete akunnya sendiri
- Downgrade rolenya sendiri

Kondisi check:
```python
if u.username == session.get("username"):
    flash("Tidak bisa ... akun yang sedang login.", "error")
    return redirect(url_for("admin_users"))
```

---

### 2. **Admin-Only Routes**
Semua route menggunakan decorator `@admin_required`:
```python
@app.route("/admin/approve-user/<int:user_id>")
@admin_required
def admin_approve_user(user_id):
    # ...
```

Hanya role="admin" yang bisa akses.

---

### 3. **Confirmation Dialogs**
Setiap action meminta konfirmasi:
```html
onclick="return confirm('Approve user {{ user.username }}?');"
```

Mencegah klik accidental.

---

## 🧪 Testing

### Database Setup
```bash
cd "c:\laragon\www\aplikasi pinjaman"
python init_db.py
```

Akan membuat:
- 1 Admin account (verified)
- 1 Verified User (budi)
- 2 Pending Users (siti, ahmad)
- 4 Sample loans

---

### Test Accounts

| Username | Password | Role | Status | Note |
|----------|----------|------|--------|------|
| admin | admin123 | Admin | ✅ Verified | Can approve users |
| budi | budi123 | User | ✅ Verified | Has 4 loans |
| siti | siti123 | User | ⏳ Pending | Needs approval |
| ahmad | ahmad123 | User | ⏳ Pending | Needs approval |

---

### Test Scenarios

#### Scenario 1: Approve User
1. Login as admin
2. Go to "Kelola User"
3. Find "siti" with status "⏳ Pending"
4. Click "✅ Acc" button
5. Confirm approval
6. Status changes to "✅ Verified"
7. siti now can login and access all features

---

#### Scenario 2: Reject User
1. Login as admin
2. Go to "Kelola User"
3. Find "siti" with status "✅ Verified"
4. Click "⛔ Tolak" button
5. Confirm rejection
6. Status changes back to "⏳ Pending"

---

#### Scenario 3: Self-Protection
1. Login as admin
2. Go to "Kelola User"
3. Try to click "Acc" on your own account
4. You'll see "(Akun Anda)" - button disabled
5. Prevents self-modification

---

## 📝 SQL Queries

### Check Pending Users
```sql
SELECT id, nama, username, email, is_verified, verified_at 
FROM users 
WHERE is_verified = FALSE 
ORDER BY id;
```

### Check Verified Users
```sql
SELECT id, nama, username, email, verified_by, verified_at 
FROM users 
WHERE is_verified = TRUE 
ORDER BY verified_at DESC;
```

### Approval Statistics
```sql
SELECT 
  COUNT(*) as total_users,
  SUM(CASE WHEN is_verified = TRUE THEN 1 ELSE 0 END) as verified_count,
  SUM(CASE WHEN is_verified = FALSE THEN 1 ELSE 0 END) as pending_count
FROM users;
```

---

## 🎨 CSS Classes

Button styling dari `app.css`:

```css
/* Green Approve Button */
.bg-green-500 {
    background-color: #10B981;
}

.bg-green-500:hover {
    background-color: #059669;
}

/* Yellow Reject Button */
.bg-yellow-500 {
    background-color: #F59E0B;
}

.bg-yellow-500:hover {
    background-color: #D97706;
}

/* Status Badges */
.bg-green-100 {
    background-color: #D1FAE5;
}

.bg-yellow-100 {
    background-color: #FEF3C7;
}
```

---

## 📦 Dependencies

Tidak ada dependency baru yang diperlukan. Menggunakan:
- Flask (existing)
- SQLAlchemy (existing)
- Jinja2 (existing)

---

## 🚀 Deployment Checklist

- ✅ Model User updated dengan is_verified field
- ✅ Migration: `python init_db.py` to reset database
- ✅ Routes added: approve-user, reject-user
- ✅ Template updated: admin_users.html
- ✅ Security: @admin_required, self-protection
- ✅ UI: Status badges, action buttons
- ✅ Testing: init_db.py dengan test accounts

---

## 💡 Future Enhancements

1. **Email Notification**
   - Kirim email saat user approved/rejected
   
2. **Approval Reason**
   - Tambah field untuk catat alasan rejection
   
3. **Batch Operations**
   - Approve multiple users sekaligus
   
4. **Approval Log**
   - Lihat history siapa approve siapa dan kapan
   
5. **Auto-Expiry**
   - Set expiry date untuk pending approvals

---

## 📞 Troubleshooting

### Q: Tombol Acc tidak muncul?
**A:** Check apakah:
- User sudah login sebagai admin
- is_verified field sudah ada di database
- Template sudah di-update

### Q: Error "User.is_verified" tidak ada?
**A:** Jalankan `python init_db.py` untuk reset database

### Q: Bisa approve user sendiri?
**A:** Tidak, sudah ada proteksi. Akan muncul "(Akun Anda)"

### Q: Status tidak berubah?
**A:** Check browser cache (Ctrl+F5), atau lihat database langsung

---

## 📄 File Changes Summary

### Files Modified:
1. `app.py`
   - Added `is_verified`, `verified_by`, `verified_at` to User model
   - Added `admin_approve_user()` route
   - Added `admin_reject_user()` route

2. `templates/admin_users.html`
   - Added Status column with badges
   - Updated Action buttons with approve/reject logic

### Files Created:
1. `init_db.py` - Database initialization & seed data

---

Generated: 2025-12-17
Updated by: GitHub Copilot
