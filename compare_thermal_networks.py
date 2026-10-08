"""Equal-capacity seven-node and resolved through-plane thermal networks."""
from pathlib import Path
import os,sys,json
for k in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']: os.environ[k]='1'
import numpy as np
import pandas as pd
from scipy.linalg import eigh
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT/'program_event_v2/src'))
from stack_solver import parameters,structure
import base_model as m
DEST=ROOT/'program_event_v2/results/review_revision/thermal'; DEST.mkdir(exist_ok=True)
p,theta=parameters(); g=m._grid(p); s=structure(p,g,theta); n=s['n']; A=s['area']
# The reduced network sums capacities while retaining the same intercell,
# endplate and ambient conductances. Temperature is uniform within each cell.
P=np.zeros((5*n+2,7))
for k in range(5): P[k*n:(k+1)*n,k]=1
P[-2,-2]=1; P[-1,-1]=1
Cr=P.T@s['C']; Kr=P.T@s['K']@P
times=np.arange(0,100.0001,.1)

def exact(C,K,f):
    values,vectors=eigh(K/np.sqrt(C[:,None]*C[None,:]))
    coeff=vectors.T@(f/np.sqrt(C))
    return -30+((1-np.exp(-times[:,None]*values))/values*coeff)@vectors.T/np.sqrt(C)

rows=[]
for label in ['uniform50','MEA_end50','plate50']:
    f=np.zeros(len(s['C']))
    if label=='plate50': f[-2:]=25/A
    else:
        q=np.repeat(10.,5) if label=='uniform50' else np.array([25.,0,0,0,25.])
        for k in range(5):
            f[k*n]+=q[k]/(2*A); f[(k+1)*n-1]+=q[k]/(2*A)
    full=exact(s['C'],s['K'],f); reduced=exact(Cr,Kr,P.T@f)
    mean=np.c_[full@s['W'].T,full[:,-2:]]
    d={'time_s':times}
    for k in range(7):
        d[f'resolved_{k+1}_C']=mean[:,k]; d[f'lumped_{k+1}_C']=reduced[:,k]
    pd.DataFrame(d).to_csv(DEST/(label+'.csv'),index=False)
    rows.append(dict(source=label,max_MEA_difference_C=float(abs(mean[:,:5]-reduced[:,:5]).max()),
        max_plate_difference_C=float(abs(mean[:,5:]-reduced[:,5:]).max())))
out=dict(single_endplate_capacity_J_K=float(s['C'][-1]*A),both_endplates_capacity_J_K=float(s['C'][-2:].sum()*A),
    total_capacity_J_K=float(s['C'].sum()*A),endplate_capacity_fraction=float(s['C'][-2:].sum()/s['C'].sum()),
    Ge_W_m2_K=float(s['Ge']),G_W_m2_K=float(s['G']),area_m2=A,
    endplate_path_time_s=float(s['C'][-1]/s['Ge']),comparisons=rows,
    conditions='No reaction, phase change or current; -30 C initial/ambient; constant 50 W, 100 s; exact linear-network evolution.')
(DEST/'comparison.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
