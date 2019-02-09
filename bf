FOLDERNAME=$1

cd "${FOLDERNAME}"

pdflatex *source.tex
asy *source-*.asy
pdflatex *source.tex
pdflatex *source.tex
