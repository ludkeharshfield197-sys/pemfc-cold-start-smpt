"""Recompute the configured manuscript baselines without frozen/audit entries."""
from pathlib import Path
import os,json,sys,time
for key in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']: os.environ[key]='1'
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'program_event_v2/src'))
from stack_solver import simulate
from q1_identification import evaluate

def stack(part,parts):
    cfg=json.loads((ROOT/'program_event_v2/config/manuscript_runs.json').read_text(encoding='utf-8'))
    sources=json.loads((ROOT/'records/current_result_sources.json').read_text(encoding='utf-8'))
    cases={sources[x['key']]:x['task'] for x in cfg['tasks']}
    for i,(file,task) in enumerate(cases.items()):
        if i%parts!=part: continue
        path=ROOT/file
        if path.exists(): continue
        path.parent.mkdir(parents=True,exist_ok=True)
        before=time.perf_counter(); result,trace=simulate(task,True)
        trace.to_csv(path.with_suffix('.csv'),index=False,encoding='utf-8-sig')
        path.write_text(json.dumps(dict(task=task,result=result,wall_s=time.perf_counter()-before),ensure_ascii=False,indent=2),encoding='utf-8')
        print(path.stem,result['status'],result['time_s'],flush=True)
        if result['status'] in ['numerical_failure','model_domain']: raise RuntimeError(result['reason'])

def single():
    rows,traces=evaluate(dt=.2)
    dest=ROOT/'program_event_v2/results/validation'; dest.mkdir(parents=True,exist_ok=True)
    for label,d in traces.items(): d.to_csv(dest/('Q1_正式_'+label.replace('C','℃')+'.csv'),index=False,encoding='utf-8-sig')
    # Fine response inputs used by the article generator.
    for step,stem in [(.1,'time_refined'),(.05,'time_refined_again')]: evaluate(dt=step,save=stem)
    print(rows,flush=True)

if __name__=='__main__':
    if sys.argv[1]=='stack': stack(int(sys.argv[2]),int(sys.argv[3]))
    elif sys.argv[1]=='single': single()
