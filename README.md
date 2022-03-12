# Gunn GAtM
A rewrite of _A Geometric Approach to Matrices_ (frequently abbreviated to "GAtM") by Peter Herreshoff.
If you are looking for the text, go to https://gunn-gatm.github.io/ for the PDFs without all the code.

## Information for Prospective Contributors
This project was first thrown together in summer of 2019. I'd estimate it took a couple hundred hours, but it's not remotely free of errors and is often inconsistent. Today is February 13, 2021, and after some encouragement by a certain Yu-Ting Chang, I (Timothy) have decided to work on it once more, correcting errors and making the build system less terrifying.

### File Structure
There are two main documents: the textbook, and the answer key. The textbook is composed of a cover, a credits page, sixteen chapters, and a glossary. The answer key is composed of a cover and sixteen chapters. The cover and credits are mostly handled separately. All these pages are inside the `book/` directory; there is one folder per chapter, with each folder containing a chapter source file named `chapter.tex`, and an answer key source file named `answers.tex`.

If all of the textbook were to be put into one monolithic document, it would be some thousand lines long, and even longer for the answer key. More importantly for someone working on the document, it would take ages to see if your small-scale changes worked, since you'd have to recompile the whole book each time. To combat this problem, we use the *subfiles* package and put each chapter into its own folder. The chapters are given their order by the number preceding their folder.

The *subfiles* package is relatively intuitive. When compiling the document as a whole, we include a subfile with the command `\subfile{./path/to/chapter.tex}`, which basically copy-and-pastes the contents of that file into the main document. More tricky is when we compile a subfile, each of which is topped with a special documentclass: `\documentclass[../textbook.tex]{subfiles}` or, in the case of the answer key, `\documentclass[../answers.tex]{subfiles}`. This annotation causes the entire preamble of the main document to be included in the subfile, including document styling information, macros like `\twomat`, Asymptote definitions, et cetera.

A chapter is included in the main document if it begins with a number 0–9. All the corresponding `chapter.tex` files are thus included as subfiles of `textbook.tex`, and `answers.tex` files as subfiles of `answer_key.tex`. The cover, which has different styling than the rest of the document, is included in a special way, by first compiling it to a PDF and then including the PDF in the main document.

### Building
The book builds into the `build/` folder. (Didn't expect that, huh?) The build folder has the following structure:

```
.
+-- gatm.pdf
+-- gatm_key.pdf
+-- chapters
    +-- 1 Trigonometry Review.pdf
    +-- ... rest of the chapters ...
+-- key_chapters
    +-- 1 Trigonometry Review.pdf
    +-- ... rest of the chapters ...
+-- log
    +-- gatm.log
    +-- ... various debugging files ...
+-- misc
    +-- textbook_cover.pdf
    +-- key_cover.pdf
```

Simple enough. What's not so simple is the actual building process, as we encounter some of LaTeX's most stupefying characteristics.

Building works with `python build.py`. We can either give it command line arguments, or if no arguments are provided, we enter an interactive mode. To build everything in build, run `python build.py all`, which builds the textbook and answer key and then excerpts all chapters. To build the textbook ONLY, run `python build.py textbook_no_chapters`, which will not update `textbook_chapters/`. To build the textbook and chapters, run `python build.py textbook`. Similarly, building the answer key is just `python build.py key`, and without chapters, `python build.py key_no_chapters`.

To build a specific chapter for *testing*, run `python build.py textbook -c <chapter index or name>`, like `python build.py textbook -c 10`, which will dump `chapter.pdf` into the folder `book/10 Rotations of the Plane`. In this case, the only meaningful operations are `all`, which test builds both the chapter and answer key; `chapter`; `key`; `clean_logs`. In this case, building does not build the entire textbook; it *only* builds the given chapter, and doesn't do any excerpting. This is mostly the same as the real deal and is optimal for testing, but has the following discrepancies:
- No cross-references (to figures or questions outside of the current chapter)
- Differing page numbers
- Incorrect chapter number

The build is fast, but slightly incorrect, and dumps the PDF into the *chapter folder*, not the build folder, because it's not intended for students to see. To build a chapter for *production*, where we put it into the folder `build/chapters/`, we first need to build the entire document (either `gatm.pdf` or `gatm_key.pdf`) and then *excerpt* the chapter from the full document. Otherwise there will be some small differences from the main document (most notably, cross-references like "see question 6 on page 3" will appear as "see question ?? on page ??").

#### How does building work?

Good question. The contents of *build.py* will probably elucidate some details, but the gist of it is we use the `log/` directory as an intermediate file—an arena of sorts, if you will. We first compile a given file with pdflatex. If the file contains inline Asymptote vector graphics, a bunch of `.asy` files will be dumped into the `log/` directory. We then run the `asy` command on those files, which compiles each into a PDF. We then run `pdflatex` again, which assimilates all the compiled Asymptote files into the document. We're not yet done; information about the location of figures and labels has been dumped out, but is not yet used, so things will say "Figure **??**". We thus run `pdflatex` a final time, which includes this ref information.

The cover is a special case. For reasons I forget, it's compiled into a separate PDF first, placed in `build/misc/textbook_cover.pdf` (or `key_cover.pdf`), then included via the module pdfpages into the main document. Sorry for the confusion.

Chapters are excerpted via a rather... hacky method. If you examine the macro `\inclchapter`, which inserts a chapter by name into the main document, you'll see that it writes some information to the log file via the command `\typeout`. In particular, it writes things like "Page number of chapter start:<chapter> <page num>", which is pounced upon by a corresponding regex in the `build_book` function. It records the start and end pages of chapters. The page number is the *absolute page*, meaning it doesn't care about page numbers; it's the literal nth page of the document, indexed from 1. We then use `pdfjam` to grab the chapter out and write it to `chapter/` or `key_chapters/`. Then we try to soothe ourselves, knowing that another embarrassing error will crop up soon.

Building chapters is a distinct process. We run the same three commands, but inside a *chapter folder* itself—the log file is not involved. The `subfiles` package makes the build relatively consistent, save a few differences, which are detailed above. Because the main point of building a chapter is editing it and seeing the results, the program can also automatically open the chapter (in the default system viewer, e.g., Preview on macOS) by passing the `--open` flag. For example:

```bash
python build.py textbook --chapter 1               # Builds 01 Trigonometry Review to book/01 Trigonometry Review/chapter.pdf and doesn't open it
python build.py key --chapter 2 --open             # Builds chapter 2 to book/02 It's a Snap/answers.pdf and opens it in the default program
```

This dumps a lot of random build logging shit into the chapter folders, which *is* `.gitignore`d, but can get annoying. It can be swept up with the `clean` task in `build.py`, i.e., `python build.py clean`.

#### What is Asymptote?

Asymptote Vector Graphics is a language for creating... mathematical vector graphics. Googling about it can be a bit hard because it's overshadowed by the actual mathematical concept of an asymptote, but there is [a nice long PDF](https://asymptote.sourceforge.io/asymptote_tutorial.pdf) detailing most of the language.  Its syntax is based on C++ and it's not *too* hard to pick up, but explaining it is outside the scope of this Markdown document.

Asymptote files end with the extension `.asy`, and are compiled with the command... `asy`. While often figures can be placed in their own separate asy files, I personally like the convenience of inline Asymptote, which is done in documents with `\begin{asy} ... \end{asy}`. Using inline Asymptote does make the building process a bit more complicated; running `pdflatex` looks for the compiled results of inline Asymptote files, and, seeing none, will output a bunch of intermediate `.asy` files into the log directory. (see above)

It's important to understand how the `.asy` files are generated. Their contents are not only the contents of the code between `\begin{asy}` and `\end{asy}`, but also the contents of all preceding `\begin{asydef}` / `\end{asydef}` code snippets, which are used to define shared functions. These `asydef`s may define functions or variables that later `asy`s will use.

#### Installing dependencies
Note that you will need `pdflatex` to do this, which you can get from a source like TeXLive: http://www.tug.org/texlive/ (for macOS, it is recommended to get [MacTeX](http://www.tug.org/mactex/)). You will also need Asymptote Vector Graphics, which you can get from http://asymptote.sourceforge.net/. As of February 2021, the build system has only been tested to work on macOS, with plans to possibly expand and test on Windows and Linux later.

### Repository workflows
The production build of GAtM, currently live at https://gunn-gatm.github.io/ (with source files at https://github.com/Gunn-GAtM/gunn-gatm.github.io), is automatically updated through Github Actions after every commit in this source repo. Previously, when you made an edit (even a simple, one-line typo fix), you needed to manually rebuild everything, make sure that's committed, push to this repo, and then also the production build repo. Thankfully, this process has been simplified with automatic workflows. It's still recommended, especially for larger edits, to rebuild yourself first and check whether the changes are valid, but you no longer need to go through each step described above (and also the `build/` folder is now `.gitignore`d). We can thank our Lord Yu-Ting Chang for this development.

Inside `.github/workflows/`, you will see 3 workflow `.yml` files for Github Actions: `push.yml`, `pull_request.yml`, and `autoblack.yml`. On every push to this repository, the `push.yml` workflow is activated (wow, who would've guessed?). After installing the dependencies on a macOS virtual environment using HomeBrew (sped up through some caching), the Action rebuilds everything automatically and auto-deploys to the production site repo. On every pull request (or PR sync, reopen, etc.), the `pull_request.yml` workflow rebuilds the textbook with the proposed changes, adding the `build/` directory as a Workflow Artifact to be downloaded/viewed
under the Checks tab for that PR (another way to ensure changes are valid). Finally, if a push includes a change to a `.py` file that was not formatted according to `Black` standards (https://github.com/psf/black), the `autoblack` workflow will lint and push the changes to the Python files to this repo.

**Important note to future maintainers**: an ssh key is what allows the `push.yml` Action from this repo to push to the production site repo; in case it no longer functions, just regenerate a new public/private ssh key (similar to setting up git on your computer to work with GitHub), and place the private key, with the name `DEPLOY_KEY`, as a new secret under `Settings > Secrets > Repository Secrets` in this repo, and the public key, also named `DEPLOY_KEY`, as an actual deploy key under `Settings > Deploy Keys` in the production site repo.

Enjoy!
    
### History

Just to pat myself on the back a little bit. This repository began as *anematode/gatm* and moved here to the commune (directly, I think). [Here](https://github.com/Gunn-GAtM/gatm/commit/5637169c3534f23efb92e4f2807fe39abb0fe9a2) is the first commit, on February 8, 2019. The first LaTeX is added [a few commits later](https://github.com/Gunn-GAtM/gatm/commit/284264b13b105d04305131dd9f08a6056c6aef5d). I'll note that I never had access to the original textbook source code---didn't think to ask!---but that proved to not be a problem. After working on the first couple chapters, work stagnated until about May, when I decided it was high time to [get started](https://github.com/Gunn-GAtM/gatm/commit/ed7e3e0bf637d0a2992679f18edb3e20d58d3ac0).
    
The initial build system was beyond crude. It was just a single bash file `b.sh` that changed little from [this](https://github.com/Gunn-GAtM/gatm/blob/ed7e3e0bf637d0a2992679f18edb3e20d58d3ac0/b.sh). You'll note the handy little disclaimer "expect superfluous errors" in the output. Errors indeed. Tides of them. Poor Brandon had to wade through all that and pick out what was actually the problem. At least I used subfiles from the get go.

`bf.sh` was soon created to build folders. It was nearly as crude as `b.sh`, but at least made life a bit easier. I finished most of the textbook content by the [end of May](https://github.com/Gunn-GAtM/gatm/commit/8d8dbbc9f4f2e6ead86ec8a615b28082bf1795ce) and [began work on the answer key](https://github.com/Gunn-GAtM/gatm/commit/1696dd021d7f1cc142e838e7d4b62733ea33d97a). The following month and a half was a time of prolific output on the answer key, with [corresponding](https://github.com/Gunn-GAtM/gatm/commit/c608d06a4ed20b5df4a5990ecaf28c7cbe200a9f) [high](https://github.com/Gunn-GAtM/gatm/commit/426f76e581d31c31babf8923dac7e17c605a780a) [emotion](https://github.com/Gunn-GAtM/gatm/commit/3061a73d620279d78316bd2644c2167a0ee2732f). I had little progress bars that [I'd occasionally update](https://github.com/Gunn-GAtM/gatm/commit/7d39096f9278fb2352c6eea203fd2e80dacc0662) to indicate how much I'd finished.
    
[This](https://github.com/Gunn-GAtM/gatm/commit/042df89a49bac2931e788b2233d6d7c43056508e) was the final commit from June till October 2019, when work began in earnest in preparation for the next junior class, almost entirely by Brandon. I was rewriting the textbook the summer after I took Analysis (having skipped one grade), and wanted it done before my fellow juniors took the class. Brandon finished it up and sent it in February 2020; we were in a bit of a time crunch at that point. Thanks Bulby; couldn't have done it without you.
    
The project fell silent for nearly a year. The class remained painful; errors accumulated; but the new textbook was indeed used, even appreciated. A few particularly nasty problems had been reworded or *shhh* removed. The textbook's prose had been rewritten for clarity. And an answer key, although pedantically precise at times and indubitably incorrect at others, had been created. The textbook was physically printed. I actually don't have a copy of it, but it's piss yellow.
    
COVID-19 came. I went up a year, and life matters were much more pressing than this textbook. I met Yu-Ting, who since February 2021 has been an incredible collaborator. The textbook has improved significantly even since the 2020 version, largely thanks to his keen eye. I [created a new build system](https://github.com/Gunn-GAtM/gatm/commit/a14aef357eb685ca329c12e31c2cf7c212ac87ba) and made parts of the textbook more uniform, while Yu-Ting [created a system](https://github.com/Gunn-GAtM/gatm/commit/e22152f94e7b0297340fdcf333b7b63e32099cab) that automatically rebuilds the online version of the textbook with every next commit. Works like a charm.
    
Some stats:
    
    Timoothy:gatm timoothy$ find . -name "chapter.tex" -exec wc -l {} +
     609 ./book/16 Composition of Functions/chapter.textex
     604 ./book/12 Composite Mappings of the Plane/chapter.tex
     535 ./book/06 Geometry of Complex Numbers/chapter.tex
     479 ./book/08 Matrix Multiplication/chapter.tex
     424 ./book/09 Mapping the Plane with Matrices/chapter.tex
     304 ./book/03 From Snaps to Flips/chapter.tex
     291 ./book/13 Inverses/chapter.
     245 ./book/02 It's a Snap/chapter.tex
     233 ./book/04 Rotation and Reflection Groups/chapter.tex
     231 ./book/14 Multiplication Modulo m Meets Groups/chapter.tex
     224 ./book/15 Eigenvectors and Eigenvalues/chapter.tex
     196 ./book/01 Trigonometry Review/chapter.tex
     192 ./book/11 Matrices Generate Groups/chapter.tex
     188 ./book/05 Infinite Groups/chapter.tex
      91 ./book/10 Rotations of the Plane/chapter.tex
      84 ./book/07 Your Daily Dose of Vitamin i/chapter.tex
      72 ./book/glossary/chapter.tex
      51 ./book/credits/chapter.tex
    5060 total
    
    Timoothy:gatm timoothy$ find . -name "answers.tex" -exec wc -l {} +
    1738 ./book/06 Geometry of Complex Numbers/answers.tex
    1645 ./book/04 Rotation and Reflection Groups/answers.tex
    1629 ./book/12 Composite Mappings of the Plane/answers.tex
    1170 ./book/15 Eigenvectors and Eigenvalues/answers.tex
    1120 ./book/09 Mapping the Plane with Matrices/answers.tex
    1105 ./book/08 Matrix Multiplication/answers.tex
     869 ./book/11 Matrices Generate Groups/answers.tex
     726 ./book/05 Infinite Groups/answers.tex
     722 ./book/13 Inverses/answers.tex
     703 ./book/02 It's a Snap/answers.tex
     611 ./book/03 From Snaps to Flips/answers.tex
     590 ./book/16 Composition of Functions/answers.tex
     541 ./book/01 Trigonometry Review/answers.tex
     513 ./book/07 Your Daily Dose of Vitamin i/answers.tex
     473 ./book/10 Rotations of the Plane/answers.tex
     340 ./book/14 Multiplication Modulo m Meets Groups/answers.tex
    14502 total
    
    Timoothy:book timoothy$ find . -name "*.tex" -exec wc -w {} +
     807 ./10 Rotations of the Plane/chapter.tex
    2191 ./10 Rotations of the Plane/answers.tex
    1310 ./04 Rotation and Reflection Groups/chapter.tex
    6639 ./04 Rotation and Reflection Groups/answers.tex
    1736 ./15 Eigenvectors and Eigenvalues/chapter.tex
    4707 ./15 Eigenvectors and Eigenvalues/answers.tex
     521 ./key.tex
    2840 ./08 Matrix Multiplication/chapter.tex
    5078 ./08 Matrix Multiplication/answers.tex
       8 ./template/chapter.tex
       5 ./template/answers.tex
    1401 ./11 Matrices Generate Groups/chapter.tex
    5321 ./11 Matrices Generate Groups/answers.tex
    1715 ./02 It's a Snap/chapter.tex
    4536 ./02 It's a Snap/answers.tex
    3733 ./16 Composition of Functions/chapter.tex
    2164 ./16 Composition of Functions/answers.tex
    1524 ./14 Multiplication Modulo m Meets Groups/chapter.tex
    1971 ./14 Multiplication Modulo m Meets Groups/answers.tex
    2551 ./09 Mapping the Plane with Matrices/chapter.tex
    5397 ./09 Mapping the Plane with Matrices/answers.tex
     881 ./01 Trigonometry Review/chapter.tex
    1897 ./01 Trigonometry Review/answers.tex
    2206 ./05 Infinite Groups/chapter.tex
    4565 ./05 Infinite Groups/answers.tex
     523 ./glossary/chapter.tex
    1665 ./textbook.tex
    2113 ./13 Inverses/chapter.tex
    4786 ./13 Inverses/answers.tex
    3002 ./06 Geometry of Complex Numbers/chapter.tex
    8315 ./06 Geometry of Complex Numbers/answers.tex
    3346 ./12 Composite Mappings of the Plane/chapter.tex
    6958 ./12 Composite Mappings of the Plane/answers.tex
    1792 ./03 From Snaps to Flips/chapter.tex
    2425 ./03 From Snaps to Flips/answers.tex
     332 ./07 Your Daily Dose of Vitamin i/chapter.tex
    2497 ./07 Your Daily Dose of Vitamin i/answers.tex
     279 ./credits/chapter.tex
     189 ./cover/key_cover.tex
     186 ./cover/textbook_cover.tex
    104112 total
