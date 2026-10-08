"""Small end-heater handover comparison continued from saved startup states."""
from pathlib import Path
import os,json,time,sys
for key in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']: os.environ[key]='1'
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'program_event_v2/revision'),str(ROOT/'program_event_v2/src')]
from stack_solver_revision import simulate
DEST=ROOT/'program_event_v2/results/handover'
DEST.mkdir(exist_ok=True)
CONFIG=ROOT/'program_event_v2/revision/handover_config.json'

def configurations(stage):
    # One-end heat withdrawal reaches about 30 W just before startup.
    # Bracket 30/50 W total end heating; 50 W is the two-end actuator limit.
    policies=[('fixed30',30),('fixed50',50),('gate50',50)]
    if stage=='all': labels=['Preheat','Uniform125','End50','Delayed']
    else: labels=['End50','Delayed']
    cases=[dict(name='H_'+label+'_'+policy,startup='D_'+label,policy=policy,total_power_W=power,
                 dt=.025,load_A_cm2=.1401,duration_s=30,target_C=2,band_C=2)
            for label in labels for policy,power in policies]
    if stage=='all':
        for label in ['Preheat','End50','Delayed']:
            base=next(case for case in cases if case['name']=='H_'+label+'_gate50')
            cases.append({**base,'name':base['name']+'_dt0125','dt':.0125})
    return cases

def run(case):
    path=DEST/(case['name']+'.json')
    if path.exists(): return json.loads(path.read_text(encoding='utf-8'))
    start=json.loads((ROOT/'program_event_v2/results/revision'/(case['startup']+'.json')).read_text(encoding='utf-8'))
    task={**start['task'],'q':'Q4','mode':'operation_temperature_gate' if case['policy'].startswith('gate') else 'constant_power',
          'parameters':[case['total_power_W']/50,0,0,case['duration_s']],
          'operation_current':case['load_A_cm2'],'post_start':True,'charge_cap':None,
          'max_time':case['duration_s'],'dt':case['dt'],'save_state':False,
          'hold_target_C':case['target_C'],'hold_band_C':case['band_C']}
    clock=time.perf_counter()
    result,trace=simulate(task,True,start['final_state'])
    trace.to_csv(DEST/(case['name']+'.csv'),index=False,encoding='utf-8-sig')
    out={**case,'task':task,'result':result,'wall_s':time.perf_counter()-clock}
    path.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
    print(case['name'],result['status'],'end Tmin=',min(result['final_T_C']),'Eaux=',result['total_energy_J'],flush=True)
    if result['status'] in ['numerical_failure','model_domain']: raise RuntimeError(result['reason'])
    return out

if __name__=='__main__':
    cases=configurations(sys.argv[1] if len(sys.argv)>1 else 'pilot')
    CONFIG.write_text(json.dumps(dict(load_A_cm2=.1401,duration_s=30,allocation='end cells only',
        temperature_gate='q_k=qmax_k*clip((2-T_k)/2,0,1)',cases=cases),indent=2),encoding='utf-8')
    shard=int(sys.argv[2]) if len(sys.argv)>2 else 0
    parts=int(sys.argv[3]) if len(sys.argv)>3 else 1
    for i,case in enumerate(cases):
        if i%parts==shard: run(case)
