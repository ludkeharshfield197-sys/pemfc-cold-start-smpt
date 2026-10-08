"""Within-vector onset and matched-feedback differences from actual endpoints."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'program_event_v2/results/review_revision'

def comparison_tables():
    config = json.loads((ROOT / 'program_event_v2/revision/experiment_config.json').read_text(encoding='utf-8'))
    nominal = {'Uniform125': ROOT / 'program_event_v2/results/revision/D_Uniform125.json',
               'FC_FB': ROOT / 'program_event_v2/results/revision/D_Delayed.json',
               'FC_OL': ROOT / config['baseline_sources']['同开启同功率开环_None']}
    rows = []
    for vector in ['Nominal', 'Joint', 'Qc30']:
        for strategy in ['Uniform125', 'FC_FB', 'FC_OL']:
            path = nominal[strategy] if vector == 'Nominal' else DEST / f'R_onset_{vector}_{strategy}_h0025.json'
            r = json.loads(path.read_text(encoding='utf-8'))['result']
            q = r['charge_C_cm2']
            chem = 1.48 * 125 * q
            # The existing nominal open-loop file stores cell reaction integrals;
            # use the manuscript's exact thermoneutral balance for its output.
            out = chem - sum(r['cell_reaction_J']) if vector == 'Nominal' and strategy == 'FC_OL' else r['output_energy_J']
            # Stoichiometric consumed hydrogen, five 25 cm² cells, F=96485 C/mol.
            h2 = 125 * q / (2 * 96485) * 2.016e3
            rows.append(dict(vector=vector, strategy=strategy, status=r['status'], time_s=r['time_s'],
                             charge_C_cm2=q, hydrogen_mg=h2, Eaux_J=r['total_energy_J'],
                             Echem_tn_J=chem, Eout_J=out,
                             Enet_J=r['total_energy_J'] + chem - out,
                             Vmin_V=r['min_voltage_V'], max_spread_C=r['max_delta_T_C'],
                             source=path.relative_to(ROOT).as_posix()))
    endpoints = pd.DataFrame(rows)
    pairs = []
    for vector in ['Nominal', 'Joint', 'Qc30']:
        z = endpoints[endpoints.vector == vector].set_index('strategy')
        u, f, o = [z.loc[s] for s in ['Uniform125', 'FC_FB', 'FC_OL']]
        pairs.append(dict(vector=vector, outcomes='/'.join(z.status),
                          onset_delta_time_s=f.time_s-u.time_s,
                          onset_delta_Eaux_J=f.Eaux_J-u.Eaux_J,
                          onset_aux_saving_pct=100*(u.Eaux_J-f.Eaux_J)/u.Eaux_J,
                          onset_delta_Q_C_cm2=f.charge_C_cm2-u.charge_C_cm2,
                          onset_delta_hydrogen_mg=f.hydrogen_mg-u.hydrogen_mg,
                          onset_delta_Enet_J=f.Enet_J-u.Enet_J,
                          feedback_delta_time_s=f.time_s-o.time_s,
                          feedback_delta_Eaux_J=f.Eaux_J-o.Eaux_J,
                          feedback_relative_pct=100*(f.Eaux_J-o.Eaux_J)/o.Eaux_J))
    return endpoints, pd.DataFrame(pairs)

if __name__ == '__main__':
    endpoints, pairs = comparison_tables()
    endpoints.to_csv(DEST / 'onset_parameter_endpoints.csv', index=False)
    pairs.to_csv(DEST / 'onset_parameter_differences.csv', index=False)
    print(endpoints.to_string(index=False))
    print(pairs.to_string(index=False))
