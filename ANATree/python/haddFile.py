import os, sys, glob, fnmatch, re
from optparse import OptionParser

def find_files(directory, pattern):
  for root, dirs, files in os.walk(directory):
    for basename in files:
      if fnmatch.fnmatch(basename, pattern):
        filename = os.path.join(root, basename)
        yield filename

def main():

    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-i", "--indir", dest="indir",
                     help="input directory with .root files")
    parser.add_option("-o", "--outdir",
                     help="output directory", default="/cms/user/guojl/Sample/2L2Q/UL_Legacy/2016", dest="outdir")
    (options, args) = parser.parse_args()

    indir = '/cms/user/guojl/Sample/2L2Q/UL_Legacy/2016/'+str(options.indir)
    outdir = options.outdir

    print 'Input Directory is '+indir
    print 'Output Directory is '+outdir

    samples = ''
    full_file_size = 0.0
    haddtimes = 0
    file_index = 0
    for i,filename in enumerate(find_files(indir, '*.root')):

        fullsample = filename.split('/')
        sample = fullsample[len(fullsample)-1]
        sample = re.sub('_[0-9]*.root','',sample)
        thisdir = os.path.dirname(os.path.realpath(filename))

        file_size = os.path.getsize(filename)/(1024.0*1024*1024)
        #print filename + ' :'+str(file_size)
        full_file_size +=file_size

        samples += ' '
        samples += filename

        cmd = 'hadd -a ' + outdir+'/'+sample+'_'+str(file_index)+'.root'+' '+filename

        os.system(cmd)
        #print cmd
        haddtimes +=1

        if(full_file_size>10):
            file_index += 1
            samples = ''
            full_file_size = 0.0

    print haddtimes
    print file_index


if __name__ == "__main__":
   main()
