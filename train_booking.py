#!/usr/bin/env python
# coding: utf-8

# In[1]:


import mysql.connector
import pandas as pd
import random
from datetime import datetime
import re


# In[2]:


import string


# In[7]:


cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='85@2002$gA',
    port='3306',
    database='railway'
)
cursor = cnx.cursor()    

def signup():
        
    name = input('Name: ')
    
    while not re.match(r'^[A-Za-z\s]+$', name):
        print('Invalid name. Please enter alphabets and spaces only.')
        name = input('Name: ')
        
    phone_no = input('Phone Number: ')
    
    while not re.match(r'^\d{10}$', phone_no):
        print('Invalid phone number. Please enter a 10-digit number.')
        phone_no = input('Phone Number: ')
        
        
    age = int(input('Age :'))
    
    if age>120 :
        print('Invalid Age')
     
    email = input('Email Address: ')
          
    query = "SELECT * FROM user_login WHERE email = %s"
    values = (email,)
    cursor.execute(query, values)
    existing_user = cursor.fetchone()

    if existing_user:
        print('You have already created an account please Login.\n')
        return;
    
    while True:
        password1 = input('Password: ')
        password2 = input('Confirm Password: ')
        
        if password1 != password2:
            print('Passwords do not match. Please try again.')
            continue
        
        if len(password1) < 8:
            print('Password must be at least 8 characters long. Please try again.')
            continue
        
        if not re.search(r'\d', password1):
            print('Password must contain at least 1 digit. Please try again.')
            continue
        
        if not re.search(r'[A-Z]', password1):
            print('Password must contain at least 1 uppercase letter. Please try again.')
            continue
        
        if not re.search(r'[a-z]', password1):
            print('Password must contain at least 1 lowercase letter. Please try again.')
            continue
        
        if not re.search(r'\W', password1):
            print('Password must contain at least 1 special character. Please try again.')
            continue
        
        break
        
    
    query = "INSERT INTO user_login (name,phone_no,age, email, password) VALUES (%s, %s, %s, %s , %s)"
    values = (name, phone_no, age , email, password1)
    cursor.execute(query, values)
    cnx.commit()
    print('Signup successful!\n')
   
            
                    
def login():
    
        email = input('Email Address: ')
        password = input('Password: ')        
        query = "SELECT name FROM user_login WHERE email = %s AND password = %s"
        values = (email, password)
        cursor.execute(query, values)
        user = cursor.fetchone()
        if user:
                    print('\n Welcome,', user[0], '!\n')
                    while True:
                        print('1. View Train Details')
                        print('2. Reservation')
                        print('3. Cancellation')
                        print('4. Not Interested')
                    
                        c1=input('\n Enter your choice \n') 
                    
                        if c1 == '1':
                             view_trains()
                        elif c1 =='2':
                             reservation()
                        elif c1 == '3':
                             cancellation()
                        elif c1 == '4':
                            print('Thank you Have a good day! \n')
                            break;
                        else:
                            print('\n Invalid Choice \n')                                       
        else:
             print('Invalid Credentials. Login failed.\n')
                
def view_trains():
    query = "SELECT * FROM train_details"
    cursor.execute(query)
    trains = cursor.fetchall()
    print(trains)
    print('\n')               
                
                
def reservation():
    
    name = input('Name: ')
    age = input('Age: ')
    train_name = input('Train Name: ')
    train_no = input('Train Number: ')
    source = input('Source: ')
    destination = input('Destination: ')
    journey_date = input('Journey Date (yyyy-mm-dd): ')
    
    today = datetime.now().date()
    journey_date = datetime.strptime(journey_date, '%Y-%m-%d').date()

    if journey_date < today:
        print("Invalid journey date. Journey date should be greater than or equal to today's date.\n")
        return

    travel_class = input('Class: ')

    query = "SELECT * FROM train_details WHERE train_name = %s AND train_number = %s AND source = %s AND destination = %s"
    values = (train_name, train_no, source, destination)
    cursor.execute(query, values)
    train = cursor.fetchone()

    if not train:
        print('Invalid train details.\n')
        return

    query = "SELECT * FROM seat_availability WHERE train_no = %s AND class = %s AND date = %s"
    values = (train_no, travel_class, journey_date)
    cursor.execute(query, values)
    seat_availability = cursor.fetchone()

    if not seat_availability:
        print('Seat is currently unavailable.\n')
        return

    if seat_availability[4] >= 1:
       
        query = "UPDATE seat_availability SET available = available - 1 WHERE train_no = %s AND class = %s"
        values = (train_no, travel_class)
        cursor.execute(query, values)
        cnx.commit()
        print('\nSuccess: Your seat is booked. We have sent the PDF of your booked ticket to your registered email ID. Kindly download your ticket from the provided email ID.\n')
        
        booking_date = datetime.now()
        
        pnr_number = ''.join(random.choices(string.digits, k=5))
        pnr_number = int( pnr_number)

        query = "INSERT INTO reservation_details (pnr_no, name, age, train_name, source, destination, booking_date, journey_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s )"
        values = (pnr_number, name, age, train_name, source, destination, booking_date, journey_date)
        cursor.execute(query, values)
        cnx.commit()
        
        print('\n Your PNR Number is:', pnr_number)
    else:
        print('\n Seat is currently unavailable.\n')
        
def cancellation():
    pnr_number = input("Enter PNR Number: ")
    train_no = input('Train Number: ')
    travel_class = input('Class: ')
    journey_date = input('Journey Date (yyyy-mm-dd): ')

    today = datetime.now().date()
    journey_date = datetime.strptime(journey_date, '%Y-%m-%d').date()

    if journey_date < today:
        print("Invalid journey date. Journey date should be greater than or equal to today's date.\n")
        return

    query = "SELECT * FROM reservation_details WHERE pnr_no = %s"
    cursor.execute(query, (pnr_number,))
    booking = cursor.fetchone()

    if not booking:
        print("Invalid PNR number.\n")
        return

    query = "DELETE FROM reservation_details WHERE pnr_no = %s"
    cursor.execute(query, (pnr_number,))
    cnx.commit()
    print("\n Your ticket is cancelled successfully.\n")

    query = "UPDATE seat_availability SET available = available + 1 WHERE train_no = %s AND class = %s"
    values = (train_no, travel_class)
    cursor.execute(query, values)
    cnx.commit()
    print("\n Seat availability has been updated.\n")
                                    
while True:
    
        print('Welcome to Indian Railways');
        print('****************************')
        print('\n')

        print('1. Sign Up')
        print('2. Login')
        print('3. Not interested')

        choice = input('Enter your choice: ')

        if choice == '1':
            
                  signup()
               
        elif choice == '2':
                 
                  login()
            
        elif choice =='3':
              break;
        else:
             print('Invalid choice')                   


# In[ ]:





# In[ ]:




