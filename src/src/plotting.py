import plotly.graph_objects as go
import plotly.express as px

import pandas as pd
import numpy as np
import math

from .benchmarks import BENCHMARK_COLORS

MARKERS = {
    'Aligned Few-wall CNTs': {
        'marker_symbol': 'diamond',
        'marker_color': '#305ba9'
    },
    'Aligned Multiwall CNTs': {
        'marker_symbol': 'triangle-up',
        'marker_color': '#d12232'
    },
    'Amorphous carbon': {
        'marker_symbol': 'circle',
        'marker_color': 'gray'
    },
    'Carbon Fiber': {
        'marker_symbol': 'square',
        'marker_color': 'black'
    },
    'Conductive Polymer': {
        'marker_symbol': 'square',
        'marker_color': '#cc3b8c'
    },
    'Diamond': {
        'marker_symbol': 'circle',
        'marker_color': 'gray'
    },
    'GIC': {
        'marker_symbol': 'square',
        'marker_color': 'black'
    },
    'Glassy Carbon': {
        'marker_symbol': 'circle',
        'marker_color': 'gray'
    },
    'Graphene Nanoribbon': {
        'marker_symbol': 'circle',
        'marker_color': 'gray'
    },
    'Individual Bundle': {
        'marker_symbol': 'cross',
        'marker_color': '#305ba9'
    },
    'Individual FWCNT': {
        'marker_symbol': 'x',
        'marker_color': '#305ba9'
        
    },
    'Individual Multiwall CNTs': {
        'marker_symbol': 'star',
        'marker_color': '#d12232'
    },
    'Metal': {
        'marker_symbol': 'circle',
        'marker_color': 'gray'
    },
    'Metal CNT Composite': {
        'marker_symbol': 'circle',
        'marker_color': 'gray'
    },
    'Mott minimum conductivity': {
        'marker_symbol': 'circle',
        'marker_color': 'gray'
    },
    'Paper': {
        'marker_symbol': 'circle',
        'marker_color': 'gray'
    },
    'Single crystal graphite': {
        'marker_symbol': 'square',
        'marker_color': 'black'
    },
    'Superconductor': {
        'marker_symbol': 'circle',
        'marker_color': 'gray'
    },
    'Synthetic fiber': {
        'marker_symbol': 'circle',
        'marker_color': 'gray'
    },
    'Unaligned Few-wall CNTs': {
        'marker_symbol': 'circle',
        'marker_color': '#61b84e'
    },
    'Unaligned multiwall CNTs': {
        'marker_symbol': 'square',
        'marker_color': '#ee9752'
    },
    'NaN': {
        'marker_symbol': 'circle',
        'marker_color': 'gray'
    }
}

def construct_custom_strip(df, x, y):
    traces = []

    # one trace per category/dope combo, with custom color/symbol
    for m in df['Category'].unique():
        for d in df['Doped or Acid Exposure (Yes/ No)'].unique():
        
            mask = (df['Category'] == m) & \
                (df['Doped or Acid Exposure (Yes/ No)'] == d)

            markers = {k.replace('marker_', ''):v for k,v in MARKERS[m].items()}
            markers['opacity'] = 0.8
            
            if d == 'No':
                markers['symbol'] += '-open'
                markers['opacity'] = 0.5

            traces.append({
                'x': df.loc[mask, x],
                'y': df.loc[mask, y],
                'name': m, 
                'marker': markers,
                'customdata': df.loc[mask, 'Reference'],
            })

    # Update (add) trace elements common to all traces.
    for t in traces:
        t.update({'type': 'box',
                  'boxpoints': 'all',
                  'fillcolor': 'rgba(255,255,255,0)',
                  'hoveron': 'points',
                  'hovertemplate': '%{customdata}',
                  'line': {'color': 'rgba(255,255,255,0)'},
                  'pointpos': 0,
                  'showlegend': True})
    
    return traces


def construct_fig1(df, x, y, log, squash, bm):
    
    df = df[df[x].notnull() & df[y].notnull()]
    
    fig = go.Figure()
    
    if squash:
        print('squashing')
        fig.add_trace(
            go.Box(
                y=df[y],
                name='All',
                boxpoints='all',
                fillcolor='white',
                pointpos=0,
                marker={'color': 'black'},
                line={'color':'black'},
                customdata=df['Reference'],
                hovertemplate='%{customdata}'
            )
        )
        
    else:
    
        for v in df[x].unique():
            tracedf = df.loc[df[x] == v]

            fig.add_trace(
                go.Box(
                    y=tracedf[y],
                    name=v,
                    # Don't show or hover on outlier points
                    marker={'opacity':0},
                    hoveron='boxes',
                    fillcolor='white',
                    line={'color': 'gray'},
                )
            )

        fig.add_traces(construct_custom_strip(df, x, y))
        
    if bm:
        for m,v in bm.items():
            if np.isnan(v):
                continue

            fig.add_hline(
                y=v,
                line={
                    'color': BENCHMARK_COLORS[m],
                    'dash': 'dash'
                },
                annotation_text=m, 
                annotation_position='right',
                annotation_y=math.log(v,10) if log else v
            )
    
    fig.update_yaxes(
        type='log' if log else 'linear',
        nticks=10
    )
    
    fig.update_layout(
        showlegend=False, 
        yaxis_title=y,
        xaxis_title=x
    )
    
    return fig

def construct_fig2(df, x, y, logx, logy, squash, bm):
    
    df = df[df[x].notnull() & df[y].notnull()]
    
    symbol = color = 'Category'
    symbol_map = {k:v['marker_symbol'] for k,v in MARKERS.items()}
    color_map = {k:v['marker_color'] for k,v in MARKERS.items()}
    
    fig = px.scatter(
        df,
        x=x, 
        y=y, 
        log_x=logx, 
        log_y=logy,
        symbol=symbol,
        symbol_map=symbol_map,
        color=color,
        color_discrete_map=color_map,
        hover_data=['Reference']
    )
    
    if squash:
        fig.update_traces(marker={'symbol':'circle', 'color':'black'})
        fig.update_layout(showlegend=False)
        
        # todo: Graph 2 Benchmarks
    if bm:
        bm = pd.DataFrame(bm).T.reset_index()
        bm.dropna(inplace=True)
        
        for i,r in bm.iterrows():
            fig.add_trace(
                go.Scatter(
                    mode='markers',
                    x=[r[0]],
                    y=[r[1]],
                    marker=dict(
                        color='black',
                        size=20,
                        line=dict(
                            color='black',
                            width=2
                        ),
                        symbol='x-thin'
                    ),
                    showlegend=True,
                    name=r['index']
                )
            )
    
    return fig