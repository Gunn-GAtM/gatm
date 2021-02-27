#!/usr/bin/python

# We use this document to build individual chapters/answer key chapters, the cover/credits/glossary, and the entire textbook/answer key. It's a bit involved, but you'll understand, dear traveler. Check README.md for context.

import sys
import os
import shutil
import subprocess
import re
import ntpath
import time
import argparse
import platform

# Fix input from Python 2
try:
    input = raw_input
except NameError:
    pass

# Should be the folder gatm/
working_directory = os.path.dirname(os.path.abspath(__file__))
build_directory = os.path.join(working_directory, "build")
log_directory = os.path.join(build_directory, "log")
textbook_chapter_directory = os.path.join(build_directory, "chapters")
answer_key_chapter_directory = os.path.join(build_directory, "key_chapters")

book_directory = os.path.join(working_directory, "book")

# Find errors in the log
error_regex = re.compile(":[0-9]*:")
fatal_error_test = "Fatal error occurred, no output PDF file produced!"

# First capture group is whether it's the start or end of the chapter. Second group is the number of the chapter (ex: 1 for trig review). Third group is the absolute page number, starting from first page = 0.
page_number_typeout_regex = re.compile("Page number of chapter (start|end):([0-9]+.*)\s+([0-9]+)")
shipout_page_number_regex = re.compile("\[([0-9]+)")

FNULL = None

def make_progress_bar(percent, width=50):
    """Make a silly progress bar of a given width"""
    if percent < 0:
        percent = 0
    if percent > 1:
        percent = 1

    parts = width - 2
    filled = int(round(percent * width))
    filled -= 1 # for the > character
    if filled < 0: filled = 0
    if filled > parts - 1: filled = parts - 1
    unfilled = parts - 1 - filled
    return emph('[' + filled * '=' + '>' + ' ' * unfilled + ']') + '(' + str(int(round(percent * 100))) + '%)'

def get_devnull():
    global FNULL
    if not FNULL:
        FNULL = open(os.devnull, 'w')

class LatexError(Exception):
    """Error in pdflatex"""

progress_bar_length = 0

def print_progress_bar(percent, width=50):
    """Print a progress bar to the screen. We keep track of its character length so that later we can remove it with repeated backspaces."""
    global progress_bar_length

    text = make_progress_bar(percent, width) + '\n'
    progress_bar_length = len(text) - 1
    sys.stdout.write(text)

def erase_progress_bar():
    """Erase the previous progress bar with repeated backspace (\b) characters"""
    global progress_bar_length

    if progress_bar_length != 0:
        # move up a line and then delete the progress bar
        sys.stdout.write('\x1B[A' + '\b' * progress_bar_length)
        progress_bar_length = 0

def commit_progress_bar():
    """Prevent erasure of the progress bar (when things are complete basically)"""
    global progress_bar_length
    progress_bar_length = 0

def run_pdflatex_on_file(filename,
                         output_dir=log_directory,
                         live_output=True,
                         estimate_progress=True,
                         estimated_pages=60,
                         output_errors=True,
                         throw_on_fatal=True,
                         throw_on_error=False,
                         get_chapter_pages=True):
    """Run pdflatex on a file and dump the result into the log folder, where it shall eventually be UPROOTED from"""
    time_start = time.time()

    if not live_output:
        estimate_progress = False
    if estimated_pages == -1:
        estimate_progress = False

    # Env for pdflatex to run in. Set max print line and error line to 1000
    env = os.environ.copy()
    env["max_print_line"] = "1000"
    env["error_line"] = "1000"
    env["half_error_line"] = "238"

    # Lets pdflatex search for files from the parent directory as a working directory and intermediate files in the output directory, but logging everything in the output directory
    env["TEXINPUTS"] = os.path.dirname(filename) + ':' + output_dir + ';'

    flags = "--synctex=1 --shell-escape --interaction=nonstopmode --file-line-error"
    flags = flags.split() + [f'--output-directory={output_dir}'] # Tfw directory with spaces, fuck me

    if not os.path.isfile(filename):
        raise RequirementError(f"File {filename} does not exist!")

    print(emph(f"Running pdflatex on file {filename}, outputting into directory {output_dir}"))
    outputted_chapter_page_info = {}

    process = subprocess.Popen(['pdflatex'] + flags + [filename], stdout=subprocess.PIPE, stderr=get_devnull(), env=env, cwd=output_dir, text=True)
    page_count = {"val": 0}

    commit_progress_bar()

    # LOL
    def output_error(err):
        if estimate_progress:
            erase_progress_bar()
            print(err)
            print_progress_bar(page_count["val"] / float(estimated_pages))
        else:
            print(err)

    # Handle a line, which can either be done in real time or after the fact
    def handle_line(line):
        line = line.strip()
        if throw_on_fatal:
            if fatal_error_test in line:
                raise LatexError(emph(warn("Fatal error, see log for details.")))
        if output_errors or throw_on_error:
            # Precedes a thrown error
            if line.startswith("! LaTeX Error"):
                if output_errors:
                    output_error(warn("! LaTeX Error") + ':' + line[14:])
            match = error_regex.search(line)
            if match:
                # We have a line error
                location = line[:match.end()-1]
                error = line[match.end():]

                if throw_on_error:
                    raise LatexError(emph(warn(f"Unexpected line error at {location}")) + f": {error}")
                if output_errors:
                    output_error(warn(location) + ':' + error)
        if get_chapter_pages: # Keep track of special typeout things and page shipout
            match = page_number_typeout_regex.match(line)
            if match: # See above for group meanings
                groups = match.groups()
                chapter_name = groups[1]
                abspage = int(groups[2])

                try:
                    p_info = outputted_chapter_page_info[chapter_name]
                    # start page already found, so this is the end page
                    outputted_chapter_page_info[chapter_name] = (p_info[0], abspage)
                except KeyError:
                    outputted_chapter_page_info[chapter_name] = (abspage, -1)
        if estimate_progress:
            # Page number output is of the form [(0-9)+ ... ] so we search for "[(0-9)+"
            match = shipout_page_number_regex.findall(line)
            if match:
                for pagenum in match:
                    pagenum = int(pagenum)
                    if pagenum == page_count["val"] + 1: # Catch false positives like [8pt,twosided]
                        page_count["val"] = pagenum

                    erase_progress_bar()
                    print_progress_bar(page_count["val"] / float(estimated_pages))

    # Fancy thing which allows the pdflatex command to be run and python to listen to it as a stream of lines
    if live_output:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            handle_line(line)
    else:
        out, _err = process.communicate()

        # Run the entire thing, then look at it after the fact
        for line in out.split('\n'):
            handle_line(line)

    if estimate_progress:
        erase_progress_bar()
        print_progress_bar(1)

    return outputted_chapter_page_info

def run_asy_in_dir(dirname, estimate_progress=True):
    """Compile all the .asy files in a given directory which were dumped out by the first pdflatex call"""
    print(emph("Compiling .asy files in " + dirname))
    file_list = []

    for filename in os.listdir(dirname):
        if filename.endswith(".asy"):
            file_list.append(filename)

    asy_count = len(file_list)
    print("Total Asymptote files to render: " + str(asy_count))

    commit_progress_bar()

    for i, filename in enumerate(file_list):
        # Run asymptote on each file
        process = subprocess.Popen(['asy', filename], cwd=dirname, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()

        out, err = process.communicate()

        if err:
            raise RuntimeError(warn(f"Unexpected Asymptote error in file {filename}") + f":\n{err}")

        if estimate_progress:
            erase_progress_bar()

        if out:
            print(f"Asymptote on file {filename} logged:\n{out}")

        if estimate_progress:
           print_progress_bar((i+1) / float(asy_count))

def book_path(join_with):
    return os.path.join(book_directory, *join_with.split('/'))

def log_path(join_with):
    return os.path.join(log_directory, *join_with.split('/'))

def build_path(join_with):
    return os.path.join(build_directory, *join_with.split('/'))

def build_textbook(excerpt_chapters=True):
    build_book("textbook", excerpt_chapters)

# Credit to https://stackoverflow.com/a/435669/13458117
def open_file(filepath):
    print(emph("Opening file %s." % filepath))
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))


def build_book(book="textbook", excerpt_chapters=True):
    """Build the thing. If chapter_name is given, then we build in the chapter folder. If not, we build in the log folder and move to build."""
    filename = book if not chapter_name else ("chapter" if book == "textbook" else "answers")
    textbook_path = book_path(filename + ".tex") if not chapter_name else os.path.join(chapter_path, filename + ".tex")
    local_log_directory = log_directory

    if not os.path.isfile(textbook_path):
        raise RequirementError(warn(f"File {textbook_path} does not exist!"))

    if chapter_name:
        local_log_directory = chapter_path
        clean_chapter_folders()

    if not chapter_name:
        # The textbook cover's being located at build/misc/textbook_cover.pdf is required for the textbook to compile
        build_cover(book)
        clean_logs()

    est_pages = -1 if chapter_name else (60 if book == "textbook" else 170)

    print("Building %s: Output inline Asymptote files (1/5)" % book)
    run_pdflatex_on_file(textbook_path, estimated_pages=est_pages, output_dir=local_log_directory)
    print("Building %s: Compile Asymptote figures (2/5)" % book)
    run_asy_in_dir(local_log_directory)
    print("Building %s: Create the PDF and reference/label locations (3/5)" % book)
    run_pdflatex_on_file(textbook_path, estimated_pages=est_pages, output_dir=local_log_directory)
    print("Building %s: Fill in the reference/label locations (4/5)" % book)
    run_pdflatex_on_file(textbook_path, estimated_pages=est_pages, output_dir=local_log_directory)
    print("Building %s: Compile one more time, getting correct zref locations (5/5)" % book)
    chapter_page_info = run_pdflatex_on_file(textbook_path, estimated_pages=est_pages, output_dir=local_log_directory)

    destfile = build_path("gatm.pdf" if book == "textbook" else "gatm_key.pdf") if not chapter_name else os.path.join(chapter_path, filename + '.pdf')

    if not chapter_name:
        print("Moving compiled %s file to %s." % (book, destfile))
        os.rename(log_path("%s.pdf" % book), destfile)

    if open_output_files:
        open_file(destfile)

    if not chapter_name and excerpt_chapters:
        excerpt_folder = build_path("chapters" if book == "textbook" else "key_chapters")
        chapter_count = len(chapter_page_info.keys())
        print(emph("Excerpting %s chapters using pdfjam." % chapter_count))

        for i, (chapter, page_range) in enumerate(chapter_page_info.items()):
            process = subprocess.Popen(['pdfjam', '-o', os.path.join(excerpt_folder, chapter + '.pdf'), destfile, '%s-%s' % page_range], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            indx = i + 1

            print(f"Finished excerpting chapter {chapter}. ({indx}/{chapter_count})")

def build_key(excerpt_chapters=True):
    build_book("key", excerpt_chapters)

def build_cover(book="textbook"):
    """Build either the textbook cover or key cover and move it to build/misc/<book>_cover.pdf"""
    clean_logs()

    print("Building %s cover: Output inline Asymptote files (1/3)" % book)
    run_pdflatex_on_file(book_path("cover/%s_cover.tex" % book), live_output=False)
    print("Building %s cover image (2/3)" % book)
    run_asy_in_dir(log_directory, False)
    print("Building %s cover with cover image (3/3)" % book)
    run_pdflatex_on_file(book_path("cover/%s_cover.tex" % book), live_output=False)
    print("Moving compiled %s cover file to build/misc/%s_cover.pdf." % (book, book))
    os.rename(log_path("%s_cover.pdf" % book), build_path("misc/%s_cover.pdf" % book))

def clean_logs():
    """Empty the log folder to avoid strange conflicts with past builds"""
    print(emph("Emptying logs folder."))
    shutil.rmtree(log_directory)
    os.mkdir(log_directory)

permitted_file = re.compile(".*[^0-9]\.tex")
def clean_chap_folder(path):
    print("Cleaning chapter folder %s" % path)
    for f in os.listdir(path):
        if not os.path.isdir(f) and not permitted_file.match(f):
            # DESTROY THE HEATHENS AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
            os.remove(os.path.join(path, f))

def clean_chapter_folders():
    # Cleaning chapter folders, deleting anything not of the form *[!0-9].tex
    if chapter_name:
        clean_chap_folder(chapter_path)
    else:
        for ch in chapter_list:
            clean_chap_folder(book_path(ch))


chapter_name = "" # If empty, builds as normal; if a chapter name, builds that particular chapter.
chapter_folder = ""
open_output_files = False # Whether to open output files

task_list = {
    "all": {
        "description": "Build the textbook and answer key, and dump all individual chapters into the build folder.",
        "subtasks": ["textbook", "key"]
    },
    "key": {
        "description": "Build the answer key and excerpt all answer key chapters into the build/key_chapters folder.",
        "callback": lambda: build_key(True)
    },
    "textbook": {
        "description": "Build the textbook and excerpt all textbook chapters into the build/chapters folder.",
        "callback": lambda: build_textbook(True)
    },
    "textbook_no_chapters": {
        "description": "Build the file gatm.pdf.",
        "callback": lambda: build_textbook(False)
    },
    "key_no_chapters": {
        "description": "Build the file gatm_key.pdf",
        "callback": lambda: build_key(False)
    },
    "clean": {
        "description": "Empty the logs folder and delete all files in chapter folders besides 'answers.tex' and 'chapter.tex'.",
        "subtasks": ["clean_logs", "clean_chapter_folders"]
    },
    "clean_logs": {
        "description": "Empty the build/logs folder.",
        "callback": clean_logs
    },
    "clean_chapter_folders": {
        "description": "Clean files in chapter folders left over after a chapter build.",
        "callback": clean_chapter_folders
    }
}

class RequirementError(Exception):
    """Raised when the build environment needs to be fixed."""

# Credit to https://stackoverflow.com/a/287944/13458117
class terminal_colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def color_text(color, text):
    return color + text + terminal_colors.ENDC

def yay(text):
    return color_text(terminal_colors.OKGREEN, text)

def warn(text):
    return color_text(terminal_colors.FAIL, text)

def emph(text):
    return color_text(terminal_colors.BOLD, text)

needed_directories = ["build", "build/log", "build/misc", "build/chapters", "build/key_chapters"]
requisite_files = ["book/textbook.tex", "book/answer_key.tex"]

interactive_task_list = [
    "clean",
    "all",
    "key",
    "textbook",
    "chapter",
    "key_chapter"
]

def create_needed_directories():
    for directory in needed_directories:
        dirname = os.path.join(working_directory, *directory.split('/'))
        if not os.path.exists(dirname):
            print(f"Folder {directory} does not exist!")
            os.mkdir(directory)
            print(f"Created directory {dirname}.")
        elif not os.path.isdir(dirname):
            raise RequirementError(f"{directory} exists and is not a folder!")

def check_things():
    """Check that things will work alright"""
    create_needed_directories()

def run_operations(ops):
    if isinstance(ops, str):
        ops = ops.split(' ')

    for opname in ops:
        op = task_list[opname]
        description = op["description"]
        print(f"Doing operation {opname}: {description}")

        if "callback" in op:
            op["callback"]()
        elif "subtasks" in op:
            print(f"Subtasks: {op['subtasks']}")
            run_operations(op["subtasks"])

def interactive():
    """Interactive mode, where we guide the user to whatever build option."""

    print(f"No arguments given, entering {emph('interactive mode')}.")
    print("Enter the desired operation (some will include extra options):")
    for taskname in interactive_task_list:
        details = task_list[taskname]
        print("  %s: %s" % (emph(taskname), details["description"]))

    print(f"(Enter {emph('q')} to quit.)")
    while True:
        operation = input("> ").replace(' ', '')
        if operation in ['q', 'quit']:
            sys.exit()

        if operation not in task_list:
            print("Unrecognized operation %s." % warn(operation))
        else:
            check_things()
            run_operations(operation)
            sys.exit()

chapter_list = sorted(filter(lambda p: os.path.isdir(os.path.join(book_directory, p)), os.listdir(book_directory)))
chapter_list.remove("template")

def get_chapter_name_from_arg(name):
    """Get the chapter name from a partial name, by matching the chapter which starts with the same character(s), with alphabetical precedence"""
    for ch in chapter_list:
        if ch.startswith(name):
            return ch

    raise ValueError(f"No chapter beginning with '{name}' found")

if __name__ == "__main__":
    if len(sys.argv) <= 1: # enter interactive
        interactive()
    else:
        parser = argparse.ArgumentParser(description='Build various things for gatm.pdf. Provide a list of tasks to complete.')
        parser.add_argument('taskname', metavar='task', type=str, nargs='+', help='task to complete, out of: ' + ', '.join(sorted(task_list.keys())))
        parser.add_argument('--chapter', '-c', type=str, nargs='?', default="", help='chapter to select, so that only the given chapter is built')
        parser.add_argument('--open', '-o', help="flag to open the output file as a PDF", action="store_true")

        args = parser.parse_args()
        tasks = args.taskname

        if args.chapter:
            chapter_name = get_chapter_name_from_arg(args.chapter)
            chapter_path = os.path.join(book_directory, chapter_name)

        if args.open:
            open_output_files = True

        check_things()
        run_operations(tasks)


