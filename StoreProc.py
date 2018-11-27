class Stproc:
    def __init__(self):

        self.cpCheckExist = 'SELECT * FROM User WHERE username = "username"'
        self.cpSignUpUser = 'INSERT INTO User VALUES (userid, username, password, firstname, lastname, amount, isAdmin)'
        self.sp_SignInUser = 'SELECT * FROM User WHERE username = "username"'
        self.sp_GetAmount = 'SELECT amount FROM User WHERE username="username"'
        self.sp_updateAmount = 'UPDATE User SET amount = "newamount" WHERE username = "username"'
        self.sp_checkAdmin = 'SELECT isAdmin FROM User WHERE username="current_username'
        self.sp_deleteUser= 'DELETE FROM User WHERE userid="userid"'
