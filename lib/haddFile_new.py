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
                     help="output directory", default="/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/", dest="outdir")
    parser.add_option("-y","--year", default = "2018",help = "year")
    (options, args) = parser.parse_args()

    indir = '/cms/user/guojl/Sample/2L2Q/UL_Legacy/'+str(options.year)+'/'+str(options.indir)
    outdir = options.outdir+str(options.indir)

    #try:
    #  if args.indir.find('GluGluHToZZTo2L2Q')!=-1:
    #    outdir = options.outdir+str('ggh')
    #    os.mkdir(outdir)
    #  elif args.indir.find('VBF_HToZZTo2L2Q')!=-1:
    #    outdir = options.outdir+str('vbf')
    #    os.mkdir(outdir)
    #  else:
    #    os.mkdir(outdir)
    #except:
      #print "target folder is exist"

    if options.indir.find('GluGluHToZZTo2L2Q')!=-1:
      outdir = options.outdir+str('ggh')
    elif options.indir.find('VBF_HToZZTo2L2Q')!=-1:
      outdir = options.outdir+str('vbf')
      
    if(not os.path.exists(outdir)):
      os.mkdir(outdir)

    print 'Input Directory is '+indir
    print 'Output Directory is '+outdir

    samples = ''
    full_file_size = 0.0
    haddtimes = 0
    file_index = 0
    #print list(find_files(indir, '*.root'))
    the_last = len(list(find_files(indir, '*.root')))-1
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

        #cmd = 'hadd -a ' + outdir+'/'+sample+'_'+str(file_index)+'.root'+' '+filename
        
        #os.system(cmd)
        #print cmd
        #haddtimes +=1

        if((full_file_size>10) or (i==the_last)):
            cmd = 'hadd -f ' + outdir+'/'+sample+'_'+str(file_index)+'.root'+' '+samples
            haddtimes +=1
            print cmd
            os.system(cmd)
            print '\n\n\n'

            if(i==the_last):
              print "the size of last few files is "+str(full_file_size)+" GB"

            file_index += 1
            samples = ''
            full_file_size = 0.0

    print "hadd times = "+str(haddtimes)
    print file_index


if __name__ == "__main__":
   main()
