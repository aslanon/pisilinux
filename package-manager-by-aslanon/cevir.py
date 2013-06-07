import os
password = raw_input("Password: ")
os.system('echo %s|sudo -S %s' % ("%s" % password, "python setup.py install && package-manager")) 
