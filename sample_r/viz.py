import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def create_resynthesis_row(row_idx, fig, obj):

    audio_data = obj.data
    start = obj.start_index
    end = obj.end_index
    spectrum = obj.spectrum
    harmonics = obj.harmonics[:len(obj.harmonics)//2]
    single_cycle = obj.frame
    name = obj.name
    
    fig.add_trace(
        go.Scatter(y=audio_data, line=dict(color='rgb(0,100,255)')),
        row=row_idx, col=1
    )

    fig.add_vrect(
        x0=start, x1=end,
        fillcolor='rgb(0,50,255)', 
        opacity=0.1,
        layer="below", 
        line_width=0,
        row=row_idx, 
        col=1
    )

    fig.add_trace(
        go.Scatter(y=spectrum, line=dict(color='rgb(0,100,255)')),
        row=row_idx + 1, col=1
    )

    fig.add_trace(
        go.Bar(y=harmonics, marker_color='rgb(100,0,255)'),
        row=row_idx + 1, col=2
    )

    fig.add_trace(
        go.Scatter(y=single_cycle, line=dict(color='rgb(0,100,255)')),
        row=row_idx + 1, col=3
    )

    # Update Y-axis title for the row to identify the sample
    fig.update_yaxes(title_text=name, row=row_idx, col=1)

def generate_master_plot(audio_objects):
    """
    Loops through multiple audio objects and stacks them.
    audio_objects: A list of dictionaries containing the necessary data.
    """
    num_samples = len(audio_objects)
    # Each sample takes 2 rows
    total_rows = num_samples * 2
    
    titles = []
    for i, obj in enumerate(audio_objects):
        titles.append(f"{i}) {obj.name}") # Title for Row 1
        titles.extend(["Spectrum", "Harmonics", "Cycles"])                   # Empty titles for Row 2 (3 columns)

    # Set up specs
    specs = []
    for _ in range(num_samples):
        specs.append([{"colspan": 3}, None, None]) 
        specs.append([{}, {}, {}])             

    fig = make_subplots(
        rows=total_rows, 
        cols=3,
        subplot_titles=titles, # Apply the refined list
        specs=specs,
    )

    for i, ann in enumerate(fig.layout.annotations):
        ann.update(
            xref=f"x{i+1 if i > 0 else ''} domain",
            yref=f"y{i+1 if i > 0 else ''} domain",
            x=0.98,              # Right side
            y=0.95,              # Top side
            xanchor="right",
            yanchor="top",
            showarrow=False,
            bgcolor="rgba(255, 255, 255,200)", 
            borderpad=4,
            font=dict(size=12, color="rgba(0, 0, 0, 0.9)")
        )    

    for i, obj in enumerate(audio_objects):
        # Calculate row offset (1, 3, 5...)
        start_row = (i * 2) + 1
        create_resynthesis_row(
            start_row,
            fig,
            obj
        )

    for i in range(1, num_samples):
        # Calculate Y position: 1 is top, 0 is bottom.
        # We want the line exactly between the blocks.
        y_pos = 1 - (i / num_samples) # Tiny offset to center in the gap
        
        fig.add_shape(
            type="line",
            xref="paper", yref="paper", # This is the magic part
            x0=0, x1=1,                 # Stretch from far left to far right
            y0=y_pos, y1=y_pos,
            line=dict(
                color="rgba(255, 255, 255, 0.3)" if "dark" in fig.layout.template else "gray",
                width=2,
                dash="dash"
            ),
        )

    fig.update_layout(height=400 * num_samples, showlegend=False, )
    return fig