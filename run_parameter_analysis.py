"""Response sensitivities, residual structure and six-parameter profile refits."""
from pathlib import Path
import os,sys,json,time
for k in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']: os.environ[k]='1'
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'program_event_v2/src'))
from stack_solver import parameters
import base_model as m
from q1_identification import profile_refit
DEST=ROOT/'program_event_v2/results/review_revision/parameters'; DEST.mkdir(parents=True,exist_ok=True)
p,theta=parameters(); grid=m._grid(p)
experiments={s:m._read_experiment(ROOT/'program_event_v2/inputs/experiments.xlsx',s,s) for s in ['-20C','-25C']}
names=['log10_j0','gamma_C','g','tau','eta_c0','Qc','Qr']

def response(t,label='-20C'):
    return m._simulate(experiments[label],p,grid,t,False,.2)

def residual(t):
    r=response(t); e=experiments['-20C']
    return np.r_[(r['sim_voltage_V']-e.voltage_V.to_numpy())/.045,(r['sim_temperature_C']-e.temperature_C.to_numpy())/1.5]

def local():
    scales=np.maximum(abs(theta),.1); jac=[]
    for step in [.001,.0005]:
        columns=[]
        for i in range(7):
            a=theta.copy(); b=theta.copy(); h=step*scales[i]; a[i]+=h; b[i]-=h
            columns.append((residual(a)-residual(b))/(2*h)*scales[i])
        jac.append(np.array(columns).T)
    J=jac[1]; norms=np.linalg.norm(J,axis=0); cosine=J.T@J/(norms[:,None]*norms[None,:])
    u,s,v=np.linalg.svd(J,full_matrices=False)
    # Two largest components of the least responsive scaled direction.
    weak=np.argsort(abs(v[-1]))[-2:][::-1].tolist()
    d=dict(names=names,theta=theta.tolist(),scales=scales.tolist(),column_norms=norms.tolist(),singular_values=s.tolist(),
        condition_number=float(s[0]/s[-1]),least_direction=v[-1].tolist(),profile_indices=weak,
        difference_relative_norm=float(np.linalg.norm(jac[0]-jac[1])/np.linalg.norm(J)),
        objective=float(residual(theta)@residual(theta)),residual_scales={'voltage_V':.045,'temperature_C':1.5},
        interpretation='Dimensional residual scales; no measurement-noise model or confidence interval.')
    (DEST/'local.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
    pd.DataFrame(cosine,index=names,columns=names).to_csv(DEST/'direction_cosines.csv')
    pd.DataFrame(J,columns=names).to_csv(DEST/'scaled_jacobian.csv',index=False)
    for label in experiments:
        r=response(theta,label); e=experiments[label].copy()
        for k,value in r.items(): e[k]=value
        e['voltage_residual_V']=e.sim_voltage_V-e.voltage_V
        e['temperature_residual_C']=e.sim_temperature_C-e.temperature_C
        e.to_csv(DEST/(label+'_response.csv'),index=False)
        rows=[]
        for field in ['voltage_residual_V','temperature_residual_C']:
            x=e[field].to_numpy(); x-=x.mean()
            acf=np.correlate(x,x,'full')[len(x)-1:len(x)+30]/(x@x)
            rows.extend(dict(variable=field,lag_s=.2*i,acf=float(value)) for i,value in enumerate(acf))
        pd.DataFrame(rows).to_csv(DEST/(label+'_autocorrelation.csv'),index=False)
    print('LOCAL',json.dumps(d),flush=True)

def profiles(part=0,parts=1):
    local_data=json.loads((DEST/'local.json').read_text())
    for index in local_data['profile_indices']:
        for k,factor in enumerate([.6,.8,1,1.2,1.4]):
            if k%parts!=part: continue
            path=DEST/f'profile_{names[index]}_{factor:g}.json'
            if path.exists(): continue
            before=time.perf_counter(); t,fit=profile_refit(theta,index,theta[index]*factor,residual=residual,max_nfev=60)
            metrics=[]
            for label in experiments:
                r=response(t,label); e=experiments[label]
                metrics.append(dict(condition=label,voltage_MAE_V=float(abs(r['sim_voltage_V']-e.voltage_V).mean()),
                    temperature_MAE_C=float(abs(r['sim_temperature_C']-e.temperature_C).mean())))
            out=dict(fixed_parameter=names[index],fixed_index=index,factor=factor,value=float(t[index]),theta=t.tolist(),
                fitted_indices=np.delete(np.arange(7),index).tolist(),objective=float(fit.fun@fit.fun),success=bool(fit.success),
                status=int(fit.status),message=fit.message,nfev=int(fit.nfev),optimality=float(fit.optimality),
                wall_s=time.perf_counter()-before,metrics=metrics)
            path.write_text(json.dumps(out,indent=2),encoding='utf-8')
            print('PROFILE',names[index],factor,fit.status,out['objective'],out['wall_s'],flush=True)

if __name__=='__main__':
    if sys.argv[1]=='local': local()
    if sys.argv[1]=='profile': profiles(int(sys.argv[2]),int(sys.argv[3]))
