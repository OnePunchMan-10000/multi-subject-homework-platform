#!/usr/bin/env python3
"""
Simple script to view the database contents directly
Usage: python view_db.py
"""

import sqlite3
import os
from datetime import datetime

def view_database():
    db_path = 'app_data.db'
    
    print("=" * 60)
    print("📊 DATABASE VIEWER")
    print("=" * 60)
    
    if not os.path.exists(db_path):
        print("⚠️  Database not found!")
        print(f"   Expected path: {os.path.abspath(db_path)}")
        print("   Run the app first to create it:")
        print("   streamlit run hw01.py  OR  streamlit run run.py")
        return
    
    print(f"✅ Database found: {os.path.abspath(db_path)}")
    print(f"📁 File size: {os.path.getsize(db_path)} bytes")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Show all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Tables: {[t[0] for t in tables]}")
        print()
        
        # Show users table
        if ('users',) in tables:
            print("👥 USERS TABLE:")
            print("-" * 40)
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"Total users: {user_count}")
            
            if user_count > 0:
                cursor.execute("SELECT id, username, created_at FROM users ORDER BY id")
                users = cursor.fetchall()
                print("\nUser List:")
                for user in users:
                    print(f"  ID: {user[0]:2d} | Username: {user[1]:30s} | Created: {user[2]}")
            print()
        
        # Show history table
        if ('history',) in tables:
            print("📝 HISTORY TABLE:")
            print("-" * 40)
            cursor.execute("SELECT COUNT(*) FROM history")
            history_count = cursor.fetchone()[0]
            print(f"Total questions: {history_count}")
            
            if history_count > 0:
                cursor.execute("""
                    SELECT h.id, u.username, h.subject, h.question, h.created_at 
                    FROM history h 
                    JOIN users u ON h.user_id = u.id 
                    ORDER BY h.id DESC 
                    LIMIT 10
                """)
                history = cursor.fetchall()
                print("\nRecent Questions (last 10):")
                for h in history:
                    question_preview = h[3][:50] + "..." if len(h[3]) > 50 else h[3]
                    print(f"  ID: {h[0]:3d} | User: {h[1]:20s} | Subject: {h[2]:12s}")
                    print(f"        Question: {question_preview}")
                    print(f"        Asked: {h[4]}")
                    print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    view_database()

