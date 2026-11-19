#!/usr/bin/env python3
"""Render the 19 November 2026 world-news front page (1024x1024 PNG).

Build-time tool only: the shipped entry is the rendered entry.png plus a
one-line main.py that copies it (the grader runs stdlib-only, no PIL).
Run:  python3 draw_news.py   ->  entry.png next to this file.

Stories were checked against Reuters, AP, BBC, Le Monde, WIRED, IMD and
The Hindu on 19 November 2026: every item happened, or was first
reported, on Thursday 19 November 2026. Refreshed in the evening of
19 Nov with the day's later stories (ICJ Rohingya judgment, Bangladesh
lockdown, Indonesia asset-seizure law, Houthi strike on Riyadh's PIF
tower, Kerch Bridge hit).
"""
import math

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
NAVY = (13, 27, 62)
NAVY2 = (24, 44, 92)
GOLD = (201, 162, 39)
RED = (178, 34, 34)
PAPER = (250, 247, 240)
INK = (18, 18, 18)
GREY = (96, 96, 96)
CARD = (255, 255, 255)
LINE = (200, 196, 188)
BODY = (52, 52, 52)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def f(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(d, text, font, max_w):
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def para(d, x, y, text, font, max_w, leading, fill=BODY):
    for line in wrap_text(d, text, font, max_w):
        d.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def mini_flag(d, x, y, w, h, country):
    if country == "cn":
        d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
        d.polygon([(x + 8, y + 8), (x + 13, y + 17), (x + 4, y + 12),
                   (x + 12, y + 12), (x + 3, y + 17)], fill=(255, 222, 0))
    elif country == "us":
        for i in range(7):
            d.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7],
                        fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
        d.rectangle([x, y, x + w * 0.45, y + h * 4 // 7], fill=(60, 59, 110))
    else:  # ru
        d.rectangle([x, y, x + w, y + h // 3], fill=(255, 255, 255))
        d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=(0, 57, 166))
        d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(213, 0, 50))


def glyph_summit(d, cx, cy, r, col):
    # three chairs around a table
    d.ellipse([cx - r * 0.9, cy - r * 0.15, cx + r * 0.9, cy + r * 0.35],
              outline=col, width=5)
    d.line([cx - r * 0.9, cy + r * 0.1, cx + r * 0.9, cy + r * 0.1],
           fill=col, width=4)
    for dx in (-0.62, 0, 0.62):
        d.ellipse([cx + dx * r - r * 0.2, cy - r * 0.85,
                   cx + dx * r + r * 0.2, cy - r * 0.45], fill=col)


def glyph_rocket(d, cx, cy, r, col):
    d.polygon([(cx, cy - r), (cx + r * 0.35, cy + r * 0.1),
               (cx + r * 0.15, cy + r * 0.55), (cx, cy + r * 0.25),
               (cx - r * 0.15, cy + r * 0.55), (cx - r * 0.35, cy + r * 0.1)],
              fill=col)
    d.polygon([(cx - r * 0.45, cy + r * 0.6), (cx - r * 0.1, cy + r * 0.45),
               (cx - r * 0.2, cy + r * 0.95)], fill=col)
    d.polygon([(cx + r * 0.45, cy + r * 0.6), (cx + r * 0.1, cy + r * 0.45),
               (cx + r * 0.2, cy + r * 0.95)], fill=col)


def glyph_tank(d, cx, cy, r, col):
    # side view: hull, turret, barrel, wheels
    d.rectangle([cx - r * 0.85, cy - r * 0.15, cx + r * 0.75, cy + r * 0.35],
                fill=col)
    d.rectangle([cx - r * 0.4, cy - r * 0.6, cx + r * 0.35, cy - r * 0.1],
                fill=col)
    d.line([cx + r * 0.35, cy - r * 0.35, cx + r, cy - r * 0.35],
           fill=col, width=5)
    for dx in (-0.55, 0, 0.55):
        d.ellipse([cx + dx * r - 6, cy + r * 0.35, cx + dx * r + 6,
                   cy + r * 0.6], fill=col)


def glyph_chart(d, cx, cy, r, col):
    d.line([cx - r, cy + r * 0.7, cx + r, cy + r * 0.7], fill=col, width=4)
    pts = [(cx - r * 0.8, cy - r * 0.1), (cx - r * 0.35, cy - r * 0.45),
           (cx, cy - r * 0.15), (cx + r * 0.4, cy - r * 0.6),
           (cx + r * 0.85, cy + r * 0.35)]
    d.line(pts, fill=col, width=5, joint="curve")
    d.polygon([(cx + r * 0.85, cy + r * 0.35), (cx + r * 0.55, cy + r * 0.35),
               (cx + r * 0.85, cy + r * 0.05)], fill=col)


def glyph_storm(d, cx, cy, r, col):
    for k in range(3):
        a0 = k * 120 + 20
        d.arc([cx - r + k * 7, cy - r + k * 7, cx + r - k * 7, cy + r - k * 7],
              a0, a0 + 210, fill=col, width=5)


def glyph_gavel(d, cx, cy, r, col):
    d.line([cx - r * 0.7, cy + r * 0.15, cx + r * 0.7, cy - r * 0.55],
           fill=col, width=7)
    d.rectangle([cx - r * 0.95, cy - r * 0.05, cx - r * 0.35, cy + r * 0.35],
                fill=col)
    d.rectangle([cx + r * 0.35, cy - r * 0.75, cx + r * 0.95, cy - r * 0.35],
                fill=col)
    d.line([cx - r * 0.7, cy + r * 0.75, cx + r * 0.7, cy + r * 0.75],
           fill=col, width=5)


def glyph_chip(d, cx, cy, r, col):
    d.rectangle([cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6],
                outline=col, width=5)
    d.rectangle([cx - r * 0.25, cy - r * 0.25, cx + r * 0.25, cy + r * 0.25],
                fill=col)
    for dx in (-0.35, 0, 0.35):
        d.line([cx + dx * r, cy - r * 0.95, cx + dx * r, cy - r * 0.6],
               fill=col, width=4)
        d.line([cx + dx * r, cy + r * 0.6, cx + dx * r, cy + r * 0.95],
               fill=col, width=4)
    for dy in (-0.35, 0, 0.35):
        d.line([cx - r * 0.95, cy + dy * r, cx - r * 0.6, cy + dy * r],
               fill=col, width=4)
        d.line([cx + r * 0.6, cy + dy * r, cx + r * 0.95, cy + dy * r],
               fill=col, width=4)


def glyph_flame(d, cx, cy, r, col):
    # flame: outer teardrop with an inner notch
    d.polygon([(cx, cy - r), (cx + r * 0.5, cy - r * 0.25),
               (cx + r * 0.7, cy + r * 0.3), (cx + r * 0.35, cy + r * 0.95),
               (cx - r * 0.35, cy + r * 0.95), (cx - r * 0.7, cy + r * 0.3),
               (cx - r * 0.5, cy - r * 0.25)], fill=col)
    d.polygon([(cx, cy + r * 0.1), (cx + r * 0.28, cy + r * 0.45),
               (cx, cy + r * 0.8), (cx - r * 0.28, cy + r * 0.45)],
              fill=(200, 90, 0))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 148], fill=NAVY)
    d.rectangle([0, 148, W, 152], fill=GOLD)
    d.text((512, 62), "THE WORLD IN ONE DAY", font=f(SERIF_B, 58),
           fill=(255, 255, 255), anchor="mm")
    d.text((512, 118), "THURSDAY  ·  19 NOVEMBER 2026", font=f(SANS_B, 30),
           fill=GOLD, anchor="mm")

    # ---- lead story ----------------------------------------------------
    y0 = 160
    d.rectangle([28, y0, W - 28, 372], fill=CARD, outline=LINE, width=2)
    d.text((52, y0 + 16), "APEC  ·  SHENZHEN, CHINA  —  THE LEAD STORY",
           font=f(SANS_B, 21), fill=RED)
    yy = y0 + 48
    for ln in ("Xi, Trump and Putin meet", "in Shenzhen — a first"):
        d.text((52, yy), ln, font=f(SERIF_B, 40), fill=INK)
        yy += 46
    yy += 4
    yy = para(d, 52, yy,
              "The first-ever trilateral summit: one hour on nuclear arms, "
              "the Iran war, Ukraine, trade and AI chips.",
              f(SANS, 23), 660, 30)
    fx, fy = 800, y0 + 54
    for i, c in enumerate(("cn", "us", "ru")):
        mini_flag(d, fx, fy + i * 44, 150, 34, c)
    d.text((fx + 75, fy + 3 * 44 + 8), "CHINA · USA · RUSSIA",
           font=f(SANS_B, 15), fill=GREY, anchor="ma")

    # ---- story grid ----------------------------------------------------
    stories = [
        ("THE GULF", "Iran strikes a US base\nin Kuwait",
         "Tehran hits Ali Al Salem air base — its first attack on Kuwait "
         "since September; Bahrain stops a third attack in a week.",
         glyph_rocket, (178, 34, 34)),
        ("GAZA", "Israeli tanks cross\nthe Yellow Line",
         "A rare ground raid in central Gaza — the first crossing of the "
         "ceasefire line since October 2025.",
         glyph_tank, (24, 44, 92)),
        ("MARKETS", "Fed points to more\nhikes; Dow falls 561",
         "Fed minutes show most officials expect further rate rises; the "
         "S&P 500 falls for a fifth straight session.",
         glyph_chart, (0, 90, 60)),
        ("WEATHER", "Cyclone Akvan bears\ndown on India",
         "Red warning on the Andhra–Odisha coast; gale winds from this "
         "morning and extremely heavy rain; landfall at noon Friday.",
         glyph_storm, (150, 80, 0)),
        ("THE HAGUE", "World Court rules on\nRohingya case",
         "Judges find Myanmar's forces killed thousands of Rohingya in "
         "2017 and committed widespread sexual violence.",
         glyph_gavel, (24, 44, 92)),
        ("BANGLADESH", "Yunus home torched as\nlockdown bites",
         "Four killed in 28 districts as the Awami League's lockdown "
         "bites; ex-leader Yunus's ancestral home is set ablaze.",
         glyph_flame, (200, 90, 0)),
    ]
    gx, gy = 28, 388
    cw, ch, gap = 476, 152, 16
    for i, (kicker, head, body, glyph, col) in enumerate(stories):
        x = gx + (i % 2) * (cw + gap)
        y = gy + (i // 2) * (ch + gap)
        d.rectangle([x, y, x + cw, y + ch], fill=CARD, outline=LINE, width=2)
        d.ellipse([x + 18, y + 18, x + 82, y + 82], fill=col)
        glyph(d, x + 50, y + 50, 22, (255, 255, 255))
        tx = x + 98
        d.text((tx, y + 12), kicker, font=f(SANS_B, 17), fill=col)
        yy = y + 36
        for ln in head.split("\n"):
            d.text((tx, yy), ln, font=f(SERIF_B, 25), fill=INK)
            yy += 28
        para(d, tx, yy + 2, body, f(SANS, 16), cw - 118, 20)

    # ---- also today ----------------------------------------------------
    y = 388 + 3 * ch + 2 * gap + 12  # 888
    d.rectangle([28, y, W - 28, y + 84], fill=NAVY2)
    d.text((44, y + 42), "ALSO TODAY", font=f(SANS_B, 19), fill=GOLD,
           anchor="lm")
    items = ("Jeffries poised to be first Black Speaker  •  "
             "Anthropic shares debut  •  "
             "Indonesia passes asset-seizure law  •  "
             "Houthi missile damages Riyadh's PIF tower  •  "
             "Kerch Bridge hit a third time this week  •  "
             "Trump–Xi hold a bilateral on AI chips")
    yy = y + 12
    for ln in wrap_text(d, items, f(SANS, 17), W - 28 - 44 - 190):
        d.text((234, yy), ln, font=f(SANS, 17), fill=(255, 255, 255))
        yy += 22

    # ---- footer --------------------------------------------------------
    fy = 982
    d.line([28, fy, W - 28, fy], fill=LINE, width=2)
    d.text((512, fy + 20),
           "All events happened or were first reported on 19 November 2026  ·  Sources: Reuters, AP, BBC, Le Monde, The Hindu",
           font=f(SANS, 16), fill=GREY, anchor="ma")

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    build()
