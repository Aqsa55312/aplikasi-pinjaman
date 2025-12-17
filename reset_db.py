#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script untuk reset database dan apply foreign key constraint fix
Jalankan: python reset_db.py
"""

import os
from datetime import datetime
from app import app, db, User, Pinjaman, LoanStatus, LoanPayment

def reset_database():
    """Drop dan recreate semua tables dengan constraint yang benar"""
    with app.app_context():
        print("🗑️  Menghapus semua tabel lama...")
        db.drop_all()
        
        print("✅ Membuat tabel baru dengan constraint yang benar...")
        db.create_all()
        
        print("👤 Membuat user admin...")
        admin = User(
            nama="Administrator",
            email="admin@koperasi.com",
            telepon="081234567890",
            username="admin",
            role="admin",
            is_verified=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        
        print("👥 Membuat user testing...")
        user1 = User(
            nama="Budi Santoso",
            email="budi@gmail.com",
            telepon="081234567891",
            username="budi",
            role="user",
            is_verified=True
        )
        user1.set_password("budi123")
        db.session.add(user1)
        
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
        
        db.session.commit()
        
        print("💰 Membuat sample pinjaman...")
        pinjaman1 = Pinjaman(
            peminjam="Budi Santoso",
            user_id=user1.id,
            jumlah=5000000,
            tenor=12,
            keperluan="Modal Usaha Kelontong",
            bunga=1.0,
            total_bunga=600000,
            total_bayar=5600000,
            angsuran=466667
        )
        db.session.add(pinjaman1)
        db.session.commit()
        
        loan_status1 = LoanStatus(pinjaman_id=pinjaman1.id, status="disbursed")
        db.session.add(loan_status1)
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ DATABASE BERHASIL DIRESET!")
        print("="*60)
        print("\n📋 Akun Testing:")
        print("   Admin:")
        print("     Username: admin")
        print("     Password: admin123")
        print("     Status: ✅ Verified (Admin)")
        print("\n   User (Verified):")
        print("     Username: budi")
        print("     Password: budi123")
        print("     Status: ✅ Verified")
        print("\n   User (Pending):")
        print("     Username: siti")
        print("     Password: siti123")
        print("     Status: ⏳ Pending (butuh approval)")
        print("\n   User (Pending):")
        print("     Username: ahmad")
        print("     Password: ahmad123")
        print("     Status: ⏳ Pending (butuh approval)")
        print("\n💡 Foreign Key Fix: Penghapusan user sekarang aman!")
        print("   - verified_by akan di-set NULL saat user dihapus")
        print("   - Tidak ada IntegrityError saat delete user")
        print("="*60 + "\n")

if __name__ == "__main__":
    reset_database()
