# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# Figures Makefile
# ================

# Targets
# -------

# global pdd figures
GLOPDD_SOURCES = cera5 cw5e5 fdiff pdiff sdiff
GLOPDD_WORLD_FIGS = $(foreach src, $(GLOPDD_SOURCES), glopdd_world_$(src).pdf)

# all figures
ALL_FIGS = $(GLOPDD_WORLD_FIGS)


# Rules
# -----

# default rule
all: $(ALL_FIGS)

# global pdd rules
$(foreach src, $(GLOPDD_SOURCES), %_$(src).pdf) : %.py glopdd_utils.py matplotlibrc
	python $<

# clean up
.PHONY: clean
clean:
	rm -f $(ALL_FIGS)
