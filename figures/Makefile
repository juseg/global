# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# Figures Makefile
# ================

# Variables
# ---------

# default figure extension
EXT = pdf

# python executable
PY = python

# all python figures (except: asijap_domains asimis_domains)
PY_FIGS = \
    $(addprefix glopdd_, altitude threshold)
PY_FIGS := $(addsuffix .$(EXT), $(PY_FIGS))

# all figures
ALL_FIGS = $(PY_FIGS)


# Rules
# -----

# default rule
all: $(ALL_FIGS)

# rules and dependencies for python figures
$(PY_FIGS): %.pdf : %.py matplotlibrc
	$(PY) $<

# clean up
.PHONY: clean
clean:
	rm -f $(ALL_FIGS)
