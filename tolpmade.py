"""
Created: Oct 29, 2014:
    To convert the collab_xyz.txt datasets to LPmade source format, where
    vertices are listed first and then the hyperedges
"""

import sys
import os
import subprocess

if len(sys.argv)!=2:
    sys.exit('Input a co-authorship dataset for conversion\n')
ipfilename = sys.argv[1]
basefname = os.path.splitext(ipfilename)[0]#assuming there is only one .(dot)
opfilename = basefname+"-lpmade.txt"
authlist=[]
#used to write all the hyperedges at once to the file as a single large string
alloutedges=[]
alloutverts=[]
hyperedgescnt = 0
ipf = open(ipfilename, 'r')
for oneline in ipf:
    hyperedgescnt = hyperedgescnt + 1
    yr, names = oneline.split()
    #just randomly gave 3rd of March to avoid boundary dates
    cmdline = "date +%s -d\"{0}-03-03\"".format(yr)
    epoch = subprocess.check_output(cmdline, shell=True).strip()
    allauths = names.split('&')
    edgewritestring = "{0} {1} [ ".format(epoch, len(allauths))
    for name in allauths:
        try:
            idx = authlist.index(name)
        except ValueError:
            idx = len(authlist)
            authlist.append(name)
            alloutverts.append("{0} {1}".format(idx, name))
        edgewritestring = edgewritestring + str(idx)+ " "
    edgewritestring = edgewritestring + "]"
    alloutedges.append(edgewritestring)
ipf.close()


opf = open(opfilename, 'w')
print>>opf, "*Vertices: {0}".format(len(authlist))
print>>opf, "\n".join(alloutverts)
print>>opf, "*Hyperedges: {0}".format(hyperedgescnt)
print>>opf, "\n".join(alloutedges)
opf.close()
