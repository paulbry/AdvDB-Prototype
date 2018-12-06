import sys
from mpi4py.futures import MPIPoolExecutor
import api


if __name__ == '__main__':
    with MPIPoolExecutor() as executor:
        executor.submit(api.Cloud.put, sys.argv[1], sys.argv[2], sys.argv[3])