import json
import os
from flask import Flask, render_template, session, redirect, url_for
from flaskext.mysql import MySQL
from flask_restful import Api, request, Resource
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


@app.route('/signout')
def signout():
        return render_template('templates/production/login.html')


@app.route('/success')
def success():
    if 'username' in session:
        return render_template('templates/production/user_dashboard.html', data=login_user.get_data(),
                               amount=login_user.get_amount(), password=login_user.get_password())

    else:
        return render_template('templates/production/login.html')


@app.route('/allusers')
def allusers():
    if 'username' in session:
        if login_user.get_all_data():

            return render_template('templates/production/get_all_data.html',
                                   data=login_user.get_all_data(), login_data=login_user.get_data(),
                                   amount=login_user.get_amount(), password=login_user.get_password())
        else:
            return render_template('templates/production/page_403.html')

    else:
        return render_template('templates/production/login.html')


@app.route('/changepassword')
def changepassword():
    if 'username' in session:
        return render_template('templates/production/change_password.html')

    else:
        return render_template('templates/production/login.html')


@app.route('/amountupdate')
def amountupdate():
    if 'username' in session:
        return render_template('templates/production/update_amount.html', amount=login_user.get_amount())

    else:
        return render_template('templates/production/login.html')


# Logout the user
class SignOutUser(Resource):
    def get(self):
        try:
            login_user.set_userid("")
            login_user.set_username("")
            login_user.set_password("")
            login_user.set_firstname("")
            login_user.set_lastname("")
            login_user.set_amount("")
            login_user.set_isadmin("")
            login_user.set_data("")
            login_user.set_all_data("")
            session.pop('username', None)
            return redirect(url_for('signout'))

        except Exception as exception:
            return {'error': str(exception)}


# Sign In Already Created User
class SignIn(Resource):
    def get(self):
        if 'username' in session:
            return redirect(url_for('success', name=login_user.get_username()))
        else:
            return render_template('templates/production/login.html')

    def post(self):
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


# Show All Created Users
class GetAllData(Resource):
    def get(self):
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            sp_get_all = "SELECT * FROM `User`"
            cursor.execute(sp_get_all)
            data = cursor.fetchall()
            if login_user.get_isadmin() == 1:
                login_user.set_all_data(data)
                 # return data
                return redirect(url_for('allusers'))
            else:
                return redirect(url_for('allusers'))

        except Exception as exception:
            return {'error': str(exception)}


# Update Method to update the Password
class UpdatePassword(Resource):
    def get(self):
        if 'username' in session:
            return render_template('templates/production/change_password.html')
        else:
            return render_template('templates/production/login.html')

    def post(self):
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


# Update Method to update the Amount after Adding and Deducting
class UpdateAmount(Resource):
    def get(self):
        if 'username' in session:
            return render_template('templates/production/update_amount.html', amount=login_user.get_amount())
        else:
            return render_template('templates/production/login.html')

    def post(self):
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


# Delete Method to delete user

class DeleteUser(Resource):
    def delete(self, delt_username):
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
class SignUp(Resource):
    def get(self):
        if 'username' in session:
            return redirect(url_for('success', name=login_user.get_username()))
        else:
            return render_template('templates/production/login.html#signup')

    def post(self):
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
                return redirect(url_for('success'))
                # return {'StatusCode': '200', 'Message': 'User creation success'}
            else:
                return 'Username Exist'+str(is_admin)
                # return {'StatusCode': '1000', 'Message': str(data[0])}

        except Exception as exception:
            return {'error': str(exception)}


api.add_resource(SignIn, '/SignInUser')
api.add_resource(SignUp, '/SignUpUser')
api.add_resource(SignOutUser, '/SignOutUser')
api.add_resource(GetAllData, '/GetDataAll')
api.add_resource(UpdatePassword, '/UpdatePassword')
api.add_resource(UpdateAmount, '/UpdateAmount')
api.add_resource(DeleteUser, '/DeleteUser/<username>')


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
