from itertools import permutations

perms = permutations([0, 1, 2, 3])

labels = list("IABCDEFGHJKLMNOPQRSTUVWX")

elements = {}


def snap(elem1, elem2):
    return [elem1[elem2[n]] for n in range(4)]


def name_from(elem):
    for key in elements:
        test_elem = elements[key]
        if elem == test_elem:
            return key
    return None


for i, perm in enumerate(perms):
    elements[labels[i]] = list(perm)

print("$\\begin{array}{" + "c|" * 25 + "}")
print("\\cdot & " + " & ".join(labels) + " \\\\ \\hline")

for label in labels:
    print(
        label
        + " & "
        + " & ".join(
            [name_from(snap(elements[label], elements[label2])) for label2 in labels]
        )
        + " \\\\ \\hline"
    )
print("\\end{array}$")
