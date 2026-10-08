"""Seven-coordinate training fits; the colder record is evaluated after fitting."""
import json,sys,time,os
for key in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']: os.environ[key]='1'
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from run_parameter_analysis import theta,response,residual,experiments,DEST,names
from q1_identification import profile_refit

JOINT=DEST/'joint'; JOINT.mkdir(exist_ok=True)
LOW=np.array([-.5,.5,.1,.5,0,.5,.1]); HIGH=np.array([3,2,4,20,.8,30,10])
PROFILE14=json.loads((DEST/'profile_Qc_1.4.json').read_text())['theta']
SEEDS=[theta.tolist(),PROFILE14,[1.8,1.05,1.3,7,.25,20,2.5]]
SETTINGS=dict(training_record='-20C',validation_record='-25C',dt_s=.2,
    residual_scales=dict(voltage_V=.045,temperature_C=1.5),parameter_names=names,
    lower=LOW.tolist(),upper=HIGH.tolist(),initial_vectors=SEEDS,method='trf',
    max_nfev=200,ftol=1e-7,xtol=1e-7,gtol=1e-7,
    selection='Minimum converged training objective; colder validation is excluded from the fitting objective and from fitted-vector selection; its response-transfer comparison informs retention of the supplied nominal reference.')

def evaluate_vector(t,stem):
    metrics=[]
    for label,e in experiments.items():
        r=response(t,label); d=e.copy()
        for k,v in r.items(): d[k]=v
        ev=r['sim_voltage_V']-e.voltage_V.to_numpy(); et=r['sim_temperature_C']-e.temperature_C.to_numpy()
        metrics.append(dict(condition=label,voltage_MAE_V=float(abs(ev).mean()),
            voltage_RMSE_V=float(np.sqrt(np.mean(ev**2))),temperature_MAE_C=float(abs(et).mean()),
            temperature_RMSE_C=float(np.sqrt(np.mean(et**2))),objective=float(np.sum((ev/.045)**2+(et/1.5)**2))))
        d['voltage_residual_V']=ev; d['temperature_residual_C']=et
        d.to_csv(JOINT/(stem+'_'+label+'.csv'),index=False)
    return metrics

def joint(index):
    stem=f'joint_seed{index+1}'; path=JOINT/(stem+'.json')
    if path.exists(): return
    start=time.perf_counter()
    fit=least_squares(residual,SEEDS[index],bounds=(LOW,HIGH),method='trf',
        x_scale=np.maximum(abs(theta),.1),max_nfev=200,ftol=1e-7,xtol=1e-7,gtol=1e-7)
    out=dict(seed=index+1,initial_theta=SEEDS[index],theta=fit.x.tolist(),objective=float(fit.fun@fit.fun),
        success=bool(fit.success),status=int(fit.status),message=fit.message,nfev=int(fit.nfev),
        optimality=float(fit.optimality),active_mask=fit.active_mask.tolist(),wall_s=time.perf_counter()-start,
        metrics=evaluate_vector(fit.x,stem))
    path.write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(stem,out['status'],out['objective'],out['theta'],out['metrics'],flush=True)

def extended(qc):
    stem=f'extended_Qc{qc:g}'; path=JOINT/(stem+'.json')
    if path.exists(): return
    start=time.perf_counter()
    t,fit=profile_refit(np.array(PROFILE14),5,qc,residual=residual,max_nfev=120)
    out=dict(fixed_parameter='Qc',value=qc,theta=t.tolist(),objective=float(fit.fun@fit.fun),
        success=bool(fit.success),status=int(fit.status),message=fit.message,nfev=int(fit.nfev),
        optimality=float(fit.optimality),max_nfev=120,ftol=1e-5,xtol=1e-5,gtol=1e-5,
        initial_theta=PROFILE14,wall_s=time.perf_counter()-start,metrics=evaluate_vector(t,stem))
    path.write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(stem,out['status'],out['objective'],out['theta'],flush=True)

if __name__=='__main__':
    if sys.argv[1]=='configure':
        (JOINT/'settings.json').write_text(json.dumps(SETTINGS,indent=2),encoding='utf-8')
        (JOINT/'supplied_metrics.json').write_text(json.dumps(evaluate_vector(theta,'supplied'),indent=2),encoding='utf-8')
    elif sys.argv[1]=='joint': joint(int(sys.argv[2]))
    elif sys.argv[1]=='profile': extended(float(sys.argv[2]))
