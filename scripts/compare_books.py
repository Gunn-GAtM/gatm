import re

# This program compares the gatm textbook and the answer key to make sure that all questions correspond correctly.

chapter_names = "trig_review itsasnap snap_flip rrg inf cmplx_geo vitamin_i mtrx_mult map_plane plane_rot mat_gen " \
                "comp_map inverses mod_m eigen".split(" ")

counters = {"enumi": 0, "enumii": 0, "enumiii": 0}


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


get_enumeration_name = re.compile(r"\\(?:begin|end)\s*{([^{}]+)}")
get_setcounters1 = re.compile(r"\\setcounter\s*{([^{}]+)}{\\value{([^{}]+)}}")
get_setcounters2 = re.compile(r"\\setcounter\s*{([^{}]+)}{([0-9]+)}")
get_setcounters3 = re.compile(r"\\setcounter\s*{([^{}]+)}{\\the([^{}]+)}")


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
            return next_match.group(1, 2)

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
            code += '.' + str(self.part)  # todo: convert to roman

        return "%s: %s" % (code, self.contents)


begin_enumerate_regex = re.compile(r"\\begin{(?:enumerate|(?:(?:outer|i?inner)_problem))}")
end_enumerate_regex = re.compile(r"\\end{(?:enumerate|(?:(?:outer|i?inner)_problem))}")
setcounter_regex = re.compile(r"\\setcounter\s*{[^{}]+}{(?:\\value{)?[^{}]+}?}")
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

        starts = list(map(get_start, [be_match, ee_match, sc_match, item_match]))
        min_start = min(starts)

        i = min_start + 1

        if is_item_active:
            is_item_active = False
            start = file_string.find("\n", item_start_index)

            if start == -1:
                start = float("inf")

            yield Token("item", file_string[item_start_index:min(start, min_start)].strip())

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


# Must consider: \begin{enumerate}, \end{enumerate}, \item, \setcounter{...}{...}, \begin{outer_problem},
# \begin{inner_problem}, \begin{iinner_problem}
def problem_generator(file_string, is_answer_key=False):
    global counters

    # no idea what's supposed to be local and what's supposed to shadow, so am just leaving it like this
    enum_depth = 0
    record_problem_n = 0

    set_counter_by_value("outer", 0)
    set_counter_by_value("inner", 0)
    set_counter_by_value("iinner", 0)

    for x in range(1, 4):
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

                for x in range(enum_depth + 1, 4):
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

for chapter in chapter_names:
    # 0 means not in an enumerate, 1 means in a top level enumerate, 2 means in a a,b,c enumerate,
    # 3 means in a i, ii, iii enumerate
    enum_depth = 0

    with open("%s/%s_source.tex" % (chapter, chapter), 'r') as problem_file:
        with open("%s/%s_answers.tex" % (chapter, chapter), 'r') as answer_file:
            file_string = problem_file.read()
            answer_file_string = answer_file.read()

            textbook_problems = list(problem_generator(file_string, False))
            key_problems = list(problem_generator(answer_file_string, True))

            problem_count += len(textbook_problems)

            for tb_problem in textbook_problems:
                if "%compare-books-disable" in tb_problem.contents:
                    continue
                if not any(tb_problem.equals(key_problem) for key_problem in key_problems):
                    # Potential desync
                    print("Chapter %s, Problem %s" % (chapter, tb_problem))

                    for key_problem in key_problems:
                        if tb_problem.same_problem_encoding(key_problem):
                            print("ANSWER KEY: Problem %s" % key_problem)

print("Checked %s problems." % problem_count)
