import decimal

# Cantor's diagonal argument figure generator

digits = 16
# pairs of (name, decimal)
decimal.getcontext().prec = digits + 5

numbers = [
    ("0", decimal.Decimal("0")),
    ("\\frac{1}{4}", decimal.Decimal("0.25")),
    (
        "\\frac{\pi}{4}",
        decimal.Decimal("0.7853981633974483096156608458198757210492923498"),
    ),
    ("C_{10}", decimal.Decimal("0.123456789101112131415161718192021222324")),
    ("e-2", decimal.Decimal("0.7182818284590452353602874713526624977572470937")),
    (
        "\\frac{\\sqrt{2}}{10}",
        decimal.Decimal("0.1414213562373095048801688724209698078569671875"),
    ),
]


header = """\\begin{tabular}{%s}
& & & \\multicolumn{%s}{c}{Decimal Expansion $\\rightarrow$} \\\\
""" % (
    "r" + "l" * (digits + 3),
    digits,
)

footer = """\\end{tabular}"""

table = [[] for i in range(len(numbers) + 2)]

for i, pair in enumerate(numbers):
    table[i].extend(
        [
            "$r_{%s}$" % (i + 1),
            "$%s$" % pair[0],
            "\\tcg{0.}" + ("" if i != 0 else "\\Aboxed{"),
        ]
    )
    expansion = str(pair[1])[2 : digits + 2].ljust(digits, "0")
    table[i].extend(
        ("%s}" if i == j else ("\\tcg{%s}" if i != j + 1 else "\\tcg{%s} \\Aboxed{"))
        % char
        for j, char in enumerate(expansion)
    )
    table[i].append("$\\cdots{}$")

for i in range(digits + 3):
    table[-2].append(
        "$\\vdots{}$" if (i < 2 or i % 2 == 0) else ""
    )  # so it doesn't get too cramped

table[-2].append("$\\ddots{}$")

table[-1].extend(["$r$", "", "$0.$"])

for i in range(digits):
    table_index = i + 3

    if i >= len(numbers):
        table[-1].append("\multicolumn{5}{l}{$\cdots{}$}")
        break

    table[-1].append(
        "$%s$" % ((int(str(numbers[i][1]).ljust(digits, "0")[2 + i]) + 1) % 10)
    )

print(header)
print("\n".join("%s \\\\" % " & ".join(table[i]) for i in range(len(numbers) + 2)))
print(footer)
