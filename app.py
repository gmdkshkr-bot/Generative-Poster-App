import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# --- (A) Random Color Palette --- #
def random_palette(n=6, s_range=(0.3, 0.9), l_range=(0.3, 0.7), seed=None):
    if seed is not None:
        np.random.seed(seed)
    hues = np.linspace(0, 1, n, endpoint=False)
    np.random.shuffle(hues)
    colors = []
    for h in hues:
        s = np.random.uniform(*s_range)
        l = np.random.uniform(*l_range)
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = l - c / 2
        if h < 1/6: rgb = (c, x, 0)
        elif h < 2/6: rgb = (x, c, 0)
        elif h < 3/6: rgb = (0, c, x)
        elif h < 4/6: rgb = (0, x, c)
        elif h < 5/6: rgb = (x, 0, c)
        else: rgb = (c, 0, x)
        colors.append(tuple(np.clip(np.array(rgb) + m, 0, 1)))
    return colors


# --- (B) Smooth Blob Generator --- #
def generate_blob(center=(0, 0), radius=1, wobble=0.08, smoothness=5, resolution=300, seed=None):
    """Generate smooth, slightly wobbly organic blob."""
    if seed is not None:
        np.random.seed(seed)
    angles = np.linspace(0, 2*np.pi, resolution)
    base_noise = np.random.normal(0, wobble, smoothness)
    interp = np.interp(np.linspace(0, smoothness, resolution), np.arange(smoothness), base_noise)
    r = radius * (1 + interp)
    x = center[0] + r * np.cos(angles)
    y = center[1] + r * np.sin(angles)
    return x, y


# --- Utility for adaptive text color --- #
def luminance(rgb):
    r, g, b = rgb
    return 0.2126*r + 0.7152*g + 0.0722*b


# --- (C) Poster Drawing --- #
def draw_poster(
    n_blobs=8,
    radius=1.0,
    wobble=0.06,
    smoothness=6,
    spread=1.0,
    seed=None,
    bg_color='black',
    main_title="Generative Poster",
    subtitle="Week 2 - Arts and Advanced Big Data"
):
    if seed is not None:
        np.random.seed(seed)

    colors = random_palette(n_blobs, seed=seed)
    fig, ax = plt.subplots(figsize=(7, 10))
    ax.set_facecolor(bg_color)
    ax.axis('off')

    # Draw blobs
    for i, color in enumerate(colors):
        r = radius * (1 + i * 0.15)
        wob = wobble * (1 + i * 0.1)
        angle = np.random.uniform(0, 2 * np.pi)
        dist = np.random.uniform(0.2, spread) * (i / n_blobs + 0.3)
        cx = np.cos(angle) * dist
        cy = np.sin(angle) * dist
        x, y = generate_blob(center=(cx, cy), radius=r, wobble=wob,
                             smoothness=smoothness, seed=seed+i)
        ax.fill(x, y, color=color, alpha=0.7, lw=0.5)

    # Adaptive text color
    if isinstance(bg_color, str):
        text_color = 'white' if bg_color.lower() == 'black' else 'black'
    else:
        text_color = 'white' if luminance(bg_color) < 0.5 else 'black'

    # Titles
    fig.text(0.03, 0.96, main_title, ha='left', va='top', fontsize=24,
             color=text_color, weight='bold', family='sans-serif')
    fig.text(0.03, 0.92, subtitle, ha='left', va='top', fontsize=18,
             color=text_color, family='sans-serif')

    # Params
    param_text = (
        f"n_blobs = {n_blobs}\n"
        f"radius = {radius}\n"
        f"wobble = {wobble}\n"
        f"smoothness = {smoothness}\n"
        f"spread = {spread}\n"
        f"seed = {seed}"
    )
    fig.text(0.97, 0.03, param_text,
             ha='right', va='bottom',
             fontsize=9, color=text_color, alpha=0.8, family='monospace')

    plt.subplots_adjust(top=0.9, bottom=0.1)
    return fig

from io import BytesIO

def fig_to_png(fig):
    """Convert Matplotlib figure to PNG bytes."""
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    buf.seek(0)
    return buf.getvalue()



# --- (D) Streamlit UI --- #
st.title("🎨 Generative Art Poster")
st.caption("An interactive generative poster powered by Matplotlib and Streamlit")

# Sidebar controls
with st.sidebar:
    st.header("🧩 Poster Controls")
    n_blobs = st.slider("Number of blobs", 3, 20, 10)
    radius = st.slider("Base radius", 1.0, 10.0, 4.5)
    wobble = st.slider("Wobble", 0.0, 0.2, 0.06)
    smoothness = st.slider("Smoothness", 5, 1000, 900)
    spread = st.slider("Spread", 0.1, 30.0, 24.8)
    seed = st.number_input("Random Seed", value=183535)
    bg_color = st.color_picker("Background color", "#000000")
    main_title = st.text_input("Main Title", "Generative Poster")
    subtitle = st.text_input("Subtitle", "Week 2 - Arts and Advanced Big Data")

# Draw figure
fig = draw_poster(
    n_blobs=n_blobs,
    radius=radius,
    wobble=wobble,
    smoothness=smoothness,
    spread=spread,
    seed=int(seed),
    bg_color=bg_color,
    main_title=main_title,
    subtitle=subtitle
)

# Display figure
st.pyplot(fig)

# Optional save button
st.download_button(
    label="💾 Download Poster as PNG",
    data=fig_to_png(fig),
    file_name="generative_poster.png",
    mime="image/png"
)
