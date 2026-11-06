"""Render the matched metric and genuinely frozen regional transfer."""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/palmer_signy_diet_external_v1'


def main():
    annual = pd.read_csv(OUT / 'annual_pair_comparison.csv')
    transfer = pd.read_csv(OUT / 'signy_to_palmer_transport.csv')
    summary = json.loads((OUT / 'summary.json').read_text())
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'pdf.fonttype': 42, 'savefig.facecolor': 'white'})
    fig = plt.figure(figsize=(12, 9.4), layout='constrained')
    grid = fig.add_gridspec(2, 2, height_ratios=[1, 1.02])
    a, b, c = fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1]), fig.add_subplot(grid[1, :])
    colors = {'Signy': '#246A9B', 'Palmer': '#CD623C'}
    for region, part in annual.groupby('region', sort=False):
        stats = summary['regions'][region]
        xs = np.linspace(part.sic_aug_nov.min(), part.sic_aug_nov.max(), 100)
        ys = 100 * (stats['intercept'] + stats['slope_per_10pp'] * xs / 10)
        a.scatter(part.sic_aug_nov, part.distance * 100, s=55, color=colors[region],
                  label=f'{region}: {len(part)} seasons', zorder=3)
        a.plot(xs, ys, color=colors[region], lw=1.6)
        if region == 'Signy':
            for row in part.itertuples():
                a.annotate(str(row.year)[-2:], (row.sic_aug_nov, row.distance * 100),
                           xytext=(5, 4), textcoords='offset points', fontsize=8, color=colors[region])
        else:
            b.scatter(part.sic_aug_nov, part.distance * 100, s=65, color=colors[region], zorder=3)
            b.plot(xs, ys, color=colors[region], lw=1.6)
            for row in part.itertuples():
                b.annotate(str(row.year), (row.sic_aug_nov, row.distance * 100),
                           xytext=(5, 6), textcoords='offset points', fontsize=9)
    a.set(title='A  Matched diet metric, same vertical scale', xlabel='Antecedent August-November SIC (%)',
          ylabel='Absolute difference in mean fish fraction (pp)', xlim=(17, 72), ylim=(-2, 91))
    a.legend(loc='upper left', frameon=False)
    a.text(.03, .66, 'Signy r = 0.782\nPalmer r = 0.207', transform=a.transAxes, fontsize=10,
           bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': .9})
    b.set(title='B  Palmer only: expanded vertical scale', xlabel='Antecedent August-November SIC (%)',
          ylabel='Absolute difference in mean fish fraction (pp)', xlim=(24, 74), ylim=(-.15, 5.1))
    b.text(.03, .94, 'Exact permutation p = 0.778\nLeave-one-season r: -0.318 to 0.737',
           va='top', transform=b.transAxes, fontsize=9)
    x = np.arange(len(transfer))
    c.plot(x, transfer.predicted_distance * 100, marker='s', color=colors['Signy'], lw=1.8,
           label='Signy-fitted line, applied without refitting')
    c.plot(x, transfer.distance * 100, marker='o', color=colors['Palmer'], lw=1.8,
           label='Observed Palmer difference')
    c.axhline(transfer.training_mean_prediction.iloc[0] * 100, color='#666666', ls='--', lw=1.5,
              label='Signy training-mean baseline')
    outside = ~transfer.in_training_ice_range
    c.scatter(x[outside], transfer.loc[outside, 'predicted_distance'] * 100,
              marker='s', s=150, facecolors='none', edgecolors='#111111', zorder=5)
    c.annotate('SIC 0.33 pp above training maximum',
               (4, transfer.predicted_distance.iloc[4] * 100), xytext=(5, 10),
               textcoords='offset points', ha='center', fontsize=9)
    c.set(title='C  External prediction: all six Palmer seasons are overpredicted',
          xlabel='Palmer breeding season', ylabel='Diet difference (pp)', ylim=(-4, 82),
          xticks=x, xticklabels=[f'{y}/{str(y + 1)[-2:]}' for y in transfer.year])
    c.legend(loc='upper left', frameon=False, fontsize=9)
    c.text(.98, .96, 'MAE: fitted line 40.60 pp; training mean 34.97 pp\n'
           'Within training SIC range (5 seasons): 35.38 vs 34.74 pp',
           transform=c.transAxes, ha='right', va='top', fontsize=9)
    for ax in (a, b, c):
        ax.grid(axis='y', alpha=.18)
        ax.set_axisbelow(True)
    fig.suptitle('Signy diet-separation model does not transfer unadjusted to Palmer',
                 fontsize=16, fontweight='bold')
    fig.get_layout_engine().set(rect=(0, .055, 1, .94))
    fig.text(.02, .012, 'Metric: |Gentoo - Adelie| in equal-stomach mean fish fraction among food. '
             'Two regions; seasons analysed separately.\n'
             'Sources: BAS Signy diet records; Pickett et al. (2018), Table 1, doi:10.1002/ece3.4445; '
             'OSI SAF SIC. Lines are descriptive OLS fits.', fontsize=8, color='#444444')
    fig.savefig(OUT / 'Figure_1_external_comparison.png', dpi=220)
    fig.savefig(OUT / 'Figure_1_external_comparison.pdf')
    plt.close(fig)


if __name__ == '__main__':
    main()
