# GAtM
A rewrite of _A Geometric Approach to Matrices_ (frequently abbreviated to "GAtM") by Peter Herreshoff.
If you are looking for the text, go to https://gunn-gatm.github.io/ for the PDFs without all the code.

## Information for prospective contributors
This project was first bodged together in summer of 2019. I'd estimate it took a couple hundred hours, but it's not remotely free of errors and is often inconsistent. Today is February 13, 2021, and after some encouragement by a certain Yu-Ting Chang, I (Timothy) have decided to work on it once more, correcting errors and making the build system less terrifying.

### Structure
There are two main documents: the textbook, and the answer key. The textbook comprises a cover, a credits page, sixteen chapters, and a glossary. The answer key comprises a cover and sixteen chapters. For simplicity, we treat the cover and credits as pseudo-chapters sometimes, even though they are handled separately. 

If all of the textbook were to be put into one monolithic document, it would be some thousand lines long, and even longer for the answer key. More importantly as someone working on the document, it would take ages to see if your changes worked on a particular chapter, since you'd have to recompile the whole book each time. To combat this problem, we use the *subfiles* package, and put each chapter into its own folder. The chapters are given their order by the number preceding their folder.

The *subfiles* package is relatively intuitive. When compiling the document as a whole, we include a subfile with the command \subfile{./path/to/chapter.tex}, which basically transcludes the contents of that file into the main document. More tricky is when we compile a subfile, each of which is topped with a special documentclass: \documentclass[../textbook.tex]{subfiles} or, in the case of the answer key, \documentclass[../answers.tex]{subfiles}. This causes the entire preamble
of the main document to be included in the subfile, including document styling information, macros like \twomat, Asymptote definitions, et cetera.

A chapter is included in the main document if it begins with a number 0–9. All the corresponding chapter.tex files are thus included as subfiles of textbook.tex, and answers.tex files as subfiles of answer_key.tex. The cover, which has different styling than the rest of the document, is included in a special way, by first compiling it to a PDF and then including the PDF in the main document.

### Building
The book builds into the build/ folder. (Didn't expect that, huh?) The build folder has the following structure:

- *gatm.pdf*
- *gatm_key.pdf*
- chapters
    - *cover.pdf*
    - *credits.pdf*
    - *1 Trigonometry Review.pdf*
    - ...
    - *glossary.pdf*
- key_chapters
    - *cover.pdf*
    - *1 Trigonometry Review.pdf*
    - ...
- log
    - *gatm.log*
    - ... various debugging files ...

Simple enough. What's not so simple is the actual building process, as we encounter some of LaTeX's most stupefying characteristics. 

Building works with `python build.py`. We can either give it command line arguments, or if no arguments are provided, we enter an interactive mode. To build everything in build, run `python build.py all`, which builds the textbook and answer key and then excerpts all chapters. To build the textbook ONLY, run `python build.py textbook`, which will not update textbook_chapters/. To build the textbook and chapters, run `python build.py textbook_chapters`. Similarly, building the answer key is just
`python build.py key`, and with chapters, `python build.py key_chapters`. In this case, the cover, credits and glossary are considered chapters, though they don't contribute to the chapter index.

To build a specific chapter for *testing*, run `python build.py --chapter <chapter index or name>`, like `python build.py --chapter 10`, which will dump "chapter.pdf" into the folder "10 Rotations of the Plane". To see the cover, we can do `python build.py --chapter cover`, et cetera. In this case, building does *not* build the entire textbook. It *only* builds the given chapter, and doesn't do any excerpting. This is mostly the same as the real deal and is optimal for
testing, but has the following discrepancies:
- No cross-references (to figures or questions outside of the current chapter)
- Differing page numbers
- Incorrect chapter number

The build is fast, but slightly incorrect, and dumps the PDF into the *chapter folder*, not the build folder, because it's not intended for students to see. It also automatically opens the document (this is configurable) to aid immediate testing. To build the corresponding key similarly, run `python build.py --chapter_key <chapter index or name>`. To build a chapter for *production*, where we put it into the folder "build/chapters/", we first need to build the entire document (either gatm.pdf or gatm_key.pdf) and then *excerpt* the chapter from the full document. Otherwise there will be some small differences from the main document (most notably, cross-references like "see question 6 on page 3" will appear as "see question ?? on page ??").



GAtM Rough Draft: 100%

GAtM Final: 98%

GAtM Answer Key Rough Draft: 100%

GAtM Answer Key Final: 98%

**Contributors**: Timothy Herchen

**Directions**: Run the build.sh script with bash to output the pdf file into the "build" folder.

Note that you will need pdflatex to do this, which you can get from a source like TeXLive: http://www.tug.org/texlive/. You will also need Asymptote Vector Graphics, which you can get from http://asymptote.sourceforge.net/.

Despite the tiny odds of anyone coming here, I thought I'd write down how this works for posterity. Perhaps someone will be editing this textbook in 5 years time.

The book is split up into folders, one folder per chapter. Each folder contains a chapter source file, cleverly named `[chapter]_source.tex`. All of the information for that chapter is stored in this file.

To build a chapter, navigate to the top level directory gatm/ and type in `./bf.sh [chapter]`. For example, if I want to compile Rotation and Reflection Groups, I would enter `./bf.sh rrg`. This will fill up the rrg folder with intermediate files; these are often useful in debugging. The most important output file is the PDF output, which in this case would be `rrg/rrg_source.pdf`. Note that other PDF files may be generated as intermediates.

Note: This requires a bash-like client. On Windows, you will need MinGW and something like Git Bash.

When working on a chapter, it is probably best to have three windows: the compilation terminal, the .tex file, and the output .pdf file. You can enter the command `./bf.sh [chapter]; [open/nautilus/whatever] [chapter]/[chapter]_source.pdf` which will build and then open the output PDF in the default viewer. If you're fancy, you can probably hook up the compilation step to a key command using AutoHotKey or the like.

Building a chapter alone has several differences from building it as part of the whole, most of which are cosmetic. Page and problem references to other sections will not work and result in **??** appearing in place; do not worry if this happens for a chapter build. The page number will start at 1, rather than whatever page that chapter starts on. The section number will also start at 1. Everything in the preamble of gatm.tex, however, is processed, so commands defined there work in chapter builds.

When building GAtM as a whole, run the command `./b.sh`. This will build gatm in the "/build" folder, so the output will be `build/gatm.pdf`. Note that this can take a few minutes, as there are about 60 diagrams to render. Don't worry about the spewage of errors in the command line, this is normal (unless it occurs in Stage 3 of compilation).

To build the answer key, the commands are the same, except it's `./bfa.sh` to build a chapter and `./ba.sh` to build the whole answer key. The answer key sections are `[chapter]/[chapter]_answers.tex`. Note that the whole answer key may take up to 20 minutes to render, depending on your computer's uh... clock speed?

Enjoy!
