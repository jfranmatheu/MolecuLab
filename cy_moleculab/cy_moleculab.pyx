cimport cython
from cython.parallel import parallel, prange
from libc.stdlib cimport abort, malloc, free
from libc.stdio cimport printf

# tag: numpy
# You can ignore the previous line.
# It's for internal testing of the cython documentation.

import numpy as np

# "cimport" is used to import special compile-time information
# about the numpy module (this is stored in a file numpy.pxd which is
# distributed with Numpy).
# Here we've used the name "cnp" to make it easier to understand what
# comes from the cimported module and what comes from the imported module,
# however you can use the same name for both if you wish.
cimport numpy as cnp

# It's necessary to call "import_array" if you use any part of the
# numpy PyArray_* API. From Cython 3, accessing attributes like
# ".shape" on a typed Numpy array use this API. Therefore we recommend
# always calling "import_array" whenever you "cimport numpy"
cnp.import_array()

# We now need to fix a datatype for our arrays. I've used the variable
# DTYPE for this, which is assigned to the usual NumPy runtime
# type info object.
DTYPE = np.int64

# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.
ctypedef cnp.int64_t DTYPE_t


cdef void func(int idx) nogil:
    printf("Hola Thread %i", idx)

'''
cpdef void testfunc():
    cdef Py_ssize_t i, j, n = 100
    cdef int * local_buf
    cdef size_t size = 10

    with nogil, parallel():
        local_buf = <int *> malloc(sizeof(int) * size)
        if local_buf is NULL:
            abort()

        # populate our local buffer in a sequential loop
        for i in range(size):
            local_buf[i] = i * 2

        # share the work using the thread-local buffer(s)
        for j in prange(n, schedule='guided'):
            func(j)

        free(local_buf)
'''

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cpdef void simulate_ps(
    int cpunum,
    float time_delta,
    int particle_count,
    float [:, :] par_location,
    float [:, :] par_velocity,
    float [:] par_mass,
    float [:] par_size,
    int [:] par_state):

    cdef float gravity_vel = -9.81 * time_delta

    for i in range(particle_count):
        par_location[i][2] += par_velocity[i][2] * time_delta + (-9.81 * time_delta * time_delta) / 2.0
        par_velocity[i][2] += gravity_vel

'''
with nogil:
    for i in prange(parnum,
                    schedule='dynamic',
                    chunksize=10,
                    num_threads=cpunum):

        par_location[i][1] += par_velocity[i][1] * time_delta + (-9.81 * time_delta * time_delta) / 2.0
        par_velocity[i][1] += gravity_vel
'''
