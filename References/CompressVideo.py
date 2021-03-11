##################################################################################################
#
# CompressVideo - compress a video to a smaller file size using H264 encoding standard    
#
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
#from PyQt5.QtGui import *
#from PyQt5.QtCore import *
import sys
import os
import subprocess
import datetime
#
#globals
fps = 30
crf = 24
sfwr = "handbrake"
x = ""
filename = ""
#
##################################################################################################
#
class Ui(QtWidgets.QMainWindow):

    fps = 0
    crf = 0
    filename = ""
    sfwr = ""  # handbrake or ffmpeg
    x = ""
#
    def __init__(self):
               
        super(Ui, self).__init__()
        uic.loadUi('CompressVideo.ui', self)
        
        self.lblCRF.setText(str(crf))
        self.statusbar = self.statusBar()

        # Adding a temporary message
        self.statusbar.showMessage("Ready")
#        self.show() 

        self.rbHandbrake.clicked.connect(self.rbhandbrakepushed)

        self.rbFfmpeg.clicked.connect(self.rbffmpegpushed)

        self.rb24.clicked.connect(self.rb24pushed)

        self.rb30.clicked.connect(self.rb30pushed)

        self.hsVQ.valueChanged.connect(self.crfChanged)

        self.btnBrowse.clicked.connect(self.selectFile)

        self.btnCompress.clicked.connect(self.compress)
#
    def rb24pushed (self):
        global fps        
        fps=24
        self.statusbar.showMessage("24 fps selected")
        self.show()
        return
#
    def rb30pushed (self):
        global fps
        fps=30
        self.statusbar.showMessage("30 fps selected")
        self.show()
        return
#
    def rbhandbrakepushed (self):
        global sfwr
        sfwr = "handbrake"
        self.statusbar.showMessage("'handbrake' selected")
        self.show()
        return
#
    def rbffmpegpushed (self):
        global sfwr
        sfwr = "ffmpeg"
        self.statusbar.showMessage("'ffmpeg' selected")
        self.show()
        return
#
    def crfChanged (self):
        global crf
        crf=self.hsVQ.value()
        self.lblCRF.setText(str(crf)) 
        return
#
    def selectFile (self):
        global filename 
        fname = QFileDialog.getOpenFileName(self, 'Select file', "/")
        filename = fname[0]
        self.leFname.setText(filename)
    # probe file
        self.probeFile(filename)
        return
#
    def probeFile (self, myfyl):
        probecmd = 'ffprobe "' + myfyl + '"'
  
        try:
            x = subprocess.getoutput(probecmd)
        except Exception as e:
            QMessageBox.about (self, "ERROR", "Probe Error: " + e.message)

        i = x.find("Input #0")      # locate text to drop
        if (i <= 0):
            QMessageBox.about (self, "ERROR", "No multimedia stream detected!")
        else:
            y = x[i:]          #drop preceeding text
            self.textBrowser.clear()
            self.textBrowser.append(y)
            self.show()        
            return x
#
    def compress (self):
        global fps
        global crf
        global filename
        global sfwr
        curname = ""
        newname = ""
        logfile = ""
        compresscmd = ""
        starttm = 0
        stoptm = 0
        deltatm = 0

    # has a file been selected
        if (len(filename) == 0):
            QMessageBox.about (self, "ERROR", "Must select file to compress first")  
            self.show()
            return

    # find name without file extension (ext)
        i=0
        i = filename.find(".")
        nameNoExt = filename[:i]

    # rename file, with "_ORIGINAL" appended
        newname = filename
        newname = newname.replace(".m", "_ORIGINAL.m")
        os.rename(filename, newname)
        QMessageBox.about (self, "Please note", filename + "has been renamed to " + newname)  
        self.show()

    # create new (compressed) & log filenames
        curname = nameNoExt + ".mp4"
        logfile = nameNoExt + ".log"
    #
    # print run parameters & probe input video
        mylog = open(logfile, 'w')
        mylog.write ("=========================================================== \n")
        mylog.write ("=========================================================== \n")          
        x = "\n File to Compress = " + curname + "\n"
        x = x + "\n   fps = " + str(fps) + "\n"
        x = x + "\n   crf = " + str(crf) + "\n"
        x = x + "\n   software = " + sfwr + "\n"
        x = x + "=========================================================== \n"
        x = x + "=========================================================== \n\n"
        x = x + "Input file probe: \n"
        mylog.writelines(x)
        x = self.probeFile (newname)
        mylog.writelines(x)
        mylog.writelines ("\n=========================================================== \n")        
        mylog.writelines ("=========================================================== \n Run Log:\n")        
    #
    # compress  
        starttm = datetime.datetime.now()
        
        try:
            if (sfwr == "ffmpeg"):
                compresscmd = 'ffmpeg -i "' + newname + '" -crf ' + str(crf) + ' -r ' + str(fps) + ' "' + curname + '"'
            else:
                compresscmd = 'HandBrakeCLI -i "' + newname + '" -o "' + curname + '" -e x264 -q ' + str(crf) + ' -r ' + str(fps) + ' --pfr'
#            x = subprocess.getoutput(compresscmd)
            subprocess.run(compresscmd, shell=True, capture_output=False)
            self.statusbar.showMessage("Compression complete")
        except Exception as e:
            x = "\n ERROR -> \n" +  e.args[0] + "\n"
        finally:    
            mylog.writelines(x)    
        
        stoptm = datetime.datetime.now()
        deltatm = stoptm - starttm

    # probe output video
        mylog.write ("\n\n=========================================================== \n") 
        mylog.write ("=========================================================== \n") 
        mylog.write ("Output file probe: \n")   
        x = self.probeFile (curname)
        mylog.writelines(x)
        mylog.write ("\n\n=========================================================== \n")
        mylog.write ("=========================================================== \n\n")
        return x

    # print job duration
        x = "Job took " + str(deltatm) + " long \n" 
        mylog.write (x)
        mylog.write ("=========================================================== \n") 
        mylog.write ("=========================================================== \n") 
        mylog.close()
        QMessageBox.about (self, "Done", filename + " has been compressed ")
#
        return
#
##################################################################################################
#
app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.show()
sys.exit(app.exec())
#app.exec_()
#
##################################################################################################
