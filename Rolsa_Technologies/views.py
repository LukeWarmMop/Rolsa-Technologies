"""
Routes and views for the Flask application.
"""

"""
DISCLAIMER SOME OF THESE FEATURES WERE MADE WITH THE HELP OF AI, THESE WERE THEN WORKED ON AND IMPROVED BY THE DEVELOPER
"""

from datetime import datetime
from os import error
from flask import render_template, request, redirect, url_for, session
from Rolsa_Technologies import app
from Rolsa_Technologies.main import (
    check_existing, get_cardinfo, get_userdeatils, payment_save, 
    register_acc, login_acc, booking_save, get_userdeatils, get_bookinginfo
)
import sqlite3
import re

# Route for the login page
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        message = ""
        try:
            email = request.form.get('email')  # Get user input for email
            password = request.form.get('password')  # Get user input for password

            # Check if all fields are filled
            if not email or not password:
                raise ValueError('Please Make Sure All Fields Are Filled')

            check = login_acc(email, password)  # Validate login credentials

            # Handle invalid login attempt
            if not check[1]: 
                raise ValueError('Invalid Password or Email')
            else:
                print('Good Login', flush=True)
                session['userid'] = check[0]  # Save user session ID
                return redirect(url_for('home'))

        except ValueError as error:
            message = str(error)

        return render_template('login.html', title='Login Page', message=message)

    return render_template('login.html', title='Login Page', message="")


# Function to validate email format
def validate_email(email):
    emailformat = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(emailformat, email) is not None

# Function to check password strength
def pass_check(password):
    length_check = len(password) >= 8
    lowercase_check = re.search(r'[a-z]', password) is not None
    uppercase_check = re.search(r'[A-Z]', password) is not None
    number_check = re.search(r'\d', password) is not None
    specialchar_check = re.search(r'[!@#$%^&*(),.?":{}|<>]', password) is not None

    # Validate password meets all criteria
    if all([length_check, lowercase_check, uppercase_check, number_check, specialchar_check]):
        return True
    else:
        return False

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        try:
            fname = request.form.get('fname')  # First name
            lname = request.form.get('lname')  # Last name
            email = request.form.get('email')  # Email
            password = request.form.get('password')  # Password
            passwordcheck = request.form.get('passwordcheck')  # Confirm password

            # Ensure all fields are filled
            if not fname or not lname or not email or not password or not passwordcheck:
                raise ValueError('Please make sure all fields are filled')

            namecheck_f = fname.isalpha()  # Validate first name
            namecheck_l = lname.isalpha()  # Validate last name

            if namecheck_f == False or namecheck_l == False:
                raise ValueError('Please make sure to not use numbers or special characters in your name')

            emailcheck = validate_email(email)  # Validate email format
            if emailcheck == False:
                raise ValueError('Please make sure that email follows the correct format i.e example@gmail.com')

            password_check = pass_check(password)  # Validate password strength

            if password_check != True:
                raise ValueError('''
                            Password Too Weak, please include: 
                            Length: At least 8 characters.
                            Lowercase Letters: At least one lowercase letter.
                            Uppercase Letters: At least one uppercase letter.
                            Digits: At least one digit.
                            Special Characters: At least one special character.
                ''')

            if password != passwordcheck:
                raise ValueError('Password does not match!')

            register_acc(fname, lname, email, password)  # Register the account
            message = 'Account Created, Please Log In'

        except ValueError as error:
            message = error

        return render_template('register.html', title='Register', message=message)
    return render_template('register.html', title='Register', message='')


# Route for the home page
@app.route('/home')
def home():
    userid = session.get('userid')  # Check if user is logged in
    if userid is not None:
        return render_template(
            'index.html',
            title='Home Page',
            year=datetime.now().year,
        )
    return redirect(url_for('login'))


# Route for the contact page
@app.route('/contact')
def contact():
    """Renders the contact page."""
    userid = session.get('userid')  # Check if user is logged in
    if userid is not None:
        return render_template(
            'contact.html',
            title='Contact',
            year=datetime.now().year,
            message='Please use the following information to get in touch with us!'
        )
    return redirect(url_for('login'))


# Route for the information page
@app.route('/information')
def information():
    """Renders the information page."""
    userid = session.get('userid')  # Check if user is logged in
    if userid is not None:
        return render_template(
            'information.html',
            title='Information',
            year=datetime.now().year,
            message='Your application description page.'
        )
    return redirect(url_for('login'))


# Route for the booking page
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    """Renders the booking page."""
    userid = session.get('userid')  # Check if user is logged in
    if userid is not None:
        current_date = datetime.today().strftime('%Y-%m-%d')  # Get current date
        if request.method == 'POST':
            date = ""
            time = ""
            message = ""

            try:
                booking_type = request.form.get('type')  # Get booking type
                time = request.form.get('time')  # Get booking time
                date = request.form.get('date')  # Get booking date

                # Validate booking fields
                if not booking_type or not time or not date:
                    raise ValueError("!!Please make sure all fields are filled!!")
                if booking_type == None or time == None or date == None:
                    raise ValueError("!!Please make sure all fields are selected!!")

                booking_save(userid, booking_type, date, time)  # Save booking details
                message = f"Bo"
            except ValueError as error:
                message = error
                booking_type = ""
                time = ""
                date = ""

            return render_template(
                'booking.html', title='Booking', current_date=current_date, 
                booking_type=booking_type, date=date, time=time, message=message
            )
        return render_template(
            'booking.html', title='Booking', current_date=current_date,
            booking_type="", date="", time="", message=""
        )
    return redirect(url_for('login'))


# Function to calculate energy costs
def calculate_energy_costs(kwh, usage):
    result_daily = kwh * usage  # Calculate daily energy costs
    result_yearly = result_daily * 365  # Calculate yearly energy costs
    result_monthly = result_yearly / 12  # Calculate monthly energy costs

    # Round results for cleaner presentation
    result_daily = round(result_daily, 2)
    result_yearly = round(result_yearly, 2)
    result_monthly = round(result_monthly, 2)

    return result_daily, result_yearly, result_monthly


# Function to calculate carbon footprint emissions based on energy usage
def carbon_footprint_emission(total_kwh):
    # Emission factor for electricity usage (in kg CO2 per kWh)
    emission_factor = 0.233
    # Calculate total carbon emissions
    total_emission = total_kwh * emission_factor
    # Round the result to 2 decimal places for cleaner output
    total_emission = round(total_emission, 2)
    return total_emission


# Route for the tools page
@app.route('/tools', methods=['POST', 'GET'])
def tools():
    """Renders the tools page."""
    userid = session.get('userid')  # Check if user is logged in
    if userid is not None:
        if request.method == 'POST':  # Handle form submission
            result = None  # Default value for results
            message = ""  # Default message for feedback
            carbon_talk = ""  # Default message about carbon emissions

            try:
                # Validate user inputs for energy usage and consumption
                kwh_input = request.form.get('kwh')  # Energy consumption in kWh
                usage_input = request.form.get('usage')  # Daily usage hours

                if not kwh_input or not usage_input:
                    raise ValueError("!!Please make sure all fields are filled!!")

                # Convert inputs to float for calculations
                kwh = float(kwh_input)
                usage = float(usage_input)

                # Ensure input values are greater than zero
                if kwh <= 0 or usage <= 0:
                    raise ValueError("!!Please make sure all fields are above 0!!")

                # Calculate energy costs and carbon emissions
                results = calculate_energy_costs(kwh, usage)
                carbon = carbon_footprint_emission(kwh)

                # Provide feedback based on daily carbon emissions
                if carbon <= 5:
                    carbon_talk = "This is a very good daily carbon emission, keep it up! Visit our information page to see if you could be doing even more!"
                elif carbon > 5 and carbon <= 20:
                    carbon_talk = "A balanced daily carbon emission, not bad :) Make sure to visit our information page to see how you can reduce this!"
                else:
                    carbon_talk = "This is quite a high amount of carbon emission. Could you be doing more? Visit our information page to see how you can improve!"

            # Handle validation errors
            except ValueError as error:
                message = str(error)  # Display error message
                results = [0, 0, 0]  # Set default results
                carbon = 0  # Set default carbon emissions

            # Handle other unexpected errors
            except Exception:
                message = "!!Invalid Entry, Please check your inputs!!"
                results = [0, 0, 0]  # Set default results
                carbon = 0  # Set default carbon emissions

            # Render the tools page with calculated results
            return render_template(
                'tools.html', title="Tools", 
                result_daily=results[0], result_yearly=results[1], result_monthly=results[2], 
                carbon=carbon, carbon_talk=carbon_talk, message=message
            )

        # Default rendering for GET request
        return render_template(
            'tools.html', title="Tools", 
            result_daily=0, result_yearly=0, result_monthly=0, 
            carbon=0, carbon_talk="", message=""
        )
    return redirect(url_for('login'))  # Redirect to login if user is not logged in


# Route for the account page
@app.route('/account', methods=['POST', 'GET'])
def account():
    """Renders the account page.""" 
    userid = session.get('userid')  # Check if user is logged in
    if userid is not None:
        # Fetch user details, booking information, and saved cards
        userinfo = get_userdeatils(userid)
        bookings = get_bookinginfo(userid)
        cards = get_cardinfo(userid)

        if request.method == 'POST':  # Handle form submission for saving card details
            save = request.form.get('save-card')  # Check if save-card action was triggered
            if save is not None:
                # Get card details from the form
                cardholder_name = request.form.get('cardholder-name')
                card_number = request.form.get('card-number')
                billing_address = request.form.get('billing-address')
                expiration_date = request.form.get('expiration-date')

                # Save payment details
                payment_save(userid, cardholder_name, card_number, billing_address, expiration_date)

            # Redirect to account page after POST
            return redirect(url_for('account'))

        # Render the account page with user details
        return render_template(
            'account.html', title='Account', year=datetime.now().year,
            message='Your application description page.',
            fname=userinfo[0], lname=userinfo[1], email=userinfo[2],
            bookings=bookings, cards=cards
        )

    return redirect(url_for('login'))  # Redirect to login if user is not logged in
