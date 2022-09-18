class User:
    def __init__(self, _uid, _phone_number, _password, _display_name, _age):
        self._uid = _uid
        self._phone_number = _phone_number
        self._password = _password
        self._display_name = _display_name
        self._age = _age
        self._email = ""

    def getuid(self):
        return self._uid

    def setphonenumber(self, phone_number):
        self._phone_number = phone_number

    def getphonenumber(self):
        return self._phone_number

    def setpassword(self, password):
        self._password = password

    def getpassword(self):
        return self._password

    def getdisplayname(self):
        return self._display_name

    def getage(self):
        return self._age

    def setemail(self, email):
        self._email = email

    def getemail(self):
        return self._email
