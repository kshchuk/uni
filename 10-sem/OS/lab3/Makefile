.PHONY: all build supervisor process_a process_b clean run run-racy run-nosync tidy test report report-clean

GO        := go
BIN_DIR   := bin
TAGS      ?=

all: build

build: supervisor process_a process_b

supervisor:
	$(GO) build $(if $(TAGS),-tags=$(TAGS)) -o $(BIN_DIR)/supervisor ./cmd/supervisor

process_a:
	$(GO) build $(if $(TAGS),-tags=$(TAGS)) -o $(BIN_DIR)/process_a ./cmd/process_a

process_b:
	$(GO) build $(if $(TAGS),-tags=$(TAGS)) -o $(BIN_DIR)/process_b ./cmd/process_b

run: build
	./$(BIN_DIR)/supervisor

run-racy:
	$(MAKE) build TAGS=racy
	./$(BIN_DIR)/supervisor

run-nosync:
	$(MAKE) build TAGS=nosync
	./$(BIN_DIR)/supervisor

tidy:
	$(GO) mod tidy

test:
	$(GO) test ./...

report:
	cd report && xelatex -interaction=nonstopmode -halt-on-error report.tex >/dev/null
	cd report && xelatex -interaction=nonstopmode -halt-on-error report.tex >/dev/null
	@echo "Built report/report.pdf"

report-clean:
	cd report && rm -f *.aux *.log *.out *.toc *.synctex.gz

clean: report-clean
	rm -rf $(BIN_DIR)
	-ipcs -m 2>/dev/null | awk '/^m / && $$3 == ENVIRON["USER"] {print $$2}' | xargs -I{} ipcrm -m {} 2>/dev/null || true
