#!/usr/bin/env python
"""
Script untuk inisialisasi database dan seed data test
Jalankan: python init_db.py
"""

from datetime import datetime
from app import app, db, User, Pinjaman, LoanStatus, LoanPayment

def init_database():
    """Initialize database tables"""
    with app.app_context():
        print("🔨 Menghapus tabel lama...")
        db.drop_all()
        
        print("✅ Membuat tabel baru...")
        db.create_all()
        
        print("\n📝 Membuat data test...\n")
        
        # ===== ADMIN USER =====
        admin = User(
            nama="Administrator",
            email="admin@koperasi.com",
            telepon="081234567890",
            username="admin",
            role="admin",
            is_verified=True,
            verified_at=datetime.utcnow()
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.flush()
        print(f"✅ Admin: {admin.username} (verified=True)")
        
        # ===== VERIFIED USER =====
        user1 = User(
            nama="Budi Santoso",
            email="budi@gmail.com",
            telepon="081234567891",
            username="budi",
            role="user",
            is_verified=True,
            verified_by=admin.id,
            verified_at=datetime.utcnow()
        )
        user1.set_password("budi123")
        db.session.add(user1)
        db.session.flush()
        print(f"✅ User: {user1.username} (verified=True)")
        
        # ===== PENDING USER (Belum diapprove) =====
        user2 = User(
            nama="Siti Nurhaliza",
            email="siti@gmail.com",
            telepon="081234567892",
            username="siti",
            role="user",
            is_verified=False
        )
        user2.set_password("siti123")
        db.session.add(user2)
        db.session.flush()
        print(f"⏳ User: {user2.username} (verified=False) - PENDING APPROVAL")
        
        # ===== PENDING USER 2 =====
        user3 = User(
            nama="Ahmad Wijaya",
            email="ahmad@gmail.com",
            telepon="081234567893",
            username="ahmad",
            role="user",
            is_verified=False
        )
        user3.set_password("ahmad123")
        db.session.add(user3)
        db.session.flush()
        print(f"⏳ User: {user3.username} (verified=False) - PENDING APPROVAL")
        
        db.session.commit()
        
        # ===== SAMPLE LOANS =====
        print("\n💰 Membuat data pinjaman sample...\n")
        
        # Loan 1: Status Pending
        pinjaman1 = Pinjaman(
            peminjam=user1.nama,
            user_id=user1.id,
            jumlah=5000000,
            tenor=12,
            keperluan="Modal Usaha Kelontong",
            bunga=12.0,
            total_bunga=600000,
            total_bayar=5600000,
            angsuran=466666.67
        )
        db.session.add(pinjaman1)
        db.session.flush()
        
        loan_status1 = LoanStatus(
            pinjaman_id=pinjaman1.id,
            status="pending"
        )
        db.session.add(loan_status1)
        print(f"✅ Pinjaman #{pinjaman1.id}: Rp{pinjaman1.jumlah:,} - Status: pending")
        
        # Loan 2: Status Approved
        pinjaman2 = Pinjaman(
            peminjam=user1.nama,
            user_id=user1.id,
            jumlah=10000000,
            tenor=24,
            keperluan="Renovasi Rumah",
            bunga=12.0,
            total_bunga=2400000,
            total_bayar=12400000,
            angsuran=516666.67
        )
        db.session.add(pinjaman2)
        db.session.flush()
        
        loan_status2 = LoanStatus(
            pinjaman_id=pinjaman2.id,
            status="approved",
            approved_by=admin.id,
            approved_at=datetime.utcnow()
        )
        db.session.add(loan_status2)
        print(f"✅ Pinjaman #{pinjaman2.id}: Rp{pinjaman2.jumlah:,} - Status: approved")
        
        # Loan 3: Status Disbursed
        pinjaman3 = Pinjaman(
            peminjam=user1.nama,
            user_id=user1.id,
            jumlah=7500000,
            tenor=18,
            keperluan="Pendidikan Anak",
            bunga=12.0,
            total_bunga=1350000,
            total_bayar=8850000,
            angsuran=491666.67
        )
        db.session.add(pinjaman3)
        db.session.flush()
        
        loan_status3 = LoanStatus(
            pinjaman_id=pinjaman3.id,
            status="disbursed",
            approved_by=admin.id,
            approved_at=datetime.utcnow(),
            disbursed_by=admin.id,
            disbursed_at=datetime.utcnow()
        )
        db.session.add(loan_status3)
        print(f"✅ Pinjaman #{pinjaman3.id}: Rp{pinjaman3.jumlah:,} - Status: disbursed")
        
        # Loan 4: Status Lunas (Paid Off)
        pinjaman4 = Pinjaman(
            peminjam=user1.nama,
            user_id=user1.id,
            jumlah=3000000,
            tenor=6,
            keperluan="Peralatan Dapur",
            bunga=12.0,
            total_bunga=180000,
            total_bayar=3180000,
            angsuran=530000
        )
        db.session.add(pinjaman4)
        db.session.flush()
        
        loan_status4 = LoanStatus(
            pinjaman_id=pinjaman4.id,
            status="lunas",
            approved_by=admin.id,
            approved_at=datetime.utcnow(),
            disbursed_by=admin.id,
            disbursed_at=datetime.utcnow()
        )
        db.session.add(loan_status4)
        print(f"✅ Pinjaman #{pinjaman4.id}: Rp{pinjaman4.jumlah:,} - Status: lunas")
        
        # Add payment history for loan 4
        for i in range(6):
            payment = LoanPayment(
                pinjaman_id=pinjaman4.id,
                user_id=user1.id,
                jumlah=530000,
                metode="transfer",
                status="verified",
                verified_by=admin.id,
                verified_at=datetime.utcnow()
            )
            db.session.add(payment)
        print(f"   └─ Ditambahkan 6 pembayaran terverifikasi\n")
        
        db.session.commit()
        
        print("=" * 60)
        print("✅ DATABASE BERHASIL DIINISIALISASI!")
        print("=" * 60)
        print("\n📋 TEST ACCOUNTS:\n")
        print("ADMIN:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Email: admin@koperasi.com")
        print("\nUSER (Verified):")
        print("  Username: budi")
        print("  Password: budi123")
        print("  Email: budi@gmail.com")
        print("  → Status: ✅ Verified")
        print("  → Has 4 loans (pending, approved, disbursed, lunas)")
        print("\nUSER (Pending Approval):")
        print("  Username: siti")
        print("  Password: siti123")
        print("  Email: siti@gmail.com")
        print("  → Status: ⏳ Pending")
        print("\nUSER (Pending Approval):")
        print("  Username: ahmad")
        print("  Password: ahmad123")
        print("  Email: ahmad@gmail.com")
        print("  → Status: ⏳ Pending")
        print("\n" + "=" * 60)
        print("🌐 Buka: http://127.0.0.1:5000")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
