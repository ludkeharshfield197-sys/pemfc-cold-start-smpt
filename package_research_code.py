"""Package scientific implementations, inputs, actual trajectories and generators."""
from pathlib import Path
import json,re
from zipfile import ZipFile,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parent
scripts=['README.md','代码说明.md','修改与实验说明_20261007.md','requirements.txt',
    'run_revision_experiments.py','run_handover_experiments.py','run_baseline_experiments.py',
    'run_review_revision_experiments.py','run_review_refinements.py','run_parameter_analysis.py','run_joint_calibration.py',
    'propagate_profile_parameters.py','propagate_joint_parameters.py','run_onset_parameter_comparisons.py','summarize_onset_parameters.py','compare_thermal_networks.py','summarize_revision.py',
    'summarize_handover.py','summarize_review_revision.py','build_assets.py','build_revision_assets.py',
    'build_integrated_assets.py','build_review_assets.py','revise_manuscript.py','integrate_manuscript.py',
    'review_manuscript_text.py','followup_manuscript_text.py','final_small_revision.py','compile_paper.ps1','render_final_pdfs.py',
    'package_research_code.py','submission/build_submission_documents.py','submission/package_sources.py',
    'submission/author_metadata.json','submission/Cover_letter.docx','submission/Highlights.docx',
    'submission/Cover_letter_draft.md','submission/Highlights.txt','submission/投稿使用说明_20261007.md',
    'repository/README.md','manuscript/main.tex','manuscript/main.pdf','manuscript/references.bib',
    'build/handover_originals/manuscript/main.tex','records/current_result_sources.json','records/manuscript_result_index.json']
files={ROOT/x for x in scripts}
for name in ['base_model.py','implicit_water.py','io_labels.py','stack_solver.py','q1_identification.py']:
    files.add(ROOT/'program_event_v2/src'/name)
files.add(ROOT/'program_event_v2/revision/stack_solver_revision.py')
for name in ['input_labels.json','manuscript_runs.json','formal_q4_None.json','formal_q4_20.json','formal_q4_40.json']:
    files.add(ROOT/'program_event_v2/config'/name)
for folder in ['program_event_v2/inputs','program_event_v2/results/revision',
    'program_event_v2/results/handover','program_event_v2/results/review_revision','program_event_v2/results/validation']:
    for path in (ROOT/folder).rglob('*'):
        if path.is_file() and path.suffix in ['.json','.csv','.xlsx']: files.add(path)
files.update((ROOT/'program_event_v2/revision').glob('*.json'))
sources=json.loads((ROOT/'records/current_result_sources.json').read_text(encoding='utf-8'))
index=json.loads((ROOT/'records/manuscript_result_index.json').read_text(encoding='utf-8'))
for source in set(sources.values())|{x['source'] for x in index}:
    path=ROOT/source; files.add(path)
    if path.with_suffix('.csv').exists(): files.add(path.with_suffix('.csv'))
doc=(ROOT/'manuscript/main.tex').read_text(encoding='utf-8')
for name in re.findall(r'^\\fig\{([^}]+)\}',doc,re.M):
    files.update(ROOT/'manuscript/figures'/(name+'.'+ext) for ext in ['pdf','svg','png'])
dest=ROOT/'repository/SMPT_research_code_20261007.zip'
with ZipFile(dest,'w',ZIP_DEFLATED) as archive:
    for path in sorted(files): archive.write(path,path.relative_to(ROOT).as_posix())
print('Research archive:',dest)
print('Files:',len(files),'compressed MB:',round(dest.stat().st_size/1e6,2))
