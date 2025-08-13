#!/usr/bin/env python3
"""
Simple script to view users in the database
"""

import sqlite3
from datetime import datetime

def view_users():
    try:
        with sqlite3.connect('app_data.db') as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            # Get all users
            cur.execute('SELECT * FROM users ORDER BY created_at DESC')
            users = cur.fetchall()
            
            print("=== EDULLM USERS DATABASE ===")
            print(f"Total users: {len(users)}")
            print()
            
            if users:
                print("ID | Username           | Created At")
                print("-" * 45)
                for user in users:
                    created = user['created_at'] or 'Unknown'
                    print(f"{user['id']:2} | {user['username']:18} | {created}")
            else:
                print("No users found in database.")
                
            print()
            
            # Show table structure
            cur.execute("PRAGMA table_info(users)")
            columns = cur.fetchall()
            print("Database Schema:")
            for col in columns:
                print(f"  {col['name']} ({col['type']})")
                
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    view_users()
