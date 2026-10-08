"""Carry selected training fits through fresh startups and their own holdings."""
import json,sys
from run_review_revision_experiments import start_task,holding,run,DEST
P=DEST/'parameters/joint'

def calculations(label,fit):
    cases=[]
    for strategy in ['A1','A5']:
        task=start_task(strategy); task.update(theta=fit['theta'],save_state=True,dt=.025)
        parent=f'R_selected_{label}_{strategy}_start_h0025'
        cases.append(dict(name=parent,group='selected_propagation',vector=label,strategy=strategy,task=task))
        if strategy=='A5':
            for policy in ['fixed','gate']:
                cases.append(dict(name=f'R_selected_{label}_A5_{policy}_h0025',group='selected_hold',vector=label,
                    startup=parent,startup_file=str(DEST/(parent+'.json')),policy=policy,load=.1401,band=2,
                    task=holding(parent,policy)))
    (P/('propagation_'+label+'.json')).write_text(json.dumps(dict(label=label,fit=fit,cases=cases),indent=2),encoding='utf-8')
    for case in cases: run(case)

if __name__=='__main__':
    label=sys.argv[1]
    if label in ['joint','refine']:
        fits=[json.loads(x.read_text(encoding='utf-8')) for x in sorted(P.glob('joint_seed*.json'))]
        fit=min((x for x in fits if x['success']),key=lambda x:x['objective'])
    elif label=='Qc30': fit=json.loads((P/'extended_Qc30.json').read_text(encoding='utf-8'))
    if label=='refine':
        cases=[]
        for strategy in ['A1','A5']:
            task=start_task(strategy); task.update(theta=fit['theta'],save_state=False,dt=.0125)
            cases.append(dict(name=f'R_selected_joint_{strategy}_start_h00125',group='selected_refinement',strategy=strategy,task=task))
        (P/'selected_refinement.json').write_text(json.dumps(dict(cases=cases),indent=2),encoding='utf-8')
        for case in cases: run(case)
    else: calculations(label,fit)
