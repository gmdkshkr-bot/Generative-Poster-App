import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random
import io
from PIL import Image, ImageFilter

st.set_page_config(layout="wide")

# ==========================================================
# Utility Functions
# ==========================================================

def color_brightness(rgb):
    return 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]

def shape(center=(0.5,0.5), r=0.2, points=1000, shape_type="blob", wobble=0.15, n_sides=6):
    # circle
    if shape_type == "circle":
        angles = np.linspace(0,2*np.pi,points)
        x = center[0] + r*np.cos(angles)
        y = center[1] + r*np.sin(angles)
        return x, y
    
    # polygon
    if shape_type == "polygon":
        angles = np.linspace(0,2*np.pi,n_sides,endpoint=False)
        x = center[0] + r*np.cos(angles)
        y = center[1] + r*np.sin(angles)
        return np.append(x,x[0]), np.append(y,y[0])

    # blob (default)
    angles = np.linspace(0,2*np.pi,points)
    wobble_radius = r*(1 + wobble*np.sin(angles*3 + random.random()*np.pi))
    x = center[0] + wobble_radius*np.cos(angles)
    y = center[1] + wobble_radius*np.sin(angles)
    return x,y


def compute_specular(i,n_layers):
    # Highlight strongest near top layers
    return max(0, 1 - (i/(n_layers-1)))**2

def metallic_noise():
    return np.random.rand()*0.3 + np.random.rand()*0.1

# ==========================================================
# Render Poster
# ==========================================================
def render_poster(
    bg_color="#222222",
    base_color="#FFB300",
    n_layers=7,
    light_angle=60,
    wobble=0.12,
    shape_type="blob",
    rim_intensity=0.3,
    specular_intensity=0.4,
    metallic_strength=0.5,
    blur_strength=0.5
):
    fig, ax = plt.subplots(figsize=(5,7))
    ax.set_facecolor(bg_color)

    light_rad = np.deg2rad(light_angle)

    for i in range(n_layers):
        t = i / (n_layers-1)

        # radius grad
        r = 0.33*(1 - 0.1*t)

        # center offset
        cx = 0.5 - 0.05*np.cos(light_rad)*(1-t)
        cy = 0.5 - 0.05*np.sin(light_rad)*(1-t)

        # polygon side fix
        n_sides = random.randint(4,9)

        # shadow softness = multiple offset layers
        for s in range(3):
            dx = 0.02*s*np.cos(light_rad)
            dy = 0.02*s*np.sin(light_rad)
            x_s, y_s = shape((cx+dx,cy+dy), r, shape_type=shape_type, wobble=wobble, n_sides=n_sides)
            ax.fill(x_s,y_s, color="black", alpha=0.05*(3-s))

        # base layer
        x,y = shape((cx,cy), r, shape_type=shape_type, wobble=wobble, n_sides=n_sides)

        # metallic roughness noise
        mr = metallic_strength*metallic_noise()

        # rim light: depends on angle
        rim = rim_intensity*(1-t)

        # specular highlight
        spec = specular_intensity*compute_specular(i,n_layers)

        # composite color
        rgb = np.array(ImageColor.getrgb(base_color))/255
        rgb = rgb + rim + spec - mr
        rgb = np.clip(rgb,0,1)

        ax.fill(x,y, color=rgb, alpha=0.42*(1-t+0.3))

    # blur (depth of field)
    fig.canvas.draw()
    image = np.array(fig.canvas.renderer._renderer)
    pil = Image.fromarray(image)
    pil = pil.filter(ImageFilter.GaussianBlur(radius=blur_strength*6))
    ax.clear()
    ax.imshow(pil)
    ax.axis("off")

    return fig


# ==========================================================
# Streamlit UI
# ==========================================================

st.sidebar.header("Poster Controls")

bg_color = st.sidebar.color_picker("Background", "#1d1d1d")
base_color = st.sidebar.color_picker("Base Color", "#fec100")
shape_type = st.sidebar.selectbox("Shape Type", ["blob","circle","polygon"])
n_layers = st.sidebar.slider("Layers", 5,15,7)
wobble = st.sidebar.slider("Blob Wobble",0.0,0.5,0.12)
light_angle = st.sidebar.slider("Light Angle",0,180,60)
rim_intensity = st.sidebar.slider("Rim Light",0.0,1.0,0.3)
specular_intensity = st.sidebar.slider("Specular",0.0,1.0,0.4)
metallic_strength = st.sidebar.slider("Metallic Roughness",0.0,1.0,0.5)
blur_strength = st.sidebar.slider("Depth Blur",0.0,1.0,0.5)

# auto render immediately
fig = render_poster(
    bg_color,
    base_color,
    n_layers,
    light_angle,
    wobble,
    shape_type,
    rim_intensity,
    specular_intensity,
    metallic_strength,
    blur_strength
)

st.pyplot(fig)

# download
buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=300)
st.download_button("Download Poster", buf, "poster.png", "image/png")
