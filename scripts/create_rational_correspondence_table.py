# REQUIRES PYTHON 3 OOF

import math


TRACK_DUPLICATES = False


def generate_correspondence(max_denom=10):

    corresponding = {}
    curr_index = 1

    for basedenom in range(1, max_denom):
        for num in range(0, basedenom):
            den = basedenom - num

            rat = num / den  # this is why

            if TRACK_DUPLICATES and rat in corresponding:
                yield num, den, "(%s)" % corresponding[rat]
            else:
                corresponding[rat] = curr_index
                curr_index += 1
                yield num, den, corresponding[rat]


rows = 5
cols = 6

header = """\\renewcommand*{{\\arraystretch}}{{2}} % stops fractions from colliding
\\begin{{tabular}}{{{column_alignments}}}
 & & \\multicolumn{{{mcol_sz}}}{{c}}{{Num. $\\rightarrow$}} & & \\\\
 & & {numerators} & $\\cdots{{}}$ \\\\
\\multirow{{{mrow_sz}}}{{*}}{{\\rotatebox[origin=c]{{-90}}{{Den. $\\rightarrow$}}}}  % "Den. ->" on the left, rotated sideways
""".format(
    column_alignments="l" * (cols + 3),
    mcol_sz=cols - 1,
    numerators=" & ".join("$%s$" % x for x in range(cols)),
    mrow_sz=rows,
)

footer = """& {vdots} {ddots} \\\\
\\end{{tabular}}""".format(
    vdots="$\\vdots{}$ &" * (cols + 1), ddots="$\\ddots{}$"
)


table_array = [["" for i in range(cols + 3)] for j in range(rows)]

for triplet in generate_correspondence(2 * max(rows, cols) + 1):
    (num, den, nat) = triplet
    # print(triplet, num, cols, den, rows) DEBUG

    if num < cols and den <= rows:
        if type(nat) == str:
            table_array[den - 1][num + 2] = (
                "\\textcolor{gray}{\\corr{%s}{%s}{\\textcolor{black}{%s}}}" % triplet
            )
        else:
            table_array[den - 1][num + 2] = "\\corr{%s}{%s}{%s}" % triplet

for x in range(rows):
    table_array[x][1] = "$%s$" % (x + 1)
    table_array[x][-1] = "$\\cdots{}$"

table_array_joined = "\n".join(
    "%s \\\\" % " & ".join(table_array[i]) for i in range(rows)
)

print(header)
print(table_array_joined)
print(footer)
