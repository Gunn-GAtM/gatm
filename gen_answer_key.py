import re

raise Error("Please don't use this program lol")

# This program generates the answer key for comp_func, kind of
counters = { "enumi": 0, "enumii": 0, "enumiii": 0 }

def set_counter(counter1, counter2):
    if counter2 in counters:
        counters[counter1] = counters[counter2]
        return
    counters[counter1] = 0

def set_counter_by_value(counter, value):
    counters[counter] = value

def increment_counter(counter):
    if counter in counters:
        counters[counter] += 1

def get_counter(counter):
    return counters[counter]

get_enumeration_name = re.compile(r"\\(?:begin|end)\s*\{([^{}]+)\}")
get_setcounters1 = re.compile(r"\\setcounter\s*\{([^{}]+)\}\{\\value\{([^{}]+)\}\}")
get_setcounters2 = re.compile(r"\\setcounter\s*\{([^{}]+)\}\{([0-9]+)\}")
get_setcounters3 = re.compile(r"\\setcounter\s*\{([^{}]+)\}\{\\the([^{}]+)\}")

# Token types: begin_enumerate, end_enumerate, item, setcounter
class Token:
    def __init__(self, token_type, contents):
        self.type = token_type
        self.contents = contents

    def get_enumeration_name(self):
        assert self.type in ["begin_enumerate", "end_enumerate"]

        return re.match(get_enumeration_name, self.contents).group(1)

    def get_counter_names(self):
        assert self.type == "setcounter"

        matches = map(lambda regex: regex.match(self.contents), [get_setcounters1, get_setcounters2, get_setcounters3])

        next_match = next(v for v in matches if v is not None)

        if next_match:
            return next_match.group(1,2)

    def __str__(self):
        return "Token %s: %s" % (self.type, self.contents)

class Problem:
    def __init__(self, number, letter, part, contents):
        self.number = number
        self.letter = letter
        self.part = part
        self.contents = contents

    def same_problem_encoding(self, problem):
        return self.number == problem.number and self.letter == problem.letter and self.part == problem.part

    def equals(self, problem):
        return self.same_problem_encoding(problem) and self.contents.lower() == problem.contents.lower()

    def __str__(self):
        return self.nice_representation()

    def nice_representation(self):
        code = str(self.number)
        if self.letter > 0:
            code += '.' + chr(self.letter + 96)
        if self.part > 0:
            code += '.' + str(self.part) # todo: convert to roman

        return "%s: %s" % (code, self.contents)

begin_enumerate_regex = re.compile(r"\\begin\{(?:enumerate|(?:(?:outer|i?inner)_problem))\}")
end_enumerate_regex = re.compile(r"\\end\{(?:enumerate|(?:(?:outer|i?inner)_problem))\}")
setcounter_regex = re.compile(r"\\setcounter\s*\{[^{}]+\}\{(?:\\value\{)?[^{}]+\}?\}")
item_regex = re.compile(r"\\item")

def get_start(match):
    if match:
        return match.start()
    return float("inf")

def problem_tokenizer(file_string):
    i = 0
    is_item_active = False
    item_start_index = 0

    while True:
        be_match = begin_enumerate_regex.search(file_string, i)
        ee_match = end_enumerate_regex.search(file_string, i)
        sc_match = setcounter_regex.search(file_string, i)
        item_match = item_regex.search(file_string, i)

        if be_match is None and ee_match is None and sc_match is None and item_match is None:
            # All tokens found
            break

        starts = map(get_start, [be_match, ee_match, sc_match, item_match])
        min_start = min(starts)

        i = min_start + 1

        if is_item_active:
            is_item_active = False
            start = file_string.find("\n", item_start_index)

            if start == -1:
                start = float("inf")

            yield Token("item", file_string[item_start_index:min(start,min_start)].strip())

        if starts[3] == min_start:
            is_item_active = True
            item_start_index = item_match.end()

            continue

        token_type = ""
        match_str = ""

        if starts[0] == min_start:
            # begin enumerate
            token_type = "begin_enumerate"
            match_str = be_match.group()
        elif starts[1] == min_start:
            # end enumerate
            token_type = "end_enumerate"
            match_str = ee_match.group()
        elif starts[2] == min_start:
            # set counter
            token_type = "setcounter"
            match_str = sc_match.group()

        if match_str is not "":
            yield Token(token_type, match_str)

# Must consider: \begin{enumerate}, \end{enumerate}, \item, \setcounter{...}{...}, \begin{outer_problem}, \begin{inner_problem}, \begin{iinner_problem}
def problem_generator(file_string, is_answer_key=False):
    global counters

    enum_depth = 0
    record_problem_n = 0

    set_counter_by_value("outer", 0)
    set_counter_by_value("inner", 0)
    set_counter_by_value("iinner", 0)

    for x in xrange(1, 4):
        set_counter_by_value("enum" + "i" * x, 0)

    for token in problem_tokenizer(file_string):
        if token.type == "begin_enumerate":
            name = token.get_enumeration_name()

            if name == "enumerate":
                enum_depth += 1

                set_counter_by_value("enum" + "i" * enum_depth, 0)
            else:
                if name == "outer_problem":
                    enum_depth = 1

                    increment_counter("outer")
                    set_counter_by_value("inner", 0)
                    set_counter_by_value("iinner", 0)
                elif name == "inner_problem":
                    enum_depth = 2

                    increment_counter("inner")
                    set_counter_by_value("iinner", 0)
                elif name == "iinner_problem":
                    enum_depth = 3

                    increment_counter("iinner")

                set_counter("enumi", "outer")
                set_counter("enumii", "inner")
                set_counter("enumiii", "iinner")


        if token.type == "end_enumerate":
            name = token.get_enumeration_name()

            if name == "enumerate":
                enum_depth -= 1

                for x in xrange(enum_depth+1, 4):
                    set_counter_by_value("enum" + "i" * x, 0)
        if token.type == "setcounter":
            counter_names = token.get_counter_names()

            try:
                value = int(counter_names[1])
                set_counter_by_value(counter_names[0], value)
                continue
            except ValueError:
                pass

            set_counter(counter_names[0], counter_names[1])
        if token.type == "item":
            if not is_answer_key:
                increment_counter("enum" + "i" * enum_depth)

            top_problem_n = get_counter("enumi")

            if top_problem_n >= record_problem_n:
                yield Problem(top_problem_n, get_counter("enumii"), get_counter("enumiii"), token.contents)
                record_problem_n = top_problem_n

problem_count = 0

chapter = "comp_func"

answer_key_file = open("comp_func/comp_func_answers.tex", "w")
answer_key_file.write(r"""
\documentclass[../gatm_answers.tex]{subfiles}

\begin{document}

\section{Composition of Functions}
""")

with open("%s/%s_source.tex" % (chapter, chapter), 'r') as problem_file:
    file_string = problem_file.read()

    textbook_problems = list(problem_generator(file_string, False))

    for tb_problem in textbook_problems:
        enum_type = ""
        str_write_out = ""
        needs_start_equals_one = False

        if tb_problem.letter == 0: # top level problem
            enum_type = "outer_problem"
        elif tb_problem.part == 0: # second level problem
            enum_type = "inner_problem"
            if tb_problem.letter == 1:
                needs_start_equals_one = True
        else:
            enum_type = "iinner_problem"
            if tb_problem.part == 1:
                needs_start_equals_one = True

        str_write_out += r"\begin{%s}" % enum_type
        if needs_start_equals_one:
            str_write_out += "[start=1]"

        str_write_out += "\n"

        str_write_out += "\\item %s\n" % tb_problem.contents

        str_write_out += "\\end{%s}\n\n" % enum_type

        answer_key_file.write(str_write_out)

answer_key_file.write(r"""
\end{document}
""")

answer_key_file.close()


print("Checked %s problems." % problem_count)
