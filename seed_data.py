"""
Script untuk seed data test di aplikasi Koperasi Simpan Pinjam
Jalankan: python seed_data.py
"""

from app import app, db, User, Pinjaman, LoanStatus
from datetime import datetime, timedelta

def seed_database():
    with app.app_context():
        # Hapus data lama (optional)
        print("🗑️  Clearing database...")
        db.drop_all()
        db.create_all()
        
        print("📝 Creating admin user...")
        admin = User(
            nama="Admin Koperasi",
            email="admin@koperasi.com",
            telepon="0812345678",
            username="admin",
            role="admin"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        
        print("👤 Creating test users...")
        user1 = User(
            nama="Budi Santoso",
            email="budi@email.com",
            telepon="0812345679",
            username="budi",
            role="user"
        )
        user1.set_password("budi123")
        db.session.add(user1)
        
        user2 = User(
            nama="Siti Nurhaliza",
            email="siti@email.com",
            telepon="0812345680",
            username="siti",
            role="user"
        )
        user2.set_password("siti123")
        db.session.add(user2)
        
        db.session.commit()
        print("✅ Users created")
        
        print("📋 Creating test loans...")
        
        # Pinjaman 1: Pending
        loan1 = Pinjaman(
            peminjam="Budi Santoso",
            user_id=user1.id,
            jumlah=5000000,
            tenor=12,
            keperluan="Modal Usaha Toko",
            bunga=12.0,
            total_bunga=600000,
            total_bayar=5600000,
            angsuran=466667
        )
        db.session.add(loan1)
        db.session.flush()
        
        status1 = LoanStatus(
            pinjaman_id=loan1.id,
            status="pending",
            catatan="Menunggu review admin"
        )
        db.session.add(status1)
        
        # Pinjaman 2: Approved
        loan2 = Pinjaman(
            peminjam="Siti Nurhaliza",
            user_id=user2.id,
            jumlah=10000000,
            tenor=24,
            keperluan="Pendidikan Anak",
            bunga=12.0,
            total_bunga=2400000,
            total_bayar=12400000,
            angsuran=516667
        )
        db.session.add(loan2)
        db.session.flush()
        
        status2 = LoanStatus(
            pinjaman_id=loan2.id,
            status="approved",
            approved_by=admin.id,
            approved_at=datetime.utcnow()
        )
        db.session.add(status2)
        
        # Pinjaman 3: Disbursed (sudah dicairkan, bisa dibayar)
        loan3 = Pinjaman(
            peminjam="Budi Santoso",
            user_id=user1.id,
            jumlah=3000000,
            tenor=6,
            keperluan="Renovasi Rumah",
            bunga=12.0,
            total_bunga=180000,
            total_bayar=3180000,
            angsuran=530000
        )
        db.session.add(loan3)
        db.session.flush()
        
        status3 = LoanStatus(
            pinjaman_id=loan3.id,
            status="disbursed",
            approved_by=admin.id,
            approved_at=datetime.utcnow() - timedelta(days=30),
            disbursed_by=admin.id,
            disbursed_at=datetime.utcnow() - timedelta(days=25)
        )
        db.session.add(status3)
        
        db.session.commit()
        print("✅ Test loans created")
        
        print("\n" + "="*60)
        print("✅ DATABASE SEED COMPLETED!")
        print("="*60)
        print("\n📊 Test Accounts:")
        print("-" * 60)
        print("Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Email: admin@koperasi.com")
        print("\nUser 1:")
        print("  Username: budi")
        print("  Password: budi123")
        print("  Email: budi@email.com")
        print("  Pinjaman: 2 (1 pending, 1 disbursed)")
        print("\nUser 2:")
        print("  Username: siti")
        print("  Password: siti123")
        print("  Email: siti@email.com")
        print("  Pinjaman: 1 (approved)")
        print("\n" + "="*60)
        print("🎯 Test Scenarios:")
        print("-" * 60)
        print("1. LOGIN as admin:")
        print("   - Lihat dashboard (/admin/dashboard)")
        print("   - Approve/Reject pinjaman Budi (pending)")
        print("   - Disburse pinjaman Siti (approved)")
        print("\n2. LOGIN as budi:")
        print("   - Lihat pinjaman di /pinjaman_saya")
        print("   - Ajukan pengambilan untuk pinjaman approved")
        print("   - Bayar cicilan untuk pinjaman disbursed")
        print("\n3. LOGIN as siti:")
        print("   - Lihat pinjaman di /pinjaman_saya")
        print("   - Tunggu admin approve & disburse")
        print("="*60 + "\n")

if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
