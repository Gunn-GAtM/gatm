# GAtM
A rewrite of _A Geometric Approach to Matrices_ (frequently abbreviated to "GAtM") by Peter Herreshoff.

GAtM Rough Draft: 100%
![](http://progressed.io/bar/100?title=progress)

GAtM Final: 80%
![](http://progressed.io/bar/80?title=progress)

GAtM Answer Key Rough Draft: 100%
![](http://progressed.io/bar/100?title=progress)

GAtM Answer Key Final: 39%
![](http://progressed.io/bar/39?title=progress)

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
