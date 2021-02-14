#!/usr/bin/python

# We use this document to build individual chapters/answer key chapters, the cover/credits/glossary, and the entire textbook/answer key. It's a bit involved, but you'll understand, dear traveler.

# When given a command line argument, the f

import sys
import os
import shutil
import subprocess
import re

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

chapter_list = os.listdir

# Find errors in the log
error_regex = re.compile(":[0-9]*:")

def run_pdflatex_on_file(filename, output_dir=log_directory):
    flags = "-shell-escape -interaction=nonstopmode -file-line-error --output-directory=%s" % log_directory
    flags = flags.split()

    if not os.path.isfile(filename):
        raise RequirementError("File %s does not exist!" + filename)

    print(emph("Running pdflatex on file %s" % filename))

    process = subprocess.Popen(['pdflatex'] + flags + [filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    return (out, err)

    """for line in (out + '\n' + err).split('\n'):
        if error_regex.search(line):
            print(line)"""

def book_path(join_with):
    return os.path.join(book_directory, *join_with.split('/'))

def build_textbook():
    clean_logs()
    run_pdflatex_on_file(book_path("textbook.tex"))


    pass

def build_key():
    pass

def interactive_build_chapter():
    pass

def interactive_build_key_chapter():
    pass

def build_textbook_cover():
    clean_logs()
    pass

def build_key_cover():
    pass

def clean_logs():
    """Empty the log folder to avoid strange conflicts with past builds"""
    print(emph("Emptying logs folder."))
    shutil.rmtree(log_directory)
    os.mkdir(log_directory)

    pass

def clean_chapter_folders():
    pass

def excerpt_chapter_folders():
    pass

def excerpt_key_folders():
    pass

task_list = {
    "all": {
        "description": "Build the textbook and answer key, and dump all individual chapters into the build folder.",
        "subtasks": ["textbook_chapters", "key_chapters"]
    },
    "key_chapters": {
        "description": "Build the answer key and excerpt all answer key chapters into the build/key_chapters folder.",
        "subtasks": ["key", "_excerpt_key_chapters"],
    },
    "textbook_chapters": {
        "description": "Build the textbook and excerpt all textbook chapters into the build/chapters folder.",
        "subtasks": ["textbook", "_excerpt_textbook_chapters"]
    },
    "textbook": {
        "description": "Build the file gatm.pdf.",
        "callback": build_textbook
    },
    "key": {
        "description": "Build the file gatm_answers.pdf",
        "callback": build_key
    },
    "chapter": {
        "description": "Quick build a chapter in its corresponding subfolder and open the PDF (you will be prompted to select the chapter).",
        "callback": interactive_build_chapter
    },
    "key_chapter": {
        "description": "Quick build a chapter of the answer key in its corresponding subfolder and open the PDF.",
        "callback": interactive_build_key_chapter
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
    },
    "_excerpt_chapter_folders": {
        "description": "Take excerpts from the main PDF and put them into the chapters folder",
        "callback": excerpt_chapter_folders
    },
    "_excerpt_key_folders": {
        "description": "Take excerpts from the main PDF and put them into the answer key chapter folder.",
        "callback": excerpt_key_folders
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
    return color_text(terminal_colors.WARNING, text)

def emph(text):
    return color_text(terminal_colors.BOLD, text)

needed_directories = ["build", "build/log", "build/chapters", "build/key_chapters"]
requisite_files = ["book/textbook.tex", "book/answer_key.tex"]

interactive_task_list = [
    "clean",
    "all",
    "textbook_chapters",
    "key_chapters",
    "key",
    "textbook",
    "chapter",
    "key_chapter"
]

def create_needed_directories():
    for directory in needed_directories:
        dirname = os.path.join(working_directory, *directory.split('/'))
        if not os.path.exists(dirname):
            print("Folder %s does not exist!" % directory)
            os.mkdir(directory)
            print("Created directory %s." % dirname)
        elif not os.path.isdir(dirname):
            raise RequirementError("%s exists and is not a folder!")

def check_things():
    """Check that things will work alright"""
    create_needed_directories()

def run_operations(ops):
    if isinstance(ops, str):
        ops = ops.split(' ')

    for opname in ops:
        op = task_list[opname]
        description = op["description"]
        print("Doing operation %s: %s" % (opname, description))

        if "callback" in op:
            op["callback"]()
        elif "subtasks" in op:
            print("Subtasks: " + str(op["subtasks"]))
            run_operations(op["subtasks"])

def interactive():
    """Interactive mode, where we guide the user to whatever build option."""

    print("No arguments given, entering %s." % emph("interactive mode"))
    print("Enter the desired operation (some will include extra options):")
    for taskname in interactive_task_list:
        details = task_list[taskname]
        print ("  %s: %s" % (emph(taskname), details["description"]))

    print("(Enter %s to quit.)" % emph('q'))
    while True:
        operation = input("> ").replace(' ', '')
        if operation in ['q', 'quit']:
            sys.exit()

        if operation not in task_list:
            print "Unrecognized operation %s." % warn(operation)
        else:
            check_things()
            run_operations(operation)
            sys.exit()

if __name__ == "__main__":
    if len(sys.argv) <= 1: # enter interactive
        interactive()
    else:
        pass

