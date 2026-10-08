"""Main-article scientific revision generated from completed research files."""
from pathlib import Path
import re,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent; R=ROOT/'program_event_v2/results/review_revision'; P=R/'parameters'

def table(caption,label,headers,rows,align,size='footnotesize',long=False):
    head=' & '.join(headers)+r'\\'; body='\n'.join(' & '.join(str(v) for v in row)+r'\\' for row in rows)
    if long:
        return r'\begingroup'+'\\'+size+r'\setlength{\tabcolsep}{3pt}\begin{longtable}{'+align+'}\n'+r'\caption{'+caption+r'}\label{tab:'+label+r'}\\\toprule '+head+r'\midrule\endfirsthead\toprule '+head+r'\midrule\endhead\bottomrule\endfoot'+'\n'+body+'\n'+r'\end{longtable}\endgroup'+'\n'
    return r'\begin{table}[htbp]\centering'+'\\'+size+'\n'+r'\caption{'+caption+r'}\label{tab:'+label+r'}\setlength{\tabcolsep}{3pt}\begin{tabular}{'+align+r'}\toprule '+head+r'\midrule'+'\n'+body+'\n'+r'\bottomrule\end{tabular}\end{table}'+'\n'

def figure(name,caption,label): return r'\fig{'+name+'}{'+caption+'}{fig:'+label+'}\n'
def load(name): return json.loads((R/(name+'.json')).read_text(encoding='utf-8'))['result']
def number(x,n=3): return f'{x:.{n}f}'
def remove_figure(doc,name): return re.sub(r'\\fig\{'+name+r'\}.*?\n','',doc)
def insert_before(doc,needle,text): return doc.replace(needle,text+'\n'+needle,1)

def merge_tables(doc,first,second,part_caption):
    pos=doc.index(r'\label{tab:'+second+'}')
    begin=doc.rfind(r'\begin{table}',0,pos); end=doc.index(r'\end{table}',pos)+len(r'\end{table}')
    block=doc[begin:end]
    tab=block[block.index(r'\begin{tabular}'):block.index(r'\end{tabular}')+len(r'\end{tabular}')]
    doc=doc[:begin]+doc[end:]
    pos=doc.index(r'\label{tab:'+first+'}'); end=doc.index(r'\end{table}',pos)
    addition=r'\medskip\par\caption*{'+part_caption+r'}\label{tab:'+second+'}'+tab+'\n'
    return doc[:end]+addition+doc[end:]

def revise_text(doc):
    local=json.loads((P/'local.json').read_text()); thermal=json.loads((R/'thermal/comparison.json').read_text())
    profiles=[json.loads(x.read_text()) for x in sorted(P.glob('profile_*.json'))]
    assert len(profiles)==10 and all(x['success'] for x in profiles)
    summary=pd.read_csv(R/'summary.csv')
    doc=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:r'''\begin{abstract}
Heater placement, onset and handover determine how a fuel-cell stack uses limited reaction resources during cold startup. A through-plane water--ice--electrochemical model is coupled to five cells, shared bipolar plates and independent endplates, with single-cell response comparisons, parameter profiles and numerical refinements. Equal total power and matched heating windows separate spatial allocation from feedback. At 50 W, end-MEA heating advances startup by 2.76 s and reduces auxiliary electricity by approximately 138 J, the same constant-power effect; the advantage persists across the examined end-cell concentration multipliers and loading-memory variations. Endplates store most of the sensible heat capacity and remain cold at the first MEA zero crossing. Applying the same 50 W directly to the plates instead exhausts the reaction-charge budget before startup. Delaying heat reduces auxiliary input while increasing hydrogen consumption and waiting time, leaving a much smaller difference in model net input. Matched-window feedback adds a small increment, and a simple temperature gate reproduces the full controller closely. All tested continuations complete the prescribed 30 s operating interval, but warm operation depends on load, gate band and inherited state. After end-MEA startup, gated holding saves 27.7\% of auxiliary electricity at 0.1401 A cm$^{-2}$; at 0.08 A cm$^{-2}$ both fixed and gated holding permit renewed subzero means. The comparison supports heater selection by separating reaction resources, thermal placement, controller complexity and the required operating state.
\end{abstract}''',doc,flags=re.S)
    doc=doc.replace('Single-cell response comparisons and temporal/spatial refinement support the strategy differences.','Single-cell response comparisons, parameter profiles and temporal/spatial refinement support the strategy comparisons.')
    doc=doc.replace('this empirical coefficient represents the end-cell distinction in the reduced transport closure.',
        'this empirical coefficient amplifies the reduced concentration-loss closure. The single-cell records do not identify its end-to-inner ratio. Its electrochemical effect is distinct from the independent endplate heat-storage and conduction terms.')
    doc=doc.replace('Two endplates together have a physical heat capacity of 197.5 J K$^{-1}$ at the stated active area.',
        'Each endplate has a physical heat capacity of 98.75 J K$^{-1}$; both together contribute 197.5 J K$^{-1}$ at the stated active area.')
    doc=doc.replace('Voltage is reevaluated at the updated state. The outer step',
        r'$\Delta\bm H^{\prime\prime}$ is the accepted step heat input per area (J m$^{-2}$): integrated reaction heat, condensation/freezing/melting heat and auxiliary heating assigned to the corresponding thermal nodes. It excludes the separately written ambient term. The areal capacity $C$ has units J m$^{-2}$ K$^{-1}$ and conductance $K$ has units W m$^{-2}$ K$^{-1}$. Voltage is reevaluated at the updated state. The outer step')
    doc=doc.replace('The residual scales 0.045 V and 1.5 $^{\\circ}$C balance the two response units. The comparisons reported here replay the supplied coefficients; recalibration is a separate executable option.',
        'The residual scales 0.045 V and 1.5 $^{\\circ}$C balance response units; they are not measured noise standard deviations. Strategy baselines retain the supplied coefficients. The following profile analysis refits six coefficients at each fixed-parameter point.')
    doc=doc.replace('MEA CV &','MEA CVs &').replace('MEA volumes','MEA CVs')
    doc=doc.replace('Thickness ($\\mu$m)& Cells &','Thickness ($\\mu$m)& CVs &')
    doc=doc.replace(r'and satisfy $0\le q_k\le1$.',r'and satisfy $0\le q_k\le q_{lim}$, with $q_{lim}=1$ W cm$^{-2}$.')
    doc=doc.replace(r'cellwise commands satisfy $0\le q_k\le1$ W cm$^{-2}$.',r'cellwise commands satisfy $0\le q_k\le q_{lim}$.')
    doc=doc.replace(r'\setlength{\parskip}{3pt}',r'\setlength{\parskip}{3pt}\setlength{\LTpre}{6pt}\setlength{\LTpost}{6pt}')
    doc=doc.replace(r'q_k\in[0,1]',r'q_k\in[0,1\ {\rm W\,cm^{-2}}]')
    doc=doc.replace(r'\operatorname{clip}(r_kg_k,0,1)',r'\operatorname{clip}(r_kg_k,0,q_{lim}),\qquad q_{lim}=1\ {\rm W\,cm^{-2}}')
    doc=doc.replace(r'\operatorname{clip}(s_bq_{base,k},0,1)',r'\operatorname{clip}(s_bq_{base,k},0,q_{lim})')
    doc=doc.replace(r'\operatorname{clip}(s_bq_{base,k}g_k,0,1)',r'\operatorname{clip}(s_bq_{base,k}g_k,0,q_{lim})')
    # Compact notation is kept alongside the equations it serves.
    symbols=table('Notation used across the model and comparisons. Celsius differences and kelvin differences are identical; electrochemical closures use absolute temperature.',
        'notation',['Symbol','Meaning','Unit'],[
        [r'$A_c$, $A$','Active area in electrochemical and thermal units',r'cm$^2$, m$^2$'],
        [r'$j$, $J$','Current density in command and voltage closure',r'A cm$^{-2}$, A m$^{-2}$'],
        [r'$Q$, $Q_{max}$','Reaction charge density and startup cap',r'C cm$^{-2}$'],
        [r'$q_k$, $P_{aux}$','Applied areal heater command and total power',r'W cm$^{-2}$, W'],
        [r'$\bar\vartheta_k$, $T_k$, $\vartheta_e$','MEA mean Celsius/kelvin and endplate Celsius temperature','K or $^{\\circ}$C'],
        [r'$C$, $G$, $G_e$','Areal capacity, intercell and endplate conductance',r'J m$^{-2}$ K$^{-1}$; W m$^{-2}$ K$^{-1}$'],
        [r'$s_{ice}$', 'Local ice volume divided by pore volume','1'],
        [r'$E_{aux}$, $E_{chem,tn}$, $E_{out}$, $E_{net}$','Auxiliary, reaction, output and algebraic net energy','J']], 'lll',size='scriptsize')
    doc=insert_before(doc,r'\subsection{Water transfer, phase changes and ice occupation}',symbols)
    doc=doc.replace('The model is uniform in-plane and resolves differences through the MEA thickness and between cell means.',
        r'The model is uniform in-plane and resolves differences through the MEA thickness and between cell means. Throughout, $\pos{x}=\max(x,0)$ denotes the positive part, while $\mathbf1_{\mathcal A}$ equals one when condition $\mathcal A$ holds and zero otherwise.')
    # Full parameter profiles and residual correlations, separate from stack validation.
    cos=pd.read_csv(P/'direction_cosines.csv',index_col=0)
    rows=[]
    display={'log10_j0':r'$\log_{10}j_0$','Qc':r'$Q_c$'}
    for x in profiles:
        t=x['theta']; m=x['metrics']; rows.append([display[x['fixed_parameter']],number(x['value'],3),number(x['objective'],4),x['nfev'],
            number(10**t[0],2),number(t[1],4),number(t[2],3),number(t[3],3),number(t[4],4),number(t[5],3),number(t[6],3),
            number(1000*m[1]['voltage_MAE_V'],2),number(m[1]['temperature_MAE_C'],3)])
    profile_text=r'''\subsection{Parameter directions and residual structure}
At the supplied vector, central differences form the scaled Jacobian $J_{ri}=s_i\partial r_r/\partial\theta_i$, with $s_i=\max(|\theta_i|,0.1)$. Perturbations are $10^{-3}s_i$ and $5\times10^{-4}s_i$; the relative Frobenius change is '''+f"{local['difference_relative_norm']:.2g}"+r'''. Its singular values are $(58.29,29.89,14.36,9.92,4.79,1.78,0.197)$ and condition number is 296. The least responsive direction is dominated by $\log_{10}j_0$, $Q_c$ and $\eta_{c,0}$, with scaled components $-0.668$, $-0.614$ and $-0.414$. Response-direction cosines describe similarity of sensitivities, rather than statistical parameter correlations.

Five fixed values are used for each of $\log_{10}j_0$ and $Q_c$: $(0.6,0.8,1,1.2,1.4)$ times the supplied coordinate. Every point refits all six other coordinates using the stated bounds, trust-region reflective least squares, a 60-evaluation limit and $10^{-5}$ stopping tolerances. All ten optimizations terminate by the objective-change criterion. Table~\ref{tab:profiles} reports their actual coefficients and colder validation errors. The supplied objective is 1.9696; the profiles continue decreasing toward their upper investigated values, so this local range does not locate an interior optimum. The calculation characterizes a weak direction rather than a confidence interval.

Residual histories in Fig.~\ref{fig:validation} show a structured early-loading voltage error at $-25\,^{\circ}$C. Figure~\ref{fig:parameters} gives the mean-centered autocorrelation $a(\ell)=\sum_{i=1}^{n-\ell}e_i e_{i+\ell}/\sum_{i=1}^n e_i^2$. The smooth colder voltage and temperature residuals persist across successive 0.2 s samples. They connect the response difference to low-temperature parameter transfer and loading history; the available records do not separate those contributions. No independent-noise assumption is used to form statistical intervals.
'''
    profile_text+=table(r'Six-coordinate profile refits. Fixed identifies the held coordinate; all other coordinates are refitted. Every row converges (objective-change termination). Last two columns are fixed-parameter errors on the $-25\,^{\circ}$C record; temperature MAE is in $^{\circ}$C. $j_0$ is in A m$^{-2}$ and remaining units follow the calibration equations.',
        'profiles',['Fixed','Value','$L$','$n_{eval}$','$j_0$',r'$\gamma_C$','$g$',r'$\tau$',r'$\eta_{c,0}$','$Q_c$','$Q_r$','V MAE (mV)','T MAE'],rows,'llrrrrrrrrrrr',size='scriptsize')
    profile_text+=figure('f20_parameter_analysis','Scaled response sensitivities, response-direction cosines, complete six-coordinate profile refits and residual autocorrelations. Profile points are computed objective values; the dotted level is the supplied-vector objective. Residual lag is measured in seconds.','parameters')
    profile_text+=r'''\subsection{Published response context and thermal-network comparison}
The published measurements use different stack structures, inputs and temperature definitions (Table~\ref{tab:external}). Lin et al.\ \cite{lin} compare a 30-cell warm-load thermal experiment and use Tabe's single-cell record for subzero voltage; their public J-STAGE Data item contains model equations, parameters and simulation tables. It provides no matching cold-start stack time series. Montaner R\'ios et al.\ \cite{montaner2026} report potentiostatic cold starts with coolant-outlet temperature, contrasting with the five MEA means used here. These records provide physical context; the experimental response support for the present parameter vector remains the supplied single-cell observations.
'''
    profile_text+=table('Published experimental context. These conditions are not used as matched independent stack validation of the present five-cell calculation.',
        'external',['Study','Experimental structure and input','Measured response / comparison'],[
        [r'Tabe et al.\ \cite{tabe}',r'25 cm$^2$ single cell; isothermal chamber; ramps at subzero temperature','Cell voltage; water-state/freezing observations'],
        [r'Lin et al.\ \cite{lin}',r'30 cells, 270 cm$^2$; 296 K initial, 284 K ambient; approximately 80 A warm loading','Stack/coolant thermal response; subzero voltage uses single-cell data'],
        ["Montaner R\\'ios et al.\\ \\cite{montaner2026}",r'40 cells, 200 cm$^2$; $-10/-20\,^{\circ}$C; voltage-controlled start; air/O$_2$ mixtures','Coolant-outlet temperature and electrical response']], 'lp{6.1cm}p{5.8cm}',size='scriptsize')
    profile_text+=r'''A separate numerical comparison removes reaction and phase changes, fixes the same 50 W input, capacities, conductances, $-30\,^{\circ}$C initial/ambient temperature and 100 s interval, and replaces each through-plane cell by one thermal node. With the constant-within-cell projection $P$, the seven-node model uses $C_r=P^{\mathsf T}C\mathbf1$ and $K_r=P^{\mathsf T}KP$. Both linear networks are integrated by their exact eigensolutions. Maximum mean-temperature differences are 0.00162 $^{\circ}$C for uniform MEA heating, 0.00230 $^{\circ}$C for end-MEA heating and $2.2\times10^{-6}\,^{\circ}$C for plate heating; corresponding plate differences are 0.00025, 0.00025 and $6.5\times10^{-7}\,^{\circ}$C. This comparison quantifies thermal aggregation under identical inputs, independently of reaction/water splitting, and is a numerical comparison rather than experimental validation.
'''
    doc=insert_before(doc,r'\subsection{Resolution of strategy differences}',profile_text)
    # Explicit reaction budget and actuator definitions.
    doc=doc.replace('A common charge cap', 'A common charge cap',1)
    doc=doc.replace('The mechanism calculations use A1 and A5 with unchanged current and calibration.',
        'The mechanism calculations use A1 and A5 with unchanged current and calibration. End-cell concentration multipliers are 1, 3, 5, 7 and 10, with inner multipliers fixed at 1. Loading-memory $g$ and $\\tau$ are varied separately by $\\pm20\\%$, without retuning power or current.')
    doc=doc.replace('Changing endplate conductivity changes the series resistance and $G_e$,',
        'A distinct heat-source comparison assigns 25 W directly to each independent endplate node, retaining the same 50 W electrical input, current, ideal conversion and charge cap; A5 assigns its input to the exterior MEA nodes. Changing endplate conductivity changes the series resistance and $G_e$,')
    doc=doc.replace('Table~\\ref{tab:coefficients} specifies all 13 settings and their units; JSON retains machine precision.',
        'Table~\\ref{tab:coefficients} specifies all 13 prescribed settings and their units; JSON retains machine precision. The stored values are scenario settings, not the output of a recorded controller optimization. The onset-neighborhood calculations vary only onset. Correction-gain comparisons multiply the four temperature-lag, warming-rate, voltage and voltage-rate coefficients by 0.5 and 2; base power, onset, cutoff, spread suppression and gate remain fixed.')
    doc=doc.replace(r'Tables~\ref{tab:allocationresources}, \ref{tab:startupresources} and \ref{tab:refinedresources} report',
        r'Tables~\ref{tab:allocationresources}, \ref{tab:startupresources} and \ref{tab:resolutionabs} report')
    budget=r' For $N=5$, $A_c=25$ cm$^2$ and $Q_{max}=20$ C cm$^{-2}$, the stoichiometric reaction-hydrogen cap is $NA_cQ_{max}M_{H_2}/(2F)=26.118$ mg. This cap sets the reaction-resource comparison; the 15/20/25 C cm$^{-2}$ levels are not a storage-bottle capacity or a manufacturer specification.'
    doc=doc.replace('Initial sensible heat is specified by the thermal initial state.','Initial sensible heat is specified by the thermal initial state.'+budget)
    doc=doc.replace(r'\frac{2\,^{\circ}{\rm C}-\bar\vartheta_k}{2\,^{\circ}{\rm C}}',r'\frac{B-\bar\vartheta_k}{B}')
    doc=doc.replace('It provides full end power at 0 $^{\\circ}$C and removes that power at 2 $^{\\circ}$C.',
        'The nominal band is $B=2\\,^{\\circ}$C; bands 1 and 3 $^{\\circ}$C are also compared. The gate provides full end power at 0 $^{\\circ}$C and removes it at $B$. Additional operating currents are 0.08 and 0.20 A cm$^{-2}$, each continued for 30 s from the same four actual nominal startup states under fixed 50 W and gated 50 W. Full intervals consume 2.400, 4.203 and 6.000 C cm$^{-2}$ respectively. Plate-source continuation uses its own charge-limited terminal state, retaining its full thermal/water/memory fields; it is not a successful startup handover.')
    # Correct command and constant-power relation.
    doc=doc.replace('The 50.65 W end-weighted reference reaches startup',
        r'The stored EW50.65 reference command is $(1,0.0099204541,0.0059733152,0.0099204541,1)$ W cm$^{-2}$, giving 50.64536 W; its label is rounded from that recorded command rather than a 50 W allocation. This reference reaches startup')
    doc=doc.replace('The common-power comparison fixes current, initial state, total power and charge cap,',
        r'At constant 50 W, $E_{aux}=50t_s$ and $\Delta E_{aux}=50\Delta t_s$, so time and auxiliary electricity express one constant-power response. The common-power comparison fixes current, initial state, total power and charge cap,')
    # One paired table combines beta and memory experiments.
    from build_review_assets import beta_pairs
    pairrows=[]
    for beta in [1,3,5,7,10]:
        if beta==1: rr=[json.loads((ROOT/'program_event_v2/results/revision'/('B_equal_beta_'+a+'.json')).read_text())['result'] for a in ['A1','A5']]
        elif beta==10:
            from build_revision_assets import old
            rr=[old('E3_allocation_'+str(i))['result'] for i in [1,5]]
        else: rr=[load(f'R_beta{beta}_{a}_h0025') for a in ['A1','A5']]
        a,b=rr; pairrows.append([r'$\beta_e='+str(beta)+'$',number(a['time_s'],3),number(b['time_s'],3),number(b['time_s']-a['time_s'],4),number(b['total_energy_J']-a['total_energy_J'],2),number(a['min_voltage_V'],4),number(b['min_voltage_V'],4),number(a['max_delta_T_C'],2),number(b['max_delta_T_C'],2)])
    for parameter in ['g','tau']:
        for f in [.8,1.2]:
            a,b=[load(f'R_memory{parameter}{f:g}_{v}_h0025') for v in ['A1','A5']]
            pairrows.append([('$g$' if parameter=='g' else r'$\tau$')+r'$\times'+str(f)+'$',number(a['time_s'],3),number(b['time_s'],3),number(b['time_s']-a['time_s'],4),number(b['total_energy_J']-a['total_energy_J'],2),number(a['min_voltage_V'],4),number(b['min_voltage_V'],4),number(a['max_delta_T_C'],2),number(b['max_delta_T_C'],2)])
    paired=table('Equal-50 W allocation under end-cell concentration and one-at-a-time memory variations. Differences are A5 minus A1; all eighteen runs reach startup. $V$ and spread columns are full-startup extrema. Step: 0.025 s.',
        'paired',['Change',r'$t_{A1}$ (s)',r'$t_{A5}$ (s)',r'$\Delta t_s$ (s)',r'$\Delta E_{aux}$ (J)',r'$V_{A1}$ (V)',r'$V_{A5}$ (V)',r'$\Delta T_{A1}$ ($^{\circ}$C)',r'$\Delta T_{A5}$ ($^{\circ}$C)'],pairrows,'lrrrrrrrr',size='scriptsize')
    mechanism=r'''Both endplates contribute 80.76\% of the assembled 244.57 J K$^{-1}$ sensible heat capacity. The computed areal end link is $G_e=1103.0$ W m$^{-2}$ K$^{-1}$; with $A=0.0025$ m$^2$, the one-plate path estimate $\tau_e=C_e/(AG_e)=35.81$ s is comparable to the 30 s handover and a substantial fraction of the 78--81 s startup. Reaching zero MEA mean therefore leaves a plate heat-storage demand.

Changing end $\beta$ from 1 to 10 preserves an A5 advantage near 2.76 s (approximately 138 J); the small variation of the paired difference is comparable to temporal resolution effects. The minimum voltages change little over this range. Changing $g$ or $\tau$ by 20\% likewise preserves an advantage of 2.762--2.765 s. These electrochemical changes do not remove the endplate demand (Table~\ref{tab:paired}).
'''+paired
    plate=load('R_endplate50_start_h0025'); holds=[load('R_endplate50_'+x+'_j01401_B2_h0025') for x in ['fixed','gate']]
    values=[plate['time_s'],plate['charge_C_cm2'],plate['total_energy_J'],plate['hydrogen_mg'],
        1.48*125*plate['charge_C_cm2'],plate['output_energy_J'],
        plate['total_energy_J']+1.48*125*plate['charge_C_cm2']-plate['output_energy_J'],
        plate['min_voltage_V'],plate['max_delta_T_C']]
    precision=[2,3,2,3,2,2,2,3,2]
    row='Plate50$^{*}$ & '+' & '.join(number(v,n) for v,n in zip(values,precision))+r'\\'+'\n'
    pos=doc.index(r'\label{tab:allocationresources}'); end=doc.index(r'\bottomrule',pos)
    doc=doc[:end]+row+doc[end:]
    doc=doc.replace(r'All reach startup.}\label{tab:allocationresources}',
        r'A1--A5 and EW50.65 reach startup. Plate50$^{*}$ applies 50 W at the independent endplates and terminates at the charge cap.}\label{tab:allocationresources}')
    mechanism+=r'''The heat-source location changes feasibility. Direct plate heating at 50 W reaches the 20 C cm$^{-2}$ charge cap at 96.67 s with end-MEA means $-1.57\,^{\circ}$C, endplates $-3.90\,^{\circ}$C and 4833 J auxiliary input. A5 heats the low-capacity MEA side of the thermal path and crosses zero at 77.93 s while its plates remain colder. The plate source spends more of the input warming the large plate mass; these two actuator locations are not interchangeable.

From the actual charge-limited plate-source terminal state, fixed and gated plate heating both complete the subsequent 30 s interval at 0.1401 A cm$^{-2}$, but neither is warm over the full interval: each begins near $-1.57\,^{\circ}$C. Fixed/gated input is 1500/958.82 J and output is 452.88/452.63 J; their final minimum MEA means recover to 3.49/2.17 $^{\circ}$C. This continuation shows recovery after budget exhaustion, not a successful finite-budget startup. Figure~\ref{fig:mechanism} distinguishes MEA and plate temperatures and the continued heater power.
'''
    doc=insert_before(doc,r'\FloatBarrier\subsection{Heating onset trades auxiliary demand for reaction resources}',mechanism)
    # Remove duplicate beta=1 rows from the physical contrasts.
    doc=re.sub(r'^All \$\\beta_k=1\$.*?\\\\\n','',doc,flags=re.M)
    doc=re.sub(r'\\fig\{f13_mechanism\}.*?\n',lambda m:figure('f13_mechanism',r'End-cell concentration multiplier, endplate-property contrasts, heat-source placement and plate-source continuation. A1/A5 use 50 W. In (a), bars translate the observed nominal A5--A1 time-step span to each 0.025 s point as a numerical scale; $\beta=3$ instead uses its own computed span, ending at the open 0.0125 s diamond. Bars are not statistical uncertainty. Crosses in (c) denote charge termination. The plate source in (d) terminates at the charge cap; (e)--(f) continue its failed-start terminal state for 30 s at 0.1401 A cm$^{-2}$.','mechanism'),doc)
    # Gain scaling complements branch removal without inflating controller benefit.
    gainrows=[]
    from build_revision_assets import old,FB
    for i,state in enumerate(['FC','P20','P40']):
        base=old(FB[i])['result']
        for f in [.5,2]:
            r=load(f'R_gain{f:g}_{state}_FB_h0025')
            gainrows.append([state,str(f),number(r['time_s']-base['time_s'],5),number(r['total_energy_J']-base['total_energy_J'],3),number(r['max_delta_T_C']-base['max_delta_T_C'],4),number(r['total_energy_J'],2)])
    gains=table('Four correction gains scaled together at otherwise identical scheduled windows, relative to nominal full feedback. FC, P20 and P40 denote fully cooled and 20/40 min precooling. All reach startup at a 0.025 s step.',
        'gain',['State','Multiplier',r'$\delta t_s$ (s)',r'$\delta E_{aux}$ (J)',r'$\delta\Delta T_{max}$ ($^{\circ}$C)',r'$E_{aux}$ (J)'],gainrows,'llrrrr')
    gains+=r'''Halving or doubling the four correction gains leaves the fully cooled trajectory unchanged. Across the other two states, the largest auxiliary change is below 0.10 J and the largest time change is below 0.006 s. Voltage correction remains inactive; saturation and the temperature gate constrain the delivered input. Together with branch removal, this supports the simpler scheduled-base and temperature-gate law rather than an additional complex controller.
'''
    doc=insert_before(doc,r'\FloatBarrier\subsection{Complete startup resource balances}',gains)
    # Full interval outcomes and resources for additional loads and bands.
    subset=summary[(summary.group=='load')|((summary.group=='band')&(summary.dt==.025))|
        ((summary.group=='endplate_hold')&(summary.dt==.025))]
    codes={'D_Preheat':'P','D_Uniform125':'U','D_End50':'E','D_Delayed':'D'}
    hrows=[]; erows=[]
    for _,r in subset.sort_values(['load','band','startup','policy']).iterrows():
        startup_code=('EP' if r.group=='endplate_hold' else ('Fit'+('1' if 'profile1' in r.startup else '2') if r.group=='propagation_hold' else codes[r.startup]))
        code=startup_code+('/F' if r.policy=='fixed' else '/G')
        current=number(r.load,4) if r.load==.1401 else number(r.load,2)
        cross='--' if pd.isna(r.first_subzero_s) else ('0' if r.first_subzero_s==0 else (r'$<0.025$' if r.first_subzero_s<.025 else number(r.first_subzero_s,2)))
        hrows.append([code+' / '+current+' / '+str(int(r.band)),number(r.min_voltage_V,3),number(r.min_MEA_C,4),cross,number(r.max_pore_ice,4),number(r.max_spread_C,2),'yes' if r.warm else 'no',number(r.Eaux_J,2),number(r.Eout_J,2),number(r.Enet_J,2)])
    handover=r'''\FloatBarrier\subsection{Load and gate band determine warm handover}
The warm-interval outcome changes with operating current (Fig.~\ref{fig:handoverdesign}). At 0.08 A cm$^{-2}$, every fixed/gated 50 W continuation completes 30 s but every startup state develops a subzero MEA mean. Even end startup has a $-0.0379\,^{\circ}$C dip under both laws, during their initial full-power interval; tapering is not the cause of that initial dip. At 0.20 A cm$^{-2}$, fixed heating preserves warmth after preheat, uniform and end startup, whereas the gate preserves it after preheat and end startup. Uniform startup develops a $-0.0735\,^{\circ}$C minimum under the gate and delayed startup remains temporarily subzero under both laws.

After end startup the gated input is 1191.93, 1083.79 and 971.27 J at the three currents, corresponding to auxiliary reductions of 20.5, 27.7 and 35.2\% against 1500 J fixed heating. The 20.5\% case completes operation but fails the warm target; the two higher-current cases maintain warmth. At nominal current, bands 1/2/3 use 1031.34/1083.79/1126.11 J and all retain warmth after end startup. After preheat, band 1 instead gives a $-0.0045\,^{\circ}$C dip, while bands 2/3 retain warmth. Uniform and delayed states remain temporarily subzero for all three bands. Increasing the band changes the taper; it does not replace unavailable heating at inner cells or remove inherited plate cooling demand.
'''
    handover+=figure('f21_handover_design',r'Full-interval minima and holding electricity across operating current and gate band for the four saved startup states. Upper panels use $B=2\,^{\circ}$C and fixed/gated 50 W; lower panels use nominal current and the gate. All points complete 30 s; circles maintain nonnegative means throughout, crosses indicate a subzero interval. Minima include the inherited endpoint.','handoverdesign')
    handover+=r'''All resources in Table~\ref{tab:additionalhold} are holding-stage increments over the same 30 s, excluding startup. At $j=0.08$, 0.1401 and 0.20 A cm$^{-2}$, respectively, $\Delta Q_{hold}=2.400$, 4.203 and 6.000 C cm$^{-2}$, $\Delta m_{H_2,hold}=3.134$, 5.489 and 7.835 mg, and $E_{chem,tn,hold}=444.00$, 777.56 and 1110.00 J. Thus $E_{net,hold}=E_{aux,hold}+E_{chem,tn,hold}-E_{out,hold}$. Startup components remain in Tables~\ref{tab:allocationresources} and \ref{tab:startupresources}; the nominal combined-phase comparison appears once in Table~\ref{tab:holdresources}.
'''
    handover+=table(r'Additional 30 s holding outcomes and incremental resources. Case gives startup/policy, current (A cm$^{-2}$) and band ($^{\circ}$C). P/U/E/D denote preheat, uniform 125 W, end 50 W and delayed startup; EP denotes the failed plate-source terminal state. F/G are fixed/gated 50 W. Every interval completes. Voltage and spread are interval extrema; ice is local pore saturation. Warm requires all MEA means nonnegative throughout. Temperatures are in $^{\circ}$C, times in s and holding energies in J. Parameter-vector continuations are reported separately in Table~\ref{tab:propagation}.',
        'additionalhold',['Case / $j$ / $B$','$V_{min}$','$T_{min}$',r'$t_{<0}$','$s_{ice,max}$',r'$\Delta T_{max}$','Warm',r'$E_{aux,hold}$',r'$E_{out,hold}$',r'$E_{net,hold}$'],hrows,'lrrrrrlrrr',size='scriptsize')
    # Focused refinements also cover plate-source failure and marginal warmth.
    fine=summary[summary.group=='refinement']; frows=[]
    for _,r in fine.iterrows():
        coarse=json.loads((R/(r['name']+'.json')).read_text(encoding='utf-8'))['coarse_name']; c=summary[summary.name==coarse].iloc[0]
        labels={'R_band1_Preheat_gate_j01401_h00125':'B1 preheat gate',
            'R_load0.08_End50_gate_B2_h00125':'0.08 end gate','R_load0.2_Uniform125_gate_B2_h00125':'0.20 uniform gate',
            'R_endplate50_start_h00125':'Plate startup','R_endplate50_fixed_j01401_B2_h00125':'Plate fixed',
            'R_endplate50_gate_j01401_B2_h00125':'Plate gate','R_beta3_A1_h00125':r'$\beta=3$, A1',
            'R_beta3_A5_h00125':r'$\beta=3$, A5'}
        label=labels[r['name']]
        frows.append([label,number(r.duration_s-c.duration_s,5),number(r.Eaux_J-c.Eaux_J,3),number(c.min_MEA_C,4),number(r.min_MEA_C,4),'charge stop' if r.status=='charge_limit' else ('startup' if r.status=='success' else ('warm' if r.warm else 'subzero'))])
    handover+=table(r'Focused 0.0125 s refinements relative to 0.025 s. Holding refinements retain the same nominal startup state; plate-source holding instead uses its own refined failed-start terminal state. Startup minima are the common $-30\,^{\circ}$C initial state. Each holding interval completes 30 s.',
        'reviewresolution',['Case',r'$\delta t$ (s)',r'$\delta E_{aux}$ (J)',r'$T_{min,.025}$ ($^{\circ}$C)',r'$T_{min,.0125}$ ($^{\circ}$C)','Outcome'],frows,'lrrrrl',size='scriptsize')
    doc=insert_before(doc,r'\FloatBarrier\subsection{Current-loading context}',handover)
    doc=doc.replace('For warm operation after end-directed startup, the simple end-temperature gate reduces holding input while achieving the all-MEA temperature target.',
        'At the nominal current after end-directed startup, the simple end-temperature gate reduces holding input while achieving the all-MEA temperature target.')
    doc=doc.replace('Figure~\\ref{fig:combined} shows', 'The combined-phase panels of Fig.~\\ref{fig:resources} show')
    doc=doc.replace('Figure~\\ref{fig:combined}', 'The combined-phase panels of Fig.~\\ref{fig:resources}')
    doc=doc.replace('Fig.~\\ref{fig:interventions}', 'the cell histories in Fig.~\\ref{fig:allocation}')
    doc=doc.replace('Figure~\\ref{fig:interventions}', 'Figure~\\ref{fig:allocation}')
    # Collapse duplicated figures into the core allocation and resource figures.
    for name in ['f19_handover_resources','f05_heating']: doc=remove_figure(doc,name)
    doc=re.sub(r'\\fig\{f06_allocation\}.*?\n',lambda m:figure('f06_allocation','Spatial allocation and power context at 0.025 s. A1/A5 position--time MEA maps share one color scale and end at their own startup events; the middle row gives the five 50 W vectors and end/center means. The lower row retains the distinct uniform 125 W and recorded EW50.65 (50.64536 W) responses.','allocation'),doc)
    doc=re.sub(r'\\fig\{f14_resources\}.*?\n',lambda m:figure('f14_resources','Startup energy components and reaction hydrogen (upper row), and startup plus nominal 30 s gated holding resources (lower row). Output is subtracted from auxiliary and thermoneutral inputs. Combined-phase circles/crosses indicate warm/subzero complete intervals. P/U/E/D follow the startup labels.','resources'),doc)
    # Preserve every refined numeric row while sharing a single float.
    end1=doc.index(r'\label{tab:resolutionabs}'); end1=doc.index(r'\end{table}',end1)
    begin2=doc.index(r'\label{tab:refinedresources}'); begin2=doc.rfind(r'\begin{table}',end1,begin2)
    # Tables occupy different scientific locations; move the resource rows next to the resolution rows.
    resource_end=doc.index(r'\end{table}',begin2)+len(r'\end{table}')
    block=doc[begin2:resource_end]
    resource_tab=block[block.index(r'\begin{tabular}'):block.index(r'\end{tabular}')+len(r'\end{tabular}')]
    doc=doc[:begin2]+doc[resource_end:]
    end1=doc.index(r'\label{tab:resolutionabs}'); end1=doc.index(r'\end{table}',end1)
    doc=doc[:end1]+r'\medskip\par\textit{Thermoneutral resource components at the finest step.}\par'+resource_tab+'\n'+doc[end1:]
    doc=doc.replace(r'\ref{tab:refinedresources}',r'\ref{tab:resolutionabs}')
    # Keep the existing resource table's original computed cumulative values, but shorten duplicate prose.
    doc=doc.replace('The 20 min state is close to the charge deadline:', 'The 20 min state is close to the charge deadline:')
    doc=doc.replace('Caps are in C cm$^{-2}$. Finite-cap nominal successes',
        'Caps are in C cm$^{-2}$. At cap 15 the 80 s deadline precedes the P20/P40 heater onsets, so their auxiliary input is zero. Finite-cap nominal successes')
    # Parameter propagation is generated after its actual simulations finish.
    propagation=json.loads((P/'propagation_config.json').read_text(encoding='utf-8')); prows=[]
    for i,fit in enumerate(propagation['chosen']):
        a,b=[load(f'R_profile{i+1}_{s}_start_h0025') for s in ['A1','A5']]
        for policy in ['fixed','gate']:
            n=f'R_profile{i+1}_A5_{policy}_h0025'; r=summary[summary.name==n].iloc[0]
            prows.append([i+1,number(fit['theta'][5],3),number(fit['objective'],4),number(a['time_s'],3),number(b['time_s'],3),
                number(b['time_s']-a['time_s'],4),policy,number(r.min_MEA_C,4),number(r.Eaux_J,2),number(r.Eout_J,2),number(r.Enet_J,2),'yes' if r.warm else 'no'])
    propagation_text=r'''\subsection{Propagation of fitted parameter combinations}
Two converged profile combinations satisfying $L\le1.05L_{supplied}$ are chosen at the smallest and largest fitted $Q_c$ within that response-tolerance set. The 5\% rule defines an exploratory response comparison, not a probability level. Each vector is used for fresh A1 and A5 startup calculations; fixed and gated end holding then inherit that same vector's actual A5 temperature, water, ice, endplates, charge and loading memory. Table~\ref{tab:propagation} shows the resulting allocation and warm-handover outcomes, rather than changing only the continuation coefficients on a nominal state.
'''
    propagation_text+=table(r'Selected parameter combinations carried through startup and holding. Vectors are the minimum/maximum $Q_c$ converged fits under the stated response-tolerance rule. All startup runs succeed and all continuations complete 30 s. Holding uses 0.1401 A cm$^{-2}$, $B=2\,^{\circ}$C and 50 W maximum. Temperature is the interval minimum; energy columns concern the holding interval only.',
        'propagation',['Vector','$Q_c$','$L$',r'$t_{A1}$',r'$t_{A5}$',r'$\Delta t_s$','Hold','$T_{min}$','$E_{aux}$','$E_{out}$','$E_{net}$','Warm'],prows,'lrrrrrlrrrrl',size='scriptsize')
    propagation_text+=r'''The fitted combinations give A5--A1 differences of $-2.7641$ and $-2.8276$ s, corresponding to $-138.20$ and $-141.38$ J at equal 50 W. Both parameter vectors preserve a warm gated interval, with 1083.79 and 1086.22 J holding input, versus 1500 J fixed input. This tests dependence on response-equivalent coefficients without assigning statistical coverage.
'''
    doc=insert_before(doc,r'\FloatBarrier\subsection{Current-loading context}',propagation_text)
    applicability=r'''\FloatBarrier\subsection{Model applicability and physical interpretation}
Single-cell response data constrain electrochemical, hydration and effective-capacity coefficients; their transfer to five cells is evaluated here through parameter directions, physical contrasts and numerical resolution. The independent thermal network represents shared plate capacity, endplate storage and exterior heat loss. Its end-cell demand persists when the empirical concentration multiplier is removed. Literature stack measurements have different areas, cooling loops, initial water preparation, loading laws and temperature definitions, so the present stack comparisons remain model-based design comparisons.

The through-plane model assumes uniform in-plane states and does not solve manifold/flow-channel transients, spatial gas supply or mechanical freeze expansion. Local pore-ice saturation refers to the resolved layers, not an observed in-plane ice map. The thermal precooling cases reinitialize the prescribed startup water inventory, separating sensible-heat history from shutdown hydration. Heater input has ideal thermal conversion; MEA-surface and direct-plate sources represent different actuator paths without an additional contact-resistance or coolant model. The conclusions concern five 25 cm$^2$ cells, the stated 15--25 C cm$^{-2}$ reaction budgets, 0.08--0.20 A cm$^{-2}$ continuations and 1--3 $^{\circ}$C gate bands. These definitions support selecting a heat allocation and handover for a specified operating target.
'''
    start=doc.index(r'\section{Conclusions}'); stop=doc.index(r'\section*{Data and code availability}',start)
    conclusions=r'''\FloatBarrier\section{Conclusions}
The comparison separates spatial power allocation, heater onset, feedback increment and thermal handover under a common reaction-charge budget. At equal 50 W, end-MEA heating advances the nominal startup by 2.76 s and reduces auxiliary electricity by about 138 J, with maximum cell spread falling from 11.42 to 3.58 $^{\circ}$C. Time/grid refinement, end $\beta=1$--10 and separate 20\% memory variations preserve the allocation advantage. Cold endplates contain 80.8\% of the sensible heat capacity and have a 35.8 s MEA--plate path estimate. Changing heat input from the MEA ends to the independent plates exhausts the same startup charge cap before reaching zero MEA means.

Delayed heating shifts demand from auxiliary electricity toward reaction hydrogen and waiting time. Its large heater reduction from early uniform 125 W heating corresponds to a much smaller model net-input change when thermoneutral reaction energy and electrical output are included. Matched-window feedback contributes approximately half a percent of auxiliary input, gain scaling adds little change, and a scheduled base with temperature taper closely reproduces the full law. These results support choosing the onset and resource allocation before adding controller complexity.

Completing low-load operation and retaining nonnegative MEA means are distinct objectives. All examined continuations complete 30 s. After end-MEA startup, nominal-current gated holding reduces auxiliary electricity by 27.7\% while maintaining warmth; at 0.20 A cm$^{-2}$ the reduction is 35.2\% with the same warm target. At 0.08 A cm$^{-2}$ both holding laws permit a subzero dip, and warm outcomes after other startup states depend on current and gate band. Direct plate heating recovers from its charge-limited terminal state during continuation, but that recovery does not change the failed finite-budget startup. Heater handover should therefore use the inherited thermal distribution and the required full-interval temperature target, alongside electrical and reaction-resource accounting.

'''
    doc=doc[:start]+applicability+conclusions+doc[stop:]
    # Retain author-supplied funding, contributions and other declarations.
    doc=doc.replace('Scientific outputs were generated by the archived numerical model and plotting scripts.',
        'Scientific outputs were generated by the numerical model and reusable plotting scripts.')
    doc=doc.replace('Temperature is the interval minimum; energy columns concern the holding interval only.',
        r'Time is in s, $Q_c$ in C cm$^{-2}$, minimum temperature in $^{\circ}$C and holding energy in J.')
    doc=doc.replace(r'C_r=P^{\mathsf T}C\mathbf1',r'C_r=P^{\mathsf T}CP')
    doc=doc.replace('a low-load interval that may cool below freezing','a low-load interval that permits subzero cooling')
    doc=doc.replace('their public J-STAGE Data item contains model equations, parameters and simulation tables.',
        r'their public J-STAGE Data item (\url{https://doi.org/10.50892/data.electrochemistry.27898581}) contains model equations, parameters and simulation tables.')
    doc=doc.replace(r'\FloatBarrier\subsection{Heating onset trades auxiliary demand for reaction resources}',
        r'\subsection{Heating onset trades auxiliary demand for reaction resources}')
    doc=doc.replace(r'\FloatBarrier\subsection{Current-loading context}',r'\subsection{Current-loading context}')
    doc=doc.replace(r'\begin{thebibliography}{99}',r'\begin{thebibliography}{99}\small')
    doc=merge_tables(doc,'simple','gain','Correction-gain scaling at unchanged window and gate, relative to the nominal full law; all six cases reach startup at 0.025 s. Multipliers apply to the four correction terms; energy and time differences are relative to the same state.')
    doc=merge_tables(doc,'loading','loadperturb',r'One-at-a-time zero-start-ramp perturbations at $-10\,^{\circ}$C and 0.025 s. Capacity multiplies $\gamma_C$, gain multiplies $g$, and exterior transfer changes heat loss; the ramp command remains fixed.')
    # Numeric references are ordered by first use after new citations are inserted.
    start=doc.index(r'\bibitem{'); end=doc.index(r'\end{thebibliography}')
    entries=re.findall(r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\Z)',doc[start:end],re.S)
    by_key={k:r'\bibitem{'+k+'}'+v.strip()+'\n\n' for k,v in entries}
    order=list(dict.fromkeys(k.strip() for group in re.findall(r'\\cite\{([^}]+)\}',doc[:start]) for k in group.split(',')))
    order += [k for k,v in entries if k not in order]
    doc=doc[:start]+''.join(by_key[k] for k in order)+doc[end:]
    from followup_manuscript_text import revise_text as followup
    return followup(doc)
