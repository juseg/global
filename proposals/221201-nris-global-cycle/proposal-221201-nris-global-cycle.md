<!-- Copyright (c) 2023, Julien Seguinot (juseg.github.io)
Creative Commons Attribution-ShareAlike 4.0 International License
(CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/) -->

# Global paleoglacier modelling with PISM

*To NRIS / Sigma2 small-scale experimental work.*

I am a postdoc at the University of Bergen where I am working on a project to
numerically mountain glacier history worldwide. For this purpose I would like
to apply for resources to run the Parallel Ice Sheet Model (PISM,
https://pism.io) on a global scale. PISM is written in C/C++, and it implements
solvers of the Portable, Extensible Toolkit for Scientific Computation (PETSc,
http://www.mcs.anl.gov/petsc), which can be run in parallel on many cores with
an excellent scalability.

I have previously used PISM to model paleoglaciers at the Swedish National
Infrastructure for Computing (SNIC, 2012-2014) and the Swiss National Centre
for Supercomputing (CSCS, 2014-2019).

https://www.cscs.ch/science/earth-env-science/2018/an-ice-age-lasting-115000-years-in-two-minutes/

The goal of this new project is to expand such previous work to many more
regions. To this purpose I am currently developing a Python package
(https://hyoga.readthedocs.io) which will handle the "embarrassingly" parallel
problem of running PISM on many independent model domains, where each
sub-problem is solved in parallel by PISM / PetSC.

* Anticipated resource needs: ideally, the maximum of 20 000 CPU-hours
* Average core count: anticipated to be low for most jobs (e.g. 8-32 cores per
  job), up ca 512 cores per job in later stages.
* Memory requirements: up to ca 8GB / node.
* If you need GPU: no.
* Software needs: GSL, FFTW, NetCDF4, PETSc (ideally).
* Expected duration:
  - Testing: until Mar 2023 (latest)
  - Production runs: Apr 2023 - Mar 2025.
