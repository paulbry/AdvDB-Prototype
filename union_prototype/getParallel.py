import sys
from mpi4py.futures import MPIPoolExecutor
import api

if __name__ == '__main__':
    with MPIPoolExecutor() as executor:
        executor.submit(api.Cloud.get, sys.argv[1])