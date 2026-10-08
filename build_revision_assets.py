"""Reproducible publication figures from observations and saved simulation outputs."""
from pathlib import Path
import json, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'program_event_v2/src'))
from io_labels import translate_label
FIG=ROOT/'manuscript/figures'; FIG.mkdir(exist_ok=True)
REV=ROOT/'program_event_v2/results/revision'
SRC=json.loads((ROOT/'records/current_result_sources.json').read_text(encoding='utf-8'))
C=['#24638c','#d97926','#398465','#9b4268','#7766a1']
NAMES=['Fully cooled','20 min precooling','40 min precooling']
STATES=['FC','P20','P40']; SUFFIX=['None','20','40']
FB=['E1_05_formal_q4_None','E1_06_formal_q4_20','E1_07_formal_q4_40']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':9,'axes.titlesize':9,
 'legend.fontsize':7,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42,
 'svg.fonttype':'none','lines.linewidth':1.3,'savefig.dpi':180,'axes.formatter.useoffset':False})
def old(key): return json.loads((ROOT/SRC[key]).read_text(encoding='utf-8'))
def tr(key): return pd.read_csv((ROOT/SRC[key]).with_suffix('.csv')).rename(columns=translate_label)
def new(name): return json.loads((REV/(name+'.json')).read_text(encoding='utf-8'))
def nt(name): return pd.read_csv(REV/(name+'.csv'))
def save(fig,name):
 for ext in ['pdf','svg','png']: fig.savefig(FIG/(name+'.'+ext),bbox_inches='tight',pad_inches=.07)
 plt.close(fig)
def panels(axes):
 for i,a in enumerate(np.asarray(axes).ravel()):
  a.text(-.03,1.04,f'({chr(97+i)})',transform=a.transAxes,fontweight='bold'); a.grid(alpha=.17,lw=.6)
  if a.get_title(): a.set_title(a.get_title(),pad=21)
def temps(a,d):
 for k,ls,c in zip([1,2,3],['-','--',':'],C):
  a.plot(d['time/s'],d[f'cell_{k}_temperature/C'],ls=ls,color=c,label=['Cells 1/5','Cells 2/4','Cell 3'][k-1])
 a.axhline(0,ls=':',color='0.4',lw=.8); a.set_xlabel('Time (s)'); a.set_ylabel('MEA mean temperature (°C)')

def base_figures():
 fig,ax=plt.subplots(2,2,figsize=(6.7,4.3),layout='constrained')
 fitdir=ROOT/'program_event_v2/results/review_revision/parameters/joint'
 fitted=[json.loads(x.read_text(encoding='utf-8')) for x in fitdir.glob('joint_seed*.json')]
 best=min(fitted,key=lambda x:x['objective'])
 for i,t in enumerate([-20,-25]):
  d=pd.read_csv(ROOT/f'program_event_v2/results/validation/Q1_正式_{t}℃.csv')
  joint=pd.read_csv(fitdir/f'joint_seed{best["seed"]}_{t}C.csv')
  for a,obs,sim in [(ax[0,0],'voltage_V','sim_voltage_V'),(ax[0,1],'temperature_C','sim_temperature_C')]:
   a.plot(d.time_s,d[obs],ls='none',marker='o',markevery=4,ms=2.6,mfc='white',mec=C[i],mew=.7,zorder=3)
   a.plot(d.time_s,d[sim],color=C[i],lw=1.2)
   a.plot(joint.time_s,joint[sim],color=C[i],lw=1.1,ls='--')
  ax[1,0].plot(d.time_s,1000*(d.sim_voltage_V-d.voltage_V),color=C[i])
  ax[1,1].plot(d.time_s,d.sim_temperature_C-d.temperature_C,color=C[i])
  ax[1,0].plot(joint.time_s,1000*joint.voltage_residual_V,color=C[i],ls='--')
  ax[1,1].plot(joint.time_s,joint.temperature_residual_C,color=C[i],ls='--')
 for a,label in zip(ax.ravel(),['Cell voltage (V)','Mean temperature (°C)','Voltage residual (mV)','Temperature residual (°C)']): a.set_ylabel(label); a.set_xlabel('Time (s)')
 for a in ax[1]: a.axhline(0,color='0.5',ls=':',lw=.8)
 handles=[Line2D([],[],color=c,label=label) for c,label in zip(C,['−20 °C: training record','−25 °C: validation record'])]+[Line2D([],[],color='0.3',marker='o',mfc='white',ls='none',label='Observations'),Line2D([],[],color='0.3',label='Supplied vector'),Line2D([],[],color='0.3',ls='--',label='Joint training fit')]
 fig.legend(handles=handles,loc='outside lower center',ncol=2); panels(ax); save(fig,'f01_validation')

 fig,ax=plt.subplots(2,2,figsize=(6.7,4.5),layout='constrained')
 loads=[('Q2_正式_恒流策略','Constant'),('Q2_正式_线性升载','Ramp'),('Q2_正式_分段阶梯加载','Staircase'),('Q2_零起点推荐复核','Zero-start ramp')]
 for i,(key,label) in enumerate(loads):
  d=tr(key)
  for a,col in zip(ax.ravel(),['current_density/A_cm2','minimum_voltage/V','minimum_temperature/C','max_pore_ice_saturation']): a.plot(d['time/s'],d[col],color=C[i],ls=['-','--','-.',':'][i],label=label)
 for a,label in zip(ax.ravel(),['Current density (A/cm²)','Minimum cell voltage (V)','Minimum MEA mean (°C)','Maximum pore-ice saturation']): a.set_ylabel(label); a.set_xlabel('Time (s)')
 ax[0,1].axhline(.3,ls=':',color='0.35',lw=.8); ax[1,0].axhline(0,ls=':',color='0.35',lw=.8)
 ins=ax[0,1].inset_axes([.49,.4,.48,.52])
 for i,(key,label) in enumerate(loads):
  d=tr(key); ins.plot(d['time/s'],d['minimum_voltage/V'],color=C[i],ls=['-','--','-.',':'][i])
 ins.set(xlim=(0,6),ylim=(.295,.41)); ins.axhline(.3,ls=':',color='0.35',lw=.7); ins.tick_params(labelsize=6); ins.set_title('Early low-voltage stage',fontsize=6.5)
 fig.legend(*ax[0,0].get_legend_handles_labels(),loc='outside lower center',ncol=4); panels(ax); save(fig,'f03_loading')

 fig,ax=plt.subplots(1,2,figsize=(6.7,2.9),layout='constrained')
 tags=['capacity_-0.1','capacity_0.1','gain_-0.2','gain_-0.1','gain_0.1','gain_0.2','h_-0.1','h_0.1']
 labels=['MEA/plate capacity -10%','MEA/plate capacity +10%','Memory gain -20%','Memory gain -10%','Memory gain +10%','Memory gain +20%','Ambient transfer -10%','Ambient transfer +10%']
 r=old('Q2_零起点推荐复核')['result']
 for a,col,label in zip(ax,['time_s','min_voltage_V'],['Startup time (s)','Minimum voltage (V)']):
  a.scatter([old('备选扰动_'+t)['result'][col] for t in tags],range(8),color=C[0]); a.axvline(r[col],color='0.5',ls='--'); a.set_xlabel(label); a.set_yticks(range(8),labels if a is ax[0] else ['']*8); a.invert_yaxis()
 panels(ax); save(fig,'f04_sensitivity')

 fig,ax=plt.subplots(1,2,figsize=(6.7,2.8),layout='constrained')
 for a,key,title in zip(ax,['E1_04_formal_uniform_cooperative_refined_4','正式_新边界_低温差备选'],['Uniform, 125 W','End-weighted, 50.65 W']): temps(a,tr(key)); a.set_title(title)
 fig.legend(*ax[0].get_legend_handles_labels(),loc='outside lower center',ncol=3); panels(ax); save(fig,'f05_heating')

 fig,ax=plt.subplots(1,3,figsize=(6.7,2.85),layout='constrained')
 for i in range(1,6):
  out=old(f'E3_allocation_{i}'); r=out['result']; z=out['task']['parameters']
  ax[0].plot(range(1,6),[z[0],z[1],z[2],z[1],z[0]],'o-',color=C[i-1],label=f'A{i}',ms=3)
  ax[1].plot(i,r['time_s'],'o',color=C[i-1]); ax[2].plot(i,r['max_delta_T_C'],'o',color=C[i-1])
 ax[0].set(xlabel='Cell index',ylabel='Heater density (W/cm²)',xticks=range(1,6)); ax[0].legend(ncol=2)
 for a,label in zip(ax[1:],['Startup time (s)','Maximum MEA spread (°C)']): a.set_xticks(range(1,6),[f'A{i}' for i in range(1,6)]); a.set(xlabel='Allocation',ylabel=label)
 panels(ax); save(fig,'f06_allocation')

 fig,ax=plt.subplots(2,3,figsize=(6.7,4.7),layout='constrained')
 for i,key in enumerate(FB):
  d=tr(key); t=d['time/s']; on=old(key)['task']['parameters'][4]; end=t.iloc[-1]
  temps(ax[0,i],d); ax[0,i].set_title(NAMES[i]); ax[0,i].axvline(on,color='0.5',ls=':')
  temps(ax[1,i],d); ax[1,i].set_xlim(on-.5,end+.1); selected=t>=on-.5
  cols=[d[f'cell_{k}_temperature/C'] for k in [1,2,3]]; ax[1,i].set_ylim(min(float(c[selected].min()) for c in cols)-.3,max(float(c[selected].max()) for c in cols)+.3)
  ax[1,i].axvline(on,color='0.5',ls=':'); ax[1,i].set_xlabel('Time (s), final interval')
 fig.legend(*ax[0,0].get_legend_handles_labels(),loc='outside lower center',ncol=3); panels(ax); save(fig,'f07_precooling')

 fig,ax=plt.subplots(2,3,figsize=(6.7,4.6),layout='constrained')
 for i,(key,suffix) in enumerate(zip(FB,SUFFIX)):
  df=tr(key); do=tr('同开启同功率开环_'+suffix); on=old(key)['task']['parameters'][4]
  for d,c,label in [(df,C[0],'Feedback'),(do,C[1],'Open loop')]:
   power=25*sum(d[f'cell_{k}_heating_power_density/W_cm2'] for k in range(1,6)); ax[0,i].step(d['time/s'],power,where='pre',color=c,label=label); ax[1,i].plot(d['time/s'],d['cumulative_auxiliary_energy/J'],color=c)
  for a in ax[:,i]: a.set_xlim(on-.15,max(df['time/s'].iloc[-1],do['time/s'].iloc[-1])+.05); a.set_xlabel('Startup time (s)')
  ax[0,i].set(title=NAMES[i],ylabel='Total heater power (W)'); ax[1,i].set_ylabel('Auxiliary energy (J)')
  delta=old(key)['result']['total_energy_J']-old('同开启同功率开环_'+suffix)['result']['total_energy_J']; ax[1,i].text(.04,.89,f'ΔE = {delta:+.3f} J',transform=ax[1,i].transAxes,fontsize=7)
 fig.legend(*ax[0,0].get_legend_handles_labels(),loc='outside lower center',ncol=2); panels(ax); save(fig,'f08_timing')

 fig,ax=plt.subplots(1,2,figsize=(6.7,2.9),layout='constrained')
 for i,(key,suffix) in enumerate(zip(FB,SUFFIX)):
  for cap in [15,20,25]:
   r=old(key if cap==20 else f'E4_{suffix}_budget_{cap}')['result']; ax[0].plot(cap+(i-1)*.25,r['time_s'],marker='o' if r['success'] else 'x',color=C[i],ms=6,ls='none')
  u=old(['零热无预算细步_0.0125','预冷零热无预算_20','预冷零热无预算_40'][i])['result']; ax[1].scatter(u['charge_C_cm2'],u['time_s'],color=C[i],marker='D',label=NAMES[i])
 ax[0].set(xticks=[15,20,25],xlabel='Fixed-policy charge cap (C/cm²)',ylabel='Termination time (s)',title='Delayed heating at finite charge caps')
 ax[0].legend(handles=[Line2D([],[],marker='o',ls='none',color='0.3',label='Success'),Line2D([],[],marker='x',ls='none',color='0.3',label='Charge stop')])
 ax[1].set(xlabel='Charge at startup (C/cm²)',ylabel='Startup time (s)',title='Zero heating without a charge cap'); ax[1].legend()
 panels(ax); save(fig,'f09_budget')

 fig,ax=plt.subplots(1,3,figsize=(6.7,2.75),layout='constrained')
 for i,(key,suffix) in enumerate(zip(FB,SUFFIX)):
  step=.2 if suffix=='20' else 1.
  for law,c,m in [('feedback',C[0],'o'),('open_loop',C[1],'s')]:
   pairs=[]
   for off in [-step,0,step]:
    r=old((key if law=='feedback' else '同开启同功率开环_'+suffix) if off==0 else f'E2_{suffix}_{law}_{off:+.1f}')['result']; pairs.append((r['time_s'],r['total_energy_J'],off))
   ax[i].plot([p[0] for p in pairs],[p[1] for p in pairs],m+'-',color=c,label=law.replace('_',' '),ms=4)
   if law=='feedback':
    for x,y,off in pairs: ax[i].annotate(f'{off:+g} s',(x,y),xytext=(3,-10),textcoords='offset points',fontsize=6.5)
  ax[i].set(title=NAMES[i],xlabel='Startup time (s)',ylabel='Auxiliary energy (J)'); ax[i].margins(.15)
 fig.legend(*ax[0].get_legend_handles_labels(),loc='outside lower center',ncol=2); panels(ax); save(fig,'f17_onset')

def diagrams():
 fig,a=plt.subplots(figsize=(6.7,3.6)); a.set(xlim=(0,12),ylim=(0,6.4)); a.axis('off')
 a.text(6,6.05,'Five cells in series: common current I(t)',ha='center',fontsize=10)
 blocks=[('Endplate',.8,.7,C[4])]; x=1.5; pos=[]
 for k in range(5):
  blocks.append(('BP',x,.24,'#c3cbd1')); x+=.24; pos.append(x+.6); blocks.append((f'MEA {k+1}',x,1.2,'#d8e9f1')); x+=1.2
 blocks.extend([('BP',x,.24,'#c3cbd1'),('Endplate',x+.24,.7,C[4])])
 for label,x,w,c in blocks:
  a.add_patch(Rectangle((x,2.65),w,1.35,fc=c,ec='#294552',lw=.8)); a.text(x+w/2,3.32,label,ha='center',va='center',rotation=90 if label in ['BP','Endplate'] else 0,fontsize=7.5,color='white' if label=='Endplate' else '#20333c')
 for k,x in enumerate(pos):
  for face in [x-.55,x+.55]: a.annotate('',(face,2.65),(face,1.98),arrowprops=dict(arrowstyle='->',color=C[1],lw=1.4))
  a.text(x,1.67,f'q{k+1}(t)',ha='center',color=C[1])
  if k<4: a.annotate('',(x+1.4,4.3),(x,4.3),arrowprops=dict(arrowstyle='<->',color=C[2],lw=1.4))
 a.text(5.5,4.7,'Shared bipolar plates: heat storage and intercell conduction',ha='center',fontsize=8)
 for x,other in [(1.15,.08),(9.29,10.65)]: a.annotate('',(other,3.3),(x,3.3),arrowprops=dict(arrowstyle='->',color=C[0],lw=1.3))
 a.text(.1,4.05,'Ambient\n−30 °C',fontsize=8); a.text(10.7,4.05,'Ambient\n−30 °C',fontsize=8)
 for j,(label,thickness) in enumerate(zip(['aGDL','aCL','Membrane','cCL','cGDL'],[150,3,12,11,150])):
  x=3.3+j*1.08; a.add_patch(Rectangle((x,.48),1.08,.65,fc=['#d8e9f1','#b9d2bc','#eee1b7','#b9d2bc','#d8e9f1'][j],ec='#476171',lw=.7))
  a.text(x+.54,.79,f'{label}\n{thickness} μm',ha='center',va='center',fontsize=7)
 a.text(6,.15,'MEA layer detail (not to scale); heaters act at both exterior MEA faces',ha='center',fontsize=7.5)
 save(fig,'f10_structure')

 fig,a=plt.subplots(figsize=(6.7,4)); a.set(xlim=(0,10),ylim=(0,7)); a.axis('off')
 def box(x,y,w,h,text,color='#e7eff4'):
  a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.08',fc=color,ec='#476171',lw=.9)); a.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=7)
 def arrow(p,q): a.annotate('',q,p,arrowprops=dict(arrowstyle='->',color='#476171',lw=1.2))
 box(.35,5.6,2.6,.85,'Accepted state at tₙ\nT, water, ice, vapor, Q, p')
 box(3.7,5.6,2.6,.85,'Current input j(t)\nAlign step with switches')
 box(7.05,5.6,2.6,.85,'Heater command qₖ(tₙ)\nBase, gate and feedback','#faead8')
 box(3.7,3.93,2.6,.95,'Implicit water-state update\nReaction source, transport\nand accepted latent heat')
 box(3.7,2.35,2.6,.95,'Voltage and reaction heat\nLoading-memory update\nJ(1.48 − Vₖ)')
 box(3.7,.78,2.6,.95,'Implicit temperature update\n(C + Δt K) Tⁿ⁺¹ = RHS\nReevaluate Vₖ')
 box(7.05,.78,2.6,.95,'Terminal event?\nT target / voltage / ice / Q\nLocalize first crossing','#e5efe5')
 box(.35,.78,2.6,.95,'Accept state and integrals\nUpdate backward rates\nProceed to tₙ₊₁')
 for p,q in [((2.95,6.02),(3.62,6.02)),((6.38,6.02),(6.97,6.02)),((5,5.52),(5,4.96)),((5,3.85),(5,3.38)),((5,2.27),(5,1.81)),((6.38,1.22),(6.97,1.22)),((1.65,1.81),(1.65,5.52))]: arrow(p,q)
 a.plot([8.35,8.35,6.6,6.6],[5.52,2,2,1.6],color=C[1],lw=1); arrow((6.6,1.6),(6.38,1.6))
 a.plot([8.35,8.35,1.65,1.65],[.70,.10,.10,.70],color='#476171',lw=1); arrow((1.65,.70),(1.65,.76))
 a.text(5,.18,'No event: accept and continue',ha='center',fontsize=6.5)
 a.text(.75,3.4,'Continue',rotation=90,fontsize=8); a.text(8.35,.40,'Event: localize and stop',ha='center',fontsize=6.5)
 save(fig,'f11_flow')

def revision_figures():
 pairs=pd.read_csv(REV/'resolution_differences.csv')
 fig,ax=plt.subplots(3,3,figsize=(6.7,6.65),layout='constrained')
 nominal={label:old(f'E3_allocation_{1 if label=="A1" else 5}')['result'] for label in ['A1','A5']}
 for i,label in enumerate(['A1','A5']):
  rr=[nominal[label]]+[new(f'T_{label}_{dt:g}')['result'] for dt in [.0125,.00625]]
  for a,col in zip(ax[0],['time_s','total_energy_J','max_delta_T_C']): a.plot([.025,.0125,.00625],[r[col] for r in rr],'o-',color=C[i],label=label,ms=4)
 for i,label in enumerate(['A5-A1','FC_FB-OL','P20_FB-OL','P40_FB-OL']):
  d=pairs[(pairs.comparison==label)&(pairs.grid=='baseline')].sort_values('dt',ascending=False)
  for a,col in zip(ax[1 if i==0 else 2],['delta_time_s','delta_energy_J','delta_spread_C']): a.plot(d.dt,d[col],marker='o',color=C[i],ls=['-','--','-.',':'][i],ms=3,label=label)
 for a,label in zip(ax[0],['Startup time (s)','Auxiliary energy (J)','Maximum MEA spread (°C)']): a.set_ylabel(label)
 for a,label in zip(ax[1],['A5 − A1: Δtime (s)','A5 − A1: Δenergy (J)','A5 − A1: Δspread (°C)']): a.set_ylabel(label)
 for a,label in zip(ax[2],['FB − OL: Δtime (s)','FB − OL: Δenergy (J)','FB − OL: Δspread (°C)']): a.set_ylabel(label); a.axhline(0,color='0.6',lw=.6)
 for a in ax.ravel(): a.set_xlabel('Outer step (s)'); a.set_xticks([.00625,.0125,.025],['.00625','.0125','.025']); a.tick_params(axis='x',labelsize=7)
 ax[0,0].legend(); fig.legend(*ax[2,0].get_legend_handles_labels(),loc='outside lower center',ncol=3); panels(ax); save(fig,'f02_verification')

 fig,ax=plt.subplots(1,3,figsize=(6.7,2.9),layout='constrained')
 for i,label in enumerate(['A1','A5']):
  d=nt(f'T_{label}_0.0125'); ax[0].plot(d['time/s'],d['left_endplate_temperature/C'],color=C[i],label=label); ax[1].plot(d['time/s'],d['left_endplate_heat_flow/W'],color=C[i]); ax[2].plot(d['time/s'],d['left_endplate_heat_input/J']+d['right_endplate_heat_input/J'],color=C[i])
 for a,label in zip(ax,['Endplate temperature (°C)','One-end heat flow (W)','Heat entering both endplates (J)']): a.set(xlabel='Time (s)',ylabel=label)
 ax[0].legend(); panels(ax); save(fig,'f12_endplate')

 variants=['equal_beta','capacity_half','capacity_1p5','coupling_low','coupling_high','ambient_half','ambient_1p5']
 labels=['Nominal','Equal β = 1','End capacity ×0.5','End capacity ×1.5','End k ×0.5','End k ×2','Ambient h ×0.5','Ambient h ×1.5']
 fig,ax=plt.subplots(1,2,figsize=(6.7,3.6),layout='constrained')
 for i,label in enumerate(['A1','A5']):
  rr=[nominal[label]]+[new(f'B_{v}_{label}')['result'] for v in variants]
  for a,col in zip(ax,['time_s','max_delta_T_C']):
   a.plot([r[col] for r in rr],np.arange(8)+(i-.5)*.1,'o',color=C[i],label=label,ms=4)
   for j,r in enumerate(rr):
    if not r['success']: a.plot(r[col],j+(i-.5)*.1,'x',color=C[i],ms=7)
 ax[0].set_yticks(range(8),labels); ax[1].set_yticks(range(8),['']*8)
 for a,label in zip(ax,['Termination time (s)','Maximum MEA spread (°C)']): a.invert_yaxis(); a.set_xlabel(label)
 ax[0].legend(); panels(ax); save(fig,'f13_mechanism')

 resources=pd.read_csv(REV/'startup_resources.csv'); use=resources[resources.strategy.isin(['Preheat','Uniform125','End50','Delayed'])]
 fig,ax=plt.subplots(1,3,figsize=(6.7,3),layout='constrained')
 for a,col,label in zip(ax,['auxiliary_J','hydrogen_mg','output_J'],['Auxiliary input (J)','Stoichiometric H₂ (mg)','Startup electrical output (J)']): a.bar(range(len(use)),use[col],color=C[:len(use)],width=.65); a.set_xticks(range(len(use)),['Preheat','Uniform','End','Delayed'],rotation=30,ha='right'); a.set_ylabel(label)
 panels(ax); save(fig,'f14_resources')

 fig,ax=plt.subplots(2,2,figsize=(6.7,4.5),layout='constrained')
 for i,label in enumerate(['Preheat','Uniform125','End50','Delayed']):
  d=nt('D_'+label+'_operation')
  for a,col in zip(ax.ravel(),['minimum_voltage/V','minimum_temperature/C','max_pore_ice_saturation','cumulative_output_energy/J']): a.plot(d['time/s'],d[col],color=C[i],ls=['-','--','-.',':'][i],label=label)
 for a,label in zip(ax.ravel(),['Minimum cell voltage (V)','Minimum MEA mean (°C)','Maximum pore-ice saturation','Electrical output (J)']): a.set(xlabel='Time after startup (s)',ylabel=label)
 ax[1,0].set_yscale('log'); ax[0,0].axhline(.3,color='0.5',ls=':',lw=.8); ax[0,1].axhline(0,color='0.5',ls=':',lw=.8)
 fig.legend(*ax[0,0].get_legend_handles_labels(),loc='outside lower center',ncol=4); panels(ax); save(fig,'f15_operation')

 fig,ax=plt.subplots(1,3,figsize=(6.7,2.9),layout='constrained')
 for i,(label,key,suffix) in enumerate(zip(STATES,FB,SUFFIX)):
  rr=[old(key)['result'],old('去电压反馈_'+suffix)['result'],old('去变化率反馈_'+suffix)['result']]
  deltas=[r['total_energy_J']-rr[0]['total_energy_J'] for r in rr]
  deltas.append(new('S_'+label+'_FB')['result']['total_energy_J']-new('T_'+label+'_FB_0.0125')['result']['total_energy_J'])
  ax[i].bar(range(4),deltas,color=C[:4]); ax[i].set_xticks(range(4),['Full','No voltage','No rate','Gate + base'],rotation=35,ha='right'); ax[i].set(title=NAMES[i],ylabel='Energy change from full law (J)')
 panels(ax); save(fig,'f16_simplification')

if __name__=='__main__':
 base_figures(); diagrams()
 if '--base-only' not in sys.argv: revision_figures()
 print('Generated publication figures in',FIG)
