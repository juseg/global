<!-- Copyright (c) 2023, Julien Seguinot (juseg.github.io)
Creative Commons Attribution-ShareAlike 4.0 International License
(CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/) -->

# Global paleoglacier modelling with PISM

*To NRIS / Sigma2 regular application.*

## 1 Project Description and Funding

*Project title*

Global paleoglacier modelling with PISM

*Project short name -- Short name, one word/acronym. It will be used wherever the full name would be too long, for instance in pie charts.*

Hyoga

*Project description (summary) -- This summary can be used for dissemination
purposes. It should be understandable to a wide audience, from research fellows
to decision makers. The summary should include objectives, a description of the
problem and its scientific and/or socio-economic relevance, the main scientific
methods and algorithms used, the challenges in particular with respect to
computation and data management, and expected results. Please limit the text to
500 words.*

Ancient glaciers have reshaped the surface of the Earth to create some of its
most fascinating landscapes. For nearly three hundred years, explorers,
scientists and outdoor-enthusiasts have learned to read these traces and
understand past climatic fluctuations. Nevertheless, the glacial landscape
record is sparse in time and space, so that a cohesive picture of global
glacial history can't be composed from geology alone.

I am a glaciologist currently employed in the terrestrial ecology group at the
university of Bergen. In this project (Apr. 2022 -- Mar. 2025), I am building
upon previous glacier modelling work in the Northern Cordillera and the Alps
(https://juseg.github.io/outreach) to produce a continuous, global
reconstruction of alpine glaciers and mountain ice sheets spanning the entire
last glacial cycle (120000 years). This product is developed within an
interdisciplinary team to reconstruct "the past, present and futures of alpine
biomes worldwide" (https://mountainsinmotion.w.uib.no). Our methods will be
shared both within and beyond academia in the form of publications, free
software, open data and outreach materials for kids and museums (see measurable
output).

To this purpose I am developing hyoga (https://hyoga.readthedocs.io), an
open-source, automated framework for paleoglacier modelling applicable anywhere
on Earth, encapsulating the entire modelling chain from preparing input files
to producing visualizations for outreach. Hyoga acts as a wrapper around the
Parallel Ice Sheet Model (PISM, https://pism.io), a numerical model
implementing ice flow physics based on laboratory experiments and observations
on modern glaciers (see software). Technically speaking, hyoga solves the
embarrassingly parallel problem of modelling paleoglaciers in many regions,
while PISM (powered by PetSC and MPI) solves the challenge of modelling ice
flow in parallel for each region.

At the time of writing this proposal, this new tool (hyoga v0.3.0) already
offers unprecedented accessibility to researchers from various disciplines
(e.g. earth sciences, ecology), and allows for fully automated, consistent,
multi-domain regional or global paleoglacier studies. In the future, it will be
automatized further and supported by an outreach web platform to improve
communication on paleoglacier research within and beyond academia.

PISM has been successfully compiled and applied on Saga. A small-scale
exploratory work (SSEW) allocation was used to benchmark the multi-domain
approach, powered by hyoga, on a subset of 12 carefully selected modelling
domains (see HPC resource justification). My next step consists in extending
this test set into a global collection of 100 to 200 modelling domains (to be
determined by trial and error) covering all glaciated mountains on Earth. This
setup will be tested for more advanced paleoclimate scenarios (2023.1), and
spatial resolution increased for the production runs (2023.2).

*Primary field of science. -- Select the option that best describes the primary
field of science of your project.*

Geosciences

*Secondary field(s) of science. -- Select additional fields of science that
applies to your project.*

Computational Fluid Dynamics

*Research Council projects -- If funded by the Research Council of Norway, list
the six-digit project code(s). Multiple projects can be listed using
comma-separation. If inapplicable, write N/A.*

N/A

*Other funding sources -- If your project is funded, in full or in part, by
other sources (e.g. EU, industry, local etc.) please list here the funding
source and the grant ID (or similar). If inapplicable, write N/A.*

University of Bergen (UiB) Trond Mohn Stiftelse (TMS) startup grant
‘TMS2022STG03’ to Suzette Flantua (UiB)

*Does any part of your project contain commercial funding? -- Answer yes if
this work is funded in part by any other source than University and Colleges,
Research Council or EU.*

No

*Commercial funding ratio (%) -- If the project contains any commercial
funding, please indicate a percentage share of commercial funding here,
otherwise 0.*

0

*I confirm I have acknowledged / I will acknowledge the use of the national
e-infrastructure in our publications.*

True

*I confirm that I have read and understood our Acceptable Use Policy (AUP) &
MAS Privacy Notice*

True

## 2 Usage and output

*Relevant usage experience -- Provide a description of your skills and
abilities to make use of the proposed resources. Please include relevant
competences, qualifications and past experiences. Also include previous
national or local allocations or other similar resources (project numbers are
sufficient). If you are applying for large allocations on computing or storage
resources it is particularly important to document that you or your team have
the necessary skills to make efficient use of the resources (a feasibility
study will be conducted based on the provided information).*

I have used and contributed to PISM for over a decade and applied it to model
paleoglaciers on multiple supercomputers at the Royal Institute of Technology
of Sweden (KTH, 2011), the Swedish National Infrastructure for Computing (SNIC
001/12-85, 2013/1-145, and 2014/1-159, 2012-2015) and the Swiss National Centre
for Supercomputing (CSCS allocations s573 and sm13, 2015-2019). While such
multi-millenial simulations typically run for weeks, I have automated restarts
and SLURM job chains in a Python wrapper script
(https://github.com/juseg/pism-palwrapper, to be documented and incorporated in
hyoga).

This work has resulted in my PhD thesis, multiple publications and a press
release at CSCS, which hosted Europe's most powerful computer at the time
(https://www.cscs.ch/science/earth-env-science/2018/an-ice-age-lasting-115000-years-in-two-minutes/).
Multi-lingual visualizations based on this latter work have received much
attention from mainstream media and teachers (https://vimeo.com/juseg, 183k
views), were projected onto building facades in Swiss villages, and became part
of several temporary and permanent museum exhibitions across the Alpine
countries (https://juseg.github.io/outreach/). I can't wait to expand such
outreach work on a global scale.

*Measurable output -- Detail the expected measurable output in number of
publications and students (master and PhD) in the requested period. For new
applications, less emphasis will be put on this question. It is important to
demonstrate that you have considered concrete measures to enhance the
exploitation, capacity or integration of new knowledge and in general that your
project has a potential for this. Details on exploitation and dissemination
measures should include potential end-users and applications of the results
that will be generated.*

My interdisciplinary colleagues and I plan the following output:

* Global reconstructions of mountain paleoglaciers over the last 120000 years,
  published as open data on Zenodo (2024).
* The open-source paleoglacier modelling framework enabling these
  reconstructions (https://hyoga.readthedocs.io, continuous development).
* Outreach in the form of scientific animations in multiple languages (2024)
  and an interactive website (2025) for teachers and museums.
* One or two scientific publications describing the paleoglacier modelling
  methods and results for academics (2024-2025).
* Two PhD theses in paleo-ecology at the University of Bergen directly
  depending on these results (E. Rentier and L. Schultz, 2023-2026).

## 3 Software

*GPU Software*

N/A

*Other Software -- Applications you plan to use, including in-house software.
Please exclude compilers libraries and tools, like GCC, MPI and Python.*

PISM is written in C/C++, and it implements solvers of the Portable, Extensible
Toolkit for Scientific Computation (PETSc), which can be run in parallel on
many cores with an excellent scalability.

A scalability test was conducted for one of the test regions on Saga, showing
efficiency of 50% on 12 cores and 35% on the 128 cores (relative to using a
single core, figure on demand). The main drop in efficiency occurs between 1
and 16 cores, with roughly constant speedup between 16 and the maximum allowed
of 128. Based on previous scalability tests on other computers (e.g. CSCS Piz
Daint, figure on demand), I expect continued speedup up to hundreds of cores.

Performance tests on other machines (using Cray's perftools) have shown
relatively high MPI waiting times. This, however, is due to PISM/PetSC inherent
design using finite differences on a regular grid to solve a problem with
irregular complexity. In my opinion, this load imbalance is a very acceptable
trade-off as compared to using more advanced (and much more demanding)
dicretization shemes.

## 4 Computing Quota

|        | 2023.1 | 2023.2 | 2024.1 | 2024.2 |
| ------ | ------ | ------ | ------ | ------ |
| Betzy  |      0 |      0 |      0 |      0 |
| Fram   |      0 |      0 |      0 |      0 |
| Saga   |     1M |    10M |      0 |      0 |
| LUMI-C |      0 |      0 |      0 |      0 |
| LUMI-G |      0 |      0 |      0 |      0 |

*HPC request justification -- Please provide information for the reviewers to
understand the request for the required HPC resources, the chosen resources and
how the requirements were estimated.*

The small-scale allocation (SSEW) was used to perform 60 benchmark simulations
for 12 hand-picked test regions of varying size and resolution (Ahklun, Nevada,
Cocuy, Cantal, Alps, Prokletije, Bale, Himalaya, Southern Alps, Akaishi and
Transbaikal Mountains) and 5 simple climate scenarios with constant temperature
lowering of 0 to 8 degrees below the present values. Each simulation was run
for either 10 model kiloyears or 24 real-time hours depending on which was
first reached. These preliminary results showed a varied glacier response from
one region to the next, as can be expected from geologic evidence (figure on
demand).

These benchmarks showed an average computing speed of 40 core-hours per model
kiloyears. I estimate that I need ca. 200 model domains to cover all
paleoglaciers on Earth. For each domain, I plan to test ca. 10 paleoclimate
scenarios following an approach similar to that employed at regional scale in
my previous publications. Each scenario will cover the last 120 thousand years.
Thus a first estimate for the total cost of production runs is `200*10*120*40 =
9.6` million core-hours. This needs to be refined in later application periods.
For comparison, the aforementioned simulation on Alpine glaciers on CSCS Piz
had a total cost of 461 thousand core-hours.

For the first phase of the project (2023.1), I apply for 1 million core-hours
to run a preliminary set of global simulations at moderate resolution. This
allocation will also be used to prepare high-resolution benchmarks for the next
period (2023.2). Future plans for 2024 depend on the results from the first
batch, and applications at the EU level will also be considered.

*I accept performance reviews*

True

*Report underusage -- In case the project did not use all (> 90 %) of the
allocated resources in the previous allocation period, please explain why. This
particular field is actively used in the allocation process, please provide
up-to-date information.*

93% of the SSEW allocation was used

## 5 Computational characteristics

*Project storage need in GB*

10 TB?

*Average number of cores*

12

*Maximum number of cores*

512 (or maximum allowed)

*Memory per core in GB*

8 GB

*I/O Needs -- Provide details on your disk accesses. During a typical run, do
you create a few large files or many small files? Do you expect mainly large
file reads/writes, or do you expect (frequent) small size accesses? Do your
application(s) use MPI-parallel I/O (MPI-IO)?*

Each run regularly writes output to disk in the form of several diagnostics
with different frequencies (stdout and error text logs, 1D time-series, 2D
output, restartable 3D snapshots). For 2D and 3D output, PISM implements
parallel output using netCDF-4 or PnetCDF, leading to demonstrated I/O
performance on very large grids. PISM was successfully compiled against
parallel netCDF-4 on Saga.
