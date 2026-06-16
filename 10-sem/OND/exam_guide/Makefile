.PHONY: all theory practika clean clean-all

THEORY_DIR = teorka_shatyrko
PRACTIKA_DIR = practika_fractals
THEORY = dovidnyk_teorka_shatyrko
PRACTIKA = dovidnyk_practika_fractals

all: theory practika

theory:
	cd $(THEORY_DIR) && pdflatex -interaction=nonstopmode $(THEORY).tex
	cd $(THEORY_DIR) && pdflatex -interaction=nonstopmode $(THEORY).tex

practika:
	cd $(PRACTIKA_DIR) && pdflatex -interaction=nonstopmode $(PRACTIKA).tex
	cd $(PRACTIKA_DIR) && pdflatex -interaction=nonstopmode $(PRACTIKA).tex

clean:
	rm -f $(THEORY_DIR)/$(THEORY).aux $(THEORY_DIR)/$(THEORY).log \
	      $(THEORY_DIR)/$(THEORY).out $(THEORY_DIR)/$(THEORY).toc
	rm -f $(PRACTIKA_DIR)/$(PRACTIKA).aux $(PRACTIKA_DIR)/$(PRACTIKA).log \
	      $(PRACTIKA_DIR)/$(PRACTIKA).out $(PRACTIKA_DIR)/$(PRACTIKA).toc

clean-all: clean
	rm -f $(THEORY_DIR)/$(THEORY).pdf $(PRACTIKA_DIR)/$(PRACTIKA).pdf
