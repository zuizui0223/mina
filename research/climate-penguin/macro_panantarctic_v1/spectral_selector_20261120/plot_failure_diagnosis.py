"""Plot paired same-image diagnostics; cohorts are intentionally separate."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent

def main():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout='constrained')
    configs = [
        ('failure_reference_selection_contrasts.csv', 'minimum_group_rows',
         ['recovery_concordant', 'recovery_other'],
         ['Reference-concordant', 'Other original positives'],
         'A  Same training-era images\n43 sites; 47 site-scenes; 6 blocks'),
        ('failure_core_contrasts.csv', 'minimum_rows_per_group',
         ['inside_core_recovery', 'outside_core_recovery'],
         ['3 x 3 positive interior', 'Other original positives'],
         'B  Same 2008–2012 images\n24 sites; 262 site-scenes; 5 blocks')]
    for ax, (file, minimum, variables, labels, title) in zip(axes, configs):
        data = pd.read_csv(ROOT / file)
        d = data[data[minimum].eq(1)].set_index('variable').loc[variables]
        y = d.estimate.to_numpy() * 100
        err = [y - d.lower95.to_numpy()*100, d.upper95.to_numpy()*100-y]
        ax.errorbar([0, 1], y, yerr=err, fmt='o', capsize=6, color='#186c83', ms=8)
        for x, value in enumerate(y):
            ax.annotate(f'{value:.1f}%', (x, value), xytext=(9, 0), textcoords='offset points')
        ax.set(xticks=[0, 1], xticklabels=labels, ylim=(0, 105), xlim=(-.4, 1.6),
               ylabel='Recovery of original positives (%)', title=title)
        ax.grid(axis='y', alpha=.2)
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Fixed threshold: post-hoc diagnosis, not a new validation pass', fontsize=13)
    fig.savefig(ROOT / 'failure_diagnosis.png', dpi=180)
    path = ROOT / 'failure_diagnosis.svg'
    fig.savefig(path)
    path.write_text('\n'.join(x.rstrip() for x in path.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8', newline='\n')
    plt.close(fig)

if __name__ == '__main__':
    main()
