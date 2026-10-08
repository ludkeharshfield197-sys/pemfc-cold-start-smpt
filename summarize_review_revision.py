"""Finite startup and full-interval handover comparisons and resource integrals."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
DEST=ROOT/'program_event_v2/results/review_revision'

def metrics(path):
    out=json.loads(path.read_text(encoding='utf-8')); r=out['result']; d=pd.read_csv(path.with_suffix('.csv'))
    t=d['time/s'].to_numpy(); T=d['minimum_temperature/C'].to_numpy(); below=np.flatnonzero(T<0)
    cross=np.nan
    if len(below):
        i=below[0]; cross=0. if i==0 else t[i-1]+(t[i]-t[i-1])*T[i-1]/(T[i-1]-T[i])
    q=r['incremental_charge_C_cm2']; chem=1.48*125*q
    return dict(name=out['name'],group=out['group'],strategy=out.get('strategy',''),startup=out.get('startup',''),
        policy=out.get('policy',''),load=out.get('load',np.nan),band=out.get('band',np.nan),beta=out.get('beta',np.nan),
        state=out.get('state',''),gain_scale=out.get('gain_scale',np.nan),parameter=out.get('parameter',''),
        multiplier=out.get('multiplier',np.nan),dt=out['task']['dt'],status=r['status'],duration_s=r['time_s'],
        min_voltage_V=r['min_voltage_V'],min_MEA_C=float(T.min()),final_min_MEA_C=float(T[-1]),
        first_subzero_s=cross,max_pore_ice=r['max_pore_ice_saturation'],max_spread_C=r['max_delta_T_C'],
        Eaux_J=r['total_energy_J'],Eout_J=r['output_energy_J'],Q_C_cm2=q,H2_mg=r['hydrogen_mg'],Echem_J=chem,
        Enet_J=r['total_energy_J']+chem-r['output_energy_J'],
        completed=r['status']=='operation_complete',warm=bool((T>=0).all() and r['status']=='operation_complete'),
        endplate_min_C=min(r['final_endplate_T_C']))

def summarize():
    frame=pd.DataFrame(metrics(path) for path in sorted(DEST.glob('R_*.json')))
    frame.to_csv(DEST/'summary.csv',index=False,encoding='utf-8-sig')
    print(frame[['name','status','duration_s','min_MEA_C','Eaux_J','Eout_J','warm']].to_string(index=False))
    return frame

if __name__=='__main__': summarize()
