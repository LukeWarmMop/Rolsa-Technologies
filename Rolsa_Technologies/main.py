
"""
DISCLAIMER SOME OF THESE FEATURES WERE MADE WITH THE HELP OF AI, THESE WERE THEN WORKED ON AND IMPROVED BY THE DEVELOPER
"""

import sqlite3
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from cryptography.fernet import Fernet

def connect_to_db():
    conn = sqlite3.connect('mainrolsa.db')
    cursor = conn.cursor()
    print(conn)

    return conn, cursor

def register_acc(fname, lname, email, password):
    hashed = generate_password_hash(password)
    conn, cursor = connect_to_db()
    cursor.execute('''
    INSERT INTO TBLuser (fname, lname, email, password) VALUES (?, ?, ?, ?)
    ''', (fname, lname, email, hashed))

    conn.commit()
    conn.close()

def login_acc(email, password):
    try:
        conn, cursor = connect_to_db()
        cursor.execute('''
        SELECT userid, email, password FROM TBLuser
        WHERE email = ?
        ''', (email,))

        user = cursor.fetchone()
        if not user:  
            return None, False

        hashedpass = user[2] 
        passmatch = check_password_hash(hashedpass, password)

        if passmatch:  
            return user[0], True
        else:
            return None, False
    except Exception as e:
        print(f"Error: {e}", flush=True)
        return None, False

        
def booking_save(userid, booking_type, date, time):
        conn, cursor = connect_to_db()
        cursor.execute('''
        INSERT INTO TBLbooking (userid, bookingtype, time, date) VALUES (?, ?, ?, ?)
        ''', (userid, booking_type, date, time))

        conn.commit()
        conn.close()

def payment_save(userid, cardholder, cardnumber, billing, expir):
    conn, cursor = connect_to_db()
    confirm = ""
    cursor.execute('''
    SELECT token FROM TBLtoken
    ''')

    result = cursor.fetchone()
    token = result[0]



    cipher = Fernet(token)
    cardnumber = cipher.encrypt(cardnumber.encode())
    cursor.execute('''
    INSERT INTO TBLuserpayments (userid, cardholdername, cardholdernumber, billingaddress, expirationdate) VALUES (?, ?, ?, ?, ?)
    ''', (userid, cardholder, cardnumber, billing, expir))
    conn.commit()
    conn.close()


def check_existing(userid, cardnumber):
    conn, cursor = connect_to_db()

    # Fetch encrypted cardholder numbers for the given user ID
    cursor.execute('''
    SELECT cardholdernumber FROM TBLuserpayments WHERE userid = ?
    ''', (userid,))
    results = cursor.fetchall()

    # Fetch the encryption token
    cursor.execute('''
    SELECT token FROM TBLtoken
    ''')
    result = cursor.fetchone()
    token = result[0]

    # Initialize Fernet cipher
    cipher = Fernet(token)

    # Compare decrypted cardholder numbers with the provided card number
    for encrypted_cardnumber in results:
        try:
            decrypted_cardnumber = cipher.decrypt(encrypted_cardnumber[0].encode()).decode()  # Decrypt and decode to string
            if decrypted_cardnumber == cardnumber:
                conn.close()
                return False  # Card already exists
        except Exception as e:
            print(f"Decryption error: {e}", flush=True)
    
    conn.close()
    return True  # Card does not exist


def get_userdeatils(userid):
    conn, cursor = connect_to_db()
    cursor.execute('''
        SELECT fname, lname, email FROM TBLuser
        WHERE userid = ?
        ''', (userid,))

    user = cursor.fetchone()
    print(user, flush=True)
    return user

def get_bookinginfo(userid):
    conn, cursor = connect_to_db()
    cursor.execute('''
        SELECT bookingtype, time, date FROM TBLbooking
        WHERE userid = ?
        ''', (userid,))
    booking = cursor.fetchall()
    return booking

def get_cardinfo(userid):
    conn, cursor = connect_to_db()
    cursor.execute('''
        SELECT cardholdername, expirationdate FROM TBLuserpayments
        WHERE userid = ?
        ''', (userid,))
    card = cursor.fetchall()
    return card