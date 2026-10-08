# PEM fuel-cell cold-start simulations

Research implementation for **Charge-constrained cold starts of PEM fuel-cell stacks: Spatial heating, onset timing and thermal handover**, prepared for Simulation Modelling Practice and Theory. This is a research manuscript, not a claim of journal acceptance.

The model couples through-plane water, ice and electrochemistry in five cells to shared bipolar plates and separate endplates. Comparisons distinguish equal-power spatial allocation, heater onset, matched-window feedback, finite reaction-resource accounting, and continuation from actual startup states.

## Download and layout

Use the [2026-10-08 research release](https://github.com/ludkeharshfield197-sys/pemfc-cold-start-smpt/releases/tag/v2026.10.08).

- `pemfc-research-source-20261008.zip`: programs, configurations, model inputs, saved numerical endpoints, publication figures and manuscript. Extract with directory structure preserved.
- `pemfc-simulation-results-20261008.zip`: the same working tree plus full published simulation trajectories. This is the recommended download for rebuilding from stored results.
- `smpt-manuscript-20261008.pdf`: the revised research manuscript, with all scientific methods and results in the main article.
- `smpt-latex-source-20261008.zip`: flat LaTeX source and its 17 referenced PDF figures.

The root Python drivers are also browsable in this repository. Run them from the extracted working tree, where `program_event_v2/` and `records/` retain their relative locations.

## Installation and stack calculations

Install Python dependencies from `requirements.txt` in an appropriate environment:

```sh
python -m pip install -r requirements.txt
```

The drivers reuse an existing result with the same scenario name. To recompute, use a separate extracted copy and move the relevant result files to a historical folder in that copy. Do not change model inputs or the stored parameter vectors.

```sh
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

The supplied nominal calibration and existing Joint-fit/Qc30 fitted vectors are included. Startup continuations inherit their corresponding actual thermal, water, ice, endplate and loading-memory states. Qc30 denotes a fitted cold-loss parameter; the startup reaction budget remains 20 C/cm².

## Latest targeted results

Six fresh startups compare Uniform125, FC_FB and FC_OL under each of the Joint-fit and Qc30 vectors, without changing windows or gains. All six reach startup. Within-vector FC_FB minus Uniform125 net inputs are −10.47 J for the supplied nominal vector, +7.48 J for Joint-fit and +4.59 J for Qc30. Auxiliary savings remain about 43%, with increased reaction hydrogen and startup time. FC_FB minus matched FC_OL auxiliary input is −0.467%, −0.431% and −0.435%, respectively; the denominator is each vector's open-loop auxiliary input.

Endpoint and paired result tables are `program_event_v2/results/review_revision/onset_parameter_endpoints.csv` and `onset_parameter_differences.csv`. Exact settings are in `parameters/joint/onset_comparisons.json`. The revision includes 79 stack calculations, 13 six-coordinate profile fits and three seven-coordinate joint fits, in addition to the baseline and earlier startup/handover comparisons.

## Figures and manuscript

Published vector figures and the current manuscript are included. `build_review_assets.py` rebuilds the allocation, parameter, handover and resource figures from the retained outputs. `revise_manuscript.py` regenerates the main article from stored numerical results. Compile `manuscript/main.tex` using an installed LaTeX distribution; on Windows, `compile_paper.ps1` updates the same `main.pdf`.

## Observation data and validation roles

The original contest observation workbook, observation-bearing response CSV files and residual/Jacobian arrays that reproduce individual observations are excluded from this public release while their source redistribution conditions remain unresolved. Model geometry/material inputs, nominal fitted coefficients, aggregate fitting metrics, fitted vectors and simulated stack trajectories are included.

The −20 °C record was used for training. The −25 °C record was excluded from fitting, but its cross-temperature validation informed retention of the supplied nominal reference. It is not a post-selection final independent test. Repeating the single-cell fitting/validation and rebuilding its observation-overlay figure requires obtaining the original observation records and placing them at the input locations expected by the supplied code. Stack calculations with the retained vectors do not require those observations.

## License and authorship

No additional reuse license has been selected for this deposit. Public access does not grant a new license to the original contest observations. Authorship and scientific attribution are given in the manuscript.
