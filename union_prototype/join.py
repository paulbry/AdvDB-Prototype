#Alfred Shaker
#join script for repository of files

import os, sys
readsize = 1024

def join(fromdir, tofile):
    output = open(tofile, 'wb')
    parts  = os.listdir(fromdir)
    parts.sort(  )
    for filename in parts:
        filepath = os.path.join(fromdir, filename)
        fileobj  = open(filepath, 'rb')
        while 1:
            filebytes = fileobj.read(readsize)
            if not filebytes: break
            output.write(filebytes)
        fileobj.close(  )
    output.close(  )

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '-help':
        print ('Use: join.py [from-dir-name to-file-name]')
    else:
        if len(sys.argv) != 3:
            exit()
        else:
            interactive = 0
            fromdir, tofile = sys.argv[1:]
        absfrom, absto = map(os.path.abspath, [fromdir, tofile])
        print ('Joining', absfrom, 'to make', absto)

        try:
            join(fromdir, tofile)
        except:
            print ('Error joining files:')
            print (sys.excepthook)
        else:
           print ('Join complete: see', absto)
