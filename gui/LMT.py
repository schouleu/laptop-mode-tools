try:
	from PyQt4 import QtGui, QtCore
	print "Using PyQT4"
except ImportError:
	from PySide import QtGui, QtCore
	print "Using PySide"

import os, sys, shutil

try:
        _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
        _fromUtf8 = lambda s: s
        
COMMENT_IDENTIFIER = "#__COMMENT"
CONTROL_IDENTIFIER = "CONTROL_"
CONFIG_DIR = "/etc/laptop-mode/conf.d"

class Log():
	def debug(self, str):
		sys.stderr.write(str + "\n")

	def msg(self, str):
		sys.stdout.write(str + "\n")

	def err(self, str):
		sys.stderr.write(str + "\n")
		
class MainWidget(QtGui.QWidget):
        def __init__(self, parent=None):
                QtGui.QWidget.__init__(self, parent)
                
		# Check for root privileges
		if os.geteuid() != 0:
			QtGui.QMessageBox.critical(self, "Error", "You need to run with root priviliges\nPlease use kdesudo, gksu or sudo/sux")
			sys.exit(1)
		else:
			QtGui.QMessageBox.warning(self, "Warning", "This tool is running with root priviliges")

		# Set Fixed Layout
		self.resize(532, 600)
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
		self.setSizePolicy(sizePolicy)
		self.setMinimumSize(QtCore.QSize(532, 600))
		self.setMaximumSize(QtCore.QSize(532, 600))


                self.layout = QtGui.QVBoxLayout(self)
                self.layout.setContentsMargins(20,70,20,70)
                self.layout.setSpacing(0)
                
                self.scrollArea = QtGui.QScrollArea()
                self.layout.addWidget(self.scrollArea)
                
                self.window = QtGui.QWidget(self)
                self.vbox = QtGui.QVBoxLayout(self.window)
                
                self.configOptions = {}
                self.findConfig(CONFIG_DIR)
                
                self.checkBoxList = {}
                self.configBool = None
                
                for eachOption in self.configOptions.keys():
                        
                        self.readConfig(eachOption, self.configOptions)
                        self.subLayout = QtGui.QHBoxLayout()
                        
                        self.checkBoxName = "checkBox" + "_" + eachOption
                        self.checkBoxList[self.checkBoxName] = QtGui.QCheckBox(self.checkBoxName, self)
                        self.checkBoxList[self.checkBoxName].setObjectName(self.checkBoxName)
                        self.checkBoxList[self.checkBoxName].setText("Enable module %s" % eachOption)
                        
                        if self.tooltip is not '':
                                self.checkBoxList[self.checkBoxName].setToolTip(self.tooltip)
                        else:
                                self.checkBoxList[self.checkBoxName].setToolTip("Configuration settings for %s" % eachOption)
                                
                        if self.configBool is True:
                                self.checkBoxList[self.checkBoxName].setChecked(True)
                        
                        self.subLayout.addWidget(self.checkBoxList[self.checkBoxName])
                        self.vbox.addLayout(self.subLayout)
                self.scrollArea.setWidget(self.window)
                
                self.pushButtonSleep = QtGui.QPushButton(self)
                self.pushButtonSleep.setGeometry(QtCore.QRect(101, 550, 71, 27))
                self.pushButtonSleep.setObjectName(_fromUtf8("pushButtonSleep"))
                self.pushButtonSleep.setToolTip(_fromUtf8("Trigger Suspend to RAM aka Sleep"))
                
                self.pushButtonHibernate = QtGui.QPushButton(self)
                self.pushButtonHibernate.setGeometry(QtCore.QRect(21, 550, 71, 27))
                self.pushButtonHibernate.setObjectName(_fromUtf8("pushButtonHibernate"))
                self.pushButtonHibernate.setToolTip(_fromUtf8("Trigger Suspend to Disk aka Hibernate"))
                
                self.pushButtonApply = QtGui.QPushButton(self)
                self.pushButtonApply.setGeometry(QtCore.QRect(431, 550, 61, 27))
                self.pushButtonApply.setObjectName(_fromUtf8("pushButtonApply"))
                self.pushButtonApply.setToolTip(_fromUtf8("Apply checked changes"))
                
                self.pushButtonDiscard = QtGui.QPushButton(self)
                self.pushButtonDiscard.setGeometry(QtCore.QRect(361, 550, 61, 27))
                self.pushButtonDiscard.setObjectName(_fromUtf8("pushButtonDiscard"))
                self.pushButtonDiscard.setToolTip(_fromUtf8("Exit application"))
                        
                self.label = QtGui.QLabel(self)
                self.label.setObjectName("label")
                self.label.setGeometry(QtCore.QRect(25, 50, 400, 16))
                self.label.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
                
                self.setGeometry(100, 100, 800, 600)
                
                # Connect the clicked signal of the Ok button to it's slot
                QtCore.QObject.connect(self.pushButtonApply, QtCore.SIGNAL("clicked()"),
                                self.writeConfig )
                
                QtCore.QObject.connect(self.pushButtonDiscard, QtCore.SIGNAL("clicked()"),
                                sys.exit )
                
                QtCore.QObject.connect(self.pushButtonSleep, QtCore.SIGNAL("clicked()"),
                                self.sleep )
                
                QtCore.QObject.connect(self.pushButtonHibernate, QtCore.SIGNAL("clicked()"),
                                self.hibernate )
                
                self.retranslateUi()
                
	def sleep(self):
		try:
			sysfsFP = open("/sys/power/state", 'w')
		except:
			log.err("Couldn't open kernel interface")
			return False
		else:
			try:
				sysfsFP.write("mem")
			except:
				log.err("Couldn't write to kernel interface")
				return False
                
	def hibernate(self):
		try:
			sysfsFP = open("/sys/power/state", 'w')
		except:
			log.err("Couldn't open kernel interface")
			return False
		else:
			try:
				sysfsFP.write("disk")
			except:
				log.err("Couldn't write to kernel interface")
				return False

        def writeConfig(self):
		finalResult = True
                for eachWriteOption in self.configOptions.keys():
                        checkBoxName = "checkBox_" + eachWriteOption
                        if self.checkBoxList[checkBoxName].isChecked() is True:
                                ret = self.populateValues(self.configOptions[eachWriteOption], 1)
                        else:
                                ret = self.populateValues(self.configOptions[eachWriteOption], 0)
			
			if ret is False:
				log.debug("Couldn't apply setting for %s" % checkBoxName)
				finalResult = False

		if finalResult is False:
			QtGui.QMessageBox.critical(self, "Error", "Couldn't apply all requested settings")
		else:
			QtGui.QMessageBox.information(self, "Success", "Applied all requested settings")

        def populateValues(self, path, value):
		try:
                	readHandle = open(path, 'r')
                	writeHandle = open(path + ".tmp", 'w')
                	for line in readHandle.readlines():
                        	if line.startswith(CONTROL_IDENTIFIER):
                                	newline = line.split("=")[0] + "=" + str(value)
                                	writeHandle.write(newline)
					writeHandle.write("\n") ### You need this newline, otherwise the next line gets overlapped here
                        	else:
                                	writeHandle.write(line)
                	readHandle.close()
                	writeHandle.close()
                	shutil.move(path + ".tmp", path)
			return True
		except:
			log.debug("Failed in populateValues() when operating on %s" % path)
			return False
        
        def retranslateUi(self):
                self.setWindowTitle(QtGui.QApplication.translate("MainWidget", "Laptop Mode Tools Configuration Tool", None, QtGui.QApplication.UnicodeUTF8))
                self.pushButtonApply.setText(QtGui.QApplication.translate("MainWidget", "Apply", None, QtGui.QApplication.UnicodeUTF8))
                self.pushButtonDiscard.setText(QtGui.QApplication.translate("MainWidget", "Exit", None, QtGui.QApplication.UnicodeUTF8))
                self.pushButtonSleep.setText(QtGui.QApplication.translate("MainWidget", "Sleep", None, QtGui.QApplication.UnicodeUTF8))
                self.pushButtonHibernate.setText(QtGui.QApplication.translate("MainWidget", "Hibernate", None, QtGui.QApplication.UnicodeUTF8))
                self.label.setText(QtGui.QApplication.translate("MainWidget", "Laptop Mode Tools - Module Configuration", None, QtGui.QApplication.UnicodeUTF8))
                
        def findConfig(self, configDir):
                if configDir is None:
                        return False
                
                # TODO: Do we need to take care of the vendor specific overrides ???
                for configFile in os.listdir(configDir):
                        if os.access(os.path.join(configDir, configFile), os.F_OK) is True:
                                self.configOptions[configFile.split(".")[0]] = os.path.join(configDir, configFile)
                        else:
                                pass
                        
        def readConfig(self, key, configOptionsDict):
                self.tooltip = ''
                                
                if key is None or configOptionsDict is None:
                        return False
                
                try:
                        fileHandle = open(configOptionsDict[key], 'r')
                except:
                        return False
                
                for line in fileHandle.readlines():
                        if line.startswith(COMMENT_IDENTIFIER):
                                self.tooltip = self.tooltip + line.lstrip(COMMENT_IDENTIFIER)
                        elif line.startswith(CONTROL_IDENTIFIER):
                                boolValue = line.split("=")[1]
                                boolValue = boolValue.rstrip("\n") ### Bloody boolValue could inherit the '\n' new line
                                
                                if boolValue == str(1) or "\"auto\"" in boolValue:
                                        self.configBool = True
                                else:
                                        self.configBool = False
                                
                # This will ensure that even if we don't read any string, tooltip doesn't fail
                self.tooltip = self.tooltip + ''             

if __name__=="__main__":
        from sys import argv, exit

	log = Log()
        a=QtGui.QApplication(argv)
        win=MainWidget()
        win.show()
        win.raise_()
        exit(a.exec_())
