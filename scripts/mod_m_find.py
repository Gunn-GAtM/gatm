#!/usr/bin/env python
from fractions import gcd

# run in a terminal as python -i mod_m_find.py,
# so you can interact with it as a REPL

modulus = 10
group_elements = []

for i in xrange(1, modulus):
    if gcd(i, modulus) == 1:
        group_elements.append(i)


def pretty_print_elements():
    print(pp_list(group_elements))


def pp_list(arr):
    return ", ".join(map(lambda s: "$%s$" % s, arr))


def make_orbit_table(sort_by_orbit=True):
    print("\\begin{tabular}{c|c|c}\nElement & Orbit & Period")

    orbits = []

    for elem in group_elements:
        x = elem
        orbit = []
        while True:
            orbit.append(str(x))
            x *= elem
            x %= modulus

            if x == elem:
                orbit.append("(%s)" % elem)
                break
        orbits.append(orbit)

    if sort_by_orbit:
        orbits.sort(key=len)

    for orbiit in orbits:
        print("$%s$ & %s & $%s$ \\\\" % (orbiit[0], pp_list(orbiit), len(orbiit) - 1))

    print("\\end{tabular}")


def create_group_table(sort_by=None):
    if not sort_by:
        group_elements.sort()
    else:
        group_elements.sort(key=sort_by)

    hline = "\\hline"

    print("\\begin{array}{c|%s}" % ("c|" * len(group_elements)))
    print("\\cdot & " + " & ".join(map(str, group_elements)) + " \\\\ " + hline)
    for i in group_elements:
        row = "%s" % i
        for j in group_elements:
            row += " & %s" % ((i * j) % modulus)
        row += " \\\\ " + hline
        print(row)
    print("\\end{array}")
