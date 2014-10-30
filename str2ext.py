"""
Created: Oct 30, 2014: To covert the string based author names to the notation
followed by lpmade (the vertex ids from source file)
"""

import subprocess
import sys
import os

if len(sys.argv)!=3:
    sys.exit('Input vertex_id file, edges list file')

source = sys.argv[1]
authslist = sys.argv[2]
cmdline1 = "grep -n \"edges\" {0}|cut -f1 -d:".format(source)
lineno = subprocess.check_output(cmdline1, shell=True).strip()
lineno = int(lineno)-1#go down to last vertex id
cmdline2 = "sed -n \'2,{0}\'p {1}".format(lineno, source)
vertexids = subprocess.check_output(cmdline2, shell=True).strip().split('\n')
vi_dict={}
for idname in vertexids:
    id, name = idname.split()
    vi_dict[name] = id
writestring=""
inputfp = open(sys.argv[2],'r')
for line in inputfp:
    a1, a2 = line.strip().split()
    id1 = vi_dict[a1]
    id2 = vi_dict[a2]
    writestring = writestring + "{0} {1}\n".format(id1, id2)
ofilename = os.path.splitext(sys.argv[2])[0]+"_ext.txt"
outputfp = open(ofilename, 'w')
print>>outputfp, writestring.rstrip()
inputfp.close()
outputfp.close()

