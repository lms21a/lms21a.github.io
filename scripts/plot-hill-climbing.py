"""Render the blog's archived measurements; requires matplotlib==3.11.2.

Run from any directory: python scripts/plot-hill-climbing.py
Sources and exact counts live in src/data; no inference or evaluation is run.
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = ROOT / "src" / "assets" / "research"
OUT.mkdir(parents=True, exist_ok=True)
PAPER, INK, MUTED, RULE = "#f8f7f3", "#242824", "#666b65", "#d9ddd5"
GREEN, SAGE, RUST = "#375c48", "#9eaf99", "#ac7052"
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "text.color": INK,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": INK,
    "axes.edgecolor": RULE,
    "axes.facecolor": PAPER,
    "figure.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "svg.fonttype": "none",
})


def style(ax, *, grid_axis="x"):
    ax.set_axisbelow(True)
    ax.grid(axis=grid_axis, color=RULE, linewidth=.7)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="both", length=0, pad=9)


def save(fig, stem, title, description):
    fig.savefig(OUT / f"{stem}.png", dpi=220)
    fig.savefig(OUT / f"{stem}.svg", metadata={"Title": title, "Description": description})
    plt.close(fig)


def plot_climb(mobile=False):
    data = json.loads((ROOT / "src/data/futoshiki-climb.json").read_text())
    fig, axes = plt.subplots(2, 1, figsize=(4.2, 6.2) if mobile else (8.2, 5.0))
    fig.subplots_adjust(left=.23 if mobile else .14, right=.93, top=.91, bottom=.12,
                        hspace=.9 if mobile else .85)
    for ax, panel in zip(axes, data["panels"]):
        records = panel["checkpoints"]
        rates = [100 * r["correct_completions"] / r["completions"] for r in records]
        ax.barh([1, 0], rates, height=.44, color=[SAGE, GREEN])
        for y, rate in zip([1, 0], rates):
            ax.text(rate + 2, y, f"{rate:.2f}%", va="center", fontsize=11.5, color=GREEN)
        ax.set_yticks([1, 0], [f"RL {r['update']:,}" for r in records])
        ax.set_xlim(0, 103)
        ax.set_ylim(-.55, 1.55)
        ax.set_xticks([0, 50, 100] if mobile else [0, 25, 50, 75, 100])
        ax.set_title(f"{panel['label'].replace('Futoshiki ', '')} · {panel['puzzles']} puzzles × 8 attempts",
                     loc="left", fontsize=12, fontweight="normal", pad=15)
        style(ax)
    axes[-1].set_xlabel("Pass@1 (%)", labelpad=12)
    stem = "futoshiki-climb" + ("-mobile" if mobile else "")
    save(fig, stem, "Matched results after the final 250 updates",
         "Both checkpoints evaluated at 8192 tokens. 4×4 pass@1: 57.13 to 77.44 percent. "
         "5×5 pass@1: 1.95 to 5.08 percent. Different puzzle counts per size.")


def plot_algorithms(mobile=False):
    data = json.loads((ROOT / "src/data/flash-cispo-comparison.json").read_text())
    flash, cispo = data["series"]
    assert [p["training_rollouts"] for p in flash["points"]] == [p["training_rollouts"] for p in cispo["points"]]
    assert flash["points"][-1]["training_rollouts"] == 58752
    fig, ax = plt.subplots(figsize=(4.2, 4.6) if mobile else (8.2, 4.6))
    fig.subplots_adjust(left=.16 if mobile else .10, right=.96, top=.81, bottom=.19)
    for series, color, marker, linestyle in [(flash, GREEN, "o", "-"), (cispo, RUST, "D", "--")]:
        points = series["points"]
        xs = [p["training_rollouts"] for p in points]
        ys = [p["pass_at_1"] * 100 for p in points]
        assert all(p["correct_completions"] / p["examples"] == p["pass_at_1"] for p in points)
        ax.plot(xs, ys, color=color, linewidth=2, marker=marker, markersize=5,
                linestyle=linestyle, label=series["algorithm"])
        ax.annotate(f"{ys[-1]:.2f}%", xy=(xs[-1], ys[-1]), xytext=(7, 0),
                    textcoords="offset points", va="center", fontsize=11, color=color)
    ax.set_xlim(0, 76000 if mobile else 70000)
    ax.set_ylim(0, 60)
    ax.set_yticks([0, 20, 40, 60])
    ax.set_xticks([0, 20000, 40000, 60000])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: "0" if value == 0 else f"{value / 1000:.0f}k"))
    ax.set_xlabel("Generated training rollouts", labelpad=13, fontsize=10.5 if mobile else 11)
    ax.set_ylabel("Pass@1 (%)", labelpad=10)
    ax.legend(loc="lower left", bbox_to_anchor=(-.03 if mobile else -.015, 1.06),
              frameon=False, ncol=1 if mobile else 2, fontsize=10.5 if mobile else 11,
              handlelength=2.0, labelspacing=.6)
    style(ax, grid_axis="y")
    stem = "flash-cispo-comparison" + ("-mobile" if mobile else "")
    save(fig, stem, "Earlier FlashREINFORCE and CISPO comparison",
         "Separate September branch, one seed. Equal generated rollout budgets, including CISPO rejections; "
         "32 validation puzzles times 8 attempts, 4096 tokens. Final pass@1 46.88 versus 21.88 percent. "
         "Optimizer updates, retained responses and generated tokens differ.")


def plot_regression(mobile=False):
    data = json.loads((ROOT / "src/data/futoshiki-regression.json").read_text())
    fig, axes = plt.subplots(2, 1, figsize=(4.2, 7.4)) if mobile else plt.subplots(1, 2, figsize=(8.2, 4.4))
    fig.subplots_adjust(left=.18 if mobile else .09, right=.95, top=.88,
                        bottom=.11 if mobile else .2, hspace=.6, wspace=.40)
    ax, test = axes
    points = data["monitor"]["points"]
    xs, ys = [p["step"] for p in points], [100 * p["pass_at_1"] for p in points]
    assert all(p["correct"] / p["completions"] == p["pass_at_1"] for p in points)
    ax.plot(xs, ys, color=RUST, marker="o", markersize=4.5, linewidth=2)
    ax.set_title("Monitor · 32 puzzles × 8", loc="left", fontsize=12, pad=17)
    ax.annotate(f"{ys[-1]:.2f}%", (xs[-1], ys[-1]), xytext=(-5, 12),
                textcoords="offset points", color=RUST, ha="right", fontsize=11)
    ax.set_xlim(90, 365)
    ax.set_xticks([100, 225, 350] if mobile else [100, 200, 300, 350])
    ax.set_xlabel("5×5 training update", labelpad=12, fontsize=10.5)
    ax.set_ylabel("Pass@1 (%)", labelpad=10)
    records = data["matched_test"]["points"]
    rates = [r["pass_at_1"] * 100 for r in records]
    test.bar([0, 1], rates, width=.48, color=[SAGE, RUST])
    for x, rate in enumerate(rates):
        test.text(x, rate + .8, f"{rate:.2f}%", ha="center", fontsize=11, color=INK)
    test.set_xticks([0, 1], ["Update 100", "Update 350"])
    test.set_xlim(-.6, 1.6)
    test.set_title("Matched test · 128 puzzles × 8", loc="left", fontsize=11.4 if mobile else 11, pad=17)
    if mobile:
        test.set_ylabel("Pass@1 (%)", labelpad=10)
    for axis in axes:
        axis.set_ylim(0, 20)
        axis.set_yticks([0, 5, 10, 15, 20])
        style(axis, grid_axis="y")
    stem = "futoshiki-regression" + ("-mobile" if mobile else "")
    save(fig, stem, "The 5×5 continuation loses ground",
         "Separate panels at 8192 tokens. The 32-puzzle monitor declines unevenly and partly recovers at update 350. "
         "The matched 128-puzzle test falls from 132/1024 to 85/1024 correct responses, or 12.89 to 8.30 percent.")


def plot_solver_projection(mobile=False):
    data = json.loads((ROOT / "src/data/solver-projection-comparison.json").read_text())
    fig, ax = plt.subplots(figsize=(4.2, 5.0) if mobile else (8.2, 4.4))
    fig.subplots_adjust(left=.44 if mobile else .33, right=.95, top=.95, bottom=.16)
    recipes = data["recipes"]
    rates = [100 * r["correct_completions"] / r["completions"] for r in recipes]
    positions = [2, 1, 0]
    ax.barh(positions, rates, height=.42, color=[RUST, SAGE, GREEN])
    labels = [
        "Solver-grounded\n512 examples × 4 epochs\n512 optimizer updates",
        "Projected\n512 examples × 2 epochs\n256 optimizer updates",
        "Projected · chosen\n256 examples × 1 epoch\n64 optimizer updates",
    ]
    ax.set_yticks(positions, labels, fontsize=9.2 if mobile else 10.5, linespacing=1.5)
    for y, rate in zip(positions, rates):
        ax.text(rate + .8, y, f"{rate:.2f}%", va="center", color=INK,
                fontsize=10.5 if mobile else 11.5)
    ax.set_xlim(0, 37 if mobile else 34)
    ax.set_ylim(-.65, 2.65)
    ax.set_xticks([0, 15, 30] if mobile else [0, 10, 20, 30])
    ax.set_xlabel("4×4 pass@1 (%)", labelpad=14, fontsize=10.5 if mobile else 11)
    style(ax)
    stem = "solver-projection-comparison" + ("-mobile" if mobile else "")
    save(fig, stem, "Solver-grounded and projected SFT endpoints",
         "Same 128-puzzle panel times eight attempts at 4096 tokens. Solver-grounded 512 examples "
         "times four epochs: 26.76 percent. Projected 512 times two: 11.43 percent. "
         "Chosen projected 256 times one: 4.20 percent. Training budgets and schedules differ; "
         "these endpoints do not establish relative learning speed.")


def plot_training_curve750(mobile=False):
    data = json.loads((ROOT / "src/data/futoshiki-training-curve.json").read_text())
    points = data["points"]
    assert len(points) == 39 and points[-1]["update"] == 750
    assert all(p["correct_completions"] / p["completions"] == p["pass_at_1"] for p in points)
    xs = [p["update"] for p in points]
    ys = [100 * p["pass_at_1"] for p in points]
    fig, ax = plt.subplots(figsize=(4.2, 4.5) if mobile else (8.2, 4.4))
    fig.subplots_adjust(left=.17 if mobile else .10, right=.95, top=.91, bottom=.19)
    ax.plot(xs, ys, color=GREEN, linewidth=2, marker="o", markersize=3.2)
    ax.scatter([xs[-1]], [ys[-1]], s=38, color=GREEN, zorder=3)
    ax.annotate(f"{ys[-1]:.2f}%", (xs[-1], ys[-1]), xytext=(-5, 13),
                textcoords="offset points", ha="right", color=GREEN, fontsize=11)
    ax.set_xlim(-10, 785)
    ax.set_ylim(0, 75)
    ax.set_xticks([0, 250, 500, 750])
    ax.set_yticks([0, 25, 50, 75])
    ax.set_xlabel("RL updates", labelpad=13)
    ax.set_ylabel("Validation pass@1 (%)", labelpad=11, fontsize=10.5 if mobile else 11)
    style(ax, grid_axis="y")
    stem = "futoshiki-training-curve750" + ("-mobile" if mobile else "")
    save(fig, stem, "4×4 learning through update 750",
         "39 archived, unsmoothed measurements on the same 32-puzzle validation monitor times eight attempts, "
         "with 4096 tokens throughout. Pass@1 increases from 9/256 (3.52 percent) before RL to "
         "134/256 (52.34 percent) at update 750. This curve is distinct from the 128-puzzle, "
         "8192-token test quoted in the prose (57.13 percent at update 750).")


for mobile in [False, True]:
    plot_climb(mobile)
    plot_algorithms(mobile)
    plot_regression(mobile)
    plot_solver_projection(mobile)
    plot_training_curve750(mobile)
print("Rendered desktop/mobile PNG and SVG figures from archived measurements.")
