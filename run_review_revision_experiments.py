"""Finite SMPT revision comparisons, continuing real startup states."""
from pathlib import Path
import os,sys,json,time,copy
for key in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']: os.environ[key]='1'
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'program_event_v2/revision'),str(ROOT/'program_event_v2/src')]
from stack_solver_revision import simulate
from stack_solver import parameters
DEST=ROOT/'program_event_v2/results/review_revision'; DEST.mkdir(exist_ok=True)
CONFIG=ROOT/'program_event_v2/revision/review_revision_config.json'
BASE=json.loads((ROOT/'program_event_v2/revision/experiment_config.json').read_text(encoding='utf-8'))
REV=ROOT/'program_event_v2/results/revision'

def start_task(strategy):
    return copy.deepcopy(json.loads((REV/('D_End50.json' if strategy=='A5' else 'T_A1_0.0125.json')).read_text(encoding='utf-8'))['task'])

def holding(startup,policy,j=.1401,band=2,location='MEA'):
    return dict(q='Q4',mode='operation_temperature_gate' if policy=='gate' else 'constant_power',
        parameters=[1,0,0,30],operation_current=j,post_start=True,charge_cap=None,max_time=30,
        dt=.025,save_state=False,hold_target_C=band,hold_band_C=band,heater_location=location,
        initial_transient='rest_step')

def configurations():
    cases=[]
    for beta in [3,5,7]:
        for strategy in ['A1','A5']:
            task=start_task(strategy); task.update(dt=.025,save_state=False,physical={'end_cell_concentration_coefficient':beta})
            cases.append(dict(name=f'R_beta{beta}_{strategy}_h0025',group='beta',strategy=strategy,beta=beta,task=task))
    for j in [.08,.20]:
        for label in ['Preheat','Uniform125','End50','Delayed']:
            for policy in ['fixed','gate']:
                cases.append(dict(name=f'R_load{j:g}_{label}_{policy}_B2_h0025',group='load',startup='D_'+label,
                    startup_file=str(REV/('D_'+label+'.json')),policy=policy,load=j,band=2,task=holding(label,policy,j)))
    for band in [1,3]:
        for label in ['Preheat','Uniform125','End50','Delayed']:
            cases.append(dict(name=f'R_band{band}_{label}_gate_j01401_h0025',group='band',startup='D_'+label,
                startup_file=str(REV/('D_'+label+'.json')),policy='gate',load=.1401,band=band,task=holding(label,'gate',band=band)))
    for scale in [.5,2]:
        for state in ['FC','P20','P40']:
            task=copy.deepcopy(BASE['strategies'][state+'_FB'])
            # Only correction coefficients: T lag, warming rate, voltage and voltage rate.
            task['parameters'][7:11]=[v*scale for v in task['parameters'][7:11]]
            task.update(dt=.025,save_state=False)
            cases.append(dict(name=f'R_gain{scale:g}_{state}_FB_h0025',group='feedback',state=state,gain_scale=scale,task=task))
    _,theta=parameters()
    for param,index in [('g',2),('tau',3)]:
        for scale in [.8,1.2]:
            for strategy in ['A1','A5']:
                task=start_task(strategy); t=theta.copy(); t[index]*=scale
                task.update(theta=t.tolist(),dt=.025,save_state=False)
                cases.append(dict(name=f'R_memory{param}{scale:g}_{strategy}_h0025',group='memory',
                    parameter=param,multiplier=scale,strategy=strategy,task=task))
    task=start_task('A5'); task.update(heater_location='endplate',dt=.025,save_state=True)
    parent='R_endplate50_start_h0025'
    cases.append(dict(name=parent,group='endplate',strategy='Plate50',task=task))
    for policy in ['fixed','gate']:
        cases.append(dict(name=f'R_endplate50_{policy}_j01401_B2_h0025',group='endplate_hold',
            startup=parent,startup_file=str(DEST/(parent+'.json')),policy=policy,load=.1401,band=2,
            task=holding(parent,policy,location='endplate')))
    return cases

def run(case):
    path=DEST/(case['name']+'.json')
    if path.exists(): return json.loads(path.read_text(encoding='utf-8'))
    task=copy.deepcopy(case['task']); task['name']=case['name']
    initial=None
    if 'startup_file' in case:
        start=json.loads(Path(case['startup_file']).read_text(encoding='utf-8'))
        initial=start['final_state']
        # Copy the parent's physical/calibration settings when continuing its state.
        for key in ['physical','theta','transient_heat_fraction']:
            if key in start['task']: task[key]=copy.deepcopy(start['task'][key])
    began=time.perf_counter(); result,trace=simulate(task,True,initial)
    out={**case,'task':task,'result':result,'wall_s':time.perf_counter()-began}
    if task['save_state']: out['final_state']=result.pop('final_state')
    trace.to_csv(path.with_suffix('.csv'),index=False,encoding='utf-8-sig')
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(case['name'],result['status'],f"t={result['time_s']:.5f}, Eaux={result['total_energy_J']:.4f}",flush=True)
    if result['status'] in ['numerical_failure','model_domain']: raise RuntimeError(result['reason'])
    return out

if __name__=='__main__':
    cases=configurations()
    stage=sys.argv[1] if len(sys.argv)>1 else 'all'
    if stage=='configure':
        CONFIG.write_text(json.dumps(dict(cases=cases,residual_scales={'V':.045,'C':1.5},
            gate_rule='qmax*clip((B-Tmean)/B,0,1)',feedback_scaled_indices=[7,8,9,10]),ensure_ascii=False,indent=2),encoding='utf-8')
    else:
        shard=int(sys.argv[2]) if len(sys.argv)>2 else 0; parts=int(sys.argv[3]) if len(sys.argv)>3 else 1
        for i,case in enumerate(cases):
            owner=0 if case['group'].startswith('endplate') else i%parts
            if owner==shard and (stage=='all' or stage==case['group']): run(case)
