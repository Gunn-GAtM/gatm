#!/usr/bin/python

# We use this document to build individual chapters/answer key chapters, the cover/credits/glossary, and the entire textbook/answer key. It's a bit involved, but you'll understand, dear traveler.

# When given a command line argument, the f

import sys
import os

# Fix input from Python 2
try:
    input = raw_input
except NameError:
    pass

def build_textbook():

    pass

def build_key():
    pass

def interactive_build_chapter():
    pass

def interactive_build_key_chapter():
    pass

def build_textbook_cover():
    pass

def build_key_cover():
    pass

def clean_logs():
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
    "textbook_cover": {
        "description": "Build the textbook cover and put it in build/key_chapters.",
        "callback": build_textbook_cover
    },
    "answer_key_cover": {
        "description": "Build the answer key cover and put it in build/chapters.",
        "callback": build_key_cover
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

# Should be the folder gatm/
working_directory = os.path.dirname(os.path.abspath(__file__))
build_directory = os.path.join(working_directory, "build")
textbook_chapter_directory = os.path.join(build_directory, "chapter_answers")

chapter_list = os.listdir

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
        dirname = os.path.join(working_directory, directory.split('/'))
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
        print("Doing operation %s: %s" % (op, description))

        if "callback" in op:
            op["callback"]()

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
            run_operations(operation)
            sys.exit()

if __name__ == "__main__":
    if len(sys.argv) <= 1: # enter interactive
        interactive()
    else:
        pass

