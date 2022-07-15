# Article Makefile
# ================


# Variables
# ---------

PAPER = 220701-uib-postdoc-plan
BIB = ../../../references/references.bib
REV = 8ee22b# $(shell git describe --abbrev=0 --match=*)


# Named rules
# -----------

# default rule
pdf: $(PAPER).pdf

# stripped bib
bib : $(PAPER).bib

# richt text format
rtf: $(PAPER).rtf

# plain text format
txt: $(PAPER).txt

# default diff
diff: $(PAPER)-diff.pdf


# Patterned rules
# ---------------

# stripped bib patterned rule
%.bib: %.aux $(BIB)
	bibtool $(BIB) -d -q -x $< > $@

# latex pdf patterned rule
%.pdf: %.tex $(BIB)
	latexmk -pdf $<

# latex rtf patterned rule (no eqs, no fields, no monospace links)
%.rtf: %.tex $(BIB)
	latex2rtf -E0 -f0 $<
	sed -i "s|\\\f3 \\\field|\\\field|g" $@

# libreoffice txt patterned rule (preserve special characters)
%.txt: %.rtf
	libreoffice --convert-to "txt:Text (encoded):UTF8" $<
	sed -i -n '/^Abstract/,/^References/p' $@

# latex diff patterned rule
%-diff.tex: %.tex
	latexdiff-vc --disable-citation-markup --force --git -r $(REV) $<
	mv $(basename $@)$(REV).tex $@

# Clean up
# --------

.PHONY: clean
clean:
	latexmk -pdf -CA
