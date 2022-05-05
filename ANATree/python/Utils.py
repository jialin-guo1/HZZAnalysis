import sys, os, pwd, commands
import fnmatch


def processCmd(cmd, quite = 0):
    #    print cmd
    status, output = commands.getstatusoutput(cmd)
    if (status !=0 and not quite):
        print 'Error in processing command:\n   ['+cmd+']'
        print 'Output:\n   ['+output+'] \n'
        return "ERROR!!! "+output
    else:
        return output

#find files in all subdir
def find_files(directory, pattern):
  for root, dirs, files in os.walk(directory):
    for basename in files:
      if fnmatch.fnmatch(basename, pattern):
        filename = os.path.join(root, basename)
        yield filename

#find root files in this dir
def find_this_rootfiles(directory):
    filename_list = os.listdir(dir)
    files = []
    for i, filename in enumerate(filename_list):
        if(filename.find(".root")==-1): continue
        files.append(filename)
    return files



def mknewdir(dir_path):
    if(not os.path.exists(dir_path)):
        os.mkdir(dir_path)
