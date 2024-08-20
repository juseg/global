# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# Figures Makefile
# ================

# Targets
# -------

# global pdd figures
GLOPDD_SOURCES = cera5 cw5e5 fdiff pdiff sdiff
GLOPDD_FIGS = \
	$(addsuffix .png, \
		$(addprefix glopdd_diffs_, fdiff pdiff sdiff) \
		$(addprefix glopdd_world_, cera5 cw5e5 fdiff pdiff sdiff) \
		$(addprefix glopdd_zonal_, cera5 cw5e5 ))

# all figures
ALL_FIGS = $(GLOPDD_FIGS)


# Rules
# -----

# default rule
all: $(ALL_FIGS)

# custom source pattern rules
# IDEA: allow positional argument for full flexibility
define GEN_SOURCE_RULE
%_$(source).png: %.py glopdd_utils.py matplotlibrc
	python $$< --source $(source)
endef
$(foreach source,$(GLOPDD_SOURCES), \
  $(eval $(call GEN_SOURCE_RULE)))

# clean up
.PHONY: clean
clean:
	rm -f $(ALL_FIGS)
