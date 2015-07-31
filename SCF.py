from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui
from PyQt4 import QtCore
import firebirdsql
import re

class mainForm(QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.setGeometry(300, 300, 350, 200)
        self.setWindowTitle('Агент управления СКФ')

        button1 = QtGui.QPushButton('Выход',self)
        self.button2 = QtGui.QPushButton('Включить режим белых списков доступа',self)
        self.button3 = QtGui.QPushButton('Включить режим чёрных списков доступа',self)
        button4 = QtGui.QPushButton('Редактировать списки доступа',self)

        button1.setGeometry(180, 160, 160, 35)        # exit
        self.button2.setGeometry(60, 40, 230, 30)     # white
        self.button3.setGeometry(60, 75, 230, 30)     # black
        button4.setGeometry(60, 110, 230, 30)         # urllist window
        
        cur.execute("select aclfk from schools where schoolid = '" + schId[0] + "'")
        aclName = cur.fetchone()
        if str(aclName[0]) == '1':
            self.button3.setEnabled(False)
            modeName = 'Режим чёрных списков доступа'
        else:
            self.button2.setEnabled(False)
            modeName = 'Режим белых списков доступа'
        
        headLabel = QtGui.QLabel('Сейчас активен:', self)
        self.modeLabel = QtGui.QLabel(modeName, self)

        headLabel.setGeometry(10, 10, 85, 20)
        self.modeLabel.setGeometry(100, 10, 200, 20)   
        
        button1.clicked.connect(lambda: self.on_button(1))
        self.button2.clicked.connect(lambda: self.on_button(2))
        self.button3.clicked.connect(lambda: self.on_button(3))
        button4.clicked.connect(lambda: self.editWindow())

    def on_button(self, n):
        if n == 1:
            conn.commit()
            conn.close()
            sys.exit(app.exec_())
        elif n == 2:
            self.button2.setEnabled(False)
            self.button3.setEnabled(True)
            modeName = 'Режим белых списков доступа'
            updSQL = "update schools set aclfk = '2' where schoolid = '" + schId[0] + "'"
        elif n == 3:
            self.button3.setEnabled(False)
            self.button2.setEnabled(True)
            modeName = 'Режим чёрных списков доступа'
            updSQL = "update schools set aclfk = '1' where schoolid = '" + schId[0] + "'"

        cur.execute(updSQL)
        self.modeLabel.setText(modeName)

    def editWindow(self):
        self.mng = manageLists()
        self.mng.show()
  
class loginForm(QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setGeometry(300, 300, 350, 200)
        self.setWindowTitle('Вход в систему')

        self.loginField = QtGui.QLineEdit(self)
        self.passField = QtGui.QLineEdit(self)
        self.passField.setEchoMode(QLineEdit.Password)
        
        loginLabel = QtGui.QLabel('Имя пользователя:', self)
        passLabel = QtGui.QLabel('Пароль:', self)
        self.errLabel = QtGui.QLabel(' ', self)
        
        loginButton = QtGui.QPushButton('Войти',self)
        cancelButton = QtGui.QPushButton('Отмена',self)
        
        self.loginField.setGeometry(140, 25, 170, 25)
        self.passField.setGeometry(140, 65, 170, 25)
        
        loginLabel.setGeometry(30, 25, 160, 25)
        passLabel.setGeometry(30, 65, 160, 25)
        self.errLabel.setGeometry(30, 100, 250, 25)
        
        loginButton.setGeometry(180, 140, 120, 35)
        cancelButton.setGeometry(30, 140, 120, 35)
        
        loginButton.clicked.connect(lambda: self.logIn())
        cancelButton.clicked.connect(lambda: sys.exit(app.exec_()))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif event.key() == QtCore.Qt.Key_Return:
            self.logIn()

    def logIn(self):
        login = self.loginField.text().upper()
        password = self.passField.text()
        try:
            global conn
            conn = firebirdsql.connect(host='', database='', user='', password='')
            global cur
            cur = conn.cursor()
            try:
                cur.execute("select passwd from SYS_USERS where LOGIN = '" + login + "'")
                passwd = cur.fetchone()
                if password == passwd[0]:
                    cur.execute("select distinct(sr.records) from SYS_RECORDSFILTER sr, SYS_AU_URS sau, SYS_USERS su where su.SYS_GUID = sau.userfk and sau.SYS_GUID = sr.SYS_GUIDFK and su.LOGIN = '" + login + "'")
                    global schId
                    schId = cur.fetchone()
                    self.nwd = mainForm()
                    self.close()
                    self.nwd.show()
                else:
                    self.errLabel.setText('Неверные имя пользователя или пароль')
            except:
                self.errLabel.setText('Неверные имя пользователя или пароль')
        except TimeoutError or AttributeError:
            self.errLabel.setText('Не удаётся подключиться к серверу')
    
class manageLists(QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.setGeometry(300, 300, 500, 400)
        self.setWindowTitle('Редактирование списков')

        self.myListWidget = QtGui.QListWidget(self)
        self.myListWidget.setGeometry(10, 50, 480, 240)

        urlLabel = QtGui.QLabel('Адрес сайта:', self)
        self.urlString = QtGui.QLineEdit(self)

        listsExitButton = QtGui.QPushButton('Закрыть',self)
        listsAddButton = QtGui.QPushButton('Добавить',self)
        listsDeleteButton = QtGui.QPushButton('Удалить',self)
        listsImportButton = QtGui.QPushButton('Импорт из файла',self)

        self.listsBlackButton = QtGui.QPushButton('Чёрный список',self)
        self.listsWhiteButton = QtGui.QPushButton('Белый список',self)

        urlLabel.setGeometry(10, 310, 80, 25)
        self.urlString.setGeometry(100, 310, 390, 25)
                
        listsExitButton.setGeometry(390, 350, 100, 35)
        listsAddButton.setGeometry(120, 350, 100, 35)
        listsDeleteButton.setGeometry(10, 350, 100, 35)
        listsImportButton.setGeometry(230, 350, 100, 35)        

        self.listsBlackButton.setGeometry(30, 10, 190, 35)
        self.listsWhiteButton.setGeometry(280, 10, 190, 35)

        self.getUrlList('BLACKLIST')
        self.checkedTable = 'BLACKLIST'
        self.listsBlackButton.setEnabled(False)
        
        listsExitButton.clicked.connect(lambda: self.close())
        listsAddButton.clicked.connect(lambda: self.insUrlList())
        listsDeleteButton.clicked.connect(lambda: self.delUrlList())
        listsImportButton.clicked.connect(lambda: self.importList())
        
        self.listsBlackButton.clicked.connect(lambda: self.getUrlList('BLACKLIST'))
        self.listsWhiteButton.clicked.connect(lambda: self.getUrlList('SCFLIST'))

    def getUrlList(self, nameTable):
        self.myListWidget.clear()
        getUrlSQL = "select URL from " + nameTable + " where SYS_GUIDFK = '" + schId[0] + "'"
        if nameTable == 'BLACKLIST':
            self.listsBlackButton.setEnabled(False)
            self.listsWhiteButton.setEnabled(True)
            cur.execute(getUrlSQL)
            for url in cur.fetchall():
                item = QtGui.QListWidgetItem(str(url[0]))
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.myListWidget.addItem(item)
            self.checkedTable = 'BLACKLIST'
        else:
            self.listsWhiteButton.setEnabled(False)
            self.listsBlackButton.setEnabled(True)
            cur.execute(getUrlSQL)
            for url in cur.fetchall():
                item = QtGui.QListWidgetItem(str(url[0]))
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.myListWidget.addItem(item)
            self.checkedTable = 'SCFLIST'

    def validateInsert(self, myUrl):
        testResult = 2  # good
        validateTest = re.match(
    r'^(?:http|ftp)s?://|' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
    r'(?::\d{1,5})?' # optional port
    r'(?:/?|[/?]\S+)$', self.urlString.text(), re.IGNORECASE)
        if validateTest:
            for index in range(self.myListWidget.count()):          
                if self.urlString.text() == self.myListWidget.item(index).text():
                    testResult = 0 # not unique
                    break
        else:
            testResult = 1 # not correct
        return testResult
                
    def insUrlList(self):
        if self.urlString.text() != '':
            if self.validateInsert(self.urlString.text()) == 2:
                insUrlSQL = "insert into " + self.checkedTable + " (SYS_GUIDFK, URL) values (" + schId[0] + ", '" + self.urlString.text() + "')"
                cur.execute(insUrlSQL)
                self.getUrlList(self.checkedTable)
                self.urlString.setText("")
            elif self.validateInsert(self.urlString.text()) == 0:
                QMessageBox.information(self, 'Добавление записи отменено', self.urlString.text() + '\nВведённый адрес сайта уже имеется в текущем списке', QMessageBox.Ok)
            elif self.validateInsert(self.urlString.text()) == 1:
                QMessageBox.information(self, 'Добавление записи отменено', self.urlString.text() + '\nВведён некорректный адрес', QMessageBox.Ok)
            
    def delUrlList(self):
        for index in range(self.myListWidget.count()):
            checkedState = self.myListWidget.item(index).checkState()
            if checkedState == 2:
                delUrlSQL = "delete from " + self.checkedTable + " where URL = '" + self.myListWidget.item(index).text() + "' and SYS_GUIDFK = " + schId[0]
                cur.execute(delUrlSQL)
        self.getUrlList(self.checkedTable)

    def importList(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '')
        if filename != '':
            with open(filename) as urlFile:
                urlList = [line.rstrip('\n') for line in urlFile]
                for lines in urlList:
                    self.urlString.setText(lines)
                    self.insUrlList()
                    self.urlString.setText('')
            urlFile.close()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = loginForm()
    form.show()
    app.exec_()
