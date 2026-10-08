"""Integrate the executed joint fits and selected fresh state continuations."""
import json,re
import numpy as np
from review_manuscript_text import table,number,ROOT,R,P,load
from summarize_review_revision import metrics

def revise_text(doc):
    J=P/'joint'
    fits=[json.loads(x.read_text(encoding='utf-8')) for x in sorted(J.glob('joint_seed*.json'))]
    ext=[json.loads((J/f'extended_Qc{q}.json').read_text(encoding='utf-8')) for q in [18,22,30]]
    nominal=json.loads((P/'local.json').read_text(encoding='utf-8'))
    errors=json.loads((J/'supplied_metrics.json').read_text(encoding='utf-8'))
    best=min((x for x in fits if x['success']),key=lambda x:x['objective'])
    doc=doc.replace('No observation or fitted coefficient is changed in the strategy comparisons.',
        'The supplied coefficients define the nominal strategy comparisons; selected fitted vectors are separately carried through fresh startup and holding calculations.')
    a=doc.index('The supplied parameter vector uses'); b=doc.index('Its optimization coordinates are',a)
    doc=doc[:a]+r'''The supplied file records $j_{0,ref}=11.87$ A m$^{-2}$, $\gamma_C=1.017$, $g=1.764$ V/(A cm$^{-2}$), $\tau=5.195$ s, $\eta_{c,0}=0.1731$ V, $Q_c=10.00$ C cm$^{-2}$ and $Q_r=1.499$ C cm$^{-2}$. The file does not preserve the original optimizer trajectory, starting vector or bounds. We therefore treat it as the supplied reference rather than reconstructing a fitting history. The joint fits executed here use only the $-20\,^{\circ}$C record; $-25\,^{\circ}$C is evaluated with the resulting coefficients fixed. SciPy's trust-region reflective least-squares solver \cite{scipy} uses the following current search box.
'''+doc[b:]
    doc=doc.replace('The following profile analysis refits six coefficients at each fixed-parameter point.',
        'Profiles refit six coefficients at each fixed-parameter point, and joint fitting varies all seven coordinates.')
    doc=doc.replace(r'The $-20\,^{\circ}$C record sets the supplied calibration and $-25\,^{\circ}$C uses fixed parameters.',
        r'The supplied vector is replayed on both records; the joint fitting uses $-20\,^{\circ}$C and keeps $-25\,^{\circ}$C as the cross-temperature validation comparison.')
    doc=doc.replace('Single-cell voltage and temperature observations and model responses. Open markers',
        'Single-cell voltage and temperature observations and model responses. Solid lines use the supplied vector and dashed lines the joint training optimum, with corresponding residual histories. Open markers')
    doc=doc.replace('so this local range does not locate an interior optimum.',
        'so the initial profile range does not locate an interior optimum. The joint and extended calculations below examine the continuation of that direction.')
    rows=[]
    records=[('Supplied',dict(theta=nominal['theta'],objective=nominal['objective'],metrics=errors))]
    records += [('Joint '+str(x['seed']),x) for x in fits]
    records += [('Fixed '+str(int(x['value'])),x) for x in ext]
    for label,x in records:
        t=x['theta']; m=x['metrics']
        rows.append([label,number(x['objective'],4),number(10**t[0],2),number(t[1],4),number(t[2],3),number(t[3],3),number(t[4],4),number(t[5],3),number(t[6],3),
            number(1000*m[0]['voltage_MAE_V'],3),number(m[0]['temperature_MAE_C'],5),number(1000*m[1]['voltage_MAE_V'],3),number(m[1]['temperature_MAE_C'],5)])
    joint=r'''\subsection{Joint training fits and fixed-parameter response transfer}
Three initial vectors are used: the supplied vector, the converged $Q_c=14$ profile vector in Table~\ref{tab:profiles}, and $(1.8,1.05,1.3,7,0.25,20,2.5)$ in the stated optimization coordinates. All seven coordinates vary within the same box, with scales $\max(|\theta_{supplied,i}|,0.1)$, a 200-evaluation limit and $10^{-7}$ objective, step and gradient tolerances. Only the $-20\,^{\circ}$C residuals enter the fit. The three starts terminate by objective change after '''+', '.join(str(x['nfev']) for x in fits)+r''' evaluations, with objectives agreeing within $4\times10^{-9}$. Their $Q_c$ values are 26.346--26.348 C cm$^{-2}$ and $\log_{10}j_0$ values 2.8624--2.8627, with no active bounds. The minimum training objective identifies the representative joint vector.

The training objective falls from 1.9696 to 1.6466 (16.4\%), and voltage MAE decreases from 3.789 to 3.411 mV. Temperature MAE changes from 0.00839 to 0.00810 $^{\circ}$C. On the colder $-25\,^{\circ}$C validation record, voltage MAE increases from 13.756 to 16.968 mV and temperature MAE from 0.11644 to 0.12732 $^{\circ}$C. Voltage RMSE changes from 4.645 to 4.246 mV in training and from 15.713 to 18.632 mV in the colder comparison. The joint solution improves the training record without improving response transfer. The supplied vector therefore remains the nominal stack-comparison setting, while the training-only optimum is retained as a separate parameter-dependence case; the colder record is not refitted. This validation comparison informs the choice of nominal reference; it is not a final independent test performed after parameter selection.

The exchange current density changes from '''+number(10**nominal['theta'][0],2)+' to '+number(10**best['theta'][0],1)+r''' A m$^{-2}$, whereas training voltage MAE improves by only 0.377 mV. In the voltage model, larger $j_{0,ref}$ lowers activation loss, while the joint fit increases the initial cold loss $\eta_{c,0}$ from 0.1731 to 0.3519 V and its charge scale $Q_c$ from 10.00 to 26.35 C cm$^{-2}$. These opposing contributions provide a compensation mechanism. At the supplied vector, the scaled Jacobian response-direction cosine between $\log_{10}j_0$ and $\eta_{c,0}$ is $-0.981$ (Fig.~\ref{fig:parameters}); the refitted profiles also admit distinct coefficients with close response objectives. These results support parameter coupling: a close response fit does not establish separate physical identification of every coefficient.

Extending the fixed-$Q_c$ profiles to 18, 22 and 30 C cm$^{-2}$, with a 120-evaluation limit and $10^{-5}$ tolerances, gives objectives 1.7183, 1.6691 and 1.7492 after 8, 9 and 12 evaluations. At 30, $\log_{10}j_0=3$ reaches its upper constraint; this point describes the search-box effect rather than an unconstrained continuation. Together with the interior joint solution near $Q_c=26.35$, the extended results resolve the apparent monotonic decrease in the initial range. These are objective profiles and selected sensitivity vectors, not statistical confidence limits.
'''
    joint+=table(r'Executed seven-coordinate fits and extended six-coordinate profiles. Joint rows differ by training initial vector; Fixed rows hold $Q_c$ at the stated value. All terminate by objective change. V MAE is in mV and T MAE in $^{\circ}$C; the last two columns concern the colder $-25\,^{\circ}$C validation record. Parameter units follow the calibration equations.',
        'jointfits',['Vector','$L$','$j_0$',r'$\gamma_C$','$g$',r'$\tau$',r'$\eta_{c,0}$','$Q_c$','$Q_r$',r'V$_{train}$',r'T$_{train}$',r'V$_{val}$',r'T$_{val}$'],rows,'lrrrrrrrrrrrr',size='scriptsize')
    needle=r'\subsection{Published response context and thermal-network comparison}'
    doc=doc.replace(needle,joint+'\n'+needle,1)
    doc=doc.replace('complete six-coordinate profile refits and residual autocorrelations.',
        'six-coordinate profile refits, the joint training minimum and residual autocorrelations. Extended $Q_c$ points use the same bounds; stars denote the joint solution.')
    # Quantitative published responses have their own structures and event definitions.
    doc=doc.replace('Coolant-outlet temperature and electrical response',
        r'$t_{50\%}=45/19/10$ s at 0.5/0.4/0.3 V per cell (S1, air, $\lambda_c=4.8$); target 2 kW. Coolant zero crossing is a separate event')
    doc=doc.replace('These records provide physical context;',
        r'For Montaner R\'ios et al., the measured cold-start event is 50\% rated power (2 kW), whereas coolant-outlet zero crossing is reported separately. These quantified responses describe voltage-controlled self-starting at $-20\,^{\circ}$C and are not errors relative to the present all-MEA zero-crossing event at $-30\,^{\circ}$C. The original curves resolve current, voltage, power and coolant temperature, but the gas/coolant inputs, plate construction and initial water preparation differ from the present model. These records provide physical context;')
    doc=doc.replace('the seven-node model', 'the projected seven-node model')
    doc=doc.replace('numerical comparison rather than experimental validation.',
        'comparison of two resolutions of this model, rather than an independently published model or experimental validation.')
    # Include selected-vector startup resources and holding extrema once.
    sources=[('Fit1',json.loads((P/'propagation_config.json').read_text(encoding='utf-8'))['chosen'][0],'R_profile1'),
        ('Fit2',json.loads((P/'propagation_config.json').read_text(encoding='utf-8'))['chosen'][1],'R_profile2'),
        ('Joint',best,'R_selected_joint'),('Qc30',ext[-1],'R_selected_Qc30')]
    srows=[]; hrows=[]
    for label,fit,prefix in sources:
        for strategy in ['A1','A5']:
            r=load(prefix+'_'+strategy+'_start_h0025'); q=r['charge_C_cm2']; chem=1.48*125*q
            srows.append([label,strategy,number(r['time_s'],3),number(q,3),number(r['total_energy_J'],2),number(r['hydrogen_mg'],3),number(chem,2),number(r['output_energy_J'],2),number(r['total_energy_J']+chem-r['output_energy_J'],2)])
        for policy in ['fixed','gate']:
            r=metrics(R/(prefix+'_A5_'+policy+'_h0025.json'))
            cross='--' if np.isnan(r['first_subzero_s']) else number(r['first_subzero_s'],2)
            hrows.append([label,policy,number(r['min_voltage_V'],3),number(r['min_MEA_C'],4),cross,number(r['max_pore_ice'],4),number(r['max_spread_C'],2),number(r['Eaux_J'],2),number(r['Eout_J'],2),number(r['Enet_J'],2),'yes' if r['warm'] else 'no'])
    a=doc.index(r'\subsection{Propagation of fitted parameter combinations}'); b=doc.index(r'\subsection{Current-loading context}',a)
    prop=r'''\subsection{Selected parameter combinations through startup and holding}
Four parameter combinations are examined. Fit1 and Fit2 are the two original profile selections (smallest/largest $Q_c$ among converged fits with $L\le1.05L_{supplied}$); Joint is the minimum-objective seven-coordinate fit, and Qc30 is the upper-box profile. The 5\% response rule is an exploratory selection threshold, not a probability level. Each vector is applied to fresh A1/A5 startup calculations; fixed and gated end heating inherit its own A5 temperature, water, ice, endplate state, cumulative charge and loading memory. Tables~\ref{tab:selectedstart} and \ref{tab:propagation} report these four combinations, without assigning comprehensive uncertainty coverage.
'''
    prop+=table(r'Startup resources for the four selected parameter combinations, all at 50 W and 0.025 s. All reach the startup event. Units: time s, charge C cm$^{-2}$, reaction hydrogen mg, energies J. Fit1/Fit2 coefficients are in Table~\ref{tab:profiles}; Joint/Qc30 in Table~\ref{tab:jointfits}.',
        'selectedstart',['Vector','Law','$t_s$','$Q$',r'$E_{aux}$',r'$m_{H_2}$',r'$E_{chem,tn}$',r'$E_{out}$',r'$E_{net}$'],srows,'llrrrrrrr',size='scriptsize')
    prop+=table(r'Holding-stage increments and full-interval extrema for the same selected combinations. Every interval completes 30 s at 0.1401 A cm$^{-2}$; fixed/gated heating has a 50 W limit and the gate uses $B=2\,^{\circ}$C. All consume 4.203 C cm$^{-2}$, 5.489 mg reaction hydrogen and 777.56 J thermoneutral input. Units: V, $^{\circ}$C, s and J. Warm requires nonnegative MEA means throughout; energies exclude startup.',
        'propagation',['Vector','Hold','$V_{min}$','$T_{min}$',r'$t_{<0}$','$s_{ice,max}$',r'$\Delta T_{max}$',r'$E_{aux,hold}$',r'$E_{out,hold}$',r'$E_{net,hold}$','Warm'],hrows,'llrrrrrrrrl',size='scriptsize')
    differences=[]
    for label,fit,prefix in sources:
        x,y=[load(prefix+'_'+s+'_start_h0025') for s in ['A1','A5']]; differences.append(label+' '+number(y['time_s']-x['time_s'],4))
    prop+=r'The A5--A1 startup differences are '+', '.join(differences)+r''' s. The reported holding extrema show how the fitted electrochemical response changes heat release and the inherited endpoint under identical external commands. These selected combinations test the two decisions jointly; they do not represent a sampled probability distribution.
'''
    fine=[load('R_selected_joint_'+s+'_start_h00125') for s in ['A1','A5']]
    coarse=[load('R_selected_joint_'+s+'_start_h0025') for s in ['A1','A5']]
    change=(fine[1]['time_s']-fine[0]['time_s'])-(coarse[1]['time_s']-coarse[0]['time_s'])
    prop+=r'For the Joint vector, reducing the step to 0.0125 s gives A1/A5 startup at '+number(fine[0]['time_s'],4)+'/'+number(fine[1]['time_s'],4)+r' s and a paired difference of '+number(fine[1]['time_s']-fine[0]['time_s'],5)+r' s. The paired change from 0.025 s is '+number(change,6)+r' s ('+number(50*change,4)+r' J at 50 W); the allocation ordering is retained.'+'\n'
    doc=doc[:a]+prop+'\n'+doc[b:]
    # State precisely which supplied inputs are retained and which work is added.
    needle=r'Table~\ref{tab:related} positions'
    paragraph=r'''The supplied input files provide single-cell current/voltage/temperature records, geometry, material properties and initial-state settings. This study retains those observations and physical inputs. Its added comparisons isolate equal-power spatial allocation, matched-window feedback, finite reaction-resource accounting and continuation from the actual startup state; joint fitting and numerical refinements characterize parameter and discretization dependence. The study's scientific increment is these coupled comparisons, rather than a change to the original observations.

'''
    doc=doc.replace(needle,paragraph+needle,1)
    doc=doc.replace('A public repository address and sharing terms are to be supplied by the authors.',
        'The implementation, exact configurations, fitted parameter vectors, simulation trajectories and figure scripts are available at https://github.com/ludkeharshfield197-sys/pemfc-cold-start-smpt. The public package excludes the original observation records; repeating single-cell fitting requires those records. No repository DOI or additional reuse license has been assigned.')
    doc=doc.replace('Time/grid refinement, end $\\beta=1$--10 and separate 20\\% memory variations preserve the allocation advantage.',
        r'Time/grid refinement, end $\beta=1$--10 and separate 20\% memory variations preserve the nominal allocation advantage. Joint training fits converge from three initial vectors but worsen the colder validation response; the supplied vector remains the nominal setting, and four selected coefficient combinations are carried through fresh startup and holding.')
    doc=doc.replace('Matched-window feedback adds a small increment,',
        'Joint training fits worsen the colder validation response, so the supplied vector remains the nominal setting. Matched-window feedback adds a small increment,',1)
    doc=doc.replace(r'After preheat, band 1 instead gives a $-0.0045\,^{\circ}$C dip, while bands 2/3 retain warmth.',
        r'After preheat, band 1 instead gives a $-0.0045\,^{\circ}$C dip, while bands 2/3 retain warmth. This is a zero-crossing classification of the model: a practical temperature margin must also exceed sensor resolution and controller deadband; the millikelvin difference is not an engineering margin.')
    doc=doc.replace('All points complete 30 s; circles maintain',
        'The lower-left inset resolves the preheat/end near-zero minima and labels the preheat band-1 dip. All points complete 30 s; circles maintain')
    doc=doc.replace('The upper row compares paired startup-time differences and voltage across end-cell concentration multipliers.',
        'The upper row compares paired startup-time differences and voltage across end-cell concentration multipliers. Bars show the full observed time-step span of the nominal A5--A1 difference, used as a numerical scale; the open diamond is the actual refined beta-3 calculation. No monotonic beta trend is inferred from sub-millisecond changes.')
    from summarize_onset_parameters import comparison_tables
    endpoints, paired = comparison_tables()
    # Extend the existing startup-resource table, keeping all three vectors together.
    pos=doc.index(r'\label{tab:startupresources}')
    end=doc.index(r'\bottomrule\end{tabular}\end{table}',pos)
    rows=[]
    for _,r in endpoints[endpoints.vector!='Nominal'].iterrows():
        rows.append([r.vector+': '+r.strategy.replace('Uniform125','U125').replace('FC_',''),
            number(r.time_s,2),number(r.charge_C_cm2,3),number(r.Eaux_J,2),number(r.hydrogen_mg,3),
            number(r.Echem_tn_J,2),number(r.Eout_J,2),number(r.Enet_J,2),number(r.Vmin_V,3),number(r.max_spread_C,2)])
    extra=r'\midrule'+'\n'+'\n'.join(' & '.join(row)+r'\\' for row in rows)+'\n'
    prows=[]
    for _,r in paired.iterrows():
        prows.append([r.vector,number(r.onset_delta_time_s,3),number(r.onset_delta_Eaux_J,2),
            number(r.onset_delta_Q_C_cm2,3),number(r.onset_delta_hydrogen_mg,3),number(r.onset_delta_Enet_J,2),
            number(r.feedback_delta_time_s,4),number(r.feedback_delta_Eaux_J,3),number(r.feedback_relative_pct,3)])
    part=table('', 'onsetparameters', ['Vector',r'$\Delta t_{on}$',r'$\Delta E_{aux,on}$',r'$\Delta Q_{on}$',
        r'$\Delta m_{H_2,on}$',r'$\Delta E_{net,on}$',r'$\Delta t_{fb}$',r'$\Delta E_{aux,fb}$',r'$\delta_{aux,fb}$'],
        prows,'lrrrrrrrr',size='scriptsize')
    part=part[part.index(r'\begin{tabular}'):part.index(r'\end{tabular}')+len(r'\end{tabular}')]
    note=r'''\medskip\par\caption*{Within-vector paired differences. Onset columns are FC\_FB minus Uniform125; feedback columns are FC\_FB minus FC\_OL. Units: s, J, C cm$^{-2}$ and mg; $\delta_{aux,fb}=100\Delta E_{aux,fb}/E_{aux}(\mathrm{FC\_OL})$ is in percent. All nine fully cooled endpoints reach startup; Joint/Qc30 use their complete vectors in Table~\ref{tab:jointfits}, with unchanged 20 C cm$^{-2}$ cap. U125 denotes Uniform125.}'''
    doc=doc[:end]+extra+r'\bottomrule\end{tabular}'+note+part+r'\end{table}'+doc[end+len(r'\bottomrule\end{tabular}\end{table}'):]
    doc=doc.replace('Startup resources at a 0.025 s step. These nominal feedback endpoints also apply',
        'Startup resources at a 0.025 s step. Unprefixed rows use the supplied nominal vector; prefixed rows give six fresh parameter-comparison startups. These nominal feedback endpoints also apply')
    # The original matching rule fixes commands, not the achieved terminal times.
    needle='Matched open loop keeps the same initial state, current, cap and preset window,'
    doc=doc.replace(needle,r'Joint and Qc30 retain the fully cooled nominal window $[75.353222,116.926474)$ s. Base power, gains and saturation also retain their nominal settings; the outcomes are not used to select a different window. Both laws stop at their own first startup event. $Q_c=30$ is a fitted cold-loss charge scale, while $Q_{max}=20$ C cm$^{-2}$ remains the reaction budget.'+'\n\n'+needle,1)
    a=doc.index('Relative to uniform 125 W heating, fully cooled delayed feedback'); b=doc.index('\n\n\\fig{f14_resources}',a)
    doc=doc[:a]+r'''For the nominal vector, delayed feedback reduces auxiliary electricity by 1660.92 J (43.80\%) relative to early uniform 125 W heating, but adds 16.450 C cm$^{-2}$ reaction charge, 21.482 mg reaction hydrogen and 62.166 s startup time. Thermoneutral reaction input rises from 425.56 to 3468.73 J and electrical output from 207.50 to 1600.21 J. With $\Delta E_{net,on}=E_{net}(\mathrm{FC\_FB})-E_{net}(\mathrm{Uniform125})$, the net difference is $-10.47$ J: 3999.31 versus 4009.77 J.

The paired rows of Table~\ref{tab:startupresources} show that this net ordering changes for the fitted vectors: $\Delta E_{net,on}=+7.48$ J for Joint and $+4.59$ J for Qc30. Their auxiliary savings are 42.99\% and 43.30\%, with additional reaction hydrogen of 21.576 and 21.540 mg and additional times of 62.383 and 62.291 s. Thus all three examined combinations retain the transfer between auxiliary electricity, reaction resources and time, but the small net-input difference has a parameter-dependent sign. The opposing energy components nearly cancel, so the nominal 10.47 J reduction is not a general delayed-heating advantage.

Pure preheating has zero reaction charge during its 34 s heating stage and a 4250 J model net input. Nominal end-50 W startup uses less auxiliary input than pure preheat, but its reaction contribution gives a 5281.17 J net input. Figure~\ref{fig:resources} resolves the components and the parameter-dependent paired differences.''' +doc[b:]
    doc=doc.replace('P/U/E/D follow the startup labels.',
        r'The lower row compares within-vector FC\_FB minus Uniform125 net input and FC\_FB minus FC\_OL auxiliary percentage for Nominal, Joint and Qc30; all reach startup at 0.025 s. The percentage denominator is matched open-loop auxiliary input. P/U/E/D follow the startup labels.')
    doc=doc.replace('startup plus nominal 30 s gated holding resources (lower row)',
        'startup plus nominal 30 s gated holding resources (middle row)')
    needle='The voltage branch is inactive in the successful nominal trajectories;'
    doc=doc.replace(needle,r'''At the unchanged fully cooled window and 0.025 s step, $\Delta E_{aux,fb}=E_{aux}(\mathrm{FC\_FB})-E_{aux}(\mathrm{FC\_OL})$ is $-10.003$, $-9.362$ and $-9.406$ J for Nominal, Joint and Qc30, respectively. Relative to each group's matched open-loop auxiliary input, these increments are $-0.467$, $-0.431$ and $-0.435$\%; startup time increases by 0.0202, 0.0184 and 0.0183 s. Table~\ref{tab:startupresources} and Fig.~\ref{fig:resources} put these paired results alongside the onset comparison. Feedback remains a small auxiliary-energy increment for the three examined vectors at the prescribed window and gains.

'''+needle,1)
    doc=doc.replace('Delayed heating shifts demand from auxiliary electricity toward reaction hydrogen and waiting time. Its large heater reduction from early uniform 125 W heating corresponds to a much smaller model net-input change when thermoneutral reaction energy and electrical output are included. Matched-window feedback contributes approximately half a percent of auxiliary input,',
        r'Delayed heating shifts demand from auxiliary electricity toward reaction hydrogen and waiting time for all three onset-comparison vectors. The net-input difference changes from $-10.47$ J for Nominal to $+7.48$ J for Joint and $+4.59$ J for Qc30, so its sign depends on the coefficients. Matched-window feedback reduces auxiliary input by 0.431--0.467\% relative to matched open loop for these vectors,')
    abstract=r'''Heater placement, onset and handover determine how a fuel-cell stack uses limited reaction resources during cold startup. A through-plane water--ice--electrochemical model couples five cells, shared bipolar plates and separate endplates. Equal total power and matched heating windows distinguish spatial allocation from feedback. At 50 W, end-MEA heating advances nominal startup by 2.76 s and reduces auxiliary electricity by approximately 138 J; the advantage persists across the examined concentration multipliers and loading-memory variations. Endplates store most sensible heat capacity and remain cold at the first MEA zero crossing. Applying 50 W directly to them instead exhausts the reaction-charge budget. Joint fits use the $-20\,^{\circ}$C training record; cross-temperature validation at $-25\,^{\circ}$C informs retention of the supplied nominal reference. Across Nominal, Joint and Qc30 vectors, delayed heating saves about 43\% auxiliary electricity while increasing reaction hydrogen and waiting time. Its much smaller net-input difference changes sign, from $-10.47$ to $+7.48$ and $+4.59$ J. Matched-window feedback reduces auxiliary input by 0.431--0.467\% relative to open loop, and a simple temperature gate closely reproduces the nominal full controller. All tested continuations complete 30 s, but warm operation depends on load, gate band and inherited state. After end-MEA startup, gated holding saves 27.7\% auxiliary electricity at 0.1401 A cm$^{-2}$; at 0.08 A cm$^{-2}$ both holding laws permit renewed subzero means. These comparisons connect heater selection to reaction resources, thermal placement, control complexity and the required operating state.'''
    doc=re.sub(r'(?<=\\begin\{abstract\}\n).*?(?=\n\\end\{abstract\})',lambda m:abstract,doc,flags=re.S)
    # Only literal LaTeX escapes are written to the generated file.
    return doc
