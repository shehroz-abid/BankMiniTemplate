
class MainUser:
    def __init__(self):
        self.userid = ""
        self.username = ""
        self.password = ""
        self.firstname = ""
        self.lastname = ""
        self.isadmin = ""
        self.amount = ""
        self.data = ""

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_userid(self):
        return self.userid

    def set_userid(self, userid):
        self.userid = userid

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def get_password(self):
        return self.password

    def set_password(self, password):
        self.password = password

    def get_firstname(self):
        return self.firstname

    def set_firstname(self, firstname):
        self.firstname = firstname

    def get_lastname(self):
        return self.lastname

    def set_lastname(self, lastname):
        self.lastname = lastname

    def get_amount(self):
        return self.amount

    def set_amount(self, amount):
        self.amount = amount

    def get_isadmin(self):
        return self.isAdmin

    def set_isadmin(self, isadmin):
        self.isadmin = isadmin


