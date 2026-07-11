#!/usr/bin/env python3
import argparse
import json
import os
import textwrap
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp")

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle


TOKENS = {
    "surface": "#FCFCFD",
    "panel": "#FFFFFF",
    "ink": "#1F2430",
    "muted": "#6F768A",
    "grid": "#E6E8F0",
    "axis": "#D7DBE7",
    "blue": "#5477C4",
    "blue_dark": "#2E4780",
    "orange": "#CC6F47",
    "olive": "#71B436",
}


def font_prop():
    candidates = [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return fm.FontProperties(fname=candidate)
    return fm.FontProperties()


FONT_PROP = font_prop()


def draw_round_rect(ax, xy, width, height, color, radius=0.018, edge=None, lw=0.8):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle=f"round,pad=0.008,rounding_size={radius}",
        linewidth=lw,
        edgecolor=edge or color,
        facecolor=color,
        transform=ax.transAxes,
        clip_on=False,
    )
    ax.add_patch(patch)
    return patch


def add_card(ax, x, y, w, h, label, value, note=None):
    draw_round_rect(ax, (x, y), w, h, TOKENS["panel"], edge=TOKENS["axis"])
    ax.text(x + 0.018, y + h - 0.028, label, transform=ax.transAxes, fontsize=11, color=TOKENS["muted"], fontproperties=FONT_PROP, va="top")
    ax.text(x + 0.018, y + 0.026, value, transform=ax.transAxes, fontsize=24, color=TOKENS["ink"], fontproperties=FONT_PROP, va="bottom")
    if note:
        ax.text(x + w - 0.018, y + 0.032, note, transform=ax.transAxes, fontsize=10, color=TOKENS["muted"], fontproperties=FONT_PROP, ha="right", va="bottom")


def setup_panel(ax, title, subtitle=None):
    ax.set_facecolor(TOKENS["panel"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="both", colors=TOKENS["muted"], labelsize=10)
    ax.grid(axis="x", color=TOKENS["grid"], linewidth=0.8)
    ax.set_axisbelow(True)
    ax.text(0, 1.17, title, transform=ax.transAxes, fontsize=14, fontweight="bold", color=TOKENS["ink"], fontproperties=FONT_PROP, va="bottom")
    if subtitle:
        ax.text(0, 1.085, subtitle, transform=ax.transAxes, fontsize=9.5, color=TOKENS["muted"], fontproperties=FONT_PROP, va="bottom")


def wrap_label(label, width=12):
    label = str(label)
    if len(label) <= width:
        return label
    if "/" not in label:
        return textwrap.fill(label, width, break_long_words=False, break_on_hyphens=False)
    parts = label.split("/")
    lines = []
    current = ""
    for part in parts:
        candidate = f"{current}/{part}" if current else part
        if current and len(candidate) > width:
            lines.append(current)
            current = part
        else:
            current = candidate
    if current:
        lines.append(current)
    return "\n".join(lines)


def ranked_bar(ax, rows, title, subtitle, color):
    setup_panel(ax, title, subtitle)
    top = rows[:7]
    labels = [row["category"] for row in top][::-1]
    values = [row["count"] for row in top][::-1]
    if not values:
        ax.text(0.5, 0.5, "데이터 없음", transform=ax.transAxes, ha="center", va="center", fontproperties=FONT_PROP)
        return
    y = range(len(labels))
    ax.barh(y, values, color=color, edgecolor=TOKENS["blue_dark"], linewidth=0.7)
    ax.set_yticks(list(y))
    ax.set_yticklabels([wrap_label(label) for label in labels], fontproperties=FONT_PROP)
    ax.set_xlim(0, max(values) * 1.18)
    ax.set_xlabel("건수", fontproperties=FONT_PROP, color=TOKENS["muted"])
    for idx, value in enumerate(values):
        ax.text(value + max(values) * 0.025, idx, str(value), va="center", fontsize=10, color=TOKENS["ink"], fontproperties=FONT_PROP)


def build_dashboard(stats, out_dir, stem, title, subtitle):
    out_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = FONT_PROP.get_name()
    plt.rcParams["axes.unicode_minus"] = False

    fig = plt.figure(figsize=(16, 10), dpi=160, facecolor=TOKENS["surface"])
    ax_bg = fig.add_axes([0, 0, 1, 1])
    ax_bg.axis("off")

    fig.text(0.04, 0.94, title, fontsize=24, color=TOKENS["ink"], fontproperties=FONT_PROP, fontweight="bold")
    fig.text(0.04, 0.905, subtitle, fontsize=12, color=TOKENS["muted"], fontproperties=FONT_PROP)

    cards = [
        ("후기 응답", f"{stats.get('responses', 0)}건", "전체"),
        ("고유 응답자", f"{stats.get('unique_respondents', 0)}명", "기준값"),
        ("평균 만족도", f"{stats.get('avg_satisfaction', 0):.2f}", "/ 5"),
        ("평균 도움도", f"{stats.get('avg_usefulness', 0):.2f}", "/ 5"),
        ("종합점수", f"{stats.get('avg_score', 0):.2f}", "/ 5"),
    ]
    x0, y0, gap = 0.04, 0.79, 0.014
    card_w = (0.92 - gap * 4) / 5
    for idx, (label, value, note) in enumerate(cards):
        add_card(ax_bg, x0 + idx * (card_w + gap), y0, card_w, 0.105, label, value, note)

    day_rows = stats.get("day_comparison", [])
    ax_score = fig.add_axes([0.06, 0.50, 0.46, 0.215])
    setup_panel(ax_score, "회차별 종합점수", "동일 기준으로 회차별 평균 점수와 응답 수 비교")
    if day_rows:
        days = [row["day"] for row in day_rows]
        scores = [row["avg_score"] for row in day_rows]
        responses = [row["responses"] for row in day_rows]
        palette = [TOKENS["blue"], TOKENS["olive"], TOKENS["orange"]]
        x_positions = list(range(len(days)))
        ax_score.bar(x_positions, scores, color=[palette[i % len(palette)] for i in x_positions], edgecolor=TOKENS["blue_dark"], linewidth=0.7)
        ax_score.set_ylim(0, 5.45)
        ax_score.set_ylabel("5점 만점", fontproperties=FONT_PROP, color=TOKENS["muted"])
        ax_score.set_xticks(x_positions)
        ax_score.set_xticklabels(days, fontproperties=FONT_PROP)
        for idx, (score, n) in enumerate(zip(scores, responses)):
            ax_score.text(idx, score + 0.08, f"{score:.2f}\n{n}건", ha="center", va="bottom", fontsize=10, color=TOKENS["ink"], fontproperties=FONT_PROP)

    ax_good = fig.add_axes([0.58, 0.50, 0.36, 0.215])
    ranked_bar(ax_good, stats.get("top_good_categories", []), "좋았던 점 Top 7", "강점으로 반복 언급된 주제", TOKENS["blue"])

    ax_request = fig.add_axes([0.06, 0.14, 0.46, 0.225])
    ranked_bar(ax_request, stats.get("top_request_categories", []), "후속 요청 Top 7", "다음 강의와 보강이 필요한 주제", TOKENS["orange"])

    ax_action = fig.add_axes([0.58, 0.14, 0.36, 0.225])
    ax_action.axis("off")
    ax_action.text(0, 1.16, "운영 제안", transform=ax_action.transAxes, fontsize=14, fontweight="bold", color=TOKENS["ink"], fontproperties=FONT_PROP)
    actions = [
        ("1", "상위 요청 주제 우선 편성", "후속 수요가 큰 주제를 다음 세미나 1순위로 배치."),
        ("2", "기초 복습 블록 추가", "심화 주제 앞 15-20분 워밍업으로 난이도 완충."),
        ("3", "고급 자동화 트랙 분리", "도구 연동, 앱 배포, 에이전트 수요는 별도 트랙으로 대응."),
    ]
    for idx, (num, action_title, body) in enumerate(actions):
        y = 0.76 - idx * 0.29
        draw_round_rect(ax_action, (0, y), 0.98, 0.21, TOKENS["panel"], radius=0.02, edge=TOKENS["axis"])
        ax_action.add_patch(Rectangle((0.025, y + 0.045), 0.055, 0.12, transform=ax_action.transAxes, facecolor=TOKENS["blue"], edgecolor="none"))
        ax_action.text(0.052, y + 0.105, num, transform=ax_action.transAxes, ha="center", va="center", color="white", fontsize=13, fontproperties=FONT_PROP, fontweight="bold")
        ax_action.text(0.1, y + 0.145, action_title, transform=ax_action.transAxes, fontsize=12, color=TOKENS["ink"], fontproperties=FONT_PROP, fontweight="bold", va="center")
        ax_action.text(0.1, y + 0.075, body, transform=ax_action.transAxes, fontsize=9.5, color=TOKENS["muted"], fontproperties=FONT_PROP, va="center")

    fig.text(0.04, 0.045, "Source: cleaned feedback stats JSON | 개인정보는 시각화에 포함하지 않음", fontsize=9, color=TOKENS["muted"], fontproperties=FONT_PROP)
    png_path = out_dir / f"{stem}.png"
    pdf_path = out_dir / f"{stem}.pdf"
    fig.savefig(png_path, bbox_inches="tight", facecolor=TOKENS["surface"])
    fig.savefig(pdf_path, bbox_inches="tight", facecolor=TOKENS["surface"])
    return png_path, pdf_path


def main():
    parser = argparse.ArgumentParser(description="Render feedback dashboard PNG/PDF from stats JSON.")
    parser.add_argument("--stats-json", required=True, help="Path to feedback stats JSON.")
    parser.add_argument("--out-dir", required=True, help="Output directory.")
    parser.add_argument("--stem", default="feedback_dashboard", help="Output file stem.")
    parser.add_argument("--title", default="후기 한눈에 보기", help="Dashboard title.")
    parser.add_argument("--subtitle", default="만족도, 회차 비교, 좋았던 점, 후속 요청 요약", help="Dashboard subtitle.")
    args = parser.parse_args()

    with open(args.stats_json, encoding="utf-8") as f:
        stats = json.load(f)

    png_path, pdf_path = build_dashboard(stats, Path(args.out_dir), args.stem, args.title, args.subtitle)
    print(json.dumps({"png": str(png_path), "pdf": str(pdf_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
