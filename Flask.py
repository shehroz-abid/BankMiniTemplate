import json
import os
from flask import Flask, render_template, session, redirect, url_for
from flaskext.mysql import MySQL
from flask_restful import Api, request
from MainUser import MainUser


app = Flask(__name__, template_folder='.')
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'BankDB'
app.secret_key = os.urandom(24)

mysql.init_app(app)
api = Api(app)

login_user = MainUser()


# Home Page

@app.route('/')
def main():
    try:
        if 'username' in session:
            return redirect(url_for('success', name=login_user.get_username()))

        else:
            return render_template('templates/production/login.html')

    except Exception as exception:
        return {'error': str(exception)}


# Logout the user

@app.route('/SignOut', methods=['GET'])
def sign_out():
    try:
        login_user.set_userid("")
        login_user.set_username("")
        login_user.set_password("")
        login_user.set_firstname("")
        login_user.set_lastname("")
        login_user.set_amount("")
        login_user.set_isadmin("")
        login_user.set_data("")
        session.pop('username', None)
        return render_template('templates/production/login.html')

    except Exception as exception:
        return {'error': str(exception)}


@app.route('/success')
def success():
    if 'username' in session:
        return render_template('templates/production/user_dashboard.html', data=login_user.get_data(),
                               amount=login_user.get_amount(), password=login_user.get_password())

    else:
        return render_template('templates/production/login.html')


# Sign In Already Created User

@app.route('/SignInUser', methods=['POST', 'GET'])
def sign_in_user():

    if request.method == 'POST':

        try:
            username = request.form['username']
            password = request.form['password']

            conn = mysql.connect()
            cursor = conn.cursor()

            sp_sign_in_user = "SELECT * FROM `User` WHERE `username`= %s"
            cursor.execute(sp_sign_in_user, username)

            data = cursor.fetchall()
            login_user.set_data(data)
            # data2 = json.dumps(data)

            if len(data) > 0:
                if data[0][2] == password:
                    login_user.set_userid(data[0][0])
                    login_user.set_username(data[0][1])
                    login_user.set_password(data[0][2])
                    login_user.set_firstname(data[0][3])
                    login_user.set_lastname(data[0][4])
                    login_user.set_amount(data[0][5])
                    login_user.set_isadmin(data[0][6])

                    session['username'] = login_user.get_username()
                    return redirect(url_for('success', name=login_user.get_username()))
                    # return render_template('dashboard.html', data = login_user.get_data(),
                    #                       amount=login_user.get_amount(), password=login_user.get_password())
                    # return {'Username': username, 'Password': password}
                else:
                    return 'InVLD PASS'
            else:
                return 'USERNAMEInvalid'
                # return {'status': 100, 'message': 'Authentication failure'}

        except Exception as exception:
            return {'error': str(exception)}

    elif 'username' in session:
        return redirect(url_for('success', name=login_user.get_username()))
    else:
        return render_template('templates/production/login.html')


# Show All Created Users

@app.route('/GetDataAll', methods=['GET'])
def get_all_data():

    # data_string = "abc"
    try:

        conn = mysql.connect()
        cursor = conn.cursor()

        sp_get_all = "SELECT * FROM `User`"
        cursor.execute(sp_get_all)
        data = cursor.fetchall()
        if login_user.get_isadmin() == 1:
            return render_template('templates/production/get_all_data.html', data=data, login_data=login_user.get_data())
        else:
            return render_template('templates/production/page_403.html')

    except Exception as exception:
        return {'error': str(exception)}


# Update Method to update the Password

@app.route('/UpdatePassword', methods=['POST', 'GET'])
def update_password():
    if request.method == 'POST':

        try:

            old_password = request.form['old_password']
            new_password = request.form['new_password']
            conn = mysql.connect()
            cursor = conn.cursor()

            if old_password == login_user.get_password():

                sp_update_amount = "UPDATE `User` SET `password` = %s WHERE `User`.`username` = %s"
                cursor.execute(sp_update_amount, (new_password, login_user.get_username()))
                conn.commit()

                login_user.set_password(new_password)
                return redirect(url_for('success', name=login_user.get_username()))
                # return {'StatusCode': '200', 'Message': 'User Amount updated success'}
            else:
                return 'PSWRD INValid'

        except Exception as exception:
            return {'error': str(exception)}

    elif 'username' in session:
        return render_template('templates/production/change_password.html')
    else:
        return render_template('templates/production/login.html')


# Update Method to update the Amount after Adding and Deducting

@app.route('/UpdateAmount', methods=['POST', 'GET'])
def update_amount():
    if request.method == 'POST':
        try:
            amount = int(request.form['updated_amount'])
            new_amount = 0
            user_amount = int(login_user.get_amount())
            new_amount = user_amount + amount

            conn = mysql.connect()
            cursor = conn.cursor()

            sp_update_amount = "UPDATE `User` SET `amount` = %s WHERE `User`.`username` = %s"
            cursor.execute(sp_update_amount, (new_amount, login_user.get_username()))
            conn.commit()

            login_user.set_amount(new_amount)

            return redirect(url_for('success', name=login_user.get_username()))
            # return {'StatusCode': '200', 'Message': 'User Amount updated success'}

        except Exception as exception:
            return {'error': str(exception)}

    elif 'username' in session:
        return render_template('templates/production/update_amount.html', amount=login_user.get_amount())
    else:
        return render_template('templates/production/login.html')


# Delete Method to delete user

@app.route('/DeleteUser/<string:delt_username>', methods=['DELETE'])
def delete_user(delt_username):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        sp_check_admin = "SELECT `is_admin` FROM `User` WHERE `username` = %s"
        cursor.execute(sp_check_admin, login_user.get_username())

        data = cursor.fetchall()

        if data[0][0] == 0:

            return 'NOOK'
            # abort(404, message="User is not admin".format(login_user.get_username()))
            # return {"You Are Not Admin"}

        elif data[0][0] == 1:
            sp_delete_user = "DELETE FROM `User` WHERE `User`.`username` = %s"
            cursor.execute(sp_delete_user, delt_username)
            conn.commit()

            return 'OKDone'
            # return {'StatusCode': '200', 'Message': 'User Deleted success'}

    except Exception as exception:
        return {'error': str(exception)}


# Sign Up Or Create New User

@app.route('/SignUpUser', methods=['POST', 'GET'])
def sign_up_user():
    if request.method == 'POST':
        try:
            username = request.form['new_username']
            password = request.form['new_password']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            amount = request.form['amount']
            is_admin = request.form['is_admin']
            conn = mysql.connect()
            cursor = conn.cursor()

            if request.form['is_admin'] == 'admin':
                is_admin = 1
            else:
                is_admin = 0

            sp_check_exist = "SELECT * FROM User WHERE username = %(username)s"
            cursor.execute(sp_check_exist, {'username': username})
            data = cursor.fetchall()
            if len(data) is 0:
                sp_sign_up = "INSERT INTO `User` " \
                            "(`username`, `password`, `firstname`, `lastname`, `amount`, `is_admin`)" \
                            " VALUES (%s,%s,%s,%s,%s,%s);"
                cursor.execute(sp_sign_up, (username, password, firstname, lastname, amount, is_admin))
                conn.commit()
                return render_template('templates/production/login.html')
                # return {'StatusCode': '200', 'Message': 'User creation success'}
            else:
                return 'Username Exist'+str(is_admin)
                # return {'StatusCode': '1000', 'Message': str(data[0])}

        except Exception as exception:
            return {'error': str(exception)}

    else:
        return render_template('templates/signup.html')


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
