elements = {"I": [0, 1, 2], "f": [0, 2, 1], "fr": [2, 1, 0], "fr^2": [1, 0, 2], "r": [2, 0, 1], "r^2": [1, 2, 0]}


def flip(elem1, elem2):
    return [elem2[elem1[n]] for n in range(3)]


def name_from(elem):
    for key in elements:
        test_elem = elements[key]
        if elem == test_elem:
            return key
    return None


elemlist = ["I", "r", "r^2", "f", "fr", "fr^2"]

for elem1key in elemlist:
    print(elem1key + " & " + " & ".join(
        [name_from(flip(elements[elem1key], elements[elem2key])) for elem2key in elemlist]) + " \\\\ \\hline")
