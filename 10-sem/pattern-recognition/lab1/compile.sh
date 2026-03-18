#!/bin/bash
# Script for compiling LaTeX report

set -e

# Install required packages (if not already installed)
# On macOS: brew install texlive
# On Ubuntu: sudo apt-get install texlive-full
# On Fedora: sudo dnf install texlive-scheme-full

echo "Compiling LaTeX report..."

# Compile LaTeX (need to run twice for TOC)
pdflatex -interaction=nonstopmode REPORT.tex
pdflatex -interaction=nonstopmode REPORT.tex

# Clean up auxiliary files
rm -f REPORT.aux REPORT.log REPORT.out REPORT.toc

echo "✓ Report compiled: REPORT.pdf"
