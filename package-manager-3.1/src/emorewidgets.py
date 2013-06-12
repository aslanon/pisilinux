#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Onur Aslan <aslanon>
#
# Please read the COPYING file

from PyQt4 import QtGui
from PyQt4 import QtWebKit
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import QSize

from PyKDE4.kdecore import i18n
from PyKDE4.kdeui import KIcon

from pds.gui import *
from pmutils import *
import pisi.db

from pds.qprogressindicator import QProgressIndicator
from ui_morewidgets import Ui_MoreWidgets

import backend
import random
import urllib
import urllib2
import shutil
import os


class MoreWidgets(PAbstractBox, Ui_MoreWidgets):
    def __init__(self, state, parent=None):
        PAbstractBox.__init__(self, parent)
        self.iface = backend.pm.Iface()
        self.state = state
        self.setupUi(self)
        # PDS Settings
        self._animation = 1
        self._duration = 400
        self.enableOverlay()
        self._disable_parent_in_shown = True
        self.parent = parent
        self._shown = False
        self.registerFunction(IN, lambda: parent.statusBar().hide())
        self.registerFunction(FINISHED, lambda: parent.statusBar().setVisible(not self.isVisible()))

        self.updateSlideButton.clicked.connect(self.updateSlideImage)
        self.cancelButton.clicked.connect(self._hide)
        self.cancelButton.setIcon(KIcon("dialog-close"))

        self.webView.page().mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)
        self.webView.page().mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        self.webView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)

        self._show()
        self.openSlider()
        
        self.__tmpUrl = "/tmp/pm-slider/index.html"
        #self.__usrUrl = "/usr/share/kde4/apps/package-manager/pm-slider/index.html"
        self.__tmpSliderDir = "/tmp/pm-slider/"
        self.__tmpDir = "/tmp"
        self.__usrDir = "/usr/share/kde4/apps/package-manager/pm-slider/"
        
    def get_isa_packages(self, isa):
        self.randomPackageList.clear()
        #finded app:gui package for list to main screen in morewidgets
        repodb = pisi.db.repodb.RepoDB()
        packages = set()
        for repo in repodb.list_repos():
            doc = repodb.get_repo_doc(repo)
            for package in doc.tags("Package"):
                if package.getTagData("IsA"):
                    for node in package.tags("IsA"):
                        if node.firstChild().data() == isa:
                            packages.add(package.getTagData("Name"))
        totalPackage = len(list(packages)) 
        randList = []
        
        for randomNumbers in range(0,21):
            randValue = random.randrange(0, totalPackage)
            randList.append(randValue)
            
        for numberList in randList:
            guiPackages = unicode(list(packages)[numberList])
            item = QtGui.QListWidgetItem(self.randomPackageList)
            item.setData(QtCore.Qt.DisplayRole, guiPackages);
            #item.setData(QtCore.Qt.UserRole + 1, "leblebi");

            if os.path.isfile("/media/Arsiv2/Screenshots/package-manager/new4/uygulama resimleri/%s.png" % guiPackages) == False:
                item.setIcon(QtGui.QIcon(":/data/package-manager.png"))
                item.setToolTip("<html><head/><body><img src=\":/data/package-manager.png\"/>%s</body></html>" % (guiPackages))         
            else:
                item.setIcon(QtGui.QIcon("/media/Arsiv2/Screenshots/package-manager/new4/uygulama resimleri/%s.png" % guiPackages))                  
                item.setToolTip("<html><head/><body><img src=\"/media/Arsiv2/Screenshots/package-manager/new4/uygulama resimleri/%s.png\"/>%s</body></html>" % (guiPackages,guiPackages)) 

            
    def openSlider(self):
        if os.path.isfile(self.__tmpUrl) == False:
            print "pm-slider not found.\nReading default file."
            os.system("cp -R %s %s" % (self.__usrDir, self.__tmpDir))
            self.webView.setUrl(QtCore.QUrl(self.__tmpUrl))
        else:
            self.webView.setUrl(QtCore.QUrl(self.__tmpUrl))
        
    def updateSlideImage(self): 
        valueList = ["1","2","3"] # slide image names
        if os.path.isfile(self.__tmpUrl) == False:
            print "pm-slider not found.\nReading default file."
            os.system("cp -R %s %s" % (self.__usrDir, self.__tmpDir))
            self.webView.setUrl(QtCore.QUrl(self.__tmpUrl))
        else:
            pass
            
        if network_available():
            imageSha1sum = open("%ssha1sum" % self.__tmpSliderDir).read()
            newImageSha1sum = urllib.urlopen("https://pmslide.googlecode.com/svn-history/r6/wiki/sha1sum.wiki").read()
            if imageSha1sum == newImageSha1sum:
                print "sha1sum actual"
                self.webView.setUrl(QtCore.QUrl(self.__tmpUrl))
            else:
                for value in valueList:
                    url = urllib.urlopen("https://pmslide.googlecode.com/svn/%s.png" % value)
                    image = url.read()
                    imageFile = open(self.__tmpSliderDir+"%s.png" % value, "w")
                    imageFile.write(image)
                    imageFile.close()      
                    oldSha1 = open("%ssha1sum" % self.__tmpSliderDir, "w")
                    oldSha1.write(newImageSha1sum)
                    oldSha1.close()    
            self.webView.setUrl(QtCore.QUrl(self.__tmpUrl))           
        else:
            self.webView.setUrl(QtCore.QUrl(self.__tmpUrl))


    def _show(self):
        self.get_isa_packages("app:gui") 
        self.animate(start = BOTCENTER, stop = MIDCENTER)
        self._shown = True

    def _hide(self):
       # self.webView.disconnect()
        self.randomPackageList.clear()
        if self._shown:
            self.animate(start = MIDCENTER, stop = BOTCENTER, direction = OUT)
            self.parent.setWindowTitle(i18n("Package Manager"))
            self._shown = False
 