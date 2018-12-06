# Alfred Shaker
# split script
# takes files name to split, directory to put the files in, and chunk size in bytes of each part

import sys, os, hashlib, itertools
from mpi4py.futures import MPIPoolExecutor

kilobytes = 1024
megabytes = kilobytes * 1000
chunksize = int(1.4 * megabytes)  # default: roughly a floppy


def split(fromfile, todir, chunksize=chunksize):
    partnum = 0

    hashfilename = hashlib.md5(open(fromfile, 'rb').read()).hexdigest()
    # input = open(fromfile, 'rb')                   # use binary mode on Windows
    hashfile = open("hash.txt", 'a')
    hashhex = hashfilename + '\n'
    print("hash of original file: " + hashfilename)
    hashfile.write(hashhex)
    hashfile.close()
    # todir = hashhex

    if not os.path.exists(todir):  # caller handles errors
        os.mkdir(todir)  # make dir, read/write parts

    hash_md5 = hashlib.md5()

    with open(fromfile, "rb") as f:
        for chunk in iter(lambda: f.read(chunksize), b""):
            if not chunk: break
            hash_md5.update(chunk)
            partnum = partnum + 1
            filename = todir + '\\' + hashfilename + '-' + str(partnum)
            # os.path.join(todir, ('part%04d' % partnum))
            fileobj = open(filename, 'wb')
            fileobj.write(chunk)
            fileobj.close()

            # input.close(  )
    assert partnum <= 9999  # join sort fails if 5 digits
    return partnum


def zip_scalar(fromfile, todir, chunksize):
    return zip(fromfile, todir, chunksize)


if __name__ == '__main__':
    with MPIPoolExecutor() as executor:
        if len(sys.argv) == 2 and sys.argv[1] == '-help':
            print('Use: split.py [file-to-split target-dir [chunksize]]')
        else:
            if len(sys.argv) < 3:
                exit()
            else:
                fromfile, todir = sys.argv[1:3]  # args in cmdline
                if len(sys.argv) == 4: chunksize = int(sys.argv[3])

            absfrom, absto = map(os.path.abspath, [fromfile, todir])
            print('Splitting', absfrom, 'to', absto, 'by', chunksize)
            splitParams = (fromfile, todir, chunksize)
            try:
                # with MPIPoolExecutor() as executor:
                parts = executor.submit(split,fromfile, todir, chunksize)
                #print(parts.result())
                # parts = split(fromfile, todir, chunksize)
            except:
                print('Error during split:')
                print(sys.excepthook)
            else:
                print('Split finished:', parts.result(), 'parts are in', absto)
