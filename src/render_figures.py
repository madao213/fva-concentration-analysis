"""Regenerate the paper-aligned figure structures from public HHI results.

Figure 1: separate China, Japan and USA panels, with geographic and industry lines.
Figure 2: country-coloured, hollow circles (excluding C19) and filled diamonds (C19).
Figure 3: separate China, Japan and USA panels, with annual mean joint HHI.\nFigure 4: C26 geographic, industry and joint HHI for 2018–2020.\nFigure 5: C26 top three 2019 source-pair shares, at manuscript precision.

These are regenerated figures, not raster copies taken from the manuscript.
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
EXPORTERS = [('CHN', 'China'), ('JPN','Japan'), ('USA','USA')]
PALETTE = {'CHN':'#ee9c57','JPN':'#b69c23','USA':'#3daea7'}
BLUE, ORANGE = '#4472c4', '#ed7d31'

def line_panels(annual, columns, out, ylim, yticks=None):
    fig, axes = plt.subplots(1,3,figsize=(11.5,3.5),sharey=True)
    for ax,(code,title) in zip(axes, EXPORTERS):
        sub = annual.loc[annual['exporter'].eq(code)].sort_values('year')
        for column,label,color in columns:
            ax.plot(sub.year, sub[column],color=color,linewidth=1.9,label=label)
        ax.set_title(title,fontweight='bold',fontsize=12)
        ax.set_xlim(1995,2022)
        ax.set_ylim(*ylim)
        if yticks is not None: ax.set_yticks(yticks)
        ax.set_xticks(range(1995,2023,3))
        ax.tick_params(axis='x',labelrotation=90,labelsize=8)
        ax.tick_params(axis='y',labelsize=8)
        ax.grid(axis='y',alpha=.22)
        ax.spines[['top','right']].set_visible(False)
    handles,labels = axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=len(labels),frameon=False,fontsize=9,
               bbox_to_anchor=(.5,-.01))
    fig.subplots_adjust(left=.06,right=.99,top=.87,bottom=.27,wspace=.18)
    fig.savefig(out,dpi=200,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def scatter(panel,out):
    fig,ax=plt.subplots(figsize=(10.5,5.0))
    for code,title in EXPORTERS:
        rows=panel.loc[panel.exporter.eq(code)]
        common=rows.loc[rows.export_industry.ne('C19')]
        c19=rows.loc[rows.export_industry.eq('C19')]
        ax.scatter(common.geo_hhi,common.industry_hhi,facecolors='none',edgecolors=PALETTE[code],
                   linewidths=.65,s=24,alpha=.52,label=f'{code}, excluding C19',marker='o')
        ax.scatter(c19.geo_hhi,c19.industry_hhi,c=PALETTE[code],s=28,alpha=.95,
                   label=f'{code}, C19',marker='D',linewidths=0)
    ax.set(xlabel='Geographic HHI',ylabel='Source-industry HHI',xlim=(.025,.25),ylim=(0,.7))
    ax.set_xticks([.025,.05,.075,.1,.125,.15,.175,.2,.225,.25])
    ax.grid(alpha=.25)
    ax.set_axisbelow(True)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.12),ncol=3,fontsize=8,frameon=False,
              columnspacing=.8,handletextpad=.3)
    fig.subplots_adjust(bottom=.21,left=.09,right=.98,top=.98)
    fig.savefig(out,dpi=200,bbox_inches='tight',facecolor='white')
    plt.close(fig)


def c26_line_panels(panel, out):
    """Figure 4: 2018–2020 C26 concentration by exporter."""
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.7), sharey=True)
    lines = [
        ('geo_hhi', 'Geographic HHI', BLUE),
        ('industry_hhi', 'Source-industry HHI', ORANGE),
        ('joint_hhi', 'Joint HHI', '#e6b800'),
    ]
    for ax, (code, title) in zip(axes, EXPORTERS):
        subset = panel.loc[
            (panel.exporter == code) &
            (panel.export_industry == 'C26') &
            (panel.year.between(2018, 2020))
        ].sort_values('year')
        if len(subset) != 3:
            raise ValueError(f'Expected three C26 annual rows for {code}')
        for column, label, color in lines:
            ax.plot(subset.year, subset[column], label=label, color=color, linewidth=2)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xticks([2018, 2019, 2020])
        ax.set_xlim(2018, 2020)
        ax.set_ylim(0, 0.20)
        ax.set_yticks([0, .05, .10, .15, .20])
        ax.grid(axis='y', alpha=.20)
        ax.spines[['top', 'right']].set_visible(False)
        ax.tick_params(labelsize=9)
    fig.legend(*axes[0].get_legend_handles_labels(), loc='lower center',
               bbox_to_anchor=(.5, -.01), ncol=3, frameon=False, fontsize=9)
    fig.subplots_adjust(left=.06, right=.99, top=.88, bottom=.25, wspace=.14)
    fig.savefig(out, dpi=220, bbox_inches='tight', facecolor='white')
    fig.savefig(out.with_suffix('.svg'), bbox_inches='tight', facecolor='white')
    plt.close(fig)


def c26_source_pair_bars(pairs, out):
    """Figure 5: published 2019 top-three shares, in all three exporters."""
    required = {'exporter','year','rank','source_economy','source_industry','share'}
    if not required.issubset(pairs.columns):
        raise ValueError('Missing C26 source pair display columns')
    if len(pairs) != 9 or not pairs.year.eq(2019).all():
        raise ValueError('Expected nine source pairs from 2019')
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.7), sharex=True)
    for ax, (code, title) in zip(axes, EXPORTERS):
        sub = pairs.loc[pairs.exporter.eq(code)].sort_values('rank')
        if len(sub) != 3 or sub['rank'].tolist() != [1, 2, 3]:
            raise ValueError(f'Expected ranks 1 to 3 for {code}')
        labels = (sub.source_economy + ' / ' + sub.source_industry).tolist()
        values = (100 * sub.share).to_numpy()
        bars = ax.barh(range(3), values, color=BLUE, height=.5)
        ax.set_yticks(range(3), labels, fontsize=8)
        ax.invert_yaxis()
        ax.set_title(f'{title} (2019)', fontsize=12, fontweight='bold')
        ax.set_xlim(0, 10)
        ax.set_xticks([0, 2, 4, 6, 8, 10],
                      ['0%', '2%', '4%', '6%', '8%', '10%'])
        ax.grid(axis='x', alpha=.2)
        ax.set_axisbelow(True)
        ax.spines[['top','right','left']].set_visible(False)
        ax.tick_params(axis='y', length=0)
        for bar, value in zip(bars, values):
            ax.text(value + .15, bar.get_y() + bar.get_height()/2,
                    f'{value:.2f}%', ha='left', va='center', fontsize=8)
    fig.subplots_adjust(left=.13, right=.99, top=.85, bottom=.16, wspace=.67)
    fig.savefig(out, dpi=220, bbox_inches='tight', facecolor='white')
    fig.savefig(out.with_suffix('.svg'), bbox_inches='tight', facecolor='white')
    plt.close(fig)

def generate(root=ROOT):
    annual=pd.read_csv(root/'results/annual_hhi.csv')
    panel=pd.read_csv(root/'results/industry_year_hhi.csv')
    if len(annual)!=84 or len(panel)!=1344:
        raise ValueError('Unexpected observation count')
    out=root/'figures'
    out.mkdir(parents=True,exist_ok=True)
    line_panels(annual,[('equal_geo_hhi','Mean geographic HHI',BLUE),
                        ('equal_industry_hhi','Mean source-industry HHI',ORANGE)],
                out/'figure1_annual_geo_industry_hhi.png',(0,.15),[0,.03,.06,.09,.12,.15])
    scatter(panel,out/'figure2_geo_vs_industry_hhi.png')
    line_panels(annual,[('equal_joint_hhi','Mean joint HHI',BLUE)],
                out/'figure3_annual_joint_hhi.png',(0,.045),[0,.01,.02,.03,.04])
    c26_line_panels(panel, out/'figure4_c26_concentration_2018_2020.png')
    pairs=pd.read_csv(root/'results/c26_source_pairs_2019.csv')
    c26_source_pair_bars(pairs, out/'figure5_c26_top_source_pairs_2019.png')
    for image in sorted(out.glob('*.png')):
        print(f'{image.relative_to(root)}: {image.stat().st_size:,} bytes')

if __name__ == '__main__':
    generate()
