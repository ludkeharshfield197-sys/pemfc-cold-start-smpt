"""Revised scientific figures from the finite revision experiments."""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import build_revision_assets as b
from build_integrated_assets import htrace,LABELS,POL,PC,LS,PL
ROOT=b.ROOT; R=ROOT/'program_event_v2/results/review_revision'; P=R/'parameters'

def read(name): return pd.read_csv(R/(name+'.csv'))
def output(name): return json.loads((R/(name+'.json')).read_text(encoding='utf-8'))['result']

def beta_pairs():
    rows=[]
    for beta in [1,3,5,7,10]:
        z=[]
        for strategy in ['A1','A5']:
            if beta==1: r=b.new('B_equal_beta_'+strategy)['result']
            elif beta==10: r=b.old('E3_allocation_'+('1' if strategy=='A1' else '5'))['result']
            else: r=output(f'R_beta{beta}_{strategy}_h0025')
            z.append(r)
        rows.append(dict(beta=beta,delta_time=z[1]['time_s']-z[0]['time_s'],
            V1=z[0]['min_voltage_V'],V5=z[1]['min_voltage_V']))
    return pd.DataFrame(rows)

def holding_frame():
    d=pd.read_csv(R/'summary.csv'); rows=d[(d.group=='load')|((d.group=='band')&(d.dt==.025))].copy()
    old=pd.read_csv(ROOT/'program_event_v2/results/handover/summary.csv')
    for label in LABELS:
        for policy,oldpol in [('fixed','fixed50'),('gate','gate50')]:
            r=old[(old.startup=='D_'+label)&(old.policy==oldpol)&(old.dt==.025)].iloc[0]
            row=dict(startup='D_'+label,policy=policy,load=.1401,band=2,min_MEA_C=r.min_MEA_C,
                Eaux_J=r.hold_auxiliary_J,Eout_J=r.output_J,warm=r.warm,completed=r.completed)
            rows=pd.concat([rows,pd.DataFrame([row])],ignore_index=True)
    return rows

def figures():
    fig,ax=plt.subplots(3,2,figsize=(6.7,6.6),layout='constrained')
    for a,label in zip(ax[0],['A1','A5']):
        full=b.tr('E3_allocation_'+('1' if label=='A1' else '5'))
        d=full.iloc[np.unique(np.r_[np.arange(0,len(full),8),len(full)-1])]
        vals=np.array([d[f'cell_{k}_temperature/C'].to_numpy() for k in range(1,6)])
        im=a.pcolormesh(d['time/s'],range(1,6),vals,shading='nearest',cmap='cividis',vmin=-30,vmax=12,rasterized=True,edgecolors='none',linewidth=0)
        a.set(xlabel='Startup time (s)',ylabel='Cell position',yticks=range(1,6),title=label+' at 50 W')
    fig.colorbar(im,ax=ax[0],label='MEA mean temperature (°C)',shrink=.8)
    for i in range(1,6):
        z=b.old(f'E3_allocation_{i}')['task']['parameters']
        ax[1,0].plot(range(1,6),[z[0],z[1],z[2],z[1],z[0]],'o-',ms=3,color=b.C[i-1],label=f'A{i}')
    ax[1,0].set(xlabel='Cell position',ylabel='Heater density (W/cm²)',xticks=range(1,6)); ax[1,0].legend(ncol=2)
    for i,label in enumerate(['A1','A5']):
        d=b.tr('E3_allocation_'+('1' if label=='A1' else '5'))
        for k,ls,where in [(1,'-','end'),(3,'--','center')]:
            ax[1,1].plot(d['time/s'],d[f'cell_{k}_temperature/C'],color=b.C[i],ls=ls,label=f'{label}, {where}')
    ax[1,1].set(xlabel='Startup time (s)',ylabel='MEA mean temperature (°C)'); ax[1,1].axhline(0,color='0.5',lw=.7); ax[1,1].legend(fontsize=6.5)
    for a,key,title in zip(ax[2],['E1_04_formal_uniform_cooperative_refined_4','正式_新边界_低温差备选'],['Uniform cooperative, 125 W','EW50.65, 50.64536 W']):
        b.temps(a,b.tr(key)); a.set_title(title); a.legend(fontsize=6.5)
    b.panels(ax)
    with plt.rc_context({'savefig.dpi':600}): b.save(fig,'f06_allocation')
    fig,ax=plt.subplots(3,2,figsize=(6.7,6.5),layout='constrained')
    d=beta_pairs()
    resolution=pd.read_csv(b.REV/'resolution_differences.csv')
    nominal=resolution[(resolution.comparison=='A5-A1')&(resolution.grid=='baseline')]
    refined=[output(f'R_beta3_{s}_h00125')['time_s'] for s in ['A1','A5']]
    reference=float(nominal[nominal.dt==.025].delta_time_s.iloc[0])
    low=np.full(len(d),reference-float(nominal.delta_time_s.min()))
    high=np.full(len(d),float(nominal.delta_time_s.max())-reference)
    shift=(refined[1]-refined[0])-float(d[d.beta==3].delta_time.iloc[0])
    low[1]=max(0,-shift); high[1]=max(0,shift)
    ax[0,0].errorbar(d.beta,d.delta_time,yerr=np.vstack([low,high]),fmt='o',color=b.C[1],ms=4,capsize=3,
        label='0.025 s; bars: observed time-step span')
    ax[0,0].plot(3,refined[1]-refined[0],'D',mfc='white',mec=b.C[0],ms=5,label='β=3 at 0.0125 s')
    ax[0,0].set(xlabel='End-cell multiplier β',ylabel='A5 − A1 startup time (s)',xticks=[1,3,5,7,10])
    ax[0,0].ticklabel_format(axis='y',style='plain',useOffset=False)
    ax[0,0].text(.98,.98,'● h=0.025 s; ◇ β=3, h=0.0125 s',transform=ax[0,0].transAxes,
        fontsize=6.5,ha='right',va='top')
    ax[0,1].plot(d.beta,d.V1,'o-',color=b.C[0],label='A1'); ax[0,1].plot(d.beta,d.V5,'s--',color=b.C[1],label='A5')
    ax[0,1].set(xlabel='End-cell multiplier β',ylabel='Interval minimum voltage (V)'); ax[0,1].legend()
    tags=['capacity_half','capacity_1p5','coupling_low','coupling_high','ambient_half','ambient_1p5']
    labels=['C ×0.5','C ×1.5','k=7.5','k=30','h=20','h=60']
    for i,strategy in enumerate(['A1','A5']):
        rr=[b.new('B_'+tag+'_'+strategy)['result'] for tag in tags]
        ax[1,0].plot(range(6),[r['time_s'] for r in rr],color=b.C[i],marker='o',label=strategy)
        for j,r in enumerate(rr):
            if r['status']!='success': ax[1,0].plot(j,r['time_s'],'x',color='black',ms=8)
    ax[1,0].set(xticks=range(6),xticklabels=labels,ylabel='Startup / charge-stop time (s)'); ax[1,0].tick_params(axis='x',labelsize=7); ax[1,0].legend()
    for name,label,c,ls in [('D_End50','MEA end heat',b.C[1],'-'),('R_endplate50_start_h0025','Plate heat',b.C[3],'--')]:
        d=b.nt(name) if name=='D_End50' else read(name)
        ax[1,1].plot(d['time/s'],d['minimum_temperature/C'],color=c,ls=ls,label=label+', MEA min')
        ax[1,1].plot(d['time/s'],d['left_endplate_temperature/C'],color=c,ls=':',label=label+', endplate')
    ax[1,1].axhline(0,color='0.4',lw=.8); ax[1,1].set(xlabel='Startup time (s)',ylabel='Temperature (°C)'); ax[1,1].legend(fontsize=6.5)
    for policy,c,ls in [('fixed',b.C[0],'--'),('gate',b.C[2],'-')]:
        d=read('R_endplate50_'+policy+'_j01401_B2_h0025'); t=d['time/s']
        ax[2,0].plot(t,d['minimum_temperature/C'],color=c,ls=ls,label=policy.title())
        q=25*d[[f'cell_{k}_heating_power_density/W_cm2' for k in range(1,6)]].sum(axis=1)
        ax[2,1].plot(t,q,color=c,ls=ls,label=policy.title())
    ax[2,0].axhline(0,color='0.4',lw=.8); ax[2,0].set(xlabel='Time from charge stop (s)',ylabel='Minimum MEA mean (°C)'); ax[2,0].legend()
    ax[2,1].set(xlabel='Time from charge stop (s)',ylabel='Plate heater power (W)')
    b.panels(ax); b.save(fig,'f13_mechanism')

    h=holding_frame(); fig,ax=plt.subplots(2,2,figsize=(6.7,4.9),layout='constrained')
    for i,label in enumerate(LABELS):
        for policy,ls in [('fixed','--'),('gate','-')]:
            z=h[(h.startup=='D_'+label)&(h.policy==policy)&(h.band==2)].sort_values('load')
            for a,field in zip(ax[0],['min_MEA_C','Eaux_J']):
                a.plot(z.load,z[field],color=b.C[i],ls=ls,lw=1.1)
                for _,r in z.iterrows(): a.plot(r.load,r[field],marker='o' if r.warm else 'x',ms=4,color=b.C[i])
        z=h[(h.startup=='D_'+label)&(h.policy=='gate')&(h.load==.1401)].sort_values('band')
        for a,field in zip(ax[1],['min_MEA_C','Eaux_J']):
            a.plot(z.band,z[field],color=b.C[i],lw=1.1)
            for _,r in z.iterrows(): a.plot(r.band,r[field],marker='o' if r.warm else 'x',ms=4,color=b.C[i])
    for a in ax[0]: a.set(xlabel='Operating current (A/cm²)',xticks=[.08,.1401,.20],xticklabels=['.08','.1401','.20'])
    for a in ax[1]: a.set(xlabel='Gate band B (°C)',xticks=[1,2,3])
    for a in ax[:,0]: a.set_ylabel('Full-interval minimum MEA (°C)'); a.axhline(0,color='0.4',lw=.7)
    for a in ax[:,1]: a.set_ylabel('Holding auxiliary electricity (J)')
    inset=ax[1,0].inset_axes([.47,.40,.49,.43])
    for i,label in enumerate(['Preheat','End50']):
        z=h[(h.startup=='D_'+label)&(h.policy=='gate')&(h.load==.1401)].sort_values('band')
        inset.plot(z.band,z.min_MEA_C,'o-',color=b.C[LABELS.index(label)],ms=3)
    inset.axhline(0,color='0.4',lw=.7); inset.set(xlim=(.85,3.15),ylim=(-.008,.025),xticks=[1,2,3])
    inset.tick_params(labelsize=6); inset.set_title('Near-zero means (°C)',fontsize=6.5)
    pre=h[(h.startup=='D_Preheat')&(h.policy=='gate')&(h.load==.1401)&(h.band==1)].iloc[0]
    inset.annotate(f'{pre.min_MEA_C:.4f} °C',xy=(1,pre.min_MEA_C),xytext=(1.5,-.0055),fontsize=6,
        arrowprops=dict(arrowstyle='-',lw=.5,color='0.3'))
    handles=[Line2D([],[],color=b.C[i],label=label.replace('Uniform125','Uniform 125 W').replace('End50','End 50 W')) for i,label in enumerate(LABELS)]
    handles += [Line2D([],[],color='0.4',ls='--',label='Fixed 50 W'),Line2D([],[],color='0.4',ls='-',label='Gate ≤50 W'),
        Line2D([],[],color='0.4',marker='o',ls='',label='Warm interval'),Line2D([],[],color='0.4',marker='x',ls='',label='Subzero interval')]
    fig.legend(handles=handles,loc='outside lower center',ncol=4,fontsize=7)
    b.panels(ax); b.save(fig,'f21_handover_design')

    local=json.loads((P/'local.json').read_text()); cos=pd.read_csv(P/'direction_cosines.csv',index_col=0)
    profiles=[json.loads(x.read_text()) for x in P.glob('profile_*.json')]
    profiles += [dict(json.loads(x.read_text()),fixed_parameter='Qc') for x in (P/'joint').glob('extended_Qc*.json')]
    fig,ax=plt.subplots(3,2,figsize=(6.7,6.4),layout='constrained')
    names=['log₁₀j₀','γC','g','τ','ηc,0','Qc','Qr']; x=np.arange(7)
    ax[0,0].bar(x,local['column_norms'],color=b.C[0]); ax[0,0].set(xticks=x,xticklabels=names,ylabel='Scaled Jacobian column norm')
    im=ax[0,1].imshow(cos,vmin=-1,vmax=1,cmap='coolwarm'); ax[0,1].set(xticks=x,yticks=x,xticklabels=names,yticklabels=names)
    ax[0,1].tick_params(labelsize=7); fig.colorbar(im,ax=ax[0,1],label='Response-direction cosine',shrink=.8)
    for a,key in zip(ax[1],['log10_j0','Qc']):
        z=sorted([v for v in profiles if v['fixed_parameter']==key],key=lambda v:v['value'])
        a.plot([v['value'] for v in z],[v['objective'] for v in z],'o-',color=b.C[1],ms=4)
        a.axhline(local['objective'],color='0.4',ls=':',label='Supplied-vector objective')
        joints=[json.loads(x.read_text()) for x in (P/'joint').glob('joint_seed*.json')]
        best=min(joints,key=lambda x:x['objective'])
        a.plot(best['theta'][0 if key=='log10_j0' else 5],best['objective'],'*',color=b.C[3],ms=9,label='Joint training fit')
        a.set(xlabel='Fixed '+('log₁₀j₀' if key=='log10_j0' else 'Qc (C/cm²)'),ylabel='Refitted residual objective'); a.legend(fontsize=6.5)
    for i,label in enumerate(['-20C','-25C']):
        d=pd.read_csv(P/(label+'_autocorrelation.csv'))
        for a,field in zip(ax[2],['voltage_residual_V','temperature_residual_C']):
            z=d[d.variable==field]; a.plot(z.lag_s,z.acf,color=b.C[i],label=label.replace('C',' °C'))
            a.set(xlabel='Residual lag (s)',ylabel=('Voltage' if field.startswith('voltage') else 'Temperature')+' residual autocorrelation')
            a.axhline(0,color='0.4',lw=.6)
    ax[2,0].legend(); b.panels(ax); b.save(fig,'f20_parameter_analysis')

    # Merge startup and combined-phase resource diagrams into one figure.
    resource=pd.read_csv(b.REV/'startup_resources.csv').iloc[:4]; x=np.arange(4)
    labels=['Preheat','Uniform\n125 W','End\n50 W','Delayed']
    fig,ax=plt.subplots(3,2,figsize=(6.7,7.2),layout='constrained')
    ax[0,0].bar(x,resource.auxiliary_J,color=b.C[0],label='Auxiliary input')
    ax[0,0].bar(x,resource.chemical_thermoneutral_J,bottom=resource.auxiliary_J,color=b.C[1],label='Reaction input')
    ax[0,0].bar(x,-resource.output_J,color=b.C[2],label='Output (subtracted)')
    ax[0,0].plot(x,resource.net_input_J,'D',color=b.C[3],ms=4,label='Model net input')
    ax[0,0].set_ylabel('Startup energy (J)'); ax[0,0].legend(fontsize=6.5,ncol=2,loc='lower left',bbox_to_anchor=(0,1.10))
    ax[0,1].bar(x,resource.hydrogen_mg,color=b.C[:4]); ax[0,1].set_ylabel('Startup reaction H₂ (mg)')
    old=pd.read_csv(ROOT/'program_event_v2/results/handover/summary.csv')
    z=old[(old.policy=='gate50')&(old.dt==.025)].set_index('startup').loc[['D_'+v for v in LABELS]]
    ax[1,0].bar(x,resource.auxiliary_J,color=b.C[0],label='Startup'); ax[1,0].bar(x,z.hold_auxiliary_J,bottom=resource.auxiliary_J,color=b.C[1],label='30 s gate holding')
    net=resource.net_input_J.to_numpy()+z.interval_net_J.to_numpy(); ax[1,1].bar(x,net,color=b.C[4])
    ax[1,0].set_ylabel('Combined auxiliary input (J)'); ax[1,1].set_ylabel('Combined model net input (J)'); ax[1,0].legend(fontsize=6.5)
    for a,height in zip(ax[1],[z.cumulative_auxiliary_J,net]):
        for i,good in enumerate(z.warm): a.plot(i,height.iloc[i]+150 if hasattr(height,'iloc') else height[i]+150,'o' if good else 'x',color='black',ms=5)
    for a in ax[:2].ravel(): a.set_xticks(x,labels); a.tick_params(axis='x',labelsize=7)
    from summarize_onset_parameters import comparison_tables
    _, paired=comparison_tables(); positions=np.arange(3)
    for a,field,ylabel in [(ax[2,0],'onset_delta_Enet_J','FC_FB − Uniform125 net input (J)'),
                           (ax[2,1],'feedback_relative_pct','100 × (FB − OL) / OL auxiliary (%)')]:
        bars=a.bar(positions,paired[field],color=b.C[:3],width=.55)
        a.axhline(0,color='0.35',lw=.8)
        a.set(xticks=positions,xticklabels=['Nominal','Joint-fit','Qc = 30'],ylabel=ylabel)
        a.tick_params(axis='x',labelsize=7)
        for bar,value in zip(bars,paired[field]):
            a.annotate(f'{value:+.2f}' if field=='onset_delta_Enet_J' else f'{value:+.3f}',
                       (bar.get_x()+bar.get_width()/2,value),xytext=(0,4 if value>0 else -4),
                       textcoords='offset points',ha='center',va='bottom' if value>0 else 'top',fontsize=7)
        a.margins(y=.22)
    b.panels(ax); b.save(fig,'f14_resources')

if __name__=='__main__': figures()
