#!/bin/bash

shopt -s extglob

echo "Building cover..."
bash bf.sh cover
echo "Built cover."

rm build/*.asy build/*.aux build/*.log build/*.out build/*.toc build/*.pre

echo "Building GaTM Stage 1"
pdflatex -shell-escape -interaction=nonstopmode -file-line-error --output-directory=build gatm.tex | grep ".*:[0-9]*:.*"
echo "Rendering Asymptote"
asy build/*.asy
echo "Building GaTM Stage 2: expect superfluous errors."
pdflatex -shell-escape -interaction=nonstopmode -file-line-error --output-directory=build gatm.tex | grep ".*:[0-9]*:.*"
echo "Building GaTM Stage 3"
pdflatex -shell-escape -interaction=nonstopmode -file-line-error --output-directory=build gatm.tex | grep ".*:[0-9]*:.*"
pdflatex -shell-escape -interaction=nonstopmode -file-line-error --output-directory=build gatm.tex | grep ".*:[0-9]*:.*"
echo "Cleaning"

rm *.out *.pbsdat *.js *.prc
rm *.pdf *.asy *.log *.aux gatm-*.tex *.pre >/dev/null 2>&1
