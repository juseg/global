# Article Makefile
# ================


# Variables
# ---------

PAPER = proposal-200214-jsps-asia
REFS = ../../../references/references.bib
REV = $(shell git describe --abbrev=0 --match=asijap*)


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
%.bib: %.aux $(REFS)
	bibtool $(REFS) -x $< > $@

# latex pdf patterned rule
%.pdf: %.tex # ../../references/references.bib
	latexmk -pdf -dvi- -ps- $<

# latex rtf patterned rule (no eqs, no fields)
%.rtf: %.tex $(REFS)
	latex2rtf -E0 -f0 $<

# libreoffice txt patterned rule (preserve special characters)
%.txt: %.rtf
	libreoffice --convert-to "txt:Text (encoded):UTF8" $<

# latex diff patterned rule
%-diff.tex: %.tex
	latexdiff-vc --math-markup=3 --append-textcmd=centerline --force --git -r $(REV) $<
	mv $(basename $@)$(REV).tex $@

# clean up
.PHONY: clean
clean:
	latexmk -pdf -CA
