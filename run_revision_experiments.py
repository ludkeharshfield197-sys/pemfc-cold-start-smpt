"""Run the fixed revision batch. Usage: python run_revision_experiments.py SHARD [NSHARDS]."""
from pathlib import Path
import json
import sys
import time
import os

for key in ['OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS']:
    os.environ[key] = '1'
ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'program_event_v2/revision'), str(ROOT/'program_event_v2/src')]
from stack_solver_revision import simulate

CONFIG = ROOT/'program_event_v2/revision/experiment_config.json'
batch = json.loads(CONFIG.read_text(encoding='utf-8'))
DEST = ROOT/'program_event_v2/results/revision'
DEST.mkdir(exist_ok=True)

def run_case(case, initial_state=None):
    name = case['name']; target = DEST/(name+'.json')
    if target.exists():
        return json.loads(target.read_text(encoding='utf-8'))
    start = time.perf_counter()
    r, trace = simulate(case['task'], True, initial_state)
    state = r.pop('final_state', None)
    trace.to_csv(DEST/(name+'.csv'), index=False, encoding='utf-8-sig')
    out = {**case, 'result':r, 'wall_s':time.perf_counter()-start}
    if state is not None:
        out['final_state'] = state
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(name, r['status'], f"t={r['time_s']:.6f}", f"E={r['total_energy_J']:.3f}", f"wall={out['wall_s']:.1f}", flush=True)
    if r['status'] in ['numerical_failure', 'model_domain']:
        raise RuntimeError(name + ': ' + r['reason'])
    return out

if __name__ == '__main__':
    shard = int(sys.argv[1]); nshards = int(sys.argv[2]) if len(sys.argv)>2 else 3
    for i, case in enumerate(batch['cases']):
        if i % nshards != shard:
            continue
        result = run_case(case)
        if case['group'] == 'continuation' and result['result']['success']:
            task = {**case['task'], 'q':'Q4', 'mode':'constant_power', 'parameters':[0,0,0,0],
                    'operation_current':batch['operation_current_A_cm2'], 'post_start':True,
                    'charge_cap':None, 'max_time':batch['operation_duration_s'], 'save_state':False,
                    'name':case['name']+'_operation'}
            run_case(dict(name=task['name'], group='operation', strategy=case['task']['strategy'], task=task), result['final_state'])
