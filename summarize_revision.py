"""Summarize the finite experiment batch and save reusable research table fragments."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
REV=ROOT/'program_event_v2/results/revision'
CONFIG=json.loads((ROOT/'program_event_v2/revision/experiment_config.json').read_text(encoding='utf-8'))
SRC=CONFIG['baseline_sources']
SUP=REV/'tables'; SUP.mkdir(exist_ok=True)
def old(key): return json.loads((ROOT/SRC[key]).read_text(encoding='utf-8'))
def new(name): return json.loads((REV/(name+'.json')).read_text(encoding='utf-8'))
def texnum(x,digits=3): return f'{float(x):.{digits}f}'
def table(caption,label,headers,rows,alignment=None):
 alignment=alignment or 'l'+'r'*(len(headers)-1)
 return '\\begin{table}[htbp]\\centering\\small\n\\caption{'+caption+'}\\label{'+label+'}\n\\setlength{\\tabcolsep}{4pt}\n\\begin{tabular}{'+alignment+'}\\toprule\n'+' & '.join(headers)+'\\\\\\midrule\n'+'\n'.join(' & '.join(str(v) for v in row)+'\\\\' for row in rows)+'\n\\bottomrule\\end{tabular}\n\\end{table}\n'

cases=[]
for case in CONFIG['cases']:
 out=new(case['name']); cases.append(out)
 if case['group']=='continuation' and out['result']['success']: cases.append(new(case['name']+'_operation'))
rows=[]
for out in cases:
 t=out['task']; r=out['result']
 rows.append(dict(name=out['name'],group=out['group'],strategy=t.get('strategy',out.get('strategy','')),
   variant=t.get('variant','nominal'),dt=t['dt'],counts=str(t.get('counts',[8,3,4,4,8])),
   status=r['status'],time_s=r['time_s'],energy_J=r['total_energy_J'],charge_C_cm2=r['incremental_charge_C_cm2'],
   output_J=r['output_energy_J'],hydrogen_mg=r['hydrogen_mg'],spread_C=r['max_delta_T_C'],
   min_voltage_V=r['min_voltage_V'],final_min_T_C=min(r['final_T_C']),final_ice=r['final_max_pore_ice_saturation'],
   wall_s=out['wall_s']))
pd.DataFrame(rows).to_csv(REV/'summary.csv',index=False)

basekeys={'A1':'E3_allocation_1','A5':'E3_allocation_5','FC_FB':'E1_05_formal_q4_None','P20_FB':'E1_06_formal_q4_20','P40_FB':'E1_07_formal_q4_40',
 'FC_OL':'同开启同功率开环_None','P20_OL':'同开启同功率开环_20','P40_OL':'同开启同功率开环_40'}
def at(label,dt,grid='baseline'):
 if grid=='doubled': return new('X_'+label)['result']
 return old(basekeys[label])['result'] if dt==.025 else new(f'T_{label}_{dt:g}')['result']
pairs=[]
for grid,steps,comparisons in [('baseline',[.025,.0125,.00625],[('A5-A1','A5','A1'),('FC_FB-OL','FC_FB','FC_OL'),('P20_FB-OL','P20_FB','P20_OL'),('P40_FB-OL','P40_FB','P40_OL')]),('doubled',[.0125],[('A5-A1','A5','A1'),('FC_FB-OL','FC_FB','FC_OL')])]:
 for dt in steps:
  for name,a,b in comparisons:
   ra,rb=at(a,dt,grid),at(b,dt,grid)
   pairs.append(dict(comparison=name,dt=dt,grid=grid,delta_time_s=ra['time_s']-rb['time_s'],
    delta_energy_J=ra['total_energy_J']-rb['total_energy_J'],delta_energy_percent=100*(ra['total_energy_J']/rb['total_energy_J']-1),delta_spread_C=ra['max_delta_T_C']-rb['max_delta_T_C']))
pd.DataFrame(pairs).to_csv(REV/'resolution_differences.csv',index=False)

resources=[]
for label in ['Preheat','Uniform125','End50','Delayed']:
 r=new('D_'+label)['result']; q=r['charge_C_cm2']; chem=5*25*q*1.48
 resources.append(dict(strategy=label,time_s=r['time_s'],auxiliary_J=r['total_energy_J'],charge_C_cm2=q,
  hydrogen_mg=r['hydrogen_mg'],chemical_thermoneutral_J=chem,output_J=r['output_energy_J'],net_input_J=r['total_energy_J']+chem-r['output_energy_J']))
for label in basekeys:
 r=new('T_'+label+'_0.00625')['result']; q=r['charge_C_cm2']; chem=5*25*q*1.48
 resources.append(dict(strategy=label,time_s=r['time_s'],auxiliary_J=r['total_energy_J'],charge_C_cm2=q,
  hydrogen_mg=r['hydrogen_mg'],chemical_thermoneutral_J=chem,output_J=r['output_energy_J'],net_input_J=r['total_energy_J']+chem-r['output_energy_J']))
pd.DataFrame(resources).to_csv(REV/'startup_resources.csv',index=False)

matched=[]
for state,label in [('FC','Fully cooled'),('P20','20 min'),('P40','40 min')]:
 a,b=at(state+'_FB',.00625),at(state+'_OL',.00625)
 matched.append([label,texnum(b['total_energy_J'],2),texnum(a['total_energy_J'],2),texnum(100*(a['total_energy_J']/b['total_energy_J']-1)),texnum(a['time_s']-b['time_s'],5),texnum(a['max_delta_T_C']-b['max_delta_T_C'])])
(SUP/'matched_table.tex').write_text(table('Matched-window feedback effects at a 0.00625 s step. Differences are feedback minus open loop.','tab:matched',['State','$E_{OL}$ (J)','$E_{FB}$ (J)','$\\Delta E$ (\\%)','$\\Delta t$ (s)','$\\Delta T_{max}$ ($^{\\circ}$C)'],matched),encoding='utf-8')

resrows=[]
for r in resources[:4]:
 resrows.append([{'Preheat':'Pure preheat','Uniform125':'Uniform 125 W','End50':'End-only 50 W','Delayed':'Delayed feedback'}[r['strategy']],texnum(r['time_s'],2),texnum(r['auxiliary_J'],1),texnum(r['charge_C_cm2'],3),texnum(r['hydrogen_mg'],2),texnum(r['output_J'],1)])
(SUP/'resource_table.tex').write_text(table('Startup resource accounting for four representative interventions. The integration endpoint is the startup event, including the load switch for preheating.','tab:resources',['Strategy','$t_s$ (s)','$E_{aux}$ (J)','$Q$ (C cm$^{-2}$)','$m_{H_2}$ (mg)','$E_{out}$ (J)'],resrows),encoding='utf-8')

oprows=[]
for label in ['Preheat','Uniform125','End50','Delayed']:
 r=new('D_'+label+'_operation')['result']
 oprows.append([{'Preheat':'Pure preheat','Uniform125':'Uniform 125 W','End50':'End-only 50 W','Delayed':'Delayed feedback'}[label],{'operation_complete':'complete','voltage_limit':'voltage stop','ice_limit':'ice stop'}.get(r['status'],r['status'].replace('_',' ')),texnum(r['min_voltage_V']),texnum(min(r['final_T_C']),2),f"{r['final_max_pore_ice_saturation']:.2e}",texnum(r['output_energy_J'],1)])
(SUP/'operation_table.tex').write_text(table('Common-load continuation: 0.1401 A cm$^{-2}$ for 30 s, with auxiliary heating off. Temperature and ice columns are endpoint values; voltage is the interval minimum.','tab:operation',['Startup policy','Outcome','$V_{min}$ (V)','$T_{min,f}$ ($^{\\circ}$C)','$s_{ice,f}$','$E_{out}$ (J)'],oprows,'llrrrr'),encoding='utf-8')

simprows=[]
for state,label in [('FC','Fully cooled'),('P20','20 min'),('P40','40 min')]:
 r=new('S_'+state+'_FB')['result']; b=at(state+'_FB',.0125)
 simprows.append([label,texnum(r['total_energy_J']-b['total_energy_J']),texnum(r['time_s']-b['time_s'],5),texnum(r['max_delta_T_C']-b['max_delta_T_C']),texnum(r['total_energy_J'],2)])
(SUP/'simplification_table.tex').write_text(table('Base-and-temperature-gate law compared with the full feedback law at a 0.0125 s step. The window and base vector are unchanged.','tab:simple',['State','$\\Delta E$ (J)','$\\Delta t$ (s)','$\\Delta T_{max}$ ($^{\\circ}$C)','$E_{simple}$ (J)'],simprows),encoding='utf-8')

# Save reusable table fragments; the manuscript generator integrates scientific rows by topic.
lines=['\\begingroup\\scriptsize\\setlength{\\tabcolsep}{3pt}\\begin{longtable}{llrrrrr}','\\caption{Complete additional experiment outcomes. Time is seconds, energies are joules, charge is C cm$^{-2}$, and temperature spread is Celsius.}\\label{tab:allrevision}\\\\','\\toprule Case & Status & $t$ & $E_{aux}$ & $Q$ & $E_{out}$ & $\\Delta T_{max}$\\\\\\midrule\\endfirsthead','\\toprule Case & Status & $t$ & $E_{aux}$ & $Q$ & $E_{out}$ & $\\Delta T_{max}$\\\\\\midrule\\endhead','\\bottomrule\\endfoot']
for row in rows:
 name=row['name'].replace('_','\\_'); status={'success':'success','operation_complete':'complete','charge_limit':'charge stop','voltage_limit':'voltage stop','ice_limit':'ice stop'}.get(row['status'],row['status'].replace('_',' '))
 lines.append(' & '.join([name,status,texnum(row['time_s'],3),texnum(row['energy_J'],3),texnum(row['charge_C_cm2'],3),texnum(row['output_J'],3),texnum(row['spread_C'],3)])+'\\\\')
lines.append('\\end{longtable}\\endgroup')
(SUP/'additional_results.tex').write_text('\n'.join(lines),encoding='utf-8')
lines=['\\begingroup\\footnotesize\\setlength{\\tabcolsep}{3pt}\\begin{longtable}{llrrrr}','\\caption{Strategy differences across integration resolutions. A5--A1 compares two continuous 50 W allocations. FB--OL uses identical preset windows.}\\\\','\\toprule Comparison & Grid & $\\Delta t$ (s) & $\\Delta E$ (J) & $\\Delta E$ (\\%) & $\\Delta T_{max}$ ($^{\\circ}$C)\\\\\\midrule\\endfirsthead','\\toprule Comparison & Grid & $\\Delta t$ (s) & $\\Delta E$ (J) & $\\Delta E$ (\\%) & $\\Delta T_{max}$ ($^{\\circ}$C)\\\\\\midrule\\endhead','\\bottomrule\\endfoot']
for p in pairs:
 lines.append(' & '.join([p['comparison'].replace('_','\\_'),('27' if p['grid']=='baseline' else '54')+f" CV, {p['dt']:g} s",texnum(p['delta_time_s'],6),texnum(p['delta_energy_J'],5),texnum(p['delta_energy_percent'],4),texnum(p['delta_spread_C'],5)])+'\\\\')
lines.append('\\end{longtable}\\endgroup')
(SUP/'resolution_table.tex').write_text('\n'.join(lines),encoding='utf-8')
print(pd.DataFrame(pairs).to_string(index=False))
print(pd.DataFrame(resources[:4]).to_string(index=False))
print('Completed',len(cases),'additional simulations; wall seconds',round(sum(x['wall_s'] for x in cases),1))
