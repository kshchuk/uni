# Спочатку Commons-ілюстрації, потім Python-рисунки, далі PDF (bibtex).
.PHONY: all pdf figures clean

all: pdf

figures:
	bash scripts/fetch_external_figures.sh
	MPLBACKEND=Agg python3 scripts/generate_figures.py

pdf: figures
	pdflatex -interaction=nonstopmode referat.tex
	bibtex referat
	pdflatex -interaction=nonstopmode referat.tex
	pdflatex -interaction=nonstopmode referat.tex

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.synctex.gz referat.pdf
