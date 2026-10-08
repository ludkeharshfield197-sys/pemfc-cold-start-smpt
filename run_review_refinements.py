"""Time-step checks for marginal warmth and changed heat-input location."""
from pathlib import Path
import copy,json
from run_review_revision_experiments import configurations,run,DEST
names=['R_band1_Preheat_gate_j01401_h0025','R_load0.08_End50_gate_B2_h0025',
    'R_load0.2_Uniform125_gate_B2_h0025','R_endplate50_start_h0025',
    'R_endplate50_fixed_j01401_B2_h0025','R_endplate50_gate_j01401_B2_h0025',
    'R_beta3_A1_h0025','R_beta3_A5_h0025']
cases=[]
for case in configurations():
    if case['name'] not in names: continue
    c=copy.deepcopy(case); c['coarse_name']=c['name']; c['name']=c['name'].replace('h0025','h00125')
    c['group']='refinement'; c['task']['dt']=.0125
    if c.get('startup','').startswith('R_endplate'):
        c['startup']=c['startup'].replace('h0025','h00125')
        c['startup_file']=str(DEST/(c['startup']+'.json'))
    cases.append(c)
(DEST/'refinement_config.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf-8')
for c in cases: run(c)
