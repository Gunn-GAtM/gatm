#!/bin/bash

bash buildfolder.sh cover

pdflatex --output-directory=build gatm.tex
asy build/*.asy
pdflatex --output-directory=build gatm.tex

rm *.pdf
rm *.asy
rm *.aux
rm *.log
rm *.pre
rm gatm-*.tex
