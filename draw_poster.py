#!/usr/bin/env python3
"""Render the Tuesday 17 November 2026 world-news front page, 1024x1024.

Fresh v3 rewrite: a newspaper front page called THE WORLD. It carries
31 stories and 13 illustrations across six continents -- a lead summit
story with a skyline and three flags, two illustrated rail panels, a
world map with twelve numbered flashpoints, a four-story middle band
with drawn icons, and a 24-item day in brief.

Run: python3 draw_poster.py
Writes entry.png next to this file. Deterministic: same input, same bytes.
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 242, 230)
INK = (24, 24, 24)
NAVY = (18, 32, 60)
RED = (184, 28, 28)
TEAL = (14, 74, 90)
GOLD = (198, 160, 38)
GREY = (92, 92, 92)
WHITE = (255, 255, 255)
SEA = (213, 225, 234)
SKY = (222, 231, 239)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap into lines that fit max_w pixels."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(draw, x, y, lines, fnt, fill, leading=None):
    """Draw lines from (x, y); return the y just below the last line."""
    step = leading if leading is not None else int(fnt.size * 1.22)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += step
    return y


def star(draw, cx, cy, outer, inner, points=5):
    """Five-pointed star polygon centred on (cx, cy)."""
    pts = []
    for i in range(points * 2):
        r = outer if i % 2 == 0 else inner
        a = math.radians(-90 + i * 180.0 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def paint_us(draw, x, y, w, h):
    """Thirteen stripes and a starred canton."""
    stripe = h / 13.0
    for i in range(13):
        colour = (178, 34, 52) if i % 2 == 0 else WHITE
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe], fill=colour)
    cw, ch = w * 0.4, stripe * 7
    draw.rectangle([x, y, x + cw, y + ch], fill=(30, 51, 101))
    for r in range(5):
        for c in range(6):
            sx = x + 6 + c * (cw - 10) / 5.0
            sy = y + 5 + r * (ch - 8) / 4.0
            draw.ellipse([sx - 1.6, sy - 1.6, sx + 1.6, sy + 1.6], fill=WHITE)


def paint_cn(draw, x, y, w, h):
    """Red field, one large star and four small ones."""
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    draw.polygon(star(draw, x + w * 0.18, y + h * 0.30, h * 0.20, h * 0.08),
                 fill=(255, 222, 0))
    for fx, fy in [(0.42, 0.14), (0.52, 0.26), (0.52, 0.44), (0.42, 0.56)]:
        draw.polygon(star(draw, x + w * fx, y + h * fy, h * 0.07, h * 0.03),
                     fill=(255, 222, 0))


def paint_ru(draw, x, y, w, h):
    """White over blue over red."""
    for i, colour in enumerate([WHITE, (0, 57, 166), (213, 0, 50)]):
        draw.rectangle([x, y + i * h / 3.0, x + w, y + (i + 1) * h / 3.0], fill=colour)


def towers(draw, x, y, w, h, colour):
    """A dark city skyline with lit windows and one spire."""
    base = y + h
    shapes = [(0.00, 0.55), (0.10, 0.75), (0.20, 0.45), (0.30, 0.85),
              (0.42, 0.60), (0.52, 0.95), (0.64, 0.50), (0.74, 0.70),
              (0.84, 0.58), (0.93, 0.80)]
    tw = w / len(shapes)
    for i, (fx, fh) in enumerate(shapes):
        tx = x + i * tw
        th = h * fh
        draw.rectangle([tx, base - th, tx + tw - 2, base], fill=colour)
        if i == 5:
            draw.polygon([(tx + tw / 2 - 3, base - th), (tx + tw / 2 + 3, base - th),
                          (tx + tw / 2, base - th - 26)], fill=colour)
    for i in range(46):
        wx = x + 8 + (i * 37) % int(w - 16)
        wy = base - 14 - (i * 53) % int(h * 0.7)
        draw.rectangle([wx, wy, wx + 4, wy + 6], fill=GOLD)


def globe(draw, cx, cy, r):
    """A small line-drawn globe for the masthead."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=3)
    draw.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], outline=NAVY, width=2)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=NAVY, width=2)
    draw.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], 0, 360, fill=NAVY, width=2)


def icon_chip(draw, x, y, s):
    draw.rectangle([x, y, x + s, y + s], fill=(118, 185, 0))
    draw.rectangle([x + s * 0.18, y + s * 0.18, x + s * 0.82, y + s * 0.82],
                   fill=(20, 60, 0))
    for k in range(3):
        yy = y + s * 0.22 + k * s * 0.28
        draw.rectangle([x - s * 0.12, yy, x, yy + s * 0.12], fill=GREY)
        draw.rectangle([x + s, yy, x + s * 1.12, yy + s * 0.12], fill=GREY)
    draw.text((x + s / 2, y + s / 2), "NV", font=load_font(SANS_B, 15),
              fill=WHITE, anchor="mm")


def icon_phone(draw, x, y, s):
    draw.rounded_rectangle([x + s * 0.18, y, x + s * 0.82, y + s], radius=6,
                           outline=NAVY, width=3)
    draw.polygon([(x + s * 0.5, y + s * 0.22), (x + s * 0.78, y + s * 0.66),
                  (x + s * 0.22, y + s * 0.66)], fill=(255, 200, 40), outline=INK)
    draw.text((x + s * 0.5, y + s * 0.52), "!", font=load_font(SANS_B, 14),
              fill=INK, anchor="mm")


def icon_cross(draw, x, y, s):
    draw.ellipse([x, y, x + s, y + s], fill=RED)
    draw.rectangle([x + s * 0.44, y + s * 0.18, x + s * 0.56, y + s * 0.82], fill=WHITE)
    draw.rectangle([x + s * 0.18, y + s * 0.44, x + s * 0.82, y + s * 0.56], fill=WHITE)


def icon_camera(draw, x, y, s):
    draw.rounded_rectangle([x, y + s * 0.18, x + s, y + s], radius=8, fill=NAVY)
    draw.rectangle([x + s * 0.32, y, x + s * 0.62, y + s * 0.22], fill=NAVY)
    draw.ellipse([x + s * 0.28, y + s * 0.32, x + s * 0.72, y + s * 0.86],
                 outline=GOLD, width=3)
    draw.ellipse([x + s * 0.42, y + s * 0.46, x + s * 0.58, y + s * 0.68],
                 fill=GOLD)


# ---- World map: simplified continent outlines as (lon, lat) ----------
LAND = [
    [(-168, 66), (-140, 70), (-120, 71), (-95, 72), (-80, 73), (-70, 62),
     (-60, 55), (-65, 45), (-75, 38), (-80, 26), (-86, 16), (-92, 14),
     (-97, 16), (-105, 22), (-114, 29), (-122, 37), (-125, 48), (-135, 58),
     (-155, 60), (-165, 64)],
    [(-79, 9), (-70, 11), (-60, 8), (-50, 4), (-40, -3), (-35, -8),
     (-40, -20), (-48, -27), (-57, -35), (-65, -41), (-70, -50), (-73, -40),
     (-72, -25), (-77, -12), (-80, -3), (-79, 9)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (12, 56),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 68), (40, 68),
     (35, 60), (30, 55), (28, 48), (23, 45), (19, 42), (15, 40), (12, 38),
     (8, 38), (3, 37), (0, 36)],
    [(-17, 15), (-12, 25), (-6, 33), (0, 36), (10, 37), (20, 32), (30, 31),
     (34, 28), (38, 20), (43, 12), (48, 11), (51, 10), (46, 0), (40, -10),
     (35, -20), (30, -29), (25, -34), (18, -33), (14, -25), (12, -15),
     (9, -5), (9, 4), (-8, 5), (-14, 10)],
    [(32, 70), (45, 68), (60, 69), (75, 72), (90, 75), (105, 76), (120, 74),
     (135, 72), (150, 70), (162, 66), (170, 64), (160, 58), (150, 55),
     (140, 50), (130, 42), (127, 38), (122, 32), (115, 24), (108, 15),
     (104, 9), (100, 8), (97, 15), (92, 21), (86, 19), (80, 10), (76, 15),
     (72, 20), (66, 25), (58, 26), (52, 28), (48, 30), (44, 32), (40, 36),
     (36, 40), (33, 44), (30, 48), (32, 60), (32, 70)],
    [(113, -22), (120, -15), (128, -13), (136, -12), (142, -11), (147, -19),
     (150, -27), (150, -37), (143, -38), (135, -34), (128, -32), (120, -34),
     (114, -30), (113, -22)],
]
# (number, label, lon, lat) -- a few nudged so the dots do not overlap.
SPOTS = [
    (1, "SHENZHEN", 114.1, 22.5),
    (2, "HORMUZ", 59.0, 29.0),
    (3, "BAHRAIN", 51.0, 23.0),
    (4, "KERCH", 38.0, 44.0),
    (5, "KYIV", 28.0, 52.0),
    (6, "GAZA", 32.0, 28.0),
    (7, "PARIS", 2.35, 48.85),
    (8, "TOKYO", 139.7, 35.7),
    (9, "WASHINGTON", -77.0, 38.9),
    (10, "RIYADH", 43.0, 18.0),
    (11, "BERLIN", 13.4, 52.5),
    (12, "FLORIDA", -84.0, 25.0),
]


def chart(draw, x, y, w, h):
    """Stylised world map with numbered flashpoints."""
    draw.rectangle([x, y, x + w, y + h], fill=SEA)

    def px(lon, lat):
        return (x + (lon + 180.0) / 360.0 * w,
                y + (75.0 - lat) / 115.0 * h)

    for poly in LAND:
        draw.polygon([px(lon, lat) for lon, lat in poly], fill=NAVY)
    num_f = load_font(SANS_B, 9)
    for n, _label, lon, lat in SPOTS:
        mx, my = px(lon, lat)
        draw.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=RED,
                     outline=WHITE, width=2)
        draw.text((mx, my), str(n), font=num_f, fill=WHITE, anchor="mm")


def brief_line(draw, x, y, kicker, text, max_w):
    """One brief line: bold red kicker, dash, plain text. Warns on overflow."""
    kf = load_font(SANS_B, 12)
    tf = load_font(SANS, 12)
    draw.text((x, y), kicker, font=kf, fill=RED)
    tx = x + draw.textlength(kicker, font=kf)
    draw.text((tx, y), " \u2014 " + text, font=tf, fill=INK)
    total = tx + draw.textlength(" \u2014 " + text, font=tf) - x
    if total > max_w:
        print(f"WARNING: brief line overflows by {total - max_w:.0f}px: {kicker}")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, W - 11, H - 11], outline=NAVY, width=5)
    d.rectangle([20, 20, W - 21, H - 21], outline=NAVY, width=1)

    # ---- Masthead -------------------------------------------------------
    globe(d, 150, 62, 24)
    globe(d, 874, 62, 24)
    d.text((512, 28), "THE WORLD", font=load_font(SERIF_B, 66), fill=NAVY, anchor="ma")
    d.line([(36, 110), (988, 110)], fill=NAVY, width=2)
    d.text((36, 118), "TUESDAY, 17 NOVEMBER 2026", font=load_font(SANS_B, 17), fill=INK)
    d.text((988, 120), "31 STORIES  \u2022  13 ILLUSTRATED  \u2022  6 CONTINENTS",
           font=load_font(SANS_B, 14), fill=INK, anchor="ra")
    d.line([(36, 148), (988, 148)], fill=NAVY, width=2)

    # ---- Lead story: Trump-Xi-Putin summit ------------------------------
    lx, lw = 36, 636
    d.text((lx, 160), "APEC SUMMIT  \u2022  SHENZHEN, CHINA",
           font=load_font(SANS_B, 19), fill=RED)
    head = wrap(d, "TRUMP, XI & PUTIN TO MEET IN SHENZHEN", load_font(SERIF_B, 44), lw)
    y = 188
    for line in head:
        d.text((lx, y), line, font=load_font(SERIF_B, 44), fill=NAVY)
        y += 52
    sub = ("Trump lands in China for the first three-way summit with "
           "Xi Jinping and Vladimir Putin \u2014 as war in the Gulf and a "
           "spy scandal hang over the talks.")
    y = block(d, lx, 296, wrap(d, sub, load_font(SANS, 21), lw),
              load_font(SANS, 21), INK, 26)

    # Skyline with the three flags underneath the lead text.
    vx, vy, vw, vh = lx, 386, lw, 110
    d.rectangle([vx, vy, vx + vw, vy + vh], fill=SKY)
    towers(d, vx, vy + 30, vw, vh - 30, NAVY)
    for i, flag in enumerate([paint_us, paint_cn, paint_ru]):
        fx = vx + 56 + i * 210
        d.line([(fx + 44, vy + 6), (fx + 44, vy + 86)], fill=GREY, width=3)
        d.ellipse([fx + 41, vy + 2, fx + 47, vy + 8], fill=GOLD)
        flag(d, fx - 44, vy + 8, 88, 56)
    d.rectangle([vx, vy + vh - 4, vx + vw, vy + vh], fill=NAVY)

    # ---- Right rail ------------------------------------------------------
    rx, rw = 700, 288
    # Panel A: US strikes Iran.
    d.rectangle([rx, 156, rx + rw, 296], fill=TEAL)
    d.text((rx + 14, 168), "US STRIKES IRAN", font=load_font(SANS_B, 22), fill=WHITE)
    d.text((rx + 14, 196), "HORMUZ STANDOFF", font=load_font(SANS_B, 22),
           fill=(255, 214, 130))
    d.rectangle([rx, 240, rx + rw, 296], fill=(16, 90, 110))
    for k in range(4):
        d.arc([rx - 40 + k * 80, 282, rx + 40 + k * 80, 318], 200, 340,
              fill=(120, 190, 205), width=3)
    d.rectangle([rx + 96, 274, rx + 200, 294], fill=(225, 225, 225))
    d.rectangle([rx + 116, 254, rx + 180, 274], fill=(150, 150, 150))
    d.polygon(star(d, rx + 148, 250, 22, 9), fill=(255, 170, 40))
    d.polygon(star(d, rx + 148, 250, 12, 5), fill=(255, 220, 120))
    block(d, rx + 14, 304, wrap(d, "US hits missile sites; Iran drones Bahrain again.",
          load_font(SANS, 16), rw - 28), load_font(SANS, 16), INK, 21)
    # Panel B: Kerch Bridge hit.
    by = 352
    d.rectangle([rx, by, rx + rw, by + 100], fill=(64, 58, 74))
    d.text((rx + 14, by + 10), "KERCH BRIDGE HIT", font=load_font(SANS_B, 22), fill=WHITE)
    d.line([(rx, by + 60), (rx + 110, by + 60)], fill=(230, 230, 230), width=4)
    d.line([(rx + 178, by + 60), (rx + rw, by + 60)], fill=(230, 230, 230), width=4)
    d.line([(rx + 110, by + 60), (rx + 150, by + 82)], fill=(230, 230, 230), width=4)
    for cx, cy, r in [(rx + 128, by + 46, 8), (rx + 144, by + 38, 11),
                      (rx + 160, by + 48, 7)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 150, 150))
    d.rectangle([rx, by + 88, rx + rw, by + 100], fill=(30, 44, 66))
    block(d, rx + 14, 460, wrap(d, "Drones hit the Crimea link; Russia hits back.",
          load_font(SANS, 16), rw - 28), load_font(SANS, 16), INK, 21)

    d.line([(36, 510), (988, 510)], fill=NAVY, width=2)

    # ---- World map strip --------------------------------------------------
    d.text((36, 518), "WHERE THE DAY HAPPENED", font=load_font(SANS_B, 15), fill=RED)
    d.text((988, 520), "SIX CONTINENTS  \u2022  TWELVE FLASHPOINTS",
           font=load_font(SANS_B, 13), fill=GREY, anchor="ra")
    chart(d, 36, 540, 952, 96)
    legend = "  \u2022  ".join(f"{n} {label}" for n, label, _lo, _la in SPOTS)
    size = 13
    while d.textlength(legend, font=load_font(SANS, size)) > 952 and size > 9:
        size -= 1
    d.text((36, 642), legend, font=load_font(SANS, size), fill=INK)

    d.line([(36, 664), (988, 664)], fill=NAVY, width=2)

    # ---- Middle band: four stories ---------------------------------------
    mids = [
        (icon_chip, "NVIDIA CHIEF OUT IN SPY SCANDAL",
         "Huang resigns over an affair with an alleged Chinese agent."),
        (icon_phone, "SCREENS GO DARK AT APPLE AND THE NSA",
         "Outages hit airports, banks, Microsoft and Apple; officials "
         "insist it is patching."),
        (icon_cross, "US LOSES MEASLES-FREE STATUS",
         "Elimination status gone for the first time since 2000 as "
         "vaccination rates fall."),
        (icon_camera, "NAT GEO PICTURES OF THE YEAR",
         "The year's best photographs are out."),
    ]
    for (cx, cw), (icon, head, body) in zip([(36, 226), (278, 226), (520, 226),
                                             (762, 226)], mids):
        icon(d, cx, 674, 44)
        y = block(d, cx, 726, wrap(d, head, load_font(SANS_B, 17), cw),
                  load_font(SANS_B, 17), NAVY, 21)
        y = block(d, cx, y + 4, wrap(d, body, load_font(SANS, 13), cw),
                  load_font(SANS, 13), INK, 16)
        if y > 828:
            print(f"WARNING: middle column overflows to y={y}: {head[:30]}")

    d.line([(36, 830), (988, 830)], fill=NAVY, width=2)

    # ---- Bottom: the day in brief ----------------------------------------
    d.text((36, 838), "THE DAY IN BRIEF", font=load_font(SANS_B, 17), fill=RED)
    brief = [
        [("DIRTY BOMB", "Trump takes report seriously"),
         ("3RD CARRIER", "Another carrier for the Gulf"),
         ("HOUTHIS", "5 drones at Saudi pipeline"),
         ("LEBANON", "Strikes and shelling in south"),
         ("UK SANCTIONS", "West Bank firms hit"),
         ("GAZA AID", "Four nations urge access"),
         ("C-130", "Activist held over $60m jet"),
         ("ETHANOL PLANT", "Worker held in plot")],
        [("FLORIDA", "Floods as western storm builds"),
         ("TIGER WOODS", "Golf return in December"),
         ("APPLE", "Sign-in and store faults fixed"),
         ("IRAQ", "Oil flows via Kirkuk\u2013Ceyhan"),
         ("BERLIN", "28 raids in Hezbollah-linked ban"),
         ("GAZA RAINS", "Winter rain floods shelters"),
         ("OMAN", "24 saved from burning tanker"),
         ("PARIS", "Depardieu pleads guilty in court")],
        [("TOKYO", "Japan scrambles jets at Russians"),
         ("KYIV", "Air alerts as Russia answers bridge hit"),
         ("WASHINGTON", "Trump flies to Shenzhen"),
         ("RIYADH", "Saudis on alert after pipeline attack"),
         ("MOSCOW", "Kremlin vows reply to bridge strike"),
         ("SUMMIT", "First meeting of all three leaders"),
         ("STRAIT", "Hormuz shipping on alert"),
         ("BEIJING", "China hosts first three-way summit")],
    ]
    for col, items in enumerate(brief):
        ix = 36 + col * 326
        for row, (kw, txt) in enumerate(items):
            brief_line(d, ix, 864 + row * 15, kw, txt, 300)

    d.line([(36, 984), (988, 984)], fill=NAVY, width=1)
    d.text((512, 990), "DRAWN FROM TUESDAY'S REPORTING  \u2022  17 NOVEMBER 2026",
           font=load_font(SANS, 12), fill=GREY, anchor="ma")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG")
    data = open(out, "rb").read()
    print("wrote", out, len(data), "bytes,",
          hashlib.sha256(data).hexdigest()[:16], "size", img.size)


if __name__ == "__main__":
    main()
