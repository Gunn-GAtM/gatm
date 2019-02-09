#!/bin/bash

echo "Building cover..."
bash bf.sh cover
echo "Built cover."

echo "Clearing build folder"
rm build/*

echo "Building GaTM Stage 1"
pdflatex -shell-escape -interaction=nonstopmode --output-directory=build gatm.tex | grep ".*:[0-9]*:.*"
echo "Rendering Asymptote"
asy build/*.asy
echo "Building GaTM Stage 2"
pdflatex -shell-escape -interaction=nonstopmode --output-directory=build gatm.tex | grep ".*:[0-9]*:.*"

echo "Cleaning"
rm *.pdf *.asy *.log *.aux gatm-*.tex *.pre >/dev/null 2>&1
