FOLDERNAME=$1

cd "${FOLDERNAME}"

echo "Building ${FOLDERNAME} Stage 1"
pdflatex -shell-escape -interaction=nonstopmode *source.tex | grep ".*:[0-9]*:.*"
echo "Rendering Asymptote"
asy *source-*.asy
echo "Building ${FOLDERNAME} Stage 2"
pdflatex -shell-escape -interaction=nonstopmode *source.tex | grep ".*:[0-9]*:.*"
