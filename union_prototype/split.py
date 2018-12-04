#Alfred Shaker
#split script
#takes files name to split, directory to put the files in, and chunk size in bytes of each part

import sys, os, hashlib
kilobytes = 1024
megabytes = kilobytes * 1000
chunksize = int(1.4 * megabytes)                   # default: roughly a floppy

def split(fromfile, todir, chunksize=chunksize): 
    
    partnum = 0
    
    hashfilename = hashlib.md5(open(fromfile,'rb').read()).hexdigest()
    #input = open(fromfile, 'rb')                   # use binary mode on Windows
    hashfile = open("hash.txt", 'a')
    hashhex = hashfilename + '\n'
    print ("hash of original file: " + hashfilename)
    hashfile.write(hashhex)
    hashfile.close()
    #todir = hashhex


    if not os.path.exists(todir):                  # caller handles errors
        os.mkdir(todir)                            # make dir, read/write parts
    else:
        for fname in os.listdir(todir):            # delete any existing files
            os.remove(os.path.join(todir, fname)) 


    hash_md5 = hashlib.md5()

    with open(fromfile, "rb") as f:
        for chunk in iter(lambda: f.read(chunksize), b""):
                if not chunk: break
                hash_md5.update(chunk)
                partnum  = partnum+1
                filename = todir + '\\' + hashfilename + '-' + str(partnum)
                #os.path.join(todir, ('part%04d' % partnum))
                fileobj  = open(filename, 'wb')
                fileobj.write(chunk)
                fileobj.close() 
  
  

    #input.close(  )
    assert partnum <= 9999                         # join sort fails if 5 digits
    return partnum

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
            
if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '-help':
        print ('Use: split.py [file-to-split target-dir [chunksize]]')
    else:
        if len(sys.argv) < 3:
            exit()
        else:
            interactive = 0
            fromfile, todir = sys.argv[1:3]                  # args in cmdline
            if len(sys.argv) == 4: chunksize = int(sys.argv[3])
        absfrom, absto = map(os.path.abspath, [fromfile, todir])
        print ('Splitting', absfrom, 'to', absto, 'by', chunksize)

        try:
            parts = split(fromfile, todir, chunksize)
        except:
            print ('Error during split:')
            print (sys.excepthook)
        else:
            print ('Split finished:', parts, 'parts are in', absto)
        
