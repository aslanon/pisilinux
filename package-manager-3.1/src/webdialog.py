#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file

import webbrowser
import os

from PyQt4 import QtGui
from PyQt4 import QtWebKit
from PyQt4.QtCore import *

from PyKDE4.kdeui import *
from PyKDE4.kdecore import *

from pds.gui import *
from pmutils import *
from pds.thread import PThread

from ui_preview import Ui_Preview
from ui_webdialog import Ui_WebDialog

from statemanager import StateManager
import urllib2

class WebDialog(PAbstractBox, Ui_WebDialog):
    def __init__(self, state, parent):
        PAbstractBox.__init__(self, parent)
        self.setupUi(self)
        self.state = state
        # PDS Settings
        self._animation = 1
        self._duration = 400
        self.enableOverlay()
        self._disable_parent_in_shown = True
        self.webView.hide()
      
        #Url list for package pisi source files
        global packageUrlList
        packageUrlList = []
        
        self._as = 'http://youtube.googleapis.com/v'
        self.cancelButton.clicked.connect(self._hide)
        self.cancelButton.setIcon(KIcon("dialog-close"))

        self.packageHomepage.clicked.connect(self.openWebsite)
        self.packagePisiSource.clicked.connect(self.openPisiSource)
        #self.wdInstallButton.clicked.connect(self.showBasket)
        # Hide Scrollbars and context menu in webview
        self.webView.setContextMenuPolicy(Qt.NoContextMenu)
        self.webView.page().mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)
        self.webView.page().mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        self.webView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.webView.page().linkClicked.connect(self.showFullImage)

        self.tabWidget.removeTab(0)

        self._filesThread = PThread(self, self.getFiles, self.getFilesFinished)
        self.filterLine.setListWidget(self.filesList)
        self.noconnection.hide()
        self.parent = parent


    def showFullImage(self, url):
        PreviewDialog(self, url)

    def getFiles(self):
        return self.iface.getPackageFiles(str(self.packageName.text()))

    def getFilesFinished(self):
        self.filesList.addItems(self._filesThread.get())
        self.filesList.sortItems()

    def _tabSwitched(self, index):
        if index == 0 and self.tabWidget.count() > 1:
            if self.filesList.count() == 0:
                self._filesThread.start()

    def _sync_template(self, status, package = '', summary = '', description = ''):
        def _replace(key, value):
            self.webView.page().mainFrame().evaluateJavaScript(\
                    '%s.innerHTML="%s";' % (key, value))
        if status:
            _replace('title', package)
            _replace('summary', summary)
            _replace('description', description)
            self.webWidget.show()
            self.noconnection.hide()
        else:
            self.noconnection.hide()
            self.webWidget.show()

        reset_proxy_settings()

    def openWebsite(self):
        webbrowser.open_new_tab(packageUrlList[1])
        
    def openPisiSource(self):
        webbrowser.open_new_tab(packageUrlList[0]) 
    
    def showBasket(self):
        package = [self.packageName.text()]
        print package
        self.basket.__initList(package)
        self.basket._show()
        
    def __makePath(self, path, package):
        #Package Component configure for PiSi source files url.
        #And added new urls to packageUrlList       
        global packageSourceUrl
        __make = path.split(".")
        newPath = ("/").join(__make)
        packageSourceUrl = "https://github.com/pisilinux/PisiLinux/tree/master/%s/%s" % (newPath, package)
        self.packagePisiSource.setToolTip(packageSourceUrl) 
        #packageUrlList[0] => pisi source files url
        #packageUrlList[1] => package home page url
        packageUrlList.append(packageSourceUrl)
        packageUrlList.append(self.packageHomepage.text())
        
    def showPackageDetails(self, package, installed, summary='', description='', homepage='', appIsa='', appComponent='', rate="", repository='', _icon=''):
        self.packageName.setText(package)
        self.packageSummary.setText(summary)
        self.packageDescription.setText(description)
        self.packageHomepage.setText(homepage)
        self.packageComponent.setText(appComponent)
        self.packageIsa.setText(appIsa)        
        self.kratingwidget.setRating(rate)
        self.packageRepo.setText(repository)

        #package big screenshot in ToolTip
        self.__ssUrl = "/tmp/pm-ss/%s.png" % package

        if os.path.isdir("/tmp/pm-ss") == False:
            os.mkdir("/tmp/pm-ss")
        else:
            pass
        
        if os.path.isfile(self.__ssUrl) == False:
            
            if network_available():
                try:
                    imageUrl = urllib2.urlopen("http://www.ozgurlukicin.org/media/upload/tema/paket-goruntusu/buyuk/%s.png" % package )
                    imageData = imageUrl.read()
                    image = open(self.__ssUrl,"w")
                    image.write(imageData)
                    imageUrl.close()
                    image.close()
                except:
                    print "%s not found." % package
                    
                self.labelScreenshot.setPixmap(QtGui.QPixmap("/tmp/pm-ss/%s.png" % package))         
                self.labelScreenshot.setToolTip("<html><head/><body><img src='/tmp/pm-ss/%s.png'/>%s</body></html>" % (package,package))         
            else:
                print "net yok" 
                if os.path.isfile(self.__ssUrl) == False:
                    self.labelScreenshot.setText(package)
                else:
                    self.labelScreenshot.setPixmap(QtGui.QPixmap(self.__ssUrl))
                    self.labelScreenshot.setToolTip("<html><head/><body><p><img src=\"%s\"/></p></body></html>" % self.__ssUrl)
        else:
            print "..."
            self.labelScreenshot.setPixmap(QtGui.QPixmap("/tmp/pm-ss/%s.png" % package)) 
            self.labelScreenshot.setToolTip("<html><head/><body><img src='/tmp/pm-ss/%s.png'/>%s</body></html>" % (package,package))  
       
        #Make path for source url
        self.__makePath(appComponent, package)
        #Package logo for package details tab and logo image control
        if os.path.isfile("/usr/share/pixmaps/%s.png" % package) == False:
            self.packageLogo.setPixmap(QtGui.QPixmap("/usr/share/icons/hicolor/32x32/mimetypes/application-x-pisi.png"))
        else:
            self.packageLogo.setPixmap(QtGui.QPixmap("/usr/share/pixmaps/%s.png" % package))        
        self.filesList.clear()
        self.tabWidget.insertTab(0, self.packageFiles, i18n('Package Files'))
        self.tabWidget.currentChanged.connect(self._tabSwitched)
        if not installed:
            self.tabWidget.removeTab(0)
            self.tabWidget.currentChanged.disconnect(self._tabSwitched)
        self.animate(start = BOTCENTER, stop = MIDCENTER)

    def _show(self):
        self.animate(start = BOTCENTER, stop = MIDCENTER)
        self._shown = True

    def _hide(self):
        if len(packageUrlList) > 0:
            del packageUrlList[:] # for package url
        else:
            pass       
        self.animate(start = MIDCENTER, stop = BOTCENTER, direction = OUT)

class PreviewDialog(PAbstractBox, Ui_Preview):
    def __init__(self, parent, url):
        PAbstractBox.__init__(self, parent.parent)
        self.setupUi(self)
        self.parent = parent
        # PDS Settings
        self._animation = 1
        self._duration = 400
        self.enableOverlay()
        
        # self._disable_parent_in_shown = True
        self.cancelButton.clicked.connect(self._hide)
        self.cancelButton.setIcon(KIcon("dialog-close"))
        
        # Hide Scrollbars and context menu in webview
        #self.webView.setContextMenuPolicy(Qt.NoContextMenu)
        #self.webView.page().mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)
        #self.webView.page().mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)

        self.parent._hide()
        self.setOverlayClickMethod(lambda x:self._hide())

    def _hide(self):
        self.webView.loadFinished.disconnect()
        self.animate(start = MIDCENTER, stop = BOTCENTER, direction = OUT)
        self.parent.animate(start = BOTCENTER, stop = MIDCENTER)