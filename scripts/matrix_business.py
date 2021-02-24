import numpy as np

P = np.matrix([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
Q = np.matrix([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
R = np.matrix([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])

generators = [P, Q]
temp = []


def temp_contain(matrix):
    return any(np.array_equal(k, matrix) for k in temp)


def run_products():
    global temp, generators
    temp = [k for k in generators]
    for i in temp:
        for j in temp:
            mtrx = i * j  # for some reason my install doesn't have numpy.matmul
            if not temp_contain(mtrx):
                temp.append(mtrx)
    generators = temp


for i in xrange(5):
    print "Calculating to step %s" % i
    run_products()
    if len(temp) == len(generators):
        break

print (generators)
print (len(generators))
