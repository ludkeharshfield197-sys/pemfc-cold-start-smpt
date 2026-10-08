"""Compute interval metrics directly from accepted common-load trajectories."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
REV=ROOT/'program_event_v2/results/revision'
DEST=ROOT/'program_event_v2/results/handover'

def metrics(name,startup,policy,path):
    out=json.loads(path.read_text(encoding='utf-8')); r=out['result']
    d=pd.read_csv(path.with_suffix('.csv'))
    t=d['time/s'].to_numpy(); temp=d['minimum_temperature/C'].to_numpy()
    below=np.flatnonzero(temp<0)
    cold=np.nan
    if below.size:
        i=below[0]
        cold=0 if i==0 else t[i-1]+(t[i]-t[i-1])*temp[i-1]/(temp[i-1]-temp[i])
    charge=r['incremental_charge_C_cm2']; chemical=1.48*125*charge
    start=json.loads((REV/(startup+'.json')).read_text(encoding='utf-8'))['result']
    return dict(name=name,startup=startup,policy=policy,dt=out['task']['dt'],status=r['status'],duration_s=r['time_s'],
        min_voltage_V=r['min_voltage_V'],min_MEA_C=temp.min(),final_min_MEA_C=temp[-1],
        first_subzero_s=cold,max_pore_ice=r['max_pore_ice_saturation'],final_pore_ice=r['final_max_pore_ice_saturation'],
        max_spread_C=r['max_delta_T_C'],output_J=r['output_energy_J'],hold_auxiliary_J=r['total_energy_J'],
        interval_charge_C_cm2=charge,hydrogen_mg=r['hydrogen_mg'],chemical_J=chemical,
        interval_net_J=r['total_energy_J']+chemical-r['output_energy_J'],
        completed=r['status']=='operation_complete',warm=np.all(temp>=0) and r['status']=='operation_complete',
        startup_auxiliary_J=start['total_energy_J'],startup_output_J=start['output_energy_J'],
        cumulative_auxiliary_J=start['total_energy_J']+r['total_energy_J'],
        cumulative_output_J=start['output_energy_J']+r['output_energy_J'])

def summarize():
    rows=[]
    for label in ['Preheat','Uniform125','End50','Delayed']:
        startup='D_'+label
        rows.append(metrics(startup+'_off',startup,'off',REV/(startup+'_operation.json')))
        for path in sorted(DEST.glob('H_'+label+'_*.json')):
            out=json.loads(path.read_text(encoding='utf-8'))
            rows.append(metrics(out['name'],startup,out['policy'],path))
    frame=pd.DataFrame(rows)
    frame.to_csv(DEST/'summary.csv',index=False,encoding='utf-8-sig')
    print(frame[['name','min_MEA_C','first_subzero_s','hold_auxiliary_J','output_J','warm']].to_string(index=False))
    return frame
if __name__=='__main__': summarize()
