"""Six fresh startups with existing fitted vectors and unchanged strategy commands."""
import copy
import json
import sys
from run_review_revision_experiments import BASE, DEST, REV, run

P = DEST / 'parameters/joint'

def configurations():
    fits = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(P.glob('joint_seed*.json'))]
    vectors = {'Joint': min((v for v in fits if v['success']), key=lambda v: v['objective']),
               'Qc30': json.loads((P / 'extended_Qc30.json').read_text(encoding='utf-8'))}
    uniform = json.loads((REV / 'D_Uniform125.json').read_text(encoding='utf-8'))['task']
    strategies = {'Uniform125': uniform, 'FC_FB': BASE['strategies']['FC_FB'],
                  'FC_OL': BASE['strategies']['FC_OL']}
    cases = []
    for label, fit in vectors.items():
        for strategy, source in strategies.items():
            task = copy.deepcopy(source)
            task.update(theta=fit['theta'], save_state=False)
            cases.append(dict(name=f'R_onset_{label}_{strategy}_h0025',
                              group='onset_parameters', vector=label, strategy=strategy, task=task))
    return dict(vectors=vectors, cases=cases,
                window_rule='The existing nominal FC preset onset/cutoff and clipped base vector are retained for both laws and both parameter vectors; no retuning.',
                feedback_percent_definition='100*(Eaux(FC_FB)-Eaux(FC_OL))/Eaux(FC_OL)',
                onset_net_definition='Enet(FC_FB)-Enet(Uniform125)')

if __name__ == '__main__':
    config = configurations()
    (P / 'onset_comparisons.json').write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    label = sys.argv[1] if len(sys.argv) > 1 else 'all'
    for case in config['cases']:
        if label == 'all' or case['vector'] == label:
            run(case)
