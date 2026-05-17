.PHONY: all build server client clean run-server run-client experiment report report-clean tidy test

GO      := go
BIN_DIR := bin

all: build

build: server client

server:
	$(GO) build -o $(BIN_DIR)/server ./cmd/server

client:
	$(GO) build -o $(BIN_DIR)/client ./cmd/client

run-server: build
	./$(BIN_DIR)/server

run-client: build
	./$(BIN_DIR)/client

experiment: build
	./examples/run_experiment.sh

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
