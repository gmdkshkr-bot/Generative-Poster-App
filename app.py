import numpy as np
import matplotlib.pyplot as plt

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
    # gentle, low-frequency sinusoidal perturbation
    base_noise = np.random.normal(0, wobble, smoothness)
    interp = np.interp(np.linspace(0, smoothness, resolution), np.arange(smoothness), base_noise)
    r = radius * (1 + interp)
    x = center[0] + r * np.cos(angles)
    y = center[1] + r * np.sin(angles)
    return x, y


# --- (C) Main Poster Function --- #
def draw_poster(
    n_blobs=8,
    radius=1.0,
    wobble=0.06,
    smoothness=6,
    spread=1.0,
    figsize=(8, 8),
    seed=None,
    main_title="Generative Poster",
    subtitle="Week 2 - Arts and Advanced Big Data"
):
    """Draw smooth, distributed blobs with visible title and parameters."""
    if seed is not None:
        np.random.seed(seed)

    colors = random_palette(n_blobs, seed=seed)
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor('black')
    ax.axis('off')



    # --- Draw blobs --- #
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

    # --- Title (always visible) --- #
    fig.text(
        0.03, 0.96, main_title,
        ha='left', va='top',
        fontsize=18, color='black', weight='bold', family='sans-serif'
    )
    fig.text(
        0.03, 0.92, subtitle,
        ha='left', va='top',
        fontsize=12, color='black', weight='normal', family='sans-serif'
    )

    # --- Parameter annotation (bottom-left corner) --- #
    param_text = (
        f"Parameters:\n"
        f"n_blobs = {n_blobs}\n"
        f"radius = {radius}\n"
        f"wobble = {wobble}\n"
        f"smoothness = {smoothness}\n"
        f"spread = {spread}\n"
        f"seed = {seed}"
    )
    fig.text(
        0.97, 0.03, param_text,
        ha='right', va='bottom',
        fontsize=9, color='black', alpha=0.85, family='monospace'
    )

    # do NOT call tight_layout (it cuts text)
    plt.subplots_adjust(top=0.9, bottom=0.1)  # ensures title & text visible
    plt.show()

draw_poster(
    n_blobs=10,
    radius=4.5,
    wobble=0.06,      # much smoother edge
    smoothness=900,     # fewer undulations
    spread=24.8,
    figsize=(7, 7),
    seed=183535
)
