.PHONY: all theory practika practica-shatyrko clean clean-all

THEORY_DIR = teorka_shatyrko
PRACTIKA_DIR = practika_fractals
PRACTICA_DIR = practica_shatyrko
THEORY = dovidnyk_teorka_shatyrko
PRACTIKA = dovidnyk_practika_fractals
PRACTICA = dovidnyk_practica_shatyrko

all: theory practika practica-shatyrko

theory:
	cd $(THEORY_DIR) && pdflatex -interaction=nonstopmode $(THEORY).tex
	cd $(THEORY_DIR) && pdflatex -interaction=nonstopmode $(THEORY).tex

practika:
	cd $(PRACTIKA_DIR) && pdflatex -interaction=nonstopmode $(PRACTIKA).tex
	cd $(PRACTIKA_DIR) && pdflatex -interaction=nonstopmode $(PRACTIKA).tex

practica-shatyrko:
	cd $(PRACTICA_DIR) && pdflatex -interaction=nonstopmode $(PRACTICA).tex
	cd $(PRACTICA_DIR) && pdflatex -interaction=nonstopmode $(PRACTICA).tex

clean:
	rm -f $(THEORY_DIR)/$(THEORY).aux $(THEORY_DIR)/$(THEORY).log \
	      $(THEORY_DIR)/$(THEORY).out $(THEORY_DIR)/$(THEORY).toc
	rm -f $(PRACTIKA_DIR)/$(PRACTIKA).aux $(PRACTIKA_DIR)/$(PRACTIKA).log \
	      $(PRACTIKA_DIR)/$(PRACTIKA).out $(PRACTIKA_DIR)/$(PRACTIKA).toc
	rm -f $(PRACTICA_DIR)/$(PRACTICA).aux $(PRACTICA_DIR)/$(PRACTICA).log \
	      $(PRACTICA_DIR)/$(PRACTICA).out $(PRACTICA_DIR)/$(PRACTICA).toc

clean-all: clean
	rm -f $(THEORY_DIR)/$(THEORY).pdf $(PRACTIKA_DIR)/$(PRACTIKA).pdf \
	      $(PRACTICA_DIR)/$(PRACTICA).pdf
