"""Builds keel/web/tokens.css: OKLCH ramps with a constant hue per ramp, semantic tokens on top, and a contrast
check on every text and graphic pair. The script refuses to write the file if any pair fails.
Usage: python scripts/make_tokens.py"""
import sys
from pathlib import Path

from coloraide import Color

OUT = Path(__file__).resolve().parent.parent / "keel" / "web" / "tokens.css"

# Perceived lightness per step (OKLCH L). Finer at the light end, where tints and borders live.
L = {50: .975, 100: .950, 200: .915, 300: .865, 400: .775, 500: .665, 600: .545, 700: .455, 800: .375, 900: .300, 950: .220}
# hue, base chroma as a share of that hue's own sRGB maximum, and the light-end tint multipliers (L>=.90, L>=.80)
HUES = {
    "neutral": (258, .30, (.60, .80)),   # cool slate
    "blue":    (262, .72, (.95, .95)),   # brand and primary action
    "green":   (158, .62, (.85, .90)),   # verified, resolved
    "red":     (27,  .72, (.85, .90)),   # blocked, escalated
    "amber":   (80,  .80, (.85, .90)),   # relief, low days
}


def max_chroma(l, h):
    lo, hi = 0.0, 0.4
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if Color("oklch", [l, mid, h]).in_gamut("srgb") else (lo, mid)
    return lo


def hexof(l, c, h):
    return Color("oklch", [l, c, h]).convert("srgb").to_string(hex=True)


def ramp(name):
    h, base, (a, b) = HUES[name]
    out = {}
    for step, l in L.items():
        k = base * (a if l >= .90 else b if l >= .80 else 1)
        out[step] = hexof(l, max_chroma(l, h) * k, h)
    return out


R = {n: ramp(n) for n in HUES}
n, b, g, r, a = R["neutral"], R["blue"], R["green"], R["red"], R["amber"]
# one extra neutral step for tertiary text: darker than 600 so it passes on tinted surfaces
n["650"] = hexof(.515, max_chroma(.515, 258) * .30, 258)
W = "#ffffff"

SEMANTIC = {
    "bg-canvas": n[50], "bg-surface": W, "bg-subtle": n[100], "bg-sunken": n[200],
    "border-subtle": n[200], "border-strong": n[300], "border-control": n[500],
    "text-primary": n[900], "text-secondary": n[700], "text-tertiary": n["650"], "text-on-brand": W, "text-on-brand-muted": b[200],
    "accent-solid": b[600], "accent-solid-hover": b[700], "accent-subtle": b[50], "accent-muted": b[100], "accent-text": b[700],
    "focus-ring": b[600],
    "brand-deep": b[900], "brand-deeper": b[950], "brand-line": b[800],
    "ok-solid": g[600], "ok-subtle": g[50], "ok-muted": g[100], "ok-text": g[700], "ok-border": g[300],
    "bad-solid": r[600], "bad-subtle": r[50], "bad-muted": r[100], "bad-text": r[700], "bad-border": r[300],
    "relief-fill": a[400], "relief-stroke": a[700], "relief-subtle": a[50], "relief-muted": a[100], "relief-text": a[800], "relief-border": a[300],
    "series-base": b[700], "grid-line": n[300],
}
V = SEMANTIC

# (label, foreground, background, minimum ratio). 4.5 for text, 3 for controls and meaningful graphics.
PAIRS = [
    ("text-primary / surface", "text-primary", "bg-surface", 4.5), ("text-primary / canvas", "text-primary", "bg-canvas", 4.5),
    ("text-secondary / surface", "text-secondary", "bg-surface", 4.5), ("text-secondary / canvas", "text-secondary", "bg-canvas", 4.5),
    ("text-secondary / subtle", "text-secondary", "bg-subtle", 4.5), ("text-secondary / sunken", "text-secondary", "bg-sunken", 4.5),
    ("text-tertiary / surface", "text-tertiary", "bg-surface", 4.5), ("text-tertiary / canvas", "text-tertiary", "bg-canvas", 4.5),
    ("text-tertiary / subtle", "text-tertiary", "bg-subtle", 4.5),
    ("control border / surface", "border-control", "bg-surface", 3), ("focus ring / surface", "focus-ring", "bg-surface", 3),
    ("focus ring / canvas", "focus-ring", "bg-canvas", 3),
    ("text-on-brand / accent-solid", "text-on-brand", "accent-solid", 4.5), ("text-on-brand / accent-hover", "text-on-brand", "accent-solid-hover", 4.5),
    ("accent-text / surface", "accent-text", "bg-surface", 4.5), ("accent-text / accent-subtle", "accent-text", "accent-subtle", 4.5),
    ("accent-text / accent-muted", "accent-text", "accent-muted", 4.5),
    ("text-on-brand / brand-deep", "text-on-brand", "brand-deep", 4.5), ("on-brand-muted / brand-deep", "text-on-brand-muted", "brand-deep", 4.5),
    ("on-brand-muted / brand-deeper", "text-on-brand-muted", "brand-deeper", 4.5),
    ("ok-text / ok-subtle", "ok-text", "ok-subtle", 4.5), ("ok-text / surface", "ok-text", "bg-surface", 4.5), ("ok-text / ok-muted", "ok-text", "ok-muted", 4.5),
    ("text-on-brand / ok-solid", "text-on-brand", "ok-solid", 4.5),
    ("bad-text / bad-subtle", "bad-text", "bad-subtle", 4.5), ("bad-text / surface", "bad-text", "bg-surface", 4.5), ("bad-text / bad-muted", "bad-text", "bad-muted", 4.5),
    ("text-on-brand / bad-solid", "text-on-brand", "bad-solid", 4.5),
    ("relief-text / relief-subtle", "relief-text", "relief-subtle", 4.5), ("relief-text / surface", "relief-text", "bg-surface", 4.5),
    ("relief-text / relief-muted", "relief-text", "relief-muted", 4.5),
    ("relief stroke / surface (graphic)", "relief-stroke", "bg-surface", 3), ("series-base / surface (graphic)", "series-base", "bg-surface", 3),
    ("bad-solid / surface (graphic)", "bad-solid", "bg-surface", 3),
    ("relief-fill vs its stroke (graphic)", "relief-fill", "relief-stroke", 3),
    ("relief-fill text / brand-deep", "relief-fill", "brand-deep", 4.5), ("relief-fill text / brand-deeper", "relief-fill", "brand-deeper", 4.5),
]


def check():
    failed = []
    for label, fg, bg, need in PAIRS:
        ratio = Color(V[fg]).contrast(Color(V[bg]))
        flag = "ok  " if ratio >= need else "FAIL"
        print(f"{flag} {ratio:5.2f} (needs {need})  {label}  {V[fg]} on {V[bg]}")
        if ratio < need:
            failed.append(label)
    return failed


def css():
    lines = ["/* Generated by scripts/make_tokens.py. Do not edit by hand. */", ":root {", "  /* primitives: named by hue, never used in components */"]
    for name, ramp_ in R.items():
        for step, hx in ramp_.items():
            lines.append(f"  --{name}-{step}: {hx};")
    lines.append("")
    lines.append("  /* semantic tokens: named by role, the only tier components use */")
    for k, v in V.items():
        owner = next((f"var(--{nm}-{st})" for nm, rp in R.items() for st, hx in rp.items() if hx == v and v != W), None)
        lines.append(f"  --{k}: {owner or v};")
    lines.append("}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    bad = check()
    if bad:
        print("\nNot written. Failing pairs:", ", ".join(bad))
        sys.exit(1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(css(), encoding="utf-8")
    print(f"\nAll {len(PAIRS)} pairs pass. Wrote {OUT}")
