"""Generate the single scientific manuscript from actual completed experiments."""
from pathlib import Path
import json,re
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
BACK=ROOT/'build/handover_originals'
SRC=json.loads((ROOT/'records/current_result_sources.json').read_text(encoding='utf-8'))
CONF=json.loads((ROOT/'program_event_v2/revision/experiment_config.json').read_text(encoding='utf-8'))
REV=ROOT/'program_event_v2/results/revision'; H=ROOT/'program_event_v2/results/handover'
original=(BACK/'manuscript/main.tex').read_text(encoding='utf-8')
index={r['id']:json.loads((ROOT/r['source']).read_text(encoding='utf-8')) for r in json.loads((ROOT/'records/manuscript_result_index.json').read_text(encoding='utf-8'))}
def baseline(out):
 r=out['result']
 r['output_energy_J']=1.48*125*r['charge_C_cm2']-sum(r['cell_reaction_J'])
 return out

def old(key): return baseline(json.loads((ROOT/SRC[key]).read_text(encoding='utf-8')))

index={k:baseline(v) for k,v in index.items()}
def new(key): return json.loads((REV/(key+'.json')).read_text(encoding='utf-8'))
def num(value,n=3): return f'{float(value):.{n}f}'
def status(r): return {'success':'success','charge_limit':'charge stop','voltage_limit':'voltage stop','operation_complete':'complete'}[r['status']]
def table(caption,label,headers,rows,align=None,long=False,size='footnotesize'):
 align=align or ('l'+'r'*(len(headers)-1))
 head=' & '.join(headers)+r'\\'
 body='\n'.join(' & '.join(str(x) for x in row)+r'\\' for row in rows)
 if long:
  return r'\begingroup'+'\\'+size+r'\setlength{\tabcolsep}{3pt}\begin{longtable}{'+align+'}\n'+r'\caption{'+caption+r'}\label{'+label+r'}\\'+'\n'+r'\toprule '+head+r'\midrule\endfirsthead'+'\n'+r'\toprule '+head+r'\midrule\endhead'+'\n'+r'\bottomrule\endfoot'+'\n'+body+'\n'+r'\end{longtable}\endgroup'+'\n'
 return r'\begin{table}[htbp]\centering'+'\\'+size+'\n'+r'\caption{'+caption+r'}\label{'+label+'}\n'+r'\setlength{\tabcolsep}{3pt}\begin{tabular}{'+align+r'}\toprule'+'\n'+head+r'\midrule'+'\n'+body+'\n'+r'\bottomrule\end{tabular}\end{table}'+'\n'
def figure(name,caption,label): return r'\fig{'+name+'}{'+caption+'}{'+label+'}\n'
def resource(r):
 q=r['charge_C_cm2']; e=r['total_energy_J']; out=r['output_energy_J']
 chem=1.48*125*q; h2=125*q/(2*96485)*2016
 return [num(r['time_s'],2),num(q,3),num(e,2),num(h2,3),num(chem,2),num(out,2),num(e+chem-out,2)]
units=[r'$t_s$ (s)',r'$Q$ (C cm$^{-2}$)',r'$E_{aux}$ (J)',r'$m_{H_2}$ (mg)',r'$E_{chem,tn}$ (J)',r'$E_{out}$ (J)',r'$E_{net}$ (J)']
def chunk(a,b): return original[original.index(a):original.index(b)]

def main():
 pre=original[:original.index(r'\begin{abstract}')]
 pre=re.sub(r'\\title\{.*?\}',lambda m:r'\title{Charge-constrained cold starts of PEM fuel-cell stacks: Spatial heating, onset timing and thermal handover}',pre)
 pre=pre.replace(r'\usepackage{caption}',r'\usepackage{caption,placeins}')
 pre=pre.replace(r'\begin{document}',r'\renewcommand{\topfraction}{0.92}\renewcommand{\bottomfraction}{0.85}\renewcommand{\textfraction}{0.06}\renewcommand{\floatpagefraction}{0.75}'+'\n'+r'\begin{document}')
 abstract=r"""\begin{abstract}
Auxiliary heating decisions influence both fuel-cell cold startup and the thermal state delivered to subsequent operation. This study separates spatial allocation, onset timing, feedback modulation and heater handover under a finite reaction-charge budget. A through-plane water--ice--electrochemical model is coupled to five cells, shared bipolar plates and separate endplates. Single-cell response comparisons and time/grid refinements establish the numerical comparison. At a common 50 W total power, end-directed heating reduces startup time and auxiliary electricity by 3.43\% and narrows the maximum cell temperature spread from 11.42 to 3.58 $^{\circ}$C. Endplate-property and uniform concentration-loss comparisons identify the thermal demand behind this response. Delayed heating lowers auxiliary input while increasing reaction hydrogen, electrical output and waiting time; the thermoneutral net-input balance reveals a much smaller energy difference from early uniform heating. Matched-window feedback changes auxiliary energy by about half a percent, and a base-and-temperature-gate law closely reproduces the full controller. After startup, immediate heater removal completes the common low-load interval but allows renewed subzero MEA temperatures. Following end-directed startup, simple temperature-gated holding maintains all MEA means above freezing with 27.7\% less holding electricity than fixed 50 W heating. The same handover permits transient cooling after delayed or uniform startup. These results connect heater selection to reaction resources, controller complexity and the thermal state needed for warm operation.
\end{abstract}
\begin{keyword}
PEM fuel cell \sep cold start \sep coupled simulation \sep spatial heating \sep reaction charge \sep thermal handover
\end{keyword}
\end{frontmatter}
"""
 intro=chunk(r'\section{Introduction}',r'\section{Coupled model')
 needle='Stack geometry introduces a further decision:'
 intro=intro.replace(needle,r'Haddad et al. \cite{haddad} describe an equivalent-circuit PEMFC model coupling diffusion, membrane hydration, temperature and electrical losses, with static/dynamic tests on a 50 W eight-cell unit. Their driving-cycle response emphasizes the value of coupled states for control. Cold startup additionally requires phase-change inventories, a reaction-resource limit and explicit stack-end temperatures.'+'\n\n'+needle)
 intro=intro.replace('A common charge cap makes the waiting-time cost of delaying heat explicit.','A common charge cap makes the waiting-time cost of delaying heat explicit. After the first startup crossing, the same saved state is transferred to a common load to compare immediate heater removal, fixed holding and simple temperature-gated holding.')
 intro=intro.replace('A common-load continuation connects the startup target to the state delivered for subsequent operation.','Common-load handover experiments test whether the startup endpoint supports a complete low-load interval and whether it keeps all MEA means above freezing.')
 intro=intro.replace(r'Study & Model scale & Validation/comparison & Control variables & Comparison condition\\\midrule',r'Study & Model scale & Validation/comparison & Control variables & Comparison condition\\\midrule'+'\n'+r'Haddad et al. \cite{haddad} & Equivalent circuit; eight-cell test unit & Static/dynamic tests at 50 W & Hydrogen flow; temperature and hydration inputs & Dynamic electrical response and driving cycles\\')
 intro=intro.replace('Water, temperature, loading memory and residual ice are carried into a common post-start operating interval.','The handover comparison extends this separation to warm operation by carrying temperature, water, ice and electrochemical memory from the actual startup endpoints.')
 model=chunk(r'\section{Coupled model',r'\section{Response validation')
 model+=r"""\subsection{Calculation workflow and implementation}
The executable calculation proceeds through the following sequence; Fig.~\ref{fig:flow} shows the coupled state updates.
\begin{quote}\small
\textbf{Calculation procedure.} (1) Read geometry, material coefficients, calibrated electrochemical parameters and the scenario settings. Initialize the thermal and water fields and loading memory. (2) Align the next step with prescribed current/heater switches and the charge deadline. Evaluate the current and heater command from the accepted state. (3) Advance water, vapor and ice; evaluate voltage and reaction heat; solve the coupled thermal network implicitly and reevaluate voltage. (4) Localize the earliest startup, voltage, pore-ice or charge event. Otherwise accept the step, update state rates and accumulate electrical/thermal quantities. (5) Save the actual startup state, apply the common load, reset interval integrals and continue for 30 s with the selected holding law.
\end{quote}
The calculation and post-processing use Python 3.12.3, NumPy 1.26.4, SciPy 1.13.1, pandas 2.3.3, Numba 0.60.0 and Matplotlib 3.11.1. JSON stores exact settings and accepted endpoint states; CSV stores trajectories. The experiment drivers reuse completed baseline files, evaluate the finite comparisons, and regenerate figures and tables from the saved output.
"""
 validation=chunk(r'\section{Response validation',r'\section{Simulation design')
 validation=validation.replace(r'\section{Response validation and numerical resolution}',r'\section{Calibration, validation and numerical resolution}')
 single=[
 [r'$-20\,^{\circ}$C','.200','3.789','4.65','.00839','.0107','.02307'],
 [r'$-20\,^{\circ}$C','.100','3.817','--','.00959','--','.02301'],
 [r'$-20\,^{\circ}$C','.050','3.857','--','.01313','--','.02299'],
 [r'$-25\,^{\circ}$C','.200','13.756','15.71','.11644','.1496','.02369'],
 [r'$-25\,^{\circ}$C','.100','13.442','--','.10540','--','.02364'],
 [r'$-25\,^{\circ}$C','.050','13.288','--','.09990','--','.02361']]
 start=validation.index(r'\begin{table}'); stop=validation.index(r'\end{table}',start)+len(r'\end{table}')
 validation=validation[:start]+table('Full-record single-cell errors and temporal refinements with fixed calibrated parameters. RMSE is given for the observation-step calculation; the peak ice column is local ice-volume fraction.','tab:validation',['Condition','$h$ (s)','V MAE (mV)','V RMSE (mV)',r'T MAE ($^{\circ}$C)',r'T RMSE ($^{\circ}$C)','Peak ice'],single,'lrrrrrr')+validation[stop:]
 validation=validation.replace('Voltage MAEs are 3.79 and 13.76 mV',r'Table~\ref{tab:validation} includes all observation-step and refined responses. Voltage MAEs are 3.79 and 13.76 mV')
 validation=validation.replace('All curves use the baseline 27-volume MEA grid; doubled-grid differences are listed in the supplementary material.','Circles use 27 MEA volumes; open diamonds use 54 volumes at 0.0125 s. The upper row isolates A5--A1, while the lower row gives matched feedback--open-loop differences.')
 validation=validation.replace('The upper row shows A1 and A5 startup time, auxiliary energy and maximum temperature spread. The middle row shows A5 minus A1. The lower row shows feedback minus matched open loop for the three initial states.','Panels show differences in startup time, auxiliary energy and maximum temperature spread.')
 validation=validation.replace('Complete tables are supplied in the supplementary material.','')
 validation=validation.replace('Supplementary Table S2',r'Table~\ref{tab:resolutiondiff}')
 validation=validation.replace('Detailed single-cell refinements, loading refinements and complete strategy differences are given in the supplementary material.',r'Tables~\ref{tab:validation}, \ref{tab:loading} and \ref{tab:resolutiondiff} give the corresponding refinements.')
 vstart=validation.index('Calculations use Python')
 validation=validation[:vstart]
 # Old paragraphs referring to supplemental rows are replaced by direct body cross-references.
 validation=validation.replace('absolute values and differences are listed in the supplementary material','absolute values and differences are listed in Tables~\\ref{tab:resolutionabs} and \\ref{tab:resolutiondiff}')
 pairs=pd.read_csv(REV/'resolution_differences.csv')
 drows=[]
 for _,r in pairs.iterrows():
  name={'A5-A1':'A5--A1','FC_FB-OL':'FC: FB--OL','P20_FB-OL':'20 min: FB--OL','P40_FB-OL':'40 min: FB--OL'}[r.comparison]
  drows.append([name,str(27 if r.grid=='baseline' else 54),f"{r['dt']:g}",num(r.delta_time_s,6),num(r.delta_energy_J,4),num(r.delta_energy_percent,4),num(r.delta_spread_C,4)])
 validation+=table('Differences between matched strategies across time and spatial resolutions. FC denotes the fully cooled state; FB and OL denote feedback and matched open loop.','tab:resolutiondiff',['Pair','MEA CV','$h$ (s)',r'$\Delta t_s$ (s)',r'$\Delta E_{aux}$ (J)',r'$\Delta E_{aux}$ (\%)',r'$\Delta T_{max}$ ($^{\circ}$C)'],drows,'lrrrrrr',long=True)
 grid=pd.read_csv(REV/'summary.csv'); grows=[]
 for _,r in grid[grid.group.isin(['time','space'])].iterrows():
  name=r.strategy.replace('_',': ')
  grows.append([name,str(sum(json.loads(r.counts))),f"{r['dt']:g}",num(r.time_s,3),num(r.energy_J,3),num(r.charge_C_cm2,3),num(r.output_J,3),num(r.spread_C,3)])
 validation+=table('Absolute startup outcomes for temporal and doubled-grid comparisons. Baseline 0.025 s outcomes appear in the corresponding allocation and onset/resource tables. All rows reach startup.','tab:resolutionabs',['Strategy','MEA CV','$h$ (s)','$t_s$ (s)','$E_{aux}$ (J)','$Q$ (C cm$^{-2}$)','$E_{out}$ (J)',r'$\Delta T_{max}$ ($^{\circ}$C)'],grows,'lrrrrrrr',long=True)
 hh=pd.read_csv(H/'summary.csv')
 refinement=[]
 for label in ['Preheat','End50','Delayed']:
  for dt in [.0125]:
   r=hh[(hh.startup=='D_'+label)&(hh.policy=='gate50')&(hh['dt']==dt)].iloc[0]
   refinement.append([label,f'{dt:g}',num(r.min_MEA_C,6),num(r.hold_auxiliary_J,3),num(r.output_J,3),'yes' if r.warm else 'no'])
 validation+=r'Key holding-law trajectories are refined at the same inherited startup state. Table~\ref{tab:holdgrid} preserves the warm-interval classification; the pure-preheat minimum remains positive at both steps.'+'\n'
 validation+=table(r'Temperature-gated handover refinement, with 50 W maximum end heating and a 30 s common-load interval. Baseline 0.025 s values appear in Tables~\ref{tab:handover} and \ref{tab:holdresources}. Minimum temperature includes the inherited endpoint.','tab:holdgrid',['Startup','$h$ (s)',r'$T_{min,int}$ ($^{\circ}$C)','$E_{hold}$ (J)','$E_{out,op}$ (J)','Warm throughout'],refinement,'lrrrrl')
 scenarios=chunk(r'\section{Simulation design',r'\section{Results and discussion}')
 scenarios=scenarios.replace(r'\section{Simulation design and resource accounting}',r'\section{Simulation scenarios and comparison design}')
 scenarios=scenarios.replace('Retained initial sensible heat is described by the specified thermal initial state.','Initial sensible heat is specified by the thermal initial state.')
 scenarios=scenarios.replace('The coefficients are supplied scenario settings. The project identifies their preceding candidate configurations but does not contain the original gain-search trajectory or bounds; the present study fixes the coefficients and evaluates them directly.','All gain vectors are prescribed fixed scenario settings and are evaluated without refitting.')
 scenarios=scenarios.replace('Their complete parameters are in the supplementary material.',r'The conditioned cases use $p(0)=0$: constant current is 0.5 A cm$^{-2}$; the ramp rises from 0.294359 to 0.5 A cm$^{-2}$ over 1.658156 s; the staircase starts at 0.322511 and reaches 0.463307 and 0.5 A cm$^{-2}$ after intervals 0.05 and 0.965215 s. Rest-to-load versions use $p(0)=gj(0)$. The zero-start ramp begins at zero current and therefore has $p(0)=0$.')
 scenarios=scenarios.replace('Their complete 13 coefficients are listed in Supplementary Table S1 and stored at machine precision in JSON.',r'Table~\ref{tab:coefficients} specifies all 13 settings and their units; JSON retains machine precision.')
 params=[r'$q_a$',r'$q_b$',r'$q_c$',r'$s_b$',r'$t_{on}$',r'$t_{off}$',r'$\delta_T$',r'$c_T$',r'$c_{\dot T}$',r'$c_V$',r'$c_{\dot V}$',r'$d_{spread}$',r'$c_{spread}$']
 punits=[r'W cm$^{-2}$']*3+['1','s','s',r'$^{\circ}$C',r'W cm$^{-2}$',r'W cm$^{-2}$ s $^{\circ}$C$^{-1}$',r'W cm$^{-2}$ V$^{-1}$',r'W cm$^{-2}$ s V$^{-1}$',r'$^{\circ}$C',r'$^{\circ}$C$^{-1}$']
 vec=[CONF['strategies'][s+'_FB']['parameters'] for s in ['FC','P20','P40']]
 coeff=table(r'Complete startup feedback settings. The temperature-lag term is normalized by 10 $^{\circ}$C; the gate band is 2 $^{\circ}$C.','tab:coefficients',['Parameter','Unit','Fully cooled','20 min','40 min'],[[p,u]+[num(z[i],6) for z in vec] for i,(p,u) in enumerate(zip(params,punits))],'llrrr')
 marker=r'\subsection{Resource definitions and common-load continuation}'
 scenarios=scenarios.replace(marker,coeff+'\n'+marker)
 scenarios=scenarios.replace("Supplementary resource tables report these components separately and $E_{aux}+E_{chem,tn}-E_{out}$ as net modeled input.",r'The model net input is defined by\begin{equation}E_{net}=E_{aux}+E_{chem,tn}-E_{out}.\label{eq:net}\end{equation}Tables~\ref{tab:allocationresources}, \ref{tab:startupresources} and \ref{tab:refinedresources} report the components with a common endpoint.')
 begin=scenarios.index('Four representative interventions are continued after startup:')
 scenarios=scenarios[:begin]+r"""Four startup interventions supply the actual handover states: 34 s pure preheating at 125 W, uniform cooperative heating at 125 W, A5 end heating at 50 W, and fully cooled delayed feedback. Pure preheating includes its 0.1401 A cm$^{-2}$ load switch. The subsequent load is 0.1401 A cm$^{-2}$ for 30 s, using the existing low-load operating case; temperature, mobile water, vapor, ice, cumulative charge and loading memory are inherited without reinitialization. An upward current change applies the same polarization-jump rule as during startup. Only the interval clock and resource integrals restart. The startup charge cap ends at handover, while accumulated charge remains in the electrochemical conditioning. Every complete interval adds 4.203 C cm$^{-2}$; voltage $V_k\ge0.3$ V and local pore-ice saturation below 0.99 remain operating constraints.

The holding policies apply to the two end cells: immediate heater removal, fixed total power of 30 or 50 W, and temperature-gated holding with a 50 W maximum. The observed one-end heat withdrawal near startup is about 30 W, motivating a 30 W lower comparison and the existing two-end actuator limit of 50 W. The fixed command is $(P/50,0,0,0,P/50)$ W cm$^{-2}$. The simple holding law is
\begin{equation}
q_{hold,k}=q_{max,k}\operatorname{clip}\!\left[\frac{2\,^{\circ}{\rm C}-\bar\vartheta_k}{2\,^{\circ}{\rm C}},0,1\right],
\qquad \bm q_{max}=(1,0,0,0,1)\ {\rm W\,cm^{-2}}.
\label{eq:holding}
\end{equation}
It provides full end power at 0 $^{\circ}$C and removes that power at 2 $^{\circ}$C. The gate follows the current accepted temperature, using the 0.025 s control step. These fixed choices compare heater removal, a lower fixed input, full available end input and a simple state-dependent taper.

Two operating outcomes are evaluated separately: completing the full 30 s interval without a voltage/ice termination, and keeping all five MEA means nonnegative throughout that interval. The first subzero time is interpolated between the accepted samples enclosing the first downward zero crossing; crossings within the initial step are reported as less than 0.025 s. Temperature minima, maximum local ice, maximum cell spread, minimum voltage and output are interval quantities. Holding electricity and incremental charge use their own interval integrals, and startup-plus-operation resources sum the two phases.
"""

 results=r"\section{Results and discussion}"+'\n'
 def section(title):
  return '\n'+r'\FloatBarrier\subsection{'+title+'}\n'
 results+=section('Spatial allocation at equal total power')
 results+=r"""At 50 W total heating, directing power toward the end cells accelerates startup and reduces the intercell temperature spread. A1 starts at 80.70 s and A5 at 77.93 s; A5 saves 138.21 J of auxiliary electricity and reduces the maximum spread from 11.42 to 3.58 $^{\circ}$C. The common-power comparison fixes current, initial state, total power and charge cap, so the difference identifies where heat is supplied. Table~\ref{tab:allocationresources} gives all five symmetric allocations and their resource balances.

"""
 arows=[]
 for i in range(1,6):
  r=old(f'E3_allocation_{i}')['result']; arows.append([f'A{i}']+resource(r)+[num(r['min_voltage_V'],3),num(r['max_delta_T_C'],2)])
 r=old('正式_新边界_低温差备选')['result']
 arows.append(['EW50.65']+resource(r)+[num(r['min_voltage_V'],3),num(r['max_delta_T_C'],2)])
 results+=table('Spatial-allocation outcomes. A1--A5 each supply 50 W; EW50.65 is the distinct 50.65 W end-weighted reference. All reach startup.','tab:allocationresources',['Case']+units+['$V_{min}$ (V)',r'$\Delta T_{max}$ ($^{\circ}$C)'],arows,'lrrrrrrrrr')
 results+=figure('f06_allocation','Equal-power spatial allocation at a 0.025 s step. The A1/A5 position--time MEA temperature maps share one color scale and terminate at their own startup events. Lower panels give all five power vectors and end/center trajectories.','fig:allocation')
 results+=r"""Uniform A1 heating leaves the end cells as the limiting cold locations while the interior cells accumulate surplus sensible heat. A5 compensates this end demand and brings the end and central means closer together. The end-cell concentration multiplier contributes to their voltage response, but the thermal contrast persists when that multiplier is uniform, as shown next.

Uniform cooperative heating at 125 W instead reaches startup at 30.33 s with a 19.15 $^{\circ}$C maximum spread. Its faster warm-up uses a larger total power. The 50.65 W end-weighted reference reaches startup at 77.09 s and a 3.51 $^{\circ}$C spread; its different power is stated separately from A5. Figure~\ref{fig:interventions} compares their cell histories, and Table~\ref{tab:startupresources} gives the uniform intervention's full resources.

"""
 results+=figure('f05_heating','Cell temperature histories for uniform 125 W cooperative heating and the separate 50.65 W end-weighted reference, using the 0.025 s step. Symmetric cell pairs share a curve.','fig:interventions')
 results+=section('Endplate heat uptake and its physical causes')
 results+=r"""End-directed heating meets a sustained boundary heat demand rather than simply correcting an empirical voltage penalty. At startup the endplates remain near $-11.2\,^{\circ}$C for both 50 W allocations. Their combined heat uptake is about 3.83 kJ; near the crossing, each end MEA transfers approximately 30 W to its plate (Fig.~\ref{fig:endplate}). The exterior plate is therefore a cold thermal store even when every MEA mean first reaches zero. End heating counteracts this withdrawal at the locations where it acts.

"""
 results+=figure('f12_endplate','Endplate temperature, heat flow and cumulative uptake for A1/A5 at a 0.0125 s step. Heat flow is positive from MEA into endplate; cumulative uptake sums both symmetric ends. Each history ends at its own startup event.','fig:endplate')
 brows=[]
 variants=[('equal_beta',r'All $\beta_k=1$'),('capacity_half',r'$C_e\times0.5$'),('capacity_1p5',r'$C_e\times1.5$'),('coupling_low',r'$k_e=7.5$'),('coupling_high',r'$k_e=30$'),('ambient_half',r'$h_e=20$'),('ambient_1p5',r'$h_e=60$')]
 for tag,label in variants:
  for strategy in ['A1','A5']:
   r=new('B_'+tag+'_'+strategy)['result']
   brows.append([label,strategy,status(r),num(r['time_s'],2),num(r['total_energy_J'],2),num(r['charge_C_cm2'],3),num(r['output_energy_J'],2),num(r['max_delta_T_C'],2),num(min(r['final_T_C']),2)])
 results+=table('Endplate and concentration-loss contrasts, one change at a time. Conductivity units are W m$^{-1}$ K$^{-1}$ and exterior-transfer units are W m$^{-2}$ K$^{-1}$. The final minimum MEA mean is evaluated at startup or charge termination.','tab:physical',['Change','Case','Outcome','$t$ (s)','$E_{aux}$ (J)','$Q$ (C cm$^{-2}$)','$E_{out}$ (J)',r'$\Delta T_{max}$ ($^{\circ}$C)',r'$T_{min,end}$ ($^{\circ}$C)'],brows,'lllrrrrrr',long=True)
 results+=r"""Using the same concentration-loss coefficient in all five cells leaves the A5 time advantage at 2.76 s. Halving endplate capacity shortens A1/A5 startup to 58.56/56.11 s. Increasing capacity by 50\% makes both reach the 20 C cm$^{-2}$ cap before startup, with final end means of $-1.28/-0.65\,^{\circ}$C. Lower end conductivity reduces heat uptake during MEA warm-up and gives 70.32/67.74 s; doubling it yields 86.28/83.48 s. Exterior exchange changes the time less over the selected range. A5 remains faster in every successful pair. These contrasts identify endplate storage and the MEA--endplate thermal path as the main sources of the local demand; exterior loss adds to that demand.

"""
 results+=figure('f13_mechanism','A1/A5 response to one physical change at a time, with a 0.025 s step. Equal concentration coefficients leave the thermal network unchanged. Capacity changes endplate specific heat; conductivity changes the series resistance. Crosses denote charge termination.','fig:mechanism')
 results+=section('Heating onset trades auxiliary demand for reaction resources')
 results+=r"""Delaying heating lets reaction heat supply more of the warm-up, lowering auxiliary electricity while consuming additional charge and time. The fully cooled feedback case starts at 92.50 s with 2130.79 J of auxiliary input; the 20 min and 40 min precooled states start at 96.29 and 95.77 s with 16.46 and 1062.53 J. Their prescribed initial fields and heating windows differ, so these numbers describe the complete interventions. Matching each window to its open-loop counterpart separates the smaller feedback increment in Section~\ref{sec:feedback}.

"""
 results+=figure('f07_precooling','Delayed-feedback trajectories for fully cooled, 20 min and 40 min precooling states. The lower row expands onset to startup, resolving actual heating and the limiting cell means. Dotted vertical lines mark onset; horizontal lines mark zero MEA temperature. Step: 0.025 s.','fig:precooling')
 orows=[]
 for n in range(8,20):
  o=index[f'R{n:02d}']; r=o['result']; name=o['task']['name']; state='FC' if 'None' in name else ('20 min' if '_20_' in name else '40 min')
  policy='FB' if 'feedback' in name else 'OL'; offset=name.rsplit('_',1)[1]
  orows.append([state,policy,offset]+[num(r[k],p) for k,p in [('time_s',2),('total_energy_J',2),('charge_C_cm2',3),('min_voltage_V',3),('max_delta_T_C',2)]])
 results+=table(r'Onset-neighborhood outcomes at unchanged cutoff and gains, with a 0.025 s step. All twelve cases reach startup. Zero-offset outcomes appear in Table~\ref{tab:startupresources}.','tab:onset',['State','Law',r'$\delta t_{on}$ (s)','$t_s$ (s)','$E_{aux}$ (J)','$Q$ (C cm$^{-2}$)','$V_{min}$ (V)',r'$\Delta T_{max}$ ($^{\circ}$C)'],orows,'lllrrrrr')
 results+=r"""Advancing fully cooled onset by 1 s saves about 0.87 s but adds approximately 16 J of auxiliary input. The 20 min state is close to the charge deadline: a 0.2 s onset change shifts startup by about 0.19 s. With 10\% greater exterior transfer, the nominal 20/40 min controls reach the charge cap at end means near $-1.16/-0.54\,^{\circ}$C. A 2 s advance restores startup, using 81.91/1252.39 J. Table~\ref{tab:heattransfer} also reports the same advance at nominal exchange, preserving the separate roles of the initial precooling field and the startup heat loss.

"""
 results+=figure('f17_onset','Onset offsets at unchanged cutoff, power vector and gains. Each point is a completed feedback or matched open-loop run at a 0.025 s step. Zero offset identifies the scenario setting.','fig:onset')
 erows=[]
 for suffix,state in zip(['None','20','40'],['FC','20 min','40 min']):
  r=old('第四问换热增加10百分比_'+suffix)['result']
  erows.append([state,'1.1','0',status(r)]+[num(r[k],p) for k,p in [('time_s',2),('total_energy_J',2),('charge_C_cm2',3)]]+[num(min(r['final_T_C']),2),num(r['max_delta_T_C'],2)])
 for suffix,state in [('20','20 min'),('40','40 min')]:
  for hi in [False,True]:
   r=old(f'提前两秒反馈_{suffix}_{hi}')['result']
   erows.append([state,'1.1' if hi else '1.0','-2',status(r)]+[num(r[k],p) for k,p in [('time_s',2),('total_energy_J',2),('charge_C_cm2',3)]]+[num(min(r['final_T_C']),2),num(r['max_delta_T_C'],2)])
 results+=table('Exterior-transfer and onset contrasts. The multiplier acts during precooling and startup; onset offsets use the original scenario clock.','tab:heattransfer',['State','$h/h_0$',r'$\delta t_{on}$ (s)','Outcome','$t$ (s)','$E_{aux}$ (J)','$Q$ (C cm$^{-2}$)',r'$T_{min,end}$ ($^{\circ}$C)',r'$\Delta T_{max}$ ($^{\circ}$C)'],erows,'llllrrrrr')
 results+=section('Charge budgets determine feasible waiting time')
 results+=r"""A finite charge budget turns passive waiting into a constrained startup choice. At 15 C cm$^{-2}$ all three nominal delayed controls terminate before reaching the temperature target. The 20 and 25 C cm$^{-2}$ cases share the successful endpoints in Table~\ref{tab:startupresources}: raising a cap above an already successful endpoint does not change the trajectory. With the cap removed, zero auxiliary heat eventually starts all three initial states, but the fully cooled case requires 80.21 C cm$^{-2}$ and 297.37 s. Figure~\ref{fig:budget} separates these unrestricted references from the fixed-budget heater comparisons.

"""
 qrows=[]
 for suffix,state in zip(['None','20','40'],['FC','20 min','40 min']):
  r=old('E4_'+suffix+'_budget_15')['result']
  qrows.append([state,'Delayed FB','15',status(r)]+[num(r[k],p) for k,p in [('time_s',2),('total_energy_J',2),('charge_C_cm2',3),('min_voltage_V',3),('max_delta_T_C',2)]])
 for i,state in enumerate(['FC','20 min','40 min']):
  r=index[f'B{12+i:02d}']['result']
  qrows.append([state,'Zero heater',r'$\infty$',status(r)]+[num(r[k],p) for k,p in [('time_s',2),('total_energy_J',2),('charge_C_cm2',3),('min_voltage_V',3),('max_delta_T_C',2)]])
 results+=table(r'Charge-limited failures and unrestricted zero-heater references at a 0.025 s step. Caps are in C cm$^{-2}$. Finite-cap nominal successes are reported once in Table~\ref{tab:startupresources}.','tab:budget',['State','Law','Cap','Outcome','$t$ (s)','$E_{aux}$ (J)','$Q$ (C cm$^{-2}$)','$V_{min}$ (V)',r'$\Delta T_{max}$ ($^{\circ}$C)'],qrows,'llllrrrrr')
 results+=figure('f09_budget','Finite charge caps and unrestricted zero-heater references in separate panels. Circles denote startup and crosses charge termination. Colors identify initial thermal states. Each reference is integrated to its own terminal event.','fig:budget')
 results+=section('Matched-window feedback and controller simplification')
 results+=r"""\label{sec:feedback}
Matching the base vector, onset and cutoff leaves a small feedback contribution. At the finest time step, feedback changes auxiliary input by $-10.093$ J in the fully cooled state, $+0.083$ J after 20 min and $-4.963$ J after 40 min; the corresponding time changes are $+0.020$, $-0.001$ and $+0.024$ s. The complete resolution differences in Table~\ref{tab:resolutiondiff} preserve these signs. Figure~\ref{fig:feedback} displays power and cumulative-energy differences directly, making the increment visible despite nearly coincident absolute histories.

"""
 results+=figure('f08_timing','Feedback minus matched open-loop power over the common active interval and cumulative auxiliary-energy difference over the union of the two trajectories, at a 0.025 s step. Insets resolve the unequal terminal times; power is zero after each startup and terminal cumulative energy is held constant.','fig:feedback')
 srows=[]
 for i,state in enumerate(['FC','20 min','40 min']):
  full=index[f'R{5+i:02d}']['result']
  for n,law in [(6+i,'No voltage'),(9+i,'No rate')]:
   r=index[f'B{n:02d}']['result']
   srows.append([state,law,'.025']+[num(r[k]-full[k],6) for k in ['time_s','total_energy_J','charge_C_cm2','output_energy_J','max_delta_T_C']])
  r=new('S_'+['FC','P20','P40'][i]+'_FB')['result']; full=new('T_'+['FC','P20','P40'][i]+'_FB_0.0125')['result']
  srows.append([state,'Base + gate','.0125']+[num(r[k]-full[k],6) for k in ['time_s','total_energy_J','charge_C_cm2','output_energy_J','max_delta_T_C']])
 results+=table(r'Control-removal and simplification differences relative to the full law at the matching step. Charge differences are in C cm$^{-2}$. Every case reaches startup. Base + gate sets all four correction gains and spread suppression to zero.','tab:simple',['State','Law','$h$ (s)',r'$\delta t$ (s)',r'$\delta E_{aux}$ (J)',r'$\delta Q$',r'$\delta E_{out}$ (J)',r'$\delta\Delta T_{max}$ ($^{\circ}$C)'],srows,'lllrrrrr')
 results+=r"""The voltage branch is inactive in the successful nominal trajectories; removing it leaves the outcomes unchanged. Rate removal changes the 20 min energy by only about 0.006 J. At 0.0125 s, retaining only the prescribed base and local temperature gate changes the fully cooled auxiliary input by $-0.050$ J, startup time by $-0.0014$ s and maximum spread by $+0.0075\,^{\circ}$C. The largest time change across the three simplified cases is 0.0041 s. Thus the scheduled heating window and temperature gate account for most delivered behavior. The richer correction law offers a small increment, while the simple gate provides a practical way to taper heat near the temperature target.

"""
 results+=section('Complete startup resource balances')
 results+=r"""Lower auxiliary electricity alone does not describe the complete startup resource change. Table~\ref{tab:startupresources} uses the same terminal event for charge, stoichiometric hydrogen, thermoneutral reaction input, terminal output and model net input. The end-50 W balance is already given as A5 in Table~\ref{tab:allocationresources}. The thermoneutral reaction input is the defined model chemical-energy convention, and subtracting electrical output leaves the reaction contribution to internal heating.

"""
 rrows=[]
 for label,key in [('Preheat','D_Preheat'),('Uniform 125 W','D_Uniform125'),('FC: FB','D_Delayed')]:
  r=new(key)['result']; rrows.append([label]+resource(r)+[num(r['min_voltage_V'],3),num(r['max_delta_T_C'],2)])
 for suffix,state in [('20','20 min'),('40','40 min')]:
  r=old('E1_0'+('6' if suffix=='20' else '7')+'_formal_q4_'+suffix)['result']
  rrows.append([state+': FB']+resource(r)+[num(r['min_voltage_V'],3),num(r['max_delta_T_C'],2)])
 for suffix,state in [('None','FC'),('20','20 min'),('40','40 min')]:
  r=old('同开启同功率开环_'+suffix)['result']
  rrows.append([state+': OL']+resource(r)+[num(r['min_voltage_V'],3),num(r['max_delta_T_C'],2)])
 results+=table('Startup resources at a 0.025 s step. These nominal feedback endpoints also apply to caps of 20 and 25 C cm$^{-2}$. Preheat voltage includes the instantaneous prescribed load switch.','tab:startupresources',['Intervention']+units+['$V_{min}$ (V)',r'$\Delta T_{max}$ ($^{\circ}$C)'],rrows,'lrrrrrrrrr')
 refined=[]
 for strategy in ['A1','A5','FC_FB','FC_OL','P20_FB','P20_OL','P40_FB','P40_OL']:
  r=new('T_'+strategy+'_0.00625')['result']; vals=resource(r)
  refined.append([strategy.replace('_',': ')]+[vals[3],vals[4],vals[6]])
 results+=table(r'Additional resource components at the finest 0.00625 s step. Auxiliary electricity, charge, time and electrical output for the same cases are in Table~\ref{tab:resolutionabs}.','tab:refinedresources',['Case','$m_{H_2}$ (mg)','$E_{chem,tn}$ (J)','$E_{net}$ (J)'],refined,'lrrr')
 results+=r"""Relative to uniform 125 W heating, fully cooled delayed feedback reduces auxiliary electricity from 3791.71 to 2130.79 J, but increases reaction hydrogen from 3.004 to 24.486 mg and waiting time from 30.33 to 92.50 s. Output rises from 207.50 to 1600.21 J, while thermoneutral reaction input rises from 425.56 to 3468.73 J. These concurrent changes leave model net input at 4009.77 versus 3999.31 J, a difference of only 10.47 J. The heater saving therefore represents a shift between electricity, reaction resources and time. Pure preheating has zero reaction charge during its 34 s heating stage and a 4250 J model net input. End 50 W startup uses less auxiliary input than pure preheat, but its higher reaction contribution gives a 5281.17 J net input. Figure~\ref{fig:resources} shows these terms with electrical output subtracted rather than merged into a heater-only measure.

"""
 results+=figure('f14_resources','Startup energy components and stoichiometric hydrogen for the four handover interventions at a 0.025 s step. Positive bars show auxiliary and thermoneutral reaction inputs; negative bars show output. Diamonds mark their algebraic net input. Hydrogen is shown on a separate axis.','fig:resources')
 results+=section('Post-start operation and auxiliary-heater handover')
 results+=r"""Reaching the first startup crossing does not remove the cold endplate store. All sixteen nominal handover cases complete the same 30 s, 0.1401 A cm$^{-2}$ load interval, including immediate heater removal. Keeping all MEA means warm is a different result: removal produces minimum temperatures from $-6.44$ to $-10.85\,^{\circ}$C. Fixed 30 W end holding reduces this cooling but does not preserve warm operation for any inherited startup state. Fixed 50 W and temperature-gated 50 W maintain warmth after pure preheating and A5 end startup; both permit transient subzero means after uniform 125 W or delayed startup.

"""
 hrows=[]; energyrows=[]
 primary=hh[hh['dt']==.025]
 for _,r in primary.iterrows():
  label=r.startup.replace('D_',''); pol={'off':'Off','fixed30':'Fixed 30 W','fixed50':'Fixed 50 W','gate50':'Gate 50 W'}[r.policy]
  cross='--' if pd.isna(r.first_subzero_s) else (r'$<0.025$' if r.first_subzero_s<.025 else num(r.first_subzero_s,3))
  hrows.append([label,pol,num(r.min_voltage_V,3),num(r.min_MEA_C,3),cross,num(r.max_pore_ice,4),num(r.max_spread_C,2),'yes' if r.warm else 'no'])
  start=new(r.startup)['result']; net=start['total_energy_J']+1.48*125*start['charge_C_cm2']-start['output_energy_J']
  energyrows.append([label,pol,num(r.hold_auxiliary_J,2),num(r.output_J,2),num(r.interval_net_J,2),num(r.cumulative_auxiliary_J,2),num(r.cumulative_output_J,2),num(net+r.interval_net_J,2)])
 results+=table('Post-start thermal and electrical outcomes over the full 30 s interval. All sixteen cases complete operation. Warm means every MEA mean stays nonnegative throughout; temperature, pore ice and spread are interval extrema. A minimum rounded to 0.000 is a positive startup endpoint.','tab:handover',['Startup','Holding','$V_{min}$ (V)',r'$T_{min,int}$ ($^{\circ}$C)','$t_{<0}$ (s)','$s_{ice,max}$',r'$\Delta T_{max}$ ($^{\circ}$C)','Warm'],hrows,'llrrrrrl',long=True)
 results+=figure('f15_operation','Minimum MEA mean during common-load handover for four startup states, each continued for 30 s without field reinitialization. Lines distinguish heater removal, fixed 30/50 W end holding and a temperature-gated 50 W maximum. The zero line identifies the warm-interval target.','fig:operation')
 results+=r"""Following end 50 W startup, the gate uses 1083.79 J, saving 416.21 J (27.7\%) from fixed 50 W while keeping all MEA means nonnegative. The resulting output is 446.18 versus 449.12 J, a 2.94 J difference. Its final minimum MEA mean is 1.05 $^{\circ}$C. The gate is fully active near the initial end-cell crossing, then tapers as those cells warm, as the actual power history shows in Fig.~\ref{fig:handover}. After pure preheat, the same gate uses 1335.49 J and has a 0.0060 $^{\circ}$C interval minimum; the temporal refinement in Table~\ref{tab:holdgrid} keeps this minimum positive.

Uniform and delayed startup deliver different distributions of surplus heat, water and plate temperature. Reducing current from 0.3 to 0.1401 A cm$^{-2}$ after delayed startup sharply reduces reaction heating. Although the two end cells initially warm under fixed 50 W, the inner MEA means initially cool at about 2.68 $^{\circ}$C s$^{-1}$, reducing subsequent heat supply to the ends. At the 12.83 s minimum the end means are $-1.03\,^{\circ}$C, while the adjacent and central means remain at 2.19 and 3.39 $^{\circ}$C. The first subzero time is 3.63 s for fixed 50 W and 2.75 s for the gate; their final minima recover to 0.87 and 0.32 $^{\circ}$C. Thus a positive final temperature does not imply a warm full interval. The uniform-start gate likewise permits a $-0.72\,^{\circ}$C minimum. These state-dependent responses explain why the same end-holding command can complete operation in every case but preserve warmth in only two startup states.

"""
 results+=figure('f18_handover','End-50 W and delayed-start handover: actual end-heater power, maximum local pore-ice saturation and cumulative output gain relative to immediate heater removal. Fixed and gated policies use the same inherited state and load in each column. Step: 0.025 s.','fig:handover')
 results+=table('Holding and combined-phase resources. Every interval consumes 4.203 C cm$^{-2}$, 5.489 mg stoichiometric hydrogen and 777.56 J thermoneutral reaction input. Operation net input includes holding electricity; combined columns include startup and operation.','tab:holdresources',['Startup','Holding','$E_{hold}$ (J)','$E_{out,op}$ (J)','$E_{net,op}$ (J)','$E_{aux,all}$ (J)','$E_{out,all}$ (J)','$E_{net,all}$ (J)'],energyrows,'llrrrrrr',long=True)
 results+=r"""Holding electricity dominates the output increment: for end startup the gate adds 1083.79 J and gains only 11.58 J of output relative to removal. Its purpose is to preserve the warm operating state. Table~\ref{tab:holdresources} joins the startup and holding ledgers using one reaction-energy convention. For a low-load interval that may cool below freezing, removal completes the modeled operation with the least auxiliary input. For warm operation after end-directed startup, the simple end-temperature gate reduces holding input while achieving the all-MEA temperature target. Uniform and delayed starts require a different thermal handover if that stricter target is imposed; full available end power alone does not maintain it here. Figure~\ref{fig:combined} connects the startup resource choice to this subsequent requirement.

"""
 results+=figure('f19_handover_resources','Startup and temperature-gated holding auxiliary electricity (left) and combined model net input (right). The net input includes both phases of thermoneutral reaction input and electrical output. Circle/cross markers identify whether all MEA means remain nonnegative throughout the complete common-load interval.','fig:combined')
 results+=section('Current-loading context')
 results+=r"""Loading history sets both reaction heat and the transient voltage margin. At $-10\,^{\circ}$C, conditioned constant, ramp and staircase controls start in 24.30, 22.20 and 21.96 s. The staircase minimum is near the 0.30 V cutoff, as the enlarged low-voltage interval shows in Fig.~\ref{fig:loading}. These finite initial currents use the specified conditioned memory $p(0)=0$. Starting the same commands from rest instead applies $p(0)=gj(0)$ and causes immediate voltage termination. A zero-start ramp avoids that initial jump and starts at 26.25 s with 0.371 V minimum. It succeeds at $-13.6\,^{\circ}$C but reaches the 20 C cm$^{-2}$ cap at $-13.7\,^{\circ}$C.

"""
 lrows=[]
 for tag,law in [('恒流策略','Constant'),('线性升载','Ramp'),('分段阶梯加载','Staircase')]:
  for prefix,step in [('正式','.025'),('细步复核','.0125')]:
   r=old('Q2_'+prefix+'_'+tag)['result']
   lrows.append([law,'-10','Conditioned',step,status(r)]+[num(r[k],p) for k,p in [('time_s',3),('charge_C_cm2',3),('min_voltage_V',5),('max_delta_T_C',3)]])
 for i,law in enumerate(['Constant','Ramp','Staircase']):
  r=index[f'B{1+i:02d}']['result']
  lrows.append([law,'-10','Rest','.025',status(r)]+[num(r[k],p) for k,p in [('time_s',3),('charge_C_cm2',3),('min_voltage_V',5),('max_delta_T_C',3)]])
 for key,temp in [('Q2_零起点推荐复核','-10'),('Q2_零起点临界_-13.6','-13.6'),('Q2_零起点临界_-13.7','-13.7')]:
  r=old(key)['result']; lrows.append(['Zero-start',temp,'Rest','.025',status(r)]+[num(r[k],p) for k,p in [('time_s',3),('charge_C_cm2',3),('min_voltage_V',5),('max_delta_T_C',3)]])
 results+=table('Current-loading outcomes and refinements, all with zero auxiliary input. Temperature is the uniform initial state; loading memory distinguishes conditioned and rest initialization.','tab:loading',['Law',r'$T_0$ ($^{\circ}$C)','Memory','$h$ (s)','Outcome','$t$ (s)','$Q$ (C cm$^{-2}$)','$V_{min}$ (V)',r'$\Delta T_{max}$ ($^{\circ}$C)'],lrows,'lllllrrrr',long=True)
 results+=figure('f03_loading',r'Unheated loading at $-10\,^{\circ}$C. Constant, ramp and staircase use the conditioned memory; zero-start ramp loads from rest. The inset resolves the early 0.30 V margin. Curves end at their own startup events.','fig:loading')
 prows=[]
 for tag,label in [('capacity_-0.1',r'MEA/plate capacity -10\%'),('capacity_0.1',r'MEA/plate capacity +10\%'),('gain_-0.2',r'Memory gain $g$ -20\%'),('gain_-0.1',r'Memory gain $g$ -10\%'),('gain_0.1',r'Memory gain $g$ +10\%'),('gain_0.2',r'Memory gain $g$ +20\%'),('h_-0.1',r'Ambient transfer -10\%'),('h_0.1',r'Ambient transfer +10\%')]:
  r=old('备选扰动_'+tag)['result']
  prows.append([label,status(r)]+[num(r[k],p) for k,p in [('time_s',3),('charge_C_cm2',3),('min_voltage_V',4),('max_delta_T_C',3)]])
 results+=table(r'Individual zero-start-ramp perturbations at $-10\,^{\circ}$C, with the 0.025 s step. Capacity multiplies the calibrated MEA/plate thermal-capacity factor $K$; gain multiplies the loading-memory coefficient $g$; exterior transfer changes heat loss. The current-ramp command remains fixed.','tab:loadperturb',['Change','Outcome','$t_s$ (s)','$Q$ (C cm$^{-2}$)','$V_{min}$ (V)',r'$\Delta T_{max}$ ($^{\circ}$C)'],prows,'llrrrr')
 conclusions=r"""\FloatBarrier
\section{Conclusions}
A charge-constrained comparison separates where heat is supplied, when it begins, how it is modulated and how it is handed over to subsequent operation. The coupled five-cell model retains through-plane water/ice states, shared bipolar plates, separate endplates and loading memory. Single-cell observation comparisons and temporal/spatial refinement support the strategy differences.

At equal 50 W total input, end-directed heating reduces startup time by 2.76 s and auxiliary electricity by 138 J, while narrowing maximum cell temperature spread from 11.42 to 3.58 $^{\circ}$C. Cold endplate storage and coupling create this demand; uniform concentration-loss coefficients preserve the allocation advantage. Greater endplate heat capacity can exhaust the reaction-charge budget before startup.

Delayed heating reduces auxiliary electricity by allowing more reaction heating before heater onset. Against early uniform 125 W heating, it increases hydrogen consumption and waiting time, with a larger electrical output. The corresponding model net-input difference is about 10 J despite a 1.66 kJ auxiliary reduction. Matched-window feedback changes auxiliary input by about half a percent, and the base-and-temperature-gate law closely reproduces the complete controller. These findings favor explicit onset/resource design and a simple temperature taper.

The first startup crossing leaves substantial endplate cooling demand. Every tested handover completes the common 30 s low-load interval, but heater removal permits renewed subzero MEA means. After end-directed startup, temperature-gated end holding keeps all MEA means warm using 27.7\% less holding electricity than fixed 50 W, with only 2.94 J less output. Uniform and delayed startup still develop transient subzero means under both full fixed end power and the gate. Heater selection should therefore include the inherited thermal distribution and the intended operating target: completing a low-load interval and maintaining a warm interval require different handover decisions.

"""
 ending=original[original.index(r'\section*{Data and code availability}'):]
 dstart=ending.index(r'\section*{Data and code availability}'); dend=ending.index(r'\section*{Funding}')
 ending=ending[:dstart]+r"""\section*{Data and code availability}
The research files contain the model implementation, supplied observation workbooks, calibrated parameters, exact startup and holding configurations, accepted endpoint states, simulation trajectories and reusable figure-generation scripts. All scientific methods, parameters and comparisons are reported in this article. A public repository address and sharing terms are to be supplied by the authors.

"""+ending[dend:]
 ending=re.sub(r'\\bibitem\{alfalouji\}.*?(?=\\end\{thebibliography\})',lambda m:r'\bibitem{haddad} Ahmad Haddad, Marc Mannah, Hasan Bazzi. Nonlinear time-variant model of the PEM type fuel cell for automotive applications. Simul. Model. Pract. Theory 51 (2015) 31--44. \url{https://doi.org/10.1016/j.simpat.2014.11.002}.'+'\n',ending,flags=re.S)
 doc=pre+abstract+intro+model+validation+scenarios+results+conclusions+ending
 from final_small_revision import revise_text
 doc=revise_text(doc)
 from review_manuscript_text import revise_text as revise_review
 doc=revise_review(doc)
 (ROOT/'manuscript/main.tex').write_text(doc,encoding='utf-8')
 print('Integrated manuscript:',len(doc),'characters')
 if 'supplement' in doc.lower() or r'\appendix' in doc: raise ValueError('Scientific supplement reference remains')
if __name__=='__main__': main()


