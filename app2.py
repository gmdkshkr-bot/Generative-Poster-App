# app.py
import streamlit as st
import random, math, io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# --- Utility: luminance for contrast checks
def luminance(rgb):
    r, g, b = rgb
    return 0.299*r + 0.587*g + 0.114*b

# --- Color Palette
def random_palette(style="pastel", k=20):
    if style == "pastel":
        colors = [(0.6+0.4*random.random(), 0.6+0.4*random.random(), 0.6+0.4*random.random()) for _ in range(k)]
    elif style == "neon":
        colors = [(random.uniform(0.5,1), random.uniform(0,1), random.uniform(0.5,1)) for _ in range(k)]
    elif style == "monochrome":
        base = random.random()
        colors = [(base+0.1*random.random(),)*3 for _ in range(k)]
    elif style == "earth":
        earth_tones = [
            (0.42,0.26,0.15),(0.55,0.47,0.37),(0.62,0.74,0.55),
            (0.84,0.78,0.58),(0.40,0.55,0.30)
        ]
        colors = [random.choice(earth_tones) for _ in range(k)]
    elif style == "ocean":
        ocean_tones = [
            (0.0,0.3,0.5),(0.1,0.6,0.8),(0.2,0.8,0.9),
            (0.0,0.5,0.4),(0.4,0.9,1.0)
        ]
        colors = [random.choice(ocean_tones) for _ in range(k)]
    elif style == "sunset":
        sunset_tones = [
            (1.0,0.5,0.0),(1.0,0.2,0.3),(0.8,0.3,0.6),
            (0.6,0.2,0.8),(0.9,0.7,0.3)
        ]
        colors = [random.choice(sunset_tones) for _ in range(k)]
    elif style == "cyberpunk":
        cyber_colors = [
            (1.0,0.0,0.8),(0.0,1.0,1.0),(0.2,0.2,1.0),
            (1.0,0.8,0.1),(0.1,0.0,0.1)
        ]
        colors = [random.choice(cyber_colors) for _ in range(k)]
    else:
        colors = [(random.random(), random.random(), random.random()) for _ in range(k)]
    return colors

# --- Shape Generators
def blob(center=(0.5,0.5), r=0.2, points=1000, wobble=0.15):
    angles = np.linspace(0,2*math.pi,points)
    radii = r*(1+wobble*(np.random.rand(points)-0.5))
    x = center[0] + radii*np.cos(angles)
    y = center[1] + radii*np.sin(angles)
    return x, y

def shape(center=(0.5,0.5), r=0.2, points=1000, wobble=0.15, shape_type="blob"):
    if shape_type == "circle":
        angles = np.linspace(0,2*np.pi,points)
        x = center[0] + r*np.cos(angles)
        y = center[1] + r*np.sin(angles)
        return x, y
    elif shape_type == "polygon":
        n_sides = random.randint(3,8)
        angles = np.linspace(0,2*np.pi,n_sides,endpoint=False)
        x = center[0] + r*np.cos(angles)
        y = center[1] + r*np.sin(angles)
        # ensure closed polygon by repeating first vertex
        return np.append(x,x[0]), np.append(y,y[0])
    else:
        return blob(center,r,points,wobble)

# --- Rotate coordinates for 3D effect
def rotate_coords(x, y, cx, cy, angle):
    x_rot = (x-cx)*np.cos(angle) - (y-cy)*np.sin(angle) + cx
    y_rot = (x-cx)*np.sin(angle) + (y-cy)*np.cos(angle) + cy
    return x_rot, y_rot

# --- Poster generation (returns PNG bytes)
def render_poster(
    style="pastel", shape_type="blob", n_layers=30, wobble=0.4,
    background="#FFFFFF", title_color="#000000", seed=None,
    shadow_offset=0.02, brightness_strength=0.3,
    alpha_min=0.6, alpha_max=0.9, light_angle=45,
    rotation_range=0.3, width=1200, height=1700
):
    random.seed(seed)
    np.random.seed(seed if seed is not None else None)

    # set matplotlib DPI and size
    dpi = 150
    fig_w = width / dpi
    fig_h = height / dpi
    fig = plt.figure(figsize=(fig_w, fig_h), facecolor=background)
    ax = plt.gca()
    ax.axis("off")
    ax.set_facecolor(background)

    palette = random_palette(style, 40)

    # shadow offset direction (light_angle: degrees)
    dx = shadow_offset * math.cos(math.radians(light_angle))
    dy = -shadow_offset * math.sin(math.radians(light_angle))

    for i in range(n_layers):
        # choose center but with better distribution to avoid extreme edges
        cx = random.uniform(0.05, 0.95)
        cy = random.uniform(0.05, 0.95)
        rr = random.uniform(0.02,0.22)

        # rotation
        angle = random.uniform(-rotation_range, rotation_range)

        # Shadow — draw same shape type at offset so polygon shadow matches polygon
        x_s, y_s = shape(center=(cx+dx, cy+dy), r=rr, wobble=wobble, shape_type=shape_type)
        x_s, y_s = rotate_coords(x_s, y_s, cx+dx, cy+dy, angle)
        # use a slightly blurred look by layering darker semi-transparent fills
        plt.fill(x_s, y_s, color=(0,0,0), alpha=0.35, edgecolor=(0,0,0,0))

        # Actual shape
        x, y = shape(center=(cx,cy), r=rr, wobble=wobble, shape_type=shape_type)
        x, y = rotate_coords(x, y, cx, cy, angle)
        base_color = np.array(random.choice(palette))
        brightness_factor = 0.75 + brightness_strength*(i / max(1, n_layers))
        color = np.clip(base_color * brightness_factor, 0, 1)
        alpha = random.uniform(alpha_min, alpha_max)
        plt.fill(x, y, color=color, alpha=alpha, edgecolor=(0,0,0,0))

    # Text contrast fix: ensure title_color contrasts with background
    bg_rgb = tuple(int(background.lstrip("#")[i:i+2],16)/255 for i in (0,2,4))
    try:
        text_rgb = tuple(int(title_color.lstrip("#")[i:i+2],16)/255 for i in (0,2,4))
    except Exception:
        text_rgb = (0,0,0)
    if abs(luminance(bg_rgb) - luminance(text_rgb)) < 0.5:
        title_color = "#FFFFFF" if luminance(bg_rgb) < 0.5 else "#000000"

    # Draw persistent top-left title & subtitle (always on top of layers)
    title = "3D like Generative Poster"
    subtitle = "Week 4 • Arts & Big Data"
    info = f"Style: {style.title()} / Shape: {shape_type.title()}"

    # Use transform=ax.transAxes so text stays in the same place relative to canvas
    plt.text(0.01, 0.97, title, fontsize=38, weight="bold",
             color=title_color, transform=ax.transAxes, alpha=0.95, va="top")
    plt.text(0.01, 0.93, subtitle, fontsize=16,
             color=title_color, transform=ax.transAxes, alpha=0.9, va="top")
    plt.text(0.01, 0.895, info, fontsize=13,
             color=title_color, transform=ax.transAxes, alpha=0.85, va="top")

    plt.xlim(0,1)
    plt.ylim(0,1)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Generative 3D Poster", layout="centered")
st.title("Generative 3D Poster — Streamlit")

with st.sidebar:
    st.header("Controls")
    style = st.selectbox("Style", options=['pastel','neon','monochrome','earth','ocean','sunset','cyberpunk'], index=0)
    shape_type = st.selectbox("Shape", options=['blob','circle','polygon'], index=0)
    n_layers = st.slider("Layers", min_value=5, max_value=80, value=30, step=1)
    wobble = st.slider("Wobble", min_value=0.0, max_value=1.0, value=0.4, step=0.01)
    seed = st.slider("Seed (0 = random)", min_value=0, max_value=9999, value=0, step=1)
    shadow_offset = st.slider("Shadow offset", min_value=0.0, max_value=0.06, value=0.02, step=0.001)
    brightness_strength = st.slider("Brightness strength", min_value=0.0, max_value=1.0, value=0.3, step=0.01)
    alpha_min = st.slider("Alpha min", min_value=0.05, max_value=1.0, value=0.6, step=0.01)
    alpha_max = st.slider("Alpha max", min_value=0.05, max_value=1.0, value=0.9, step=0.01)
    light_angle = st.slider("Light angle (deg)", min_value=0, max_value=360, value=45, step=1)
    rotation_range = st.slider("Rotation range (rad)", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

    st.markdown("---")
    st.subheader("Canvas & Text")
    bg = st.color_picker("Background color", value="#FFFFFF")
    text_col = st.color_picker("Text color (auto-contrasts)", value="#000000")
    st.markdown("---")
    st.write("Output size (px)")
    width = st.number_input("Width", min_value=600, max_value=3000, value=1200, step=100)
    height = st.number_input("Height", min_value=800, max_value=4000, value=1700, step=100)

    if seed == 0:
        seed_val = None
    else:
        seed_val = int(seed)

# Render button (avoid rerender spamming)
if st.button("Generate Poster"):
    with st.spinner("Rendering..."):
        poster_bytes = render_poster(
            style=style, shape_type=shape_type, n_layers=n_layers, wobble=wobble,
            background=bg, title_color=text_col, seed=seed_val,
            shadow_offset=shadow_offset, brightness_strength=brightness_strength,
            alpha_min=alpha_min, alpha_max=alpha_max, light_angle=light_angle,
            rotation_range=rotation_range, width=int(width), height=int(height)
        )
        st.image(poster_bytes, use_column_width=True)

        # Download button
        st.download_button(
            label="Download PNG",
            data=poster_bytes,
            file_name="generative_poster.png",
            mime="image/png"
        )

    st.success("Done — poster generated.")

else:
    st.info("Change controls on the left and click *Generate Poster*.")
