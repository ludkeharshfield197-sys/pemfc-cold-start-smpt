"""Fresh startups and their own state continuations for two fitted vectors."""
import json,copy
from pathlib import Path
from run_review_revision_experiments import start_task,holding,run,DEST
P=DEST/'parameters'
local=json.loads((P/'local.json').read_text(encoding='utf-8'))
profiles=[json.loads(x.read_text(encoding='utf-8')) for x in sorted(P.glob('profile_*.json'))]
assert len(profiles)==10
good=[x for x in profiles if x['success'] and x['objective']<=1.05*local['objective']]
good=sorted(good,key=lambda x:x['theta'][5])
chosen=[good[0],good[-1]]
cases=[]
for i,fit in enumerate(chosen):
    for strategy in ['A1','A5']:
        task=start_task(strategy); task.update(theta=fit['theta'],save_state=True,dt=.025)
        parent=f'R_profile{i+1}_{strategy}_start_h0025'
        cases.append(dict(name=parent,group='propagation',profile=i+1,strategy=strategy,task=task))
        if strategy=='A5':
            for policy in ['fixed','gate']:
                cases.append(dict(name=f'R_profile{i+1}_A5_{policy}_h0025',group='propagation_hold',profile=i+1,
                    startup=parent,startup_file=str(DEST/(parent+'.json')),policy=policy,load=.1401,band=2,
                    task=holding(parent,policy)))
(P/'propagation_config.json').write_text(json.dumps(dict(selection='Converged profile fits with L <= 1.05 times supplied-vector L; smallest and largest Qc.',
    chosen=chosen,cases=cases),ensure_ascii=False,indent=2),encoding='utf-8')
for case in cases: run(case)
