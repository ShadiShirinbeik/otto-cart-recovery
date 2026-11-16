# Shared look for all charts in the notebooks: one colour = one meaning.
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager

COLORS = {
    "users": "#D5DBE3",           # visited / only browsed (light grey)
    "cart": "#E8A317",            # added to cart (gold)
    "ordered": "#3A62D6",         # ordered (blue)
    "abandoner": "#F0614F",       # cart but no order = lost (coral)
    "quick_buyer": "#8FAEF5",     # ordered within 1 hour (light blue)
    "same_day_buyer": "#5B83EA",  # ordered within 1 day (blue)
    "slow_buyer": "#22409E",      # came back after 1+ day (dark blue)
    "left_out": "#EEF1F4",        # groups left out of the analysis
}
TEXT = "#111111"
MUTED = "#444444"
SOFT = "#f1f4f5"


def set_style():
    fonts = {f.name for f in font_manager.fontManager.ttflist}
    font = next((f for f in ["Inter", "Segoe UI", "Helvetica Neue", "Arial"] if f in fonts), "DejaVu Sans")
    sns.set_theme(style="white", font=font, rc={
        "axes.spines.left": True,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.spines.bottom": True,
        "axes.edgecolor": "#333333",
        "axes.linewidth": 1,
        "axes.labelcolor": MUTED,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "text.color": TEXT,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.titlepad": 12,
    })


def add_title(fig, title, subtitle=""):
    """Big title and a grey subtitle at the top left of a figure.
    Returns where the charts can start (use it in plt.tight_layout(rect=(0, 0, 1, top)))."""
    height = fig.get_figheight() * 72  # figure height in points
    fig.text(0.03, 1 - 14 / height, title, ha="left", va="top", fontsize=19, fontweight="bold", color=TEXT)
    if subtitle:
        fig.text(0.03, 1 - 44 / height, subtitle, ha="left", va="top", fontsize=11.5, color=MUTED)
    return 1 - 80 / height
