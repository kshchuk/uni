PDF=main.pdf
TEX=main.tex
ENGINE ?= xelatex

.PHONY: all pdf clean distclean

all: pdf

pdf:
	@if [ "$(ENGINE)" = "xelatex" ]; then \
	  latexmk -xelatex -interaction=nonstopmode -halt-on-error $(TEX); \
	elif [ "$(ENGINE)" = "lualatex" ]; then \
	  latexmk -lualatex -interaction=nonstopmode -halt-on-error $(TEX); \
	else \
	  latexmk -pdf -interaction=nonstopmode -halt-on-error $(TEX); \
	fi

clean:
	latexmk -c
	rm -f $(PDF)

distclean: clean
	rm -f main.bbl main.bcf main.run.xml
