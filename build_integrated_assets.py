"""Integrated main-text figures from saved observations and simulation histories."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import build_revision_assets as b
ROOT=b.ROOT; C=b.C; H=ROOT/'program_event_v2/results/handover'
POL=['off','fixed30','fixed50','gate50']
PC=['#555555',C[0],C[1],C[2]]
PL=['Heater off','Fixed 30 W','Fixed 50 W','Gate, ≤50 W']
LS=[':','--','-.','-']
LABELS=['Preheat','Uniform125','End50','Delayed']

def htrace(label,policy):
 return b.nt('D_'+label+'_operation') if policy=='off' else pd.read_csv(H/f'H_{label}_{policy}.csv')

def figures():
 pairs=pd.read_csv(b.REV/'resolution_differences.csv')
 fig,ax=plt.subplots(2,3,figsize=(6.7,4.65),layout='constrained')
 for i,label in enumerate(['A5-A1','FC_FB-OL','P20_FB-OL','P40_FB-OL']):
  row=0 if i==0 else 1
  d=pairs[(pairs.comparison==label)&(pairs.grid=='baseline')].sort_values('dt')
  for a,col in zip(ax[row],['delta_time_s','delta_energy_J','delta_spread_C']):
   name=['A5 − A1','Fully cooled: FB − OL','20 min: FB − OL','40 min: FB − OL'][i]
   a.plot(d.dt,d[col],marker='o',ms=3,color=C[i],ls=['-','--','-.',':'][i],label=name)
   doubled=pairs[(pairs.comparison==label)&(pairs.grid=='doubled')]
   if len(doubled): a.plot(doubled.dt,doubled[col],marker='D',ms=5,mfc='white',mec=C[i],ls='none')
 for row,who in zip(ax,['A5 − A1','FB − OL']):
  for a,var,unit in zip(row,['time','energy','spread'],['s','J','°C']):
   a.set(xlabel='Outer step (s)',ylabel=f'{who}: Δ{var} ({unit})')
   a.set_xticks([.00625,.0125,.025],['.00625','.0125','.025']); a.tick_params(axis='x',labelsize=7)
 ax[0,0].legend(fontsize=7)
 handles=ax[1,0].get_legend_handles_labels()[0]+[Line2D([],[],marker='D',mfc='white',mec='0.3',ls='none',label='54-volume grid')]
 fig.legend(handles=handles,loc='outside lower center',ncol=2); b.panels(ax); b.save(fig,'f02_verification')

 fig,ax=plt.subplots(2,2,figsize=(6.7,4.9),layout='constrained')
 for a,label in zip(ax[0],['A1','A5']):
  full=b.tr('E3_allocation_'+('1' if label=='A1' else '5'))
  d=full.iloc[np.unique(np.r_[np.arange(0,len(full),8),len(full)-1])]
  vals=np.array([d[f'cell_{k}_temperature/C'].to_numpy() for k in range(1,6)])
  im=a.pcolormesh(d['time/s'],range(1,6),vals,shading='nearest',cmap='cividis',vmin=-30,vmax=12,rasterized=True,edgecolors='none',linewidth=0,antialiased=False)
  a.set(xlabel='Startup time (s)',ylabel='Cell position',yticks=range(1,6),title=label+' at 50 W')
 fig.colorbar(im,ax=ax[0],label='MEA mean temperature (°C)',shrink=.85)
 for i in range(1,6):
  z=b.old(f'E3_allocation_{i}')['task']['parameters']
  ax[1,0].plot(range(1,6),[z[0],z[1],z[2],z[1],z[0]],'o-',ms=3,color=C[i-1],label=f'A{i}')
 ax[1,0].set(xlabel='Cell position',ylabel='Heater density (W/cm²)',xticks=range(1,6)); ax[1,0].legend(ncol=2)
 for i,label in enumerate(['A1','A5']):
  d=b.tr('E3_allocation_'+('1' if label=='A1' else '5'))
  for k,ls,where in [(1,'-','end'),(3,'--','center')]:
   ax[1,1].plot(d['time/s'],d[f'cell_{k}_temperature/C'],color=C[i],ls=ls,label=f'{label}, {where}')
 ax[1,1].set(xlabel='Startup time (s)',ylabel='MEA mean temperature (°C)')
 ax[1,1].axhline(0,color='0.5',ls=':',lw=.8); ax[1,1].legend(fontsize=7)
 b.panels(ax)
 with plt.rc_context({'savefig.dpi':600}): b.save(fig,'f06_allocation')

 fig,ax=plt.subplots(3,3,figsize=(6.7,6.3),layout='constrained')
 for i,(key,suffix) in enumerate(zip(b.FB,b.SUFFIX)):
  df=b.tr(key); do=b.tr('同开启同功率开环_'+suffix)
  tf=df['time/s'].to_numpy(); to=do['time/s'].to_numpy(); times=np.union1d(tf,to)
  on=b.old(key)['task']['parameters'][4]; end=min(tf[-1],to[-1]); last=max(tf[-1],to[-1])
  def power(d,t):
   native=d['time/s'].to_numpy()
   values=25*d[[f'cell_{k}_heating_power_density/W_cm2' for k in range(1,6)]].sum(axis=1).to_numpy()
   idx=np.minimum(np.searchsorted(native,t,side='left'),len(native)-1)
   return np.where((t>=on)&(t<native[-1]),values[idx],0)
  dp=power(df,times)-power(do,times)
  de=np.interp(times,tf,df['cumulative_auxiliary_energy/J'])-np.interp(times,to,do['cumulative_auxiliary_energy/J'])
  shared=(times>=on)&(times<end)
  ax[0,i].step(times[shared],dp[shared],where='pre',color=C[i])
  ax[0,i].set(xlim=(on,end),title=b.NAMES[i],ylabel='FB − OL power (W)')
  tail=times>=end-.05
  ax[1,i].step(1000*(times[tail]-end),dp[tail],where='pre',color=C[i])
  ax[1,i].set(xlim=(-50,1000*(last-end)+5),xlabel='Time from first endpoint\n(ms)',ylabel='Endpoint Δpower (W)')
  ax[1,i].axvline(0,color='0.4',ls='--',lw=.7)
  ax[2,i].plot(times,de,color=C[i]); ax[2,i].set(xlim=(on,last+.01),ylabel='FB − OL energy (J)')
  ax[2,i].text(.05,.76,f'Final ΔE = {de[-1]:+.3f} J',transform=ax[2,i].transAxes,fontsize=7,va='top')
  for a in ax[:,i]: a.axhline(0,color='0.5',ls=':',lw=.7)
  for a in ax[[0,2],i]: a.set_xlabel('Startup time (s)')
 b.panels(ax); b.save(fig,'f08_timing')

 resource=pd.read_csv(b.REV/'startup_resources.csv').iloc[:4]
 fig,ax=plt.subplots(1,2,figsize=(6.7,3.4),layout='constrained')
 x=np.arange(4); names=['Preheat\n125 W','Uniform\n125 W','End\n50 W','Delayed']
 ax[0].bar(x,resource.auxiliary_J,color=C[0],label='Auxiliary electricity')
 ax[0].bar(x,resource.chemical_thermoneutral_J,bottom=resource.auxiliary_J,color=C[1],label='Thermoneutral reaction input')
 ax[0].bar(x,-resource.output_J,color=C[2],label='Electrical output (subtracted)')
 ax[0].plot(x,resource.net_input_J,'D',color=C[3],ms=5,label='Model net input')
 ax[0].axhline(0,color='0.5',lw=.7); ax[0].set(ylabel='Startup energy (J)',xticks=x,xticklabels=names)
 ax[1].bar(x,resource.hydrogen_mg,color=C[:4]); ax[1].set(ylabel='Stoichiometric H₂ (mg)',xticks=x,xticklabels=names)
 fig.legend(*ax[0].get_legend_handles_labels(),loc='outside lower center',ncol=2)
 b.panels(ax); b.save(fig,'f14_resources')

 fig,ax=plt.subplots(3,2,figsize=(6.7,6.4),layout='constrained')
 for a,label,title in zip(ax[:2].ravel(),LABELS,['Preheat, 125 W','Uniform startup, 125 W','End startup, 50 W','Delayed startup']):
  for policy,c,ls,pname in zip(POL,PC,LS,PL):
   d=htrace(label,policy); a.plot(d['time/s'],d['minimum_temperature/C'],color=c,ls=ls,label=pname)
  a.set(xlabel='Time after startup (s)',ylabel='Minimum MEA mean (°C)',title=title)
  a.axhline(0,color='0.4',ls=':',lw=.8)
 for a,label,title in zip(ax[2],['Uniform125','Delayed'],['Uniform: near-freezing detail','Delayed: near-freezing detail']):
  for policy,c,ls in zip(POL[2:],PC[2:],LS[2:]):
   d=htrace(label,policy); a.plot(d['time/s'],d['minimum_temperature/C'],color=c,ls=ls)
  a.set(xlabel='Time after startup (s)',ylabel='Minimum MEA mean (°C)',title=title,ylim=(-1.2,.3),xlim=(0,30))
  a.axhline(0,color='0.4',ls=':',lw=.8)
 fig.legend(*ax[0,0].get_legend_handles_labels(),loc='outside lower center',ncol=4)
 b.panels(ax); b.save(fig,'f15_operation')

 fig,ax=plt.subplots(3,2,figsize=(6.7,6.1),layout='constrained')
 for i,label in enumerate(['End50','Delayed']):
  off=htrace(label,'off')
  for policy,c,ls,pname in zip(POL,PC,LS,PL):
   d=htrace(label,policy); t=d['time/s']
   q=25*d[[f'cell_{k}_heating_power_density/W_cm2' for k in range(1,6)]].sum(axis=1)
   ax[0,i].step(t,q,where='pre',color=c,ls=ls,label=pname)
   ax[1,i].plot(t,d['max_pore_ice_saturation'],color=c,ls=ls)
   delta=d['cumulative_output_energy/J']-np.interp(t,off['time/s'],off['cumulative_output_energy/J'])
   ax[2,i].plot(t,delta,color=c,ls=ls)
  ax[0,i].set_title('End startup, 50 W' if label=='End50' else 'Delayed startup')
 for row,label in zip(ax,['Hold heater power (W)','Maximum pore-ice saturation','Output gain (J)']):
  for a in row: a.set(xlabel='Time after startup (s)',ylabel=label)
 fig.legend(*ax[0,0].get_legend_handles_labels(),loc='outside lower center',ncol=4)
 b.panels(ax); b.save(fig,'f18_handover')

 h=pd.read_csv(H/'summary.csv')
 use=h[(h.policy=='gate50')&(h.dt==.025)].set_index('startup').loc[['D_'+x for x in LABELS]]
 starts=[b.new('D_'+label)['result'] for label in LABELS]
 totalchem=np.array([1.48*125*r['charge_C_cm2'] for r in starts])+use.chemical_J.to_numpy()
 net=use.cumulative_auxiliary_J.to_numpy()+totalchem-use.cumulative_output_J.to_numpy()
 fig,ax=plt.subplots(1,2,figsize=(6.7,3.3),layout='constrained')
 ax[0].bar(x,[r['total_energy_J'] for r in starts],color=C[0],label='Startup auxiliary')
 ax[0].bar(x,use.hold_auxiliary_J,bottom=[r['total_energy_J'] for r in starts],color=C[1],label='Hold auxiliary')
 ax[1].bar(x,net,color=C[4]); ax[1].set_ylabel('Startup + 30 s model net input (J)')
 for a in ax:
  a.set_xticks(x,names)
  heights=use.cumulative_auxiliary_J.to_numpy() if a==ax[0] else net
  for j,good in enumerate(use.warm): a.plot(j,heights[j]+170,'o' if good else 'x',color=C[2] if good else '#a83434',ms=6)
 ax[0].set_ylabel('Auxiliary electrical input (J)')
 handles=ax[0].get_legend_handles_labels()[0]+[Line2D([],[],marker='o',ls='none',color=C[2],label='Maintains all MEAs ≥0 °C'),Line2D([],[],marker='x',ls='none',color='#a83434',label='Returns below 0 °C')]
 fig.legend(handles=handles,loc='outside lower center',ncol=2)
 b.panels(ax); b.save(fig,'f19_handover_resources')
 from build_review_assets import figures as review_figures
 review_figures()

if __name__=='__main__':
 b.base_figures(); b.diagrams(); b.revision_figures(); figures()
 print('Generated integrated main-text figures.')

