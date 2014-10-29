"""
Created: Oct 29, 2014:
    To convert the collab_xyz.txt datasets to LPmade source format, where
    vertices are listed first and then the hyperedges
"""

import sys
import os
import subprocess

if len(sys.argv!=2):
    sys.exit('Input a co-authorship dataset for conversion\n')
ipfilename = sys.argv[1]
basefname = os.path.splitext(ipfilename)[0]#assuming there is only one .(dot)
opfilename = basefname+"-lpmade.txt"
authlist=[]
#used to write all the hyperedges at once to the file as a single large string
alloutlines=""
hyperedgescnt = 0
ipfilename = open(ipfilename, 'r')
for oneline in ipfilename:
    hyperedgescnt = hyperedgescnt + 1
    yr, names = oneline.split()
    cmdline = "date +%s -d\"{0}-03-03\"".format(yr)
    epoch = subprocess.check_output(cmdline, shell=True).strip()
    allauths = names.split('&')
    writestring = "{0} {1} [ ".format(epoch, len(allauths))
    for name in allauths:
        try:
            idx = authlist.index(name)
        except ValueError:
            idx = len(authlist)
            authlist.append(name)
ipfilename.close()


opf = open(opfilename, 'w')


