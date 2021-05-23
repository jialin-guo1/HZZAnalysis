import os,sys

inputfile = open('weight_0.85_0.9.txt')
outputfile = open('weight_abnormal_0.85_0.9.txt','w')

for line in inputfile:
    temp_line = line
    temp_line = temp_line.split(',')[0]
    weight = float(temp_line.split('=')[1])
    if(abs(weight)>=0.06):
        print "[INFO] find abnormal weight = "+str(weight)
        print >> outputfile, line
        print line
