# PEM fuel-cell cold-start simulations

Research code for **Charge-constrained cold starts of PEM fuel-cell stacks: Spatial heating, onset timing and thermal handover**, prepared for Simulation Modelling Practice and Theory.

The model couples water, ice and electrochemistry in five cells to shared bipolar plates and separate endplates. It compares spatial heater allocation, heating onset, matched-window feedback, reaction resources and thermal handover from actual startup states.

## Function-based packages

Download the [classified research release](https://github.com/ludkeharshfield197-sys/pemfc-cold-start-smpt/releases/tag/v2026.10.08-classified).

| Package | Contents |
| --- | --- |
| `pemfc-01-model-20261008.zip` | Core model, water solver, thermal network, physical inputs and configurations |
| `pemfc-02-experiments-20261008.zip` | Startup/handover experiment drivers and result summarizers |
| `pemfc-03-parameter-analysis-20261008.zip` | Fitting and sensitivity programs, saved fitted vectors and aggregate metrics |
| `pemfc-04-figures-20261008.zip` | Plotting programs and publication vector PDF figures |
| `pemfc-05-manuscript-20261008.zip` | Article, references, generation programs and reusable template |
| `pemfc-06-results-20261008.zip` | Full simulated trajectories and numerical endpoints |
| `pemfc-code-classified-20261008.zip` | Compact combined working tree, excluding full trajectory CSV files |
| `pemfc-complete-classified-20261008.zip` | All six categories together; recommended for rebuilding from saved outputs |
| `smpt-manuscript-classified-20261008.pdf` | Current article PDF |
| `smpt-latex-classified-20261008.zip` | Flat LaTeX submission source with referenced figures |

Extract the complete archive, or extract the six category archives into **one shared directory**. Paths inside each archive retain the executable project layout. The categories are components of one project: plotting and article generation use the model and saved results. Root drivers are also directly browsable here.

## Working-tree layout

```text
program_event_v2/
  src/                core coupled model and numerical solvers
  revision/           extended stack solver and exact scenarios
  inputs/             geometry/material workbook and nominal coefficients
  config/             scenario and input-label definitions
  results/            simulated trajectories and fitted parameter summaries
records/              result locations used by figures and article
manuscript/           article sources and vector figures
build/handover_originals/manuscript/  article generation template
```

## Installation and experiments

```sh
python -m pip install -r requirements.txt
python run_baseline_experiments.py stack 0 1
python run_revision_experiments.py 0 1
python run_handover_experiments.py all 0 1
python run_review_revision_experiments.py configure
python run_review_revision_experiments.py all 0 1
python run_review_refinements.py
python propagate_profile_parameters.py
python propagate_joint_parameters.py joint
python propagate_joint_parameters.py Qc30
python propagate_joint_parameters.py refine
python run_onset_parameter_comparisons.py all
python summarize_onset_parameters.py
```

Run commands in the extracted project root. Existing same-name results are reused. For fresh calculations, move the relevant result files to a separate folder in an extracted copy, then run the same commands. Retain supplied physical inputs and exact parameter vectors.

The latest six startups compare Uniform125, FC_FB and FC_OL with Joint-fit and Qc30 vectors. All reach startup. Within-vector FC_FB minus Uniform125 net inputs are -10.47 J for Nominal, +7.48 J for Joint-fit and +4.59 J for Qc30. Auxiliary savings are about 43%, with increased reaction hydrogen and time. Matched feedback auxiliary changes are -0.467%, -0.431% and -0.435%, respectively, relative to each group's matched open-loop auxiliary input. Windows, gains and the 20 C/cm² budget are unchanged. Qc30 denotes a fitted cold-loss charge scale, not the reaction budget.

Exact paired values are in `program_event_v2/results/review_revision/onset_parameter_endpoints.csv` and `onset_parameter_differences.csv`; settings are in `parameters/joint/onset_comparisons.json`. Continuations inherit the corresponding actual temperature, water, ice, endplate and loading-memory states.

## Figures and article

```sh
python build_review_assets.py
python revise_manuscript.py
```

Compile `manuscript/main.tex` using LaTeX. On Windows, `compile_paper.ps1` updates that article's PDF. `prepare_github_publication.py` rebuilds the classified public archives from the working tree. Saved-output rebuilding uses the complete archive. The observation-overlay figure and repeated fitting require separately supplied observation records.

## Data and parameter roles

Public files include model inputs, nominal coefficients, fitted parameter vectors, aggregate fitting metrics and simulated stack trajectories. Original observation workbooks and files that reproduce their individual observations are excluded.

The -20 °C record supplies training residuals. The -25 °C record was excluded from fitting, but its cross-temperature validation informed the nominal reference choice. It is not a post-selection independent test. To repeat fitting, obtain the original records and place them at the locations expected by the code. Stack simulations use the included vectors without those observations.

## Authorship and reuse

Authorship is stated in the article. No additional reuse license or repository DOI has been assigned. Public availability does not establish redistribution permission for excluded observation records.
