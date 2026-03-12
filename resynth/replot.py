import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import numpy as np

def audio_plot(d):
    
    fig = make_subplots(
        rows=1,
        cols=4,
        subplot_titles=("Audio", f"Frequency Spectrum", "Harmonics","Wavetable")
    )

    # Line plot
    fig.add_trace(
        go.Scatter(
            x=np.arange(d.data.size),
            y=d.data,
            mode="lines",
            marker=dict(color='rgb(51, 98, 163)')
        ),
        row=1,
        col=1
    )

    # Bar plot 1
    fig.add_trace(
        go.Scatter(
            x=d.nfreqs,
            y=d.nspectrum,
            mode="lines",
            marker=(dict(color='rgb(163, 60, 60)'))
        ),
        row=1,
        col=2
    )

    # Bar plot 2
    fig.add_trace(
        go.Bar(
            x=np.arange(d.hspectrum.size)+ 1,
            y=d.hspectrum,
            marker=(dict(color='rgb(31, 161, 91)'))
        ),
        row=1,
        col=3
    )

    fig.add_trace(
        go.Scatter(
            x=np.arange(d.framesize),
            y=d.frame,
            mode="lines",
            marker=(dict(color='rgb(101, 39, 156)'))
        ),
        row=1,
        col=4
    )

    # fig.update_xaxes(title_text=x_title)
    # fig.update_yaxes(title_text=y_title)

    fig.update_layout(
        title=d.name,
        height=400
    )

    return fig

def stack_plots(data):
    figs = []
    subplot_titles =["" for x in range(4 * len(data))]
    titles = [x.name for x in data]
    for i, s in enumerate(titles):
        subplot_titles[i*4] = titles[i]
    for d in data:
        figs.append(audio_plot(d))
    fig = make_subplots(rows = len(figs), cols =len(figs[0].data), subplot_titles=subplot_titles)
    for r, f in enumerate(figs):
        for c, d in enumerate(f.data):
            fig.add_trace(d,row=r+1,col=c+1)
        

    fig.update_layout(
        height=400 * len(figs),
        showlegend=False
    )
    
    return fig