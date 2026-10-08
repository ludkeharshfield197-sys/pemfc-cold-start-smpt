"""Apply the final editorial and equation changes to the integrated manuscript."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent

def apply_author_declarations(doc):
    metadata = json.loads((ROOT / 'submission/author_metadata.json').read_text(encoding='utf-8'))
    funding = metadata['funding'].replace('“', "``").replace('”', "''")
    credit = metadata['credit'].replace('–', '--')
    doc = re.sub(r'(\\section\*\{Funding\}\n).*?(?=\\section\*\{CRediT)', lambda m: m[1] + funding + '\n', doc, flags=re.S)
    doc = re.sub(r'(\\section\*\{CRediT authorship contribution statement\}\n).*?(?=\\section\*\{Declaration of competing interest)', lambda m: m[1] + credit + '\n', doc, flags=re.S)
    return doc

def keep_short_tables_together(doc):
    def convert(match):
        cols, content = match.groups()
        if not any('\\label{tab:' + label + '}' in content for label in ['resolutiondiff', 'resolutionabs', 'physical', 'handover', 'holdresources', 'loading']):
            return match.group(0)
        caption, rest = content.split(r'\toprule', 1)
        header, rest = rest.split(r'\endfirsthead', 1)
        _, rows = rest.split(r'\endhead', 1)
        rows = rows.replace(r'\bottomrule\endfoot', '')
        return (r'\begin{table}[htbp]\centering\footnotesize\setlength{\tabcolsep}{3pt}' + '\n'
                + caption.rstrip().removesuffix('\\\\') + '\n'
                + r'\begin{tabular}{' + cols + r'}\toprule' + header + rows
                + r'\bottomrule\end{tabular}\end{table}')
    return re.sub(r'\\begingroup\\footnotesize\\setlength\{\\tabcolsep\}\{3pt\}\\begin\{longtable\}\{([^}]+)\}\n(.*?)\\end\{longtable\}\\endgroup', convert, doc, flags=re.S)

def revise_text(doc):
    begin = doc.index('Transfers to liquid or ice depend on deviation')
    end = doc.index('The numerical vector has three inventory blocks', begin)
    doc = doc[:begin] + r"""For an adjoining membrane volume $m$ and porous volume $p$, let $G_m=2D_m/\Delta x_m$, $e_l=e(1)$, $e_i=e(\min(m_{v,sat,i}/m_{v,sat,l},1))$, $s_l=m_l/(\rho_l\varepsilon_0)$ and $f_i=\pos{1-s_i}$. The signed interface mass fluxes (kg m$^{-2}$ s$^{-1}$), positive from membrane to porous region, are
\begin{align}
F_{mv}&=\alpha_{mv}G_m[w_m-e(a)],\qquad
\alpha_{mv}=\begin{cases}0.001,&w_m\ge e(a),\\1,&w_m<e(a),\end{cases}\label{eq:interfaceclosures}\\
F_{ml}&=k_f\Delta x_m\left[\alpha_{ml}^{+}\pos{w_m-e_l}-\alpha_{ml}^{-}s_l\pos{e_l-w_m}\right],\nonumber\\
F_{mi}&=k_f\Delta x_m\mathbf1_{T_p<T_f}
\left[\alpha_{mi}^{+}f_i\pos{w_m-e_i}-\alpha_{mi}^{-}s_i\pos{e_i-w_m}\right].\nonumber
\end{align}
Each flux is divided by the receiving or donating volume thickness to obtain its local source. Vapor conversion within a porous volume uses
\begin{align}
S_{vl}&=k_f\left[\alpha_{vl}^{+}\pos{m_v-m_{v,sat,l}}
-\alpha_{vl}^{-}\min\{m_l,\pos{m_{v,sat,l}-m_v}\}\right],\label{eq:vaporclosures}\\
S_{vi}&=k_f\mathbf1_{T<T_f}\left[\alpha_{vi}^{+}f_i\pos{m_v-m_{v,sat,i}}
-\alpha_{vi}^{-}\min\{m_i,\pos{m_{v,sat,i}-m_v}\}\right].\nonumber
\end{align}
The coefficient pairs above specify $\alpha^{+}$ and $\alpha^{-}$. Freezing and melting follow the preceding $S_{li}$ expression. During each implicit water iteration, these transfers supply the donor coefficients; accepted transferred mass supplies the latent heat.

""" + doc[end:]
    old = 'The reversible voltage uses temperature and the supplied gas partial pressures, including the cathode concentration reduction.'
    new = r"""The reversible voltage is
\begin{align}
E_{rev,k}&=1.229-8.5\times10^{-4}(\bar T_k-298.15)
+\frac{R\bar T_k}{2F}\ln\left[\frac{p_0}{p_{ref}}\left(\frac{p_{O_2,k}}{p_{ref}}\right)^{1/2}\right],
\nonumber\\
p_{O_2,k}&=0.21p_0(1-J/J_{lim,k}).
\end{align}
where $p_{ref}=101325$ Pa and temperature is in kelvin."""
    doc = doc.replace(old, new)
    old = r'The least-squares workflow uses SciPy \cite{scipy}; exact coefficients are supplied with the executable configurations.'
    new = r"""The executable recalibration routine uses SciPy's trust-region reflective least-squares solver \cite{scipy}, with the supplied vector as its starting point and at most 40 function evaluations. Its optimization coordinates are $(\log_{10}j_{0,ref},\gamma_C,g,\tau,\eta_{c,0},Q_c,Q_r)$, with componentwise lower and upper bounds
\begin{equation}
\bm\theta_{lo}=(-0.5,0.5,0.1,0.5,0,0.5,0.1),\qquad
\bm\theta_{hi}=(3,2,4,20,0.8,30,10).
\end{equation}
The residual scales 0.045 V and 1.5 $^{\circ}$C balance the two response units. The comparisons reported here replay the supplied coefficients; recalibration is a separate executable option."""
    doc = doc.replace(old, new)
    doc = doc.replace(r'thermal-capacity factor $K$', r'thermal-capacity factor $\gamma_C$')
    old = 'Figure~\\ref{fig:combined} connects the startup resource choice to this subsequent requirement.'
    new = r"""Among the two gated combinations that maintain a warm interval, end startup plus holding uses 4980.36 J of auxiliary electricity, versus 5585.49 J for preheat plus holding, a 605.13 J reduction. Their combined model net inputs are 6696.34 and 5994.05 J, respectively: preheat is lower by 702.29 J when reaction input and electrical output are included. Thus the preferred warm combination depends on whether the objective is auxiliary electricity or model net input. Figure~\ref{fig:combined} shows this resource ordering together with the warm-state result."""
    doc = doc.replace(old, new)
    doc = doc.replace('Lines distinguish heater removal, fixed 30/50 W end holding and a temperature-gated 50 W maximum. The zero line identifies the warm-interval target.', 'Panels (a)--(d) compare heater removal, fixed 30/50 W end holding and a temperature-gated 50 W maximum. Panels (e)--(f) enlarge the near-freezing range for the fixed 50 W and gated policies after uniform and delayed startup. The zero line identifies the warm-interval target.')
    # Keep the numerical table columns while wrapping long headings.
    headers = {
        r'$Q$ (C cm$^{-2}$)': r'\shortstack{$Q$\\(C cm$^{-2}$)}',
        r'$\Delta T_{max}$ ($^{\circ}$C)': r'\shortstack{$\Delta T_{max}$\\($^{\circ}$C)}',
        r'$T_{min,end}$ ($^{\circ}$C)': r'\shortstack{$T_{min,end}$\\($^{\circ}$C)}',
        r'$E_{aux}$ (J)': r'\shortstack{$E_{aux}$\\(J)}',
        r'$E_{out}$ (J)': r'\shortstack{$E_{out}$\\(J)}',
        r'$E_{chem,tn}$ (J)': r'\shortstack{$E_{chem,tn}$\\(J)}',
        r'$m_{H_2}$ (mg)': r'\shortstack{$m_{H_2}$\\(mg)}',
        r'$E_{net}$ (J)': r'\shortstack{$E_{net}$\\(J)}',
        r'$V_{min}$ (V)': r'\shortstack{$V_{min}$\\(V)}',
    }
    for label in ['physical', 'startupresources', 'holdresources']:
        pos = doc.index('\\label{tab:' + label + '}')
        start = doc.rfind('\\begingroup', 0, pos) if label != 'startupresources' else doc.rfind('\\begin{table}', 0, pos)
        end = doc.index('\\end{longtable}\\endgroup' if label != 'startupresources' else '\\end{table}', pos)
        section = doc[start:end]
        for old, new in headers.items(): section = section.replace(old, new)
        for key in ['hold', 'out,op', 'net,op', 'aux,all', 'out,all', 'net,all']:
            section = section.replace('$E_{'+key+'}$ (J)', r'\shortstack{$E_{'+key+r'}$\\(J)}')
        doc = doc[:start] + section + doc[end:]
    doc = doc.replace('used on 3 and 6 October 2026', 'used on 3, 6 and 7 October 2026')
    doc = doc.replace('Insets resolve the unequal terminal times; power is zero after each startup and terminal cumulative energy is held constant.', 'The middle row resolves unequal terminal times on a millisecond clock measured from the first endpoint; power is zero after each startup and terminal cumulative energy is held constant.')
    # Manual numeric bibliography follows the first occurrence of each citation.
    start = doc.index('\\bibitem{')
    end = doc.index('\\end{thebibliography}')
    entries = re.findall(r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\Z)', doc[start:end], re.S)
    by_key = {key: '\\bibitem{' + key + '}' + body.strip() + '\n\n' for key, body in entries}
    order = list(dict.fromkeys(key.strip() for group in re.findall(r'\\cite\{([^}]+)\}', doc[:start]) for key in group.split(',')))
    order += [key for key, _ in entries if key not in order]
    doc = doc[:start] + ''.join(by_key[key] for key in order) + doc[end:]
    return apply_author_declarations(keep_short_tables_together(doc))

if __name__ == '__main__':
    from integrate_manuscript import main
    main()
