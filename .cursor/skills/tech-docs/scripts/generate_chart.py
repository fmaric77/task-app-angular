#!/usr/bin/env python3
"""
generate_chart.py — Create clean, minimal charts for technical documentation.

Usage:
    python scripts/generate_chart.py chart_spec.json
    python scripts/generate_chart.py chart_spec.json --output /mnt/user-data/outputs/chart.png

Or pipe JSON directly:
    echo '{"type": "line", "title": "Accuracy Trend", ...}' | python scripts/generate_chart.py -

Supported chart types:
    line        — Trend lines over time/iterations (e.g., accuracy over 10 runs)
    bar         — Comparisons across categories (e.g., per-carrier accuracy)
    stacked_bar — Stacked segments per category (e.g., error type breakdown)
    horizontal  — Horizontal bar chart (e.g., effort estimates, ranked items)
    scatter     — Scatter plot with optional labels

JSON spec format:
{
    "type": "line",
    "title": "Extraction Accuracy Over 10 Runs",
    "x_label": "Run",
    "y_label": "Accuracy (%)",
    "series": [
        {
            "label": "Accuracy",
            "x": ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10"],
            "y": [58.3, 68.0, 69.9, 70.9, 71.8, 77.95, 72.87, 77.35, 79.41, 81.14]
        }
    ],
    "target_line": {"value": 80, "label": "Target"},
    "width": 10,
    "height": 5
}

See examples at the bottom of this file for each chart type.
"""

import json
import sys
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# --- Style -------------------------------------------------------------------

COLORS = [
    "#2563EB",  # blue
    "#059669",  # green
    "#D97706",  # amber
    "#DC2626",  # red
    "#7C3AED",  # purple
    "#0891B2",  # cyan
    "#BE185D",  # pink
    "#4B5563",  # gray
]

TARGET_COLOR = "#DC2626"
TARGET_ALPHA = 0.7
GRID_ALPHA = 0.3
BG_COLOR = "#FFFFFF"
GRID_COLOR = "#E5E7EB"
TEXT_COLOR = "#1F2937"
FONT_SIZE_TITLE = 14
FONT_SIZE_LABEL = 11
FONT_SIZE_TICK = 10
FONT_SIZE_ANNOTATION = 9
DPI = 150


def apply_style(ax, title, x_label, y_label):
    """Apply clean minimal styling to an axis."""
    ax.set_facecolor(BG_COLOR)
    ax.figure.set_facecolor(BG_COLOR)

    ax.set_title(title, fontsize=FONT_SIZE_TITLE, fontweight="bold",
                 color=TEXT_COLOR, pad=12)
    if x_label:
        ax.set_xlabel(x_label, fontsize=FONT_SIZE_LABEL, color=TEXT_COLOR)
    if y_label:
        ax.set_ylabel(y_label, fontsize=FONT_SIZE_LABEL, color=TEXT_COLOR)

    ax.tick_params(colors=TEXT_COLOR, labelsize=FONT_SIZE_TICK)
    ax.grid(True, alpha=GRID_ALPHA, color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
        spine.set_linewidth(0.8)


def add_target_line(ax, spec):
    """Add a horizontal target/threshold line if specified."""
    target = spec.get("target_line")
    if target:
        val = target["value"]
        label = target.get("label", f"Target: {val}")
        ax.axhline(y=val, color=TARGET_COLOR, linestyle="--",
                    linewidth=1.5, alpha=TARGET_ALPHA, label=label)


def add_annotations(ax, spec):
    """Add text annotations if specified."""
    for ann in spec.get("annotations", []):
        ax.annotate(
            ann["text"], xy=(ann["x"], ann["y"]),
            fontsize=FONT_SIZE_ANNOTATION, color=TEXT_COLOR,
            ha=ann.get("ha", "center"), va=ann.get("va", "bottom"),
            fontweight=ann.get("weight", "normal"),
        )


# --- Chart Types -------------------------------------------------------------

def chart_line(spec, ax):
    """Line chart — trends over time/iterations."""
    for i, s in enumerate(spec["series"]):
        color = COLORS[i % len(COLORS)]
        ax.plot(s["x"], s["y"], marker="o", markersize=5, linewidth=2,
                color=color, label=s.get("label"), zorder=3)

        # Annotate last point with its value
        if spec.get("annotate_last", True) and len(s["y"]) > 0:
            last_x, last_y = s["x"][-1], s["y"][-1]
            fmt = spec.get("value_format", ".1f")
            suffix = spec.get("value_suffix", "")
            ax.annotate(
                f"{last_y:{fmt}}{suffix}", xy=(last_x, last_y),
                textcoords="offset points", xytext=(0, 10),
                fontsize=FONT_SIZE_ANNOTATION, fontweight="bold",
                color=COLORS[i % len(COLORS)], ha="center",
            )

    add_target_line(ax, spec)
    add_annotations(ax, spec)


def chart_bar(spec, ax):
    """Vertical bar chart — comparisons across categories."""
    import numpy as np

    series = spec["series"]
    categories = series[0]["x"]
    n_series = len(series)
    x = np.arange(len(categories))
    width = 0.7 / n_series

    for i, s in enumerate(series):
        offset = (i - n_series / 2 + 0.5) * width
        bars = ax.bar(x + offset, s["y"], width, label=s.get("label"),
                       color=COLORS[i % len(COLORS)], zorder=3)

        if spec.get("show_values", False):
            fmt = spec.get("value_format", ".1f")
            suffix = spec.get("value_suffix", "")
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height,
                        f"{height:{fmt}}{suffix}",
                        ha="center", va="bottom",
                        fontsize=FONT_SIZE_ANNOTATION, color=TEXT_COLOR)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=spec.get("x_rotation", 0))
    add_target_line(ax, spec)
    add_annotations(ax, spec)


def chart_stacked_bar(spec, ax):
    """Stacked bar chart — segments per category."""
    import numpy as np

    series = spec["series"]
    categories = series[0]["x"]
    x = np.arange(len(categories))
    bottom = np.zeros(len(categories))

    for i, s in enumerate(series):
        ax.bar(x, s["y"], 0.6, bottom=bottom, label=s.get("label"),
               color=COLORS[i % len(COLORS)], zorder=3)
        bottom += np.array(s["y"])

    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=spec.get("x_rotation", 0))
    add_annotations(ax, spec)


def chart_horizontal(spec, ax):
    """Horizontal bar chart — ranked items, effort estimates."""
    import numpy as np

    series = spec["series"][0]
    categories = series["x"]
    values = series["y"]
    y = np.arange(len(categories))

    colors = [COLORS[i % len(COLORS)] for i in range(len(categories))]
    if spec.get("single_color", False):
        colors = [COLORS[0]] * len(categories)

    ax.barh(y, values, 0.6, color=colors, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(categories)
    ax.invert_yaxis()

    if spec.get("show_values", True):
        fmt = spec.get("value_format", ".1f")
        suffix = spec.get("value_suffix", "")
        for i, v in enumerate(values):
            ax.text(v + max(values) * 0.02, i, f"{v:{fmt}}{suffix}",
                    va="center", fontsize=FONT_SIZE_ANNOTATION,
                    color=TEXT_COLOR)

    add_annotations(ax, spec)


def chart_scatter(spec, ax):
    """Scatter plot with optional labels."""
    for i, s in enumerate(spec["series"]):
        color = COLORS[i % len(COLORS)]
        ax.scatter(s["x"], s["y"], s=60, color=color, label=s.get("label"),
                   zorder=3, edgecolors="white", linewidth=0.5)

        for label_item in s.get("labels", []):
            idx = label_item["index"]
            ax.annotate(
                label_item["text"],
                xy=(s["x"][idx], s["y"][idx]),
                textcoords="offset points", xytext=(8, 4),
                fontsize=FONT_SIZE_ANNOTATION, color=TEXT_COLOR,
            )

    add_target_line(ax, spec)
    add_annotations(ax, spec)


CHART_TYPES = {
    "line": chart_line,
    "bar": chart_bar,
    "stacked_bar": chart_stacked_bar,
    "horizontal": chart_horizontal,
    "scatter": chart_scatter,
}


# --- Main --------------------------------------------------------------------

def generate(spec, output_path):
    """Generate a chart from a spec dict and save as PNG."""
    chart_type = spec.get("type", "line")
    if chart_type not in CHART_TYPES:
        raise ValueError(f"Unknown chart type '{chart_type}'. "
                         f"Supported: {list(CHART_TYPES.keys())}")

    w = spec.get("width", 10)
    h = spec.get("height", 5)
    fig, ax = plt.subplots(figsize=(w, h))

    apply_style(ax, spec.get("title", ""), spec.get("x_label", ""),
                spec.get("y_label", ""))

    CHART_TYPES[chart_type](spec, ax)

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    if labels and spec.get("show_legend", True):
        ax.legend(fontsize=FONT_SIZE_TICK, framealpha=0.9,
                  edgecolor=GRID_COLOR)

    plt.tight_layout()
    fig.savefig(output_path, dpi=DPI, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print(f"Created: {output_path}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    if input_path == "-":
        spec = json.load(sys.stdin)
    else:
        with open(input_path) as f:
            spec = json.load(f)

    output_path = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        output_path = sys.argv[idx + 1]

    if not output_path:
        if input_path == "-":
            output_path = "chart.png"
        else:
            output_path = os.path.splitext(input_path)[0] + ".png"

    generate(spec, output_path)


if __name__ == "__main__":
    main()
