"""Regenerate the paper-aligned figure structures from public HHI results.

Figure 1: separate China, Japan and USA panels, with geographic and industry lines.
Figure 2: country-coloured, hollow circles (excluding C19) and filled diamonds (C19).
Figure 3: separate China, Japan and USA panels, with annual mean joint HHI.

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
    for image in sorted(out.glob('*.png')):
        print(f'{image.relative_to(root)}: {image.stat().st_size:,} bytes')

if __name__ == '__main__':
    generate()
