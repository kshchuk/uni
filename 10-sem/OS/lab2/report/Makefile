# Build the LaTeX report with XeLaTeX (needed for Ukrainian + system fonts).
#
#   make        -> report.pdf
#   make clean  -> remove aux files
#   make open   -> macOS: open the pdf
#
# Requirements (install once):
#   brew install --cask mactex-no-gui
# or a full MacTeX distribution. XeLaTeX ships with MacTeX/BasicTeX.

TEX = xelatex
TEX_FLAGS = -interaction=nonstopmode -halt-on-error
SRC = report.tex
PDF = report.pdf

.PHONY: all clean open

all: $(PDF)

$(PDF): $(SRC) ../src/fs.s ../src/path_join.s ../src/png_ihdr.s ../src/pfs_fmt.s ../src/AppDelegate.m
	$(TEX) $(TEX_FLAGS) $(SRC)
	$(TEX) $(TEX_FLAGS) $(SRC)   # second pass for TOC

open: $(PDF)
	open $(PDF)

clean:
	rm -f *.aux *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk *.synctex.gz
