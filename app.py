# === generative_poster_app.py ===
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
    if seed is not None:
        np.random.seed(seed)
    angles = np.linspace(0, 2*np.pi, resolution)
    base_noise = np.random.normal(0, wobble, smoothness)
    interp = np.interp(np.linspace(0, smoothness, resolution), np.arange(smoothness), base_noise)
    r = radius * (1 + interp)
    x = center[0] + r * np.cos(angles)
    y = center[1] + r * np.sin(angles)
    return x, y

# --- (C) Draw Poster --- #
def draw_poster(n_blobs, radius, wobble, smoothness, spread, seed):
    colors = random_palette(n_blobs, seed=seed)
    fig, ax = plt.subplots(figsize=(7, 10))
    ax.set_facecolor('black')
    ax.axis('off')

    for i, color in enumerate(colors):
        r = radius * (1 + i * 0.15)
        wob = wobble * (1 + i * 0.1)
        angle = np.random.uniform(0, 2 * np.pi)
        dist = np.random.uniform(0.2, spread) * (i / n_blobs + 0.3)
        cx = np.cos(angle) * dist
        cy = np.sin(angle) * dist
        x, y = generate_blob(center=(cx, cy), radius=r, wobble=wob, smoothness=smoothness, seed=seed+i)
        ax.fill(x, y, color=color, alpha=0.7, lw=0.5)
    
    )
    ax.set_xlim(-spread, spread)
    ax.set_ylim(-spread, spread)
    st.pyplot(fig)

# --- (D) Streamlit UI --- #
st.title("🎨 Generative Poster")
st.caption("Created with NumPy, Matplotlib, and Streamlit")

with st.sidebar:
    st.header("Poster Controls")
    n_blobs = st.slider("Number of Blobs", 3, 20, 10)
    radius = st.slider("Radius", 1.0, 6.0, 4.5)
    wobble = st.slider("Wobble", 0.01, 0.2, 0.06)
    smoothness = st.slider("Smoothness", 50, 1000, 900)
    spread = st.slider("Spread", 1.0, 30.0, 24.8)
    seed = st.number_input("Random Seed", value=183535)

if st.button("Generate Poster"):
    draw_poster(n_blobs, radius, wobble, smoothness, spread, seed)
