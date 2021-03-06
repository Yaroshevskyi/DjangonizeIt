"""
    Info EN
                            'Djangonize It!' - A single-file application (Also, it is a single-window now!)
        The purpose of this application is to simplify work with images for Django developers.
        For successful using, you should to install the app into "images" folder inside the "static" folder of your
    django project (../static/../images/). This solution simultaneously supporting the recommended file
    structure of django projects and allows to avoid additional user and program activities related with path setting
    for image download. The installed PyQt4 is, also, needed.
        The application allows to perform the next operations:
        1. Search and replacement image links on django-links at frontend (HTML, CSS) files. Search is RegEx driven.
           The application have default regular expressions for CSS and HTML files, which can be changed by user (this
           is necessary for cases when name of folder with images isn't "images").
           When you run the djangonization process for the file, it isn't replaced. The app creates a copy of file
           at folder with original. Copy's name is forming as a "[0-9]old name", which allow to simplify it searching at
           folder (it was at the top or bottom). Also, created file can be opened from the program by os explorer.
        2. Download images from Internet by link (in images folder) and return valid link for user's django project.
           All results of operation are archiving (in "db.txt" at folder with program). Also, the class to simplify
           work with logs is realized. It supports sorting by name/django link/date. Also, searching can be performed
           by normal and RegEx strings.
        The application is created in object-oriented style.
    ----------------------------------------------------------
        This is an UX (user experience) version of DjangonizeIt application.
        The inheritance structure is simplified here. All child classes aren't inherit parent constructor
    (they are more independent). Maximal depth of inheritance is, also, reduced:

     PyQT Parent |          QtGui.QWidget                  QtGui.QSortFilterProxyModel          QtGui.QDialog
     Parent      |    Welcome          DjangoImages             SortFilterHistory                   Main
     1st Child   |                DjangoFiles     History

        Class attributes from magic method __call__ is transferred to internal method _view. Most of class attributes
     from constructor are, also transferred to internal methods and just calling from their constructors.
        The user interface became more friendly.

"""

import os
import sys
import re
from urllib.request import URLopener
from datetime import datetime
from random import randint
from PyQt4 import QtGui, QtCore

class Welcome(QtGui.QWidget):
    """Class-greeting.
    The purpose of this class is to give a feeling that this app is user friendly!

    """
    welcomeText = [
                   ["Hello, I'm UX version of DjangonizeIt! and I'm user friendly!", "Move me into the 'images' folder "
                    "inside the 'static' folder\nof your django project (../static/../images/) and \n"
                    "I will perform a lot of routine work instead of you!"],
                   ["I'm able to:", "1. Download your images from web and return you django links for them.\n"
                                    "\tChoose tab 'Images' if you need this\n"
                                    "2. Remember information about every image which I downloaded for you!\n"
                                    "\tChoose tab 'Images History' if you need this info\n"
                                    "3. Replace non django links in your HTML and CSS files on django links.\n"
                                    "\tChoose tab 'Files' if you need this\n"],
                   ["My hobby:", "Hide and seek"]
                  ]
    def __init__(self):
        super().__init__()
        self._view()
        self.show()

    def _view(self):
        # Contains information about positioning of elements at window
        self._groupboxes()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.helloGroupBox)
        mainLayout.addWidget(self.abilityGroupBox)
        mainLayout.addWidget(self.hobbyGroupBox)
        self.setLayout(mainLayout)

    def _groupboxes(self):
        self.helloGroupBox, self.abilityGroupBox, self.hobbyGroupBox = map(self._welcome_box, self.welcomeText)

    def _welcome_box(self, text, fontsize=9, style="color: rgb(10, 15, 150)"):
        #Transform list to GroupBox
        textLabel = QtGui.QLabel(text[1], self)
        font = QtGui.QFont()
        font.setPointSize(fontsize)
        textLayout = QtGui.QGridLayout()
        textLabel.setFont(font)
        textLayout.addWidget(textLabel, 0, 0)
        blockGroupBox = QtGui.QGroupBox(text[0])
        blockGroupBox.setFont(font)
        blockGroupBox.setLayout(textLayout)
        textLabel.setStyleSheet(style)
        blockGroupBox.setStyleSheet(style)
        return blockGroupBox


class DjangoImages(QtGui.QWidget):
    ''' Parent of functional classes of application (contains elements constructors and default variables).
    Download images from Web, return django-links, log the result.

    '''
    NOW = datetime.now()                # Constant for logs
    bFontSize = 10                      # Default font size for buttons
    bStyle = "color: rgb(0, 85, 200);"  # Default stylesheet for buttons
    lFontSize = 10                      # Default font size for labels
    lStyle = "color: rgb(0, 85, 200);"  # Default stylesheet for labels
    database = "db.txt"                 # Default name of database (for logs)
    defaultCSS = r'\.\..*/images/'      # Default pattern for re.sub function for CSS (DjangoFiles().djangonize())
    defaultHTML = r'src=\".*images/(.*\.[a-z]{3})\"'  # Default pattern for re.sub function for HTML

    def __init__(self):
        super().__init__()
        self._view()

    def _view(self):
        # Contains information about positioning of elements at window
        self._elements()

        self._linkgroupbox()
        self._namegroupbox()
        self._buttonsgroupbox()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.linkGroupBox)
        mainLayout.addWidget(self.nameGroupBox)
        mainLayout.addWidget(self.buttonsGroupBox)
        self.setLayout(mainLayout)

    def _elements(self):
        # Buttons
        self.djangonizeButton = self.create_button("Djangonize It!", self.djangonize,
                                                   tooltip="Download image,return django link, log the result")
        self.quitButton = self.create_button('Quit', self.quit_app(), tooltip="Close All Windows")
        self.emptyLabel = self.create_label("\t     ")  # Filler for buttonsLayout

        # Lines
        self.linkText = self.create_text_edit(tooltip="Enter the image URL here. "
                                                      "Like: https://www.example.com/image.png")
        self.nameLine = self.create_line_edit(tooltip="Enter the new filename here. "
                                                      "Like: image")
        self.djangoLine = self.create_line_edit(tooltip="A django link will arise here after djangonization")

    def _linkgroupbox(self):
        linkLayout = QtGui.QGridLayout()
        linkLayout.addWidget(self.linkText, 0, 0)

        self.linkGroupBox = QtGui.QGroupBox("URL:")
        self.linkGroupBox.setLayout(linkLayout)
        return  self.linkGroupBox

    def _namegroupbox(self):
        nameLayout = QtGui.QGridLayout()
        nameLayout.addWidget(self.nameLine, 1, 0)

        self.nameGroupBox = QtGui.QGroupBox("Filename:")
        self.nameGroupBox.setLayout(nameLayout)
        return  self.nameGroupBox

    def _buttonsgroupbox(self):
        buttonsLayout = QtGui.QGridLayout()
        buttonsLayout.addWidget(self.djangonizeButton, 0, 3)
        buttonsLayout.addWidget(self.quitButton, 2, 5)
        buttonsLayout.addWidget(self.emptyLabel, 2, 0)
        buttonsLayout.addWidget(self.djangoLine, 1, 3)

        self.buttonsGroupBox = QtGui.QGroupBox("Djangonization and Control buttons:")
        self.buttonsGroupBox.setLayout(buttonsLayout)
        return  self.buttonsGroupBox

    # Element constructors
    def create_button(self, text, activity, tooltip=None, fontsize=int(bFontSize), style=bStyle):
        button = QtGui.QPushButton(text, self)
        button.clicked.connect(activity)
        button.setToolTip(tooltip)
        font = QtGui.QFont()
        font.setPointSize(fontsize)
        font.setBold(True)
        font.setWeight(75)
        button.setFont(font)
        button.setStyleSheet(style)
        return button

    def create_label(self, text, fontsize=int(lFontSize), style=str(lStyle)):
        label = QtGui.QLabel(text, self)
        font = QtGui.QFont()
        font.setPointSize(fontsize)
        font.setBold(True)
        font.setWeight(75)
        label.setFont(font)
        label.setStyleSheet(style)
        return label

    def create_text_edit(self, tooltip=None):
        textEdit = QtGui.QTextEdit()
        textEdit.setToolTip(tooltip)
        return textEdit

    def create_line_edit(self, tooltip=None):
        lineEdit = QtGui.QLineEdit()
        lineEdit.setToolTip(tooltip)
        return lineEdit

    def create_combo_box(self, text=""):
        # Element constructor for DjangoFiles
        comboBox = QtGui.QComboBox()
        comboBox.setEditable(True)
        comboBox.addItem(text)
        return comboBox

    def dir_list(self):
        # Method which returns list of folders before static folder (in django structure). Optimized for Linux
        if os.name == 'nt':
            pathList = re.findall(r'static\\(.+).*$', os.getcwd()) # path is saved as a list with one element
            try:
                dirList = pathList[0].split('\\')
            except IndexError:  # Error when list is empty (for cases when the application isn't installed)
                QtGui.QMessageBox.information(self, "InstallError",
                                          "Please, move the program inside your django project "
                                          "(..\static\..\images)to solve the Error!")
                raise
            return dirList
        else:
            pathList = re.findall(r'static/(.+).*$', os.getcwd())
            try:
                dirList = pathList[0].split('/')
            except IndexError:
                QtGui.QMessageBox.information(self, "InstallError",
                                          "Please, move the program inside your django project "
                                          "(../static/../images)to solve the Error!")
                raise
            return dirList

    def djangonize(self):
        # Download image and return its django-link (Overridable)
        url = str(self.linkText.toPlainText())
        if re.search(r'\.[a-z]{3}$', url):           # Validate link by type of file
            filename = str(self.nameLine.displayText())

            if len(filename) == 0:        # If the filename line is empty save the image with its basename
                newFilename = os.path.basename(url)
            else:                         # Else, save it with entered name and original fileformat
                newFilename = filename + os.path.basename(url)[-4:]

            dirList = self.dir_list()

            # If with dir_list() all is ok, download image to django directory
            # If statement don't used here, because any Exception in dir_list() stop execution of the method
            URLopener().retrieve(str(url), newFilename)

            # Return the link to user interface
            djangoView = "{% static '" + '/'.join(dirList) + '/' + newFilename + " '%}"
            self.djangoLine.setText(djangoView)

            # Log the result
            with open(self.database, "a") as f:
                historyNote = ','.join([newFilename, djangoView, str(self.NOW.year), str(self.NOW.month),
                                       str(self.NOW.day), str(self.NOW.hour), str(self.NOW.minute)])+'\n'
                f.write(historyNote)
        else:
            QtGui.QMessageBox.information(self, "Link is wrong or not exist", "The IMAGE link should be entered!")

    def quit_app(self):
        # Complete quit from app
        return QtCore.QCoreApplication.instance().quit


class History(DjangoImages):
    ''' Class for comfortable work with logs. Ih inherits methods only because design of this class is so different.
    Sort and filter djangonized images (RegEx supports). All info in table can be copied.

    '''
    def __init__(self):
        super().__init__()

    def _view(self):
        # Contains information about positioning of elements at window
        self._elements()

        self.text_filter_changed()
        self.date_filter_changed()

        self._proxygroupbox()
        self._buttonsgroupbox()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.proxyGroupBox)
        mainLayout.addWidget(self.buttonsGroupBox)

        self.setLayout(mainLayout)

    def _elements(self):
        self.proxyModel = SortFilterHistory(self)       # Technical class (PyQt template)
        self.proxyModel.setDynamicSortFilter(True)

        self._proxy()
        self._search_box()
        self._date_boxes()

        # Buttons
        self.openButton = self.create_button('Folder', self.open_folder, tooltip="Open folder with djangonized images")
        self.quitButton = self.create_button('Quit', self.quit_app(), tooltip="Close All Windows")
        self.emptyLabel = QtGui.QLabel()  # Filler for proxyLayout

    def _search_box(self):
        # Search
        self.filterPatternLineEdit =self.create_line_edit()          # Search line
        self.filterPatternLabel = QtGui.QLabel("Filter pattern:")
        self.filterPatternLabel.setBuddy(self.filterPatternLineEdit)

        self.filterSyntaxComboBox = QtGui.QComboBox()                            # Search modes
        self.filterSyntaxComboBox.addItem("Normal", QtCore.QRegExp.FixedString)  # 1st (Default)
        self.filterSyntaxComboBox.addItem("RegEx", QtCore.QRegExp.RegExp)  # 2nd (Switch with Normal to make it default)
        self.filterSyntaxComboBox.setToolTip("Search mode")

    def _date_boxes(self):
        #Dates
        self.fromDateEdit = QtGui.QDateEdit()
        self.fromDateEdit.setDate(QtCore.QDate(2016, 1, 1))
        self.fromDateEdit.setCalendarPopup(True)                   # True calendar
        self.fromLabel = QtGui.QLabel("From:")
        self.fromLabel.setBuddy(self.fromDateEdit)

        self.toDateEdit = QtGui.QDateEdit()
        self.toDateEdit.setDate(QtCore.QDate(2026, 1, 1))
        self.toDateEdit.setCalendarPopup(True)
        self.toLabel = QtGui.QLabel("To:")
        self.toLabel.setBuddy(self.toDateEdit)

        self.filterPatternLineEdit.textChanged.connect(self.text_filter_changed)
        self.filterSyntaxComboBox.currentIndexChanged.connect(self.text_filter_changed)
        self.fromDateEdit.dateChanged.connect(self.date_filter_changed)
        self.toDateEdit.dateChanged.connect(self.date_filter_changed)

    def _proxy(self):
        self.proxyView = QtGui.QTreeView()  # Table view
        self.proxyView.setRootIsDecorated(False)
        self.proxyView.setAlternatingRowColors(True)
        self.proxyView.setModel(self.proxyModel)  # Setting of table for the view
        self.proxyView.setSortingEnabled(True)
        self.proxyView.sortByColumn(1, QtCore.Qt.AscendingOrder)
        self.proxyModel.setSourceModel(self.create_log_table())  # Setting of table for the window

        self.proxyView.setColumnWidth(0, 75)
        self.proxyView.setColumnWidth(1, 240)

    def _proxygroupbox(self):
        proxyLayout = QtGui.QGridLayout()
        proxyLayout.addWidget(self.proxyView, 0, 0, 1, 3)
        proxyLayout.addWidget(self.filterPatternLabel, 1, 0)
        proxyLayout.addWidget(self.filterPatternLineEdit, 1, 1)
        proxyLayout.addWidget(self.filterSyntaxComboBox, 1, 2)
        proxyLayout.addWidget(self.fromLabel, 3, 0)
        proxyLayout.addWidget(self.fromDateEdit, 3, 1, 1, 2)
        proxyLayout.addWidget(self.toLabel, 4, 0)
        proxyLayout.addWidget(self.toDateEdit, 4, 1, 1, 2)

        self.proxyGroupBox = QtGui.QGroupBox("Sort/Filter Links")
        self.proxyGroupBox.setLayout(proxyLayout)
        return  self.proxyGroupBox


    def _buttonsgroupbox(self):
        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.addWidget(self.openButton, 1)
        buttonsLayout.addWidget(self.emptyLabel, 3)
        buttonsLayout.addWidget(self.quitButton, 1)

        self.buttonsGroupBox = QtGui.QGroupBox("Control buttons")
        self.buttonsGroupBox.setLayout(buttonsLayout)
        return self.buttonsGroupBox

    def text_filter_changed(self):
        # Filtering by filter patterns (Normal, RegEx)
        syntax = QtCore.QRegExp.PatternSyntax(
            self.filterSyntaxComboBox.itemData(
                self.filterSyntaxComboBox.currentIndex()))

        regExp = QtCore.QRegExp(self.filterPatternLineEdit.text(), True, syntax)
        self.proxyModel.setFilterRegExp(regExp)

    def date_filter_changed(self):
        # Filtering by dates
        self.proxyModel.set_filter_minimum_date(self.fromDateEdit.date())
        self.proxyModel.set_filter_maximum_date(self.toDateEdit.date())

    def add_log(self,table, name, link, date):
        # Fill row of the table
        table.insertRow(0)
        table.setData(table.index(0, 0), name)
        table.setData(table.index(0, 1), link)
        table.setData(table.index(0, 2), date)

    def create_log_table(self):
        # Create table and fill it by log data
        table = QtGui.QStandardItemModel(0, 3, self)

        table.setHeaderData(0, QtCore.Qt.Horizontal, "Name")
        table.setHeaderData(1, QtCore.Qt.Horizontal, "Djangonized link")
        table.setHeaderData(2, QtCore.Qt.Horizontal, "Date")

        # Fill the table
        try:
            with open(self.database) as f:
                lines = f.readlines()
                for line in lines:
                        line = line.split(',')
                        self.add_log(table, line[0], line[1],           # Name,Link
                                     QtCore.QDateTime(QtCore.QDate(int(line[2]), int(line[3]), int(line[4])),  # Date
                                                                   QtCore.QTime(int(line[5]), int(line[6]))))  # Time'
        except FileNotFoundError:
            pass                        # This is good. We just need to avoid the Error
        return table

    def open_folder(self):
        # Open folder with djangonized images
        return os.system(QtGui.QFileDialog().getOpenFileName(self,'Open Dj-folder', QtCore.QDir.currentPath()))


class DjangoFiles(DjangoImages):
    ''' Class simplify work with website templates for django programmers.
    Djangonize links in CSS and HTML files, save copy of djangonized files in format [0-9]oldname, return name to user.

    '''
    def __init__(self):
        super().__init__()

    def _view(self):
        # Contains information about positioning of elements at window
        self._elements()
        self._filegroupbox()
        self._regexgroupbox()
        self._buttonsgroupbox()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.fileGroupBox)
        mainLayout.addWidget(self.regexGroupBox)
        mainLayout.addWidget(self.buttonsGroupBox)
        self.setLayout(mainLayout)

    def _elements(self):
        # Buttons
        self.browseButton = self.create_button("Browse...", self.browse)
        self.djangonizeButton = self.create_button("Djangonize It!", self.djangonize,
                         tooltip="Make a copy of file where pattern is replaced by django links, return name of copy")
        self.djangonizeLine = self.create_line_edit(
                                        tooltip=" A name of changed file will arise here after djangonization")
        self.openButton = self.create_button("Open It!", self.open_file,
                                         tooltip="Open djangonized file by default program")
        self.quitButton = self.create_button('Quit', self.quit_app(), tooltip="Close All Windows")

        # Lines
        self.regexLine = self.create_line_edit()
        self.regexLine.setText("Choose a CSS or HTML file!")
        self.fileComboBox = self.create_combo_box(QtCore.QDir.currentPath())

    def _filegroupbox(self):

        fileLayout = QtGui.QHBoxLayout()
        fileLayout.addWidget(self.fileComboBox, 4)
        fileLayout.addWidget(self.browseButton, 1)
        self.fileGroupBox = QtGui.QGroupBox("Browse file:")
        self.fileGroupBox.setLayout(fileLayout)
        return self.fileGroupBox

    def _regexgroupbox(self):
        regexLayout = QtGui.QVBoxLayout()
        regexLayout.addWidget(self.regexLine)
        self.regexGroupBox = QtGui.QGroupBox("Pattern for replacement:")
        self.regexGroupBox.setLayout(regexLayout)
        return self.regexGroupBox

    def _buttonsgroupbox(self):
        buttonsLayout = QtGui.QGridLayout()
        buttonsLayout.addWidget(self.djangonizeButton, 0, 2, 1, 3)
        buttonsLayout.addWidget(self.djangonizeLine, 1, 2, 1, 3)
        buttonsLayout.addWidget(self.openButton, 2, 0)
        buttonsLayout.addWidget(self.quitButton, 2, 5)
        self.buttonsGroupBox = QtGui.QGroupBox("Djangonization and Control buttons:")
        self.buttonsGroupBox.setLayout(buttonsLayout)
        return  self.buttonsGroupBox

    def browse(self):
        # Browse file and choose a default RegEx according to file extension
        openedFile = QtGui.QFileDialog.getOpenFileName(self, "Find a CSS or HTML", QtCore.QDir.currentPath())

        if openedFile:                            #add paths to the fileComboBox
            if self.fileComboBox.findText(openedFile) == -1:
                self.fileComboBox.addItem(openedFile)

            self.fileComboBox.setCurrentIndex(self.fileComboBox.findText(openedFile))

        filePath = self.fileComboBox.currentText()

        if filePath[-3:] == "css":
            self.regexLine.setText(self.defaultCSS)
        elif filePath[-3:] == "tml":
            self.regexLine.setText(self.defaultHTML)
        else:
            self.regexLine.setText("Wrong file. Choose a CSS or HTML!")

    def djangonize(self):
        # Method which make files more djangonized! (Overridden method for djangonizeButton)
        filePath = self.fileComboBox.currentText() # Path to file from fileComboBox
        dirList = self.dir_list()         # DjangonizeImage inherited method which returns folders before static folder
        newFilename = str(randint(0, 9)) + os.path.basename(filePath) # Filename where changes will be saved

        if filePath[-3:] == "css":
            djPath = '../' + '/'.join(dirList) + '/'  # Path to images in django project
            nonDjPath = str(self.regexLine.displayText())  # Path to images in CSS for replacement

            if os.name == 'nt':
                with open(os.path.dirname(filePath) + '/' + newFilename, 'w') as f:    # open new
                    content = open(filePath).read()                                    # copy data from old
                    f.write('{% load staticfiles %}\n')                                # connect static files to CSS
                    f.write(re.sub(nonDjPath, djPath, content))                        # replace line and write in new
                    self.djangonizeLine.setText("New filename: " + newFilename)        # return name of new

            else:
                with open(os.path.dirname(filePath) + '\\' + newFilename, 'w') as f:
                    content = open(filePath).read()
                    f.write('{% load staticfiles %}\n')
                    f.write(re.sub(nonDjPath, djPath, content))
                    self.djangonizeLine.setText("New filename: " + newFilename)

        elif filePath[-3:] == "tml":

            djPath = "src=\"{% static '" + '/'.join(dirList) + '/' + "\g<1>" + "' %}\"" # Path to django-project images
            nonDjPath = str(self.regexLine.displayText())  # Path in CSS or HTML for replace

            if os.name == 'nt':
                with open(os.path.dirname(filePath) + '/' + newFilename, 'w') as f:   # Create a new file: [0-9]old name
                    content = open(filePath).read()                              # Open old file and read it content
                    f.write(re.sub(nonDjPath, djPath, content))                  # Replacement is here
                    self.djangonizeLine.setText("New filename: " + newFilename)     # Info for user

            else:
                with open(os.path.dirname(filePath) + '\\' + newFilename, 'w') as f:
                    content = open(filePath).read()
                    f.write(re.sub(nonDjPath, djPath, content))
                    self.djangonizeLine.setText("New filename: " + newFilename)
        else:
            self.djangonizeLine.setText("Wrong file. Choose CSS or HTML!")   # When not CSS or not HTML file is browsed

    def open_file(self):
        # This method open the folder with djangonized files in os explorer and allow choose file for opening
        # It should be called as object not as function
        if re.match(r'New\sfilename', self.djangonizeLine.displayText()):
            if os.name == 'nt':
                os.system(QtGui.QFileDialog().getOpenFileName(self, 'Open Dj-file', '/'.join(
                                                            [os.path.dirname(self.fileComboBox.currentText()),
                                                             re.findall('\S+:\s(\d\S*)',
                                                                        self.djangonizeLine.displayText())[0]])))
            else:
                os.system(QtGui.QFileDialog().getOpenFileName(self, 'Open Dj-file', '\\'.join(
                                                            [os.path.dirname(self.fileComboBox.currentText()),
                                                             re.findall('\S+:\s(\d\S*)',
                                                                        self.djangonizeLine.displayText())[0]])))
        else:
            QtGui.QMessageBox.information(self,'OpenError', 'Djangonize file before opening')


class DjangoTemplates(DjangoFiles):
    exceptions = 'base.html, home.html, index.html'

    def __init__(self):
        super().__init__()

    def _view(self):
        # Contains information about positioning of elements at window
        self._elements()

        self._filegroupbox()
        self.fileGroupBox.setTitle("Browse folder:")

        self._regexgroupbox()
        self.regexGroupBox.setTitle("Except templates:")

        self._buttonsgroupbox()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.fileGroupBox)
        mainLayout.addWidget(self.regexGroupBox)
        mainLayout.addWidget(self.buttonsGroupBox)
        self.setLayout(mainLayout)

    def _elements(self):
        self.fileComboBox = self.create_combo_box(QtCore.QDir.currentPath()) # Inherit CB, Overridden for folders
        self.browseButton = self.create_button("Browse...", self.browse)

        self.regexLine = self.create_line_edit()   # Inherit line, Overridden for work with except templates
        self.regexLine.setText(self.exceptions)

        self.djangonizeButton = self.create_button("DjangonizeIt!", self.find_templates)
        self.djangonizeText = self.create_text_edit()
        self.emptyLabel = QtGui.QLabel()
        self.quitButton = self.create_button("Quit", self.quit_app())

    def _buttonsgroupbox(self):
        buttonsLayout = QtGui.QGridLayout()
        buttonsLayout.addWidget(self.djangonizeButton, 0, 2, 1, 3)
        buttonsLayout.addWidget(self.djangonizeText, 1, 2, 1, 3)
        buttonsLayout.addWidget(self.emptyLabel, 2, 0)
        buttonsLayout.addWidget(self.quitButton, 2, 5)
        self.buttonsGroupBox = QtGui.QGroupBox("Djangonization and Control buttons:")
        self.buttonsGroupBox.setLayout(buttonsLayout)
        return self.buttonsGroupBox

    def browse(self):
        openedDir = QtGui.QFileDialog.getExistingDirectory(self, "Find dir with templates",
                self.fileComboBox.currentText())

        if openedDir:
            if self.fileComboBox.findText(openedDir) == -1:
                self.fileComboBox.addItem(openedDir)

            self.fileComboBox.setCurrentIndex(self.fileComboBox.findText(openedDir))

    def find_templates(self):
        directory = self.fileComboBox.currentText()
        exceptList = self.regexLine.displayText()
        directoryList = os.listdir(directory)

        templates = list(filter(lambda x: x.endswith('.html') if x not in exceptList else None, directoryList))
        self.djangonizeText.setText('I found {} template(s) for djangonization!'.format(len(templates)))
        tempDict = {}
        for template in templates:
            pass

    def open_file(self):
        pass


class Main(QtGui.QDialog):
    """ Start window of the application
    Call the components of the application when buttons is clicking.

    """
    size = 450, 340                     # Default size of application windows (width, height)
    position = 450, 150                 # Default position of application windows (horizontal,vertical)

    def __init__(self):
        super(Main, self).__init__()
        # Buttons (djangonizeButton, openButton, browseButton and quitButton are inherited)
        self._tray_icon_actions()
        self._create_tray_icon()
        self.trayIcon.activated.connect(self.double_click)

        self.trayIcon.show()
        self._view()

    def _view(self):
        # Contains information about positioning of elements at window
        tabWidget = QtGui.QTabWidget()
        tabWidget.addTab(Welcome(), "Welcome")
        tabWidget.addTab(DjangoImages(), "Images")
        tabWidget.addTab(History(), "Images History")
        tabWidget.addTab(DjangoFiles(), "Files")
        tabWidget.addTab(DjangoTemplates(), "Templates")

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(tabWidget)
        self.setLayout(mainLayout)

        self.setWindowTitle('DjangonizeIt! - A single-file application')
        self.resize(*self.size)
        self.move(*self.position)

    def _create_tray_icon(self):
        # Create tray icon and link context menu actions to it
        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(self.minimizeAction)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)

    def _tray_icon_actions(self):
        # Context menu actions for tray icon
        self.minimizeAction = QtGui.QAction("Minimize", self, triggered=self.hide)
        self.restoreAction = QtGui.QAction("Restore", self, triggered=self.show)
        self.quitAction = QtGui.QAction("Quit", self, triggered=QtGui.qApp.quit)

    def double_click(self, event):
        # Restore window by doubleclick
        if event == QtGui.QSystemTrayIcon.DoubleClick:
            self.show()

    def closeEvent(self, event):
        # Intercepts close event (control panel), hide Main and show icon message
        if self.trayIcon.isVisible():
            self.hide()                    #hide Main
            self.trayIcon.showMessage("Tray icon without icon", "Ha-ha, I'm here!")
            event.ignore()


class SortFilterHistory(QtGui.QSortFilterProxyModel):
    ''' Technical class for the History class. (pyQt template)
    Example of the class is used for representing (filtering) of table content by date range.

    '''
    def __init__(self, parent=None):
        super(SortFilterHistory, self).__init__(parent)

        self.minDate = QtCore.QDate()
        self.maxDate = QtCore.QDate()

    def set_filter_minimum_date(self, date):
        self.minDate = date
        self.invalidateFilter()

    def filter_minimum_date(self):
        return self.minDate

    def set_filter_maximum_date(self, date):
        self.maxDate = date
        self.invalidateFilter()

    def filter_maximum_date(self):
        return self.maxDate

    def filter_accepts_row(self, sourceRow, sourceParent):
        index0 = self.sourceModel().index(sourceRow, 0, sourceParent)
        index1 = self.sourceModel().index(sourceRow, 1, sourceParent)
        index2 = self.sourceModel().index(sourceRow, 2, sourceParent)

        return ((self.filterRegExp().indexIn(self.sourceModel().data(index0)) >= 0
                 or self.filterRegExp().indexIn(self.sourceModel().data(index1)) >= 0)
                and self.date_in_range(self.sourceModel().data(index2)))

    def date_in_range(self, date):
        if isinstance(date, QtCore.QDateTime):
            date = date.date()

        return ((not self.minDate.isValid() or date >= self.minDate)
                and (not self.maxDate.isValid() or date <= self.maxDate))


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    view = Main()
    view.show()
    sys.exit(app.exec_())