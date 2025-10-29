import streamlit as st
import random
import math
import numpy as np
import matplotlib.pyplot as plt
import io

# ----------------------------------------------------
# Original functions from the code are used as is
# ----------------------------------------------------

def get_palette(mode="pastel", k=5):
    """
    Return a palette of k colors based on the chosen mode.
    Modes: "pastel", "vivid", "neon", "mono", "earth"
    """
    palette = []
    
    if mode == "pastel":
        palette = [(0.6 + 0.4*random.random(), 0.6 + 0.4*random.random(), 0.6 + 0.4*random.random()) for _ in range(k)]
    elif mode == "vivid":
        palette = [(random.random(), random.random(), random.random()) for _ in range(k)]
    elif mode == "neon":
        neon_base = [(1,0,0), (0,1,0), (0,0,1), (1,1,0), (1,0,1), (0,1,1)]
        palette = [tuple(min(1, c + 0.2*random.random()) for c in random.choice(neon_base)) for _ in range(k)]
    elif mode == "mono":
        gray = random.random()
        palette = [(gray*random.uniform(0.5,1),)*3 for _ in range(k)]
    elif mode == "earth":
        earth_colors = [(0.6,0.4,0.2), (0.4,0.3,0.2), (0.5,0.35,0.25), (0.7,0.5,0.3)]
        palette = [random.choice(earth_colors) for _ in range(k)]
    else:
        palette = [(random.random(), random.random(), random.random()) for _ in range(k)]
    
    return palette

def shape(center=(0.5,0.5), r=0.1, points=1000, wobble=0.15, kind="blob", sides=random.randint(3,10), petals=random.randint(2,10)):
    """
    Generate coordinates for different shapes.
    kind: "blob", "polygon", "heart", "star", "flower"
    """
    t = np.linspace(0, 2*np.pi, points)
    
    if kind == "blob":
        radii = r * (1 + wobble*(np.random.rand(points)-0.5))
        x = center[0] + radii * np.cos(t)
        y = center[1] + radii * np.sin(t)
    elif kind == "polygon":
        # Random sides are determined each time the function is called.
        current_sides = random.randint(3, 10)
        angles = np.linspace(0, 2*np.pi, current_sides + 1)
        x = center[0] + r * np.cos(angles)
        y = center[1] + r * np.sin(angles)
    elif kind == "heart":
        x = center[0] + r * 16*np.sin(t)**3 / 16
        y = center[1] + r * (13*np.cos(t) - 5*np.cos(2*t) - 2*np.cos(3*t) - np.cos(4*t)) / 16
    elif kind == "star":
        n = 5
        angles = np.linspace(0, 2*np.pi, 2*n+1)
        radii = np.array([r, r/2]*n + [r])
        x = center[0] + radii * np.cos(angles)
        y = center[1] + radii * np.sin(angles)
    elif kind == "flower":
         # Random petals are determined each time the function is called.
        current_petals = random.randint(3, 10)
        radii = r * (1 + 0.3 * np.sin(current_petals*t))
        x = center[0] + radii * np.cos(t)
        y = center[1] + radii * np.sin(t)
    else: # fallback to blob
        radii = r * (1 + wobble*(np.random.rand(points)-0.5))
        x = center[0] + radii * np.cos(t)
        y = center[1] + radii * np.sin(t)
    
    return x, y

# ----------------------------------------------------
# Streamlit App UI Section
# ----------------------------------------------------

st.set_page_config(layout="wide")
st.title("Generative Abstract Poster with Variety Style and Shape")
st.info("Click the button below to generate a poster with a new theme!")

# Main generation button
if st.button("✨ Generate New Poster!", type="primary", help="A new theme is applied every time you click."):
    
    # 0. Initialize seed (different art for each button click)
    random.seed() 
    
    # 1. Select random theme (core logic from user's code)
    style = random.choice(["pastel", "vivid", "neon", "mono", "earth"])
    blob_shape = random.choice(["blob", "polygon", "heart", "star", "flower"])

    # Display the generated theme on the screen
    st.subheader(f"Current Theme: `{style.capitalize()}` Style + `{blob_shape.capitalize()}` Shape")

    # 2. Prepare Matplotlib Figure
    fig, ax = plt.subplots(figsize=(7, 10))
    fig.patch.set_facecolor((0, 0, 0)) # Figure entire background color
    ax.set_facecolor((0, 0, 0))      # Plot area background color
    ax.axis('off')
    
    # 3. Create palette
    palette = get_palette(mode=style, k=20)
    n_layers = 30 # Number of layers is fixed at 30 (you can make this random too if you want!)
    
    # 4. Draw layers
    for i in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.01, 0.25)
        
        # Pass the selected shape type (blob_shape) as 'kind'
        x, y = shape(center=(cx, cy), r=rr, wobble=random.uniform(0.05, 0.9), kind=blob_shape)
        
        color = random.choice(palette)
        alpha = random.uniform(0.1, 0.9)
        edge_color = (random.random(), random.random(), random.random(), 1)
        
        ax.fill(x, y, color=color, alpha=alpha, edgecolor=edge_color)

    # 5. Add text (changed to white)
    ax.text(0.05, 0.95, "Generative Poster", fontsize=25, weight='bold', color='white', transform=ax.transAxes)
    ax.text(0.05, 0.91, "Week 3 • Arts & Advanced Big Data", fontsize=15, color='white', transform=ax.transAxes)
    # Also display the selected theme on the poster
    ax.text(0.05, 0.88, f"{style} / {blob_shape}", fontsize=15, color='white', transform=ax.transAxes)
    
    # 6. Set canvas range
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 7. Display poster in Streamlit
    st.pyplot(fig)
    
    # 8. Prepare image data for download button
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight', pad_inches=0, facecolor=fig.get_facecolor())
    buf.seek(0)
    
    st.download_button(
        label="Download Poster (PNG)",
        data=buf,
        file_name=f"poster_{style}_{blob_shape}.png",
        mime="image/png"
    )
