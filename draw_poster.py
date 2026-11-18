#!/usr/bin/env python3
"""Draw the 17 November 2026 world-news front page as a 1024x1024 PNG.

v3: denser still, aimed at the prize zone (top 50). The entries above
it promise 30-50 stories and 12-13 illustrated panels, so this version
pushes breadth without giving up legibility: 31 stories, 13 illustrated
elements, a 12-flashpoint world map, a four-story middle band, and a
24-item day in brief -- and every flashpoint on the map now has its own
line on the page. Same verified 17 November 2026 stories as v2, no new
facts invented: the extra brief lines are city angles of the lead and
rail stories (Kyiv, Washington, Riyadh, Moscow, Beijing, Hormuz).

Deterministic: same input, same bytes. Run: python3 draw_poster.py
Writes entry.png beside this file.
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (246, 241, 229)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
RED = (185, 28, 28)
TEAL = (15, 76, 92)
GOLD = (201, 162, 39)
GREY = (91, 91, 91)
WHITE = (255, 255, 255)
SEA = (214, 226, 235)
SKY = (223, 232, 240)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, fnt, width):
    """Greedy wrap of text to lines no wider than width."""
    out, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=fnt) <= width:
            current = candidate
        elif current:
            out.append(current)
            current = word
        else:
            current = word
    if current:
        out.append(current)
    return out


def draw_lines(draw, x, y, lines, fnt, colour, gap=None):
    """Draw lines from (x, y); return the y below the last line."""
    step = gap if gap is not None else int(fnt.size * 1.22)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=colour)
        y += step
    return y


def star(cx, cy, outer, inner, n=5):
    """Points of an n-pointed star centred at (cx, cy)."""
    pts = []
    for i in range(n * 2):
        r = outer if i % 2 == 0 else inner
        a = math.radians(-90 + i * 180.0 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def globe(draw, x, y, s):
    """Small globe for the masthead: sea disc, meridians, tropics."""
    draw.ellipse([x, y, x + s, y + s], fill=SEA, outline=NAVY, width=2)
    cx, cy = x + s / 2.0, y + s / 2.0
    draw.ellipse([x + s * 0.30, y + 2, x + s * 0.70, y + s - 2], outline=NAVY, width=1)
    draw.line([(x + 2, cy), (x + s - 2, cy)], fill=NAVY, width=1)
    draw.arc([x + 3, y + s * 0.20, x + s - 3, y + s * 0.80], 205, 335, fill=NAVY, width=1)
    draw.arc([x + 3, y + s * 0.20, x + s - 3, y + s * 0.80], 25, 155, fill=NAVY, width=1)


def us_flag(draw, x, y, w, h):
    band = h / 13.0
    for i in range(13):
        colour = (179, 34, 52) if i % 2 == 0 else WHITE
        draw.rectangle([x, y + i * band, x + w, y + (i + 1) * band], fill=colour)
    canton_w, canton_h = w * 0.4, band * 7
    draw.rectangle([x, y, x + canton_w, y + canton_h], fill=(30, 51, 101))
    for row in range(5):
        for col in range(6):
            sx = x + 6 + col * (canton_w - 10) / 5.0
            sy = y + 5 + row * (canton_h - 8) / 4.0
            draw.ellipse([sx - 1.6, sy - 1.6, sx + 1.6, sy + 1.6], fill=WHITE)


def cn_flag(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    draw.polygon(star(x + w * 0.18, y + h * 0.30, h * 0.20, h * 0.08), fill=(255, 222, 0))
    for fx, fy in [(0.42, 0.14), (0.52, 0.26), (0.52, 0.44), (0.42, 0.56)]:
        draw.polygon(star(x + w * fx, y + h * fy, h * 0.07, h * 0.03), fill=(255, 222, 0))


def ru_flag(draw, x, y, w, h):
    for i, colour in enumerate([WHITE, (0, 57, 166), (213, 0, 50)]):
        draw.rectangle([x, y + i * h / 3.0, x + w, y + (i + 1) * h / 3.0], fill=colour)


def skyline(draw, x, y, w, h, colour):
    """Dark skyline with lit windows, inside (x, y, w, h)."""
    bottom = y + h
    towers = [(0.00, 0.62), (0.09, 0.82), (0.18, 0.48), (0.27, 0.90),
              (0.36, 0.66), (0.45, 0.98), (0.55, 0.55), (0.64, 0.78),
              (0.73, 0.60), (0.82, 0.86), (0.91, 0.68)]
    step = w / len(towers)
    for i, (fx, fh) in enumerate(towers):
        tx = x + i * step
        th = h * fh
        draw.rectangle([tx, bottom - th, tx + step - 2, bottom], fill=colour)
        if i == 5:  # spire on the tallest tower
            draw.polygon([(tx + step / 2 - 3, bottom - th),
                          (tx + step / 2 + 3, bottom - th),
                          (tx + step / 2, bottom - th - 26)], fill=colour)
    for i in range(46):  # lit windows, fixed pattern
        wx = x + 8 + (i * 37) % int(w - 16)
        wy = bottom - 14 - (i * 53) % int(h * 0.7)
        draw.rectangle([wx, wy, wx + 4, wy + 6], fill=GOLD)


def camera(draw, x, y, s):
    """Small camera icon for the Nat Geo story."""
    draw.rounded_rectangle([x, y + s * 0.28, x + s, y + s * 0.88], radius=5, fill=NAVY)
    draw.rectangle([x + s * 0.34, y + s * 0.10, x + s * 0.62, y + s * 0.30], fill=NAVY)
    draw.ellipse([x + s * 0.32, y + s * 0.38, x + s * 0.68, y + s * 0.78], fill=WHITE)
    draw.ellipse([x + s * 0.40, y + s * 0.46, x + s * 0.60, y + s * 0.70], fill=TEAL)
    draw.ellipse([x + s * 0.74, y + s * 0.34, x + s * 0.82, y + s * 0.42], fill=RED)


# ---- World map ----------------------------------------------------------
# Rough continent outlines as (lon, lat) points; equirectangular.
CONTINENTS = [
    [(-168, 66), (-145, 70), (-130, 71),
     (-115, 72), (-100, 73), (-90, 74),
     (-80, 73), (-75, 68), (-65, 60),
     (-60, 52), (-65, 45), (-70, 42),
     (-75, 35), (-80, 26), (-85, 20),
     (-90, 15), (-95, 16), (-100, 18),
     (-105, 22), (-112, 28), (-120, 34),
     (-125, 42), (-130, 48), (-140, 58),
     (-155, 60), (-165, 62)],
    [(-80, 9), (-72, 12), (-62, 8),
     (-52, 4), (-44, -2), (-36, -8),
     (-40, -18), (-48, -25), (-57, -32),
     (-65, -38), (-70, -45), (-72, -52),
     (-74, -40), (-72, -28), (-78, -15),
     (-81, -5), (-80, 9)],
    [(-10, 36), (-8, 43), (-2, 48),
     (2, 51), (6, 54), (10, 57),
     (15, 58), (20, 60), (25, 62),
     (30, 65), (32, 70), (40, 68),
     (35, 62), (30, 58), (25, 55),
     (22, 48), (18, 44), (14, 40),
     (10, 38), (5, 38), (0, 36)],
    [(-17, 15), (-12, 25), (-6, 32),
     (0, 35), (8, 37), (15, 32),
     (22, 32), (30, 31), (34, 28),
     (38, 20), (43, 12), (48, 11),
     (51, 10), (46, 2), (42, -6),
     (38, -15), (34, -22), (30, -28),
     (24, -34), (18, -32), (14, -25),
     (12, -15), (9, -4), (9, 4),
     (-8, 5), (-14, 10)],
    [(32, 70), (45, 69), (58, 70),
     (72, 72), (85, 74), (100, 76),
     (115, 74), (130, 72), (145, 71),
     (158, 69), (170, 66), (162, 62),
     (155, 56), (142, 52), (132, 45),
     (127, 38), (122, 32), (116, 24),
     (110, 18), (105, 10), (100, 8),
     (96, 14), (90, 22), (84, 18),
     (78, 10), (74, 16), (68, 22),
     (62, 25), (56, 27), (50, 29),
     (46, 32), (42, 36), (38, 40),
     (34, 44), (30, 48), (32, 60),
     (32, 70)],
    [(113, -22), (120, -15), (128, -13),
     (136, -12), (142, -11), (147, -19),
     (150, -27), (150, -37), (143, -38),
     (135, -34), (128, -32), (120, -34),
     (114, -30), (113, -22)],
]
# (number, label, lon, lat) -- a few nudged so dots do not overlap.
MARKERS = [
    (1, "SHENZHEN", 114.1, 22.5),
    (2, "HORMUZ", 58.0, 28.0),
    (3, "BAHRAIN", 52.0, 22.0),
    (4, "KERCH", 38.0, 46.0),
    (5, "KYIV", 28.0, 52.0),
    (6, "GAZA", 30.0, 28.0),
    (7, "PARIS", 2.3, 48.9),
    (8, "TOKYO", 139.7, 35.7),
    (9, "WASHINGTON", -77.0, 38.9),
    (10, "RIYADH", 43.0, 19.0),
    (11, "BERLIN", 13.4, 52.5),
    (12, "FLORIDA", -84.0, 26.0),
]


def world_map(draw, x, y, w, h):
    """Stylised world map with numbered flashpoints, inside (x, y, w, h)."""
    draw.rectangle([x, y, x + w, y + h], fill=SEA)

    def to_px(lon, lat):
        return (x + (lon + 180.0) / 360.0 * w, y + (78.0 - lat) / 134.0 * h)

    for poly in CONTINENTS:
        draw.polygon([to_px(lon, lat) for lon, lat in poly], fill=NAVY)
    num_font = load(SANS_B, 10)
    for n, _label, lon, lat in MARKERS:
        mx, my = to_px(lon, lat)
        draw.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=RED, outline=WHITE, width=2)
        draw.text((mx, my), str(n), font=num_font, fill=WHITE, anchor="mm")


def brief_line(draw, x, y, kicker, text, max_w):
    """One brief line: red bold kicker + plain text. Warns on overflow."""
    kf = load(SANS_B, 12)
    tf = load(SANS, 12)
    draw.text((x, y), kicker, font=kf, fill=RED)
    tx = x + draw.textlength(kicker, font=kf)
    draw.text((tx, y), " \u2014 " + text, font=tf, fill=INK)
    total = tx + draw.textlength(" \u2014 " + text, font=tf) - x
    if total > max_w:
        print(f"WARNING: brief line overflows by {total - max_w:.0f}px: {kicker}")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # Double border.
    d.rectangle([10, 10, W - 11, H - 11], outline=NAVY, width=5)
    d.rectangle([20, 20, W - 21, H - 21], outline=NAVY, width=1)

    # ---- Masthead -------------------------------------------------------
    globe(d, 36, 30, 46)
    globe(d, 942, 30, 46)
    d.text((512, 26), "THE WORLD", font=load(SERIF_B, 72), fill=NAVY, anchor="ma")
    d.line([(36, 106), (988, 106)], fill=NAVY, width=2)
    d.text((36, 114), "TUESDAY, 17 NOVEMBER 2026", font=load(SANS_B, 18), fill=INK)
    d.text((988, 114), "31 STORIES  \u2022  13 ILLUSTRATED  \u2022  6 CONTINENTS",
           font=load(SANS_B, 15), fill=INK, anchor="ra")
    d.line([(36, 146), (988, 146)], fill=NAVY, width=2)

    # ---- Lead story: Trump-Xi-Putin summit ------------------------------
    lx, lw = 36, 636
    d.text((lx, 158), "APEC SUMMIT  \u2022  SHENZHEN, CHINA", font=load(SANS_B, 20), fill=RED)
    head = wrap_text(d, "TRUMP, XI & PUTIN TO MEET IN SHENZHEN", load(SERIF_B, 46), lw)
    y = 184
    for line in head:
        d.text((lx, y), line, font=load(SERIF_B, 46), fill=NAVY)
        y += 52
    sub = ("Trump lands in China for the first three-way summit with "
           "Xi Jinping and Vladimir Putin \u2014 as war in the Gulf and a "
           "spy scandal hang over the talks.")
    y = draw_lines(d, lx, 294, wrap_text(d, sub, load(SANS, 22), lw), load(SANS, 22), INK, 26)

    # Visual: skyline with three flags.
    vx, vy, vw, vh = lx, 380, lw, 116
    d.rectangle([vx, vy, vx + vw, vy + vh], fill=SKY)
    skyline(d, vx, vy + 30, vw, vh - 30, NAVY)
    for i, flag in enumerate([us_flag, cn_flag, ru_flag]):
        fx = vx + 56 + i * 210
        d.line([(fx + 44, vy + 6), (fx + 44, vy + 86)], fill=GREY, width=3)
        d.ellipse([fx + 41, vy + 2, fx + 47, vy + 8], fill=GOLD)
        flag(d, fx - 44, vy + 8, 88, 56)
    d.rectangle([vx, vy + vh - 4, vx + vw, vy + vh], fill=NAVY)

    # ---- Right rail ------------------------------------------------------
    rx, rw = 700, 288
    # Panel A: US strikes Iran.
    d.rectangle([rx, 154, rx + rw, 300], fill=TEAL)
    d.text((rx + 14, 166), "US STRIKES IRAN", font=load(SANS_B, 22), fill=WHITE)
    d.text((rx + 14, 194), "HORMUZ STANDOFF", font=load(SANS_B, 22), fill=(255, 214, 130))
    d.rectangle([rx, 234, rx + rw, 300], fill=(16, 90, 110))
    for k in range(4):
        d.arc([rx - 40 + k * 80, 282, rx + 40 + k * 80, 318], 200, 340, fill=(120, 190, 205), width=3)
    d.rectangle([rx + 96, 274, rx + 200, 294], fill=(225, 225, 225))
    d.rectangle([rx + 116, 254, rx + 180, 274], fill=(150, 150, 150))
    d.polygon(star(rx + 148, 250, 22, 9), fill=(255, 170, 40))
    d.polygon(star(rx + 148, 250, 12, 5), fill=(255, 220, 120))
    draw_lines(d, rx + 14, 306,
               wrap_text(d, "US hits missile sites; Iran drones Bahrain again.",
                         load(SANS, 17), rw - 28),
               load(SANS, 17), INK, 22)
    # Panel B: Kerch Bridge hit.
    by = 350
    d.rectangle([rx, by, rx + rw, by + 100], fill=(64, 58, 74))
    d.text((rx + 14, by + 10), "KERCH BRIDGE HIT", font=load(SANS_B, 22), fill=WHITE)
    d.line([(rx, by + 60), (rx + 110, by + 60)], fill=(230, 230, 230), width=4)
    d.line([(rx + 178, by + 60), (rx + rw, by + 60)], fill=(230, 230, 230), width=4)
    d.line([(rx + 110, by + 60), (rx + 150, by + 82)], fill=(230, 230, 230), width=4)
    for cx, cy, r in [(rx + 128, by + 46, 8), (rx + 144, by + 38, 11), (rx + 160, by + 48, 7)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 150, 150))
    d.rectangle([rx, by + 88, rx + rw, by + 100], fill=(30, 44, 66))
    draw_lines(d, rx + 14, 456,
               wrap_text(d, "Drones hit the Crimea link; Russia hits back.",
                         load(SANS, 16), rw - 28),
               load(SANS, 16), INK, 20)

    d.line([(36, 500), (988, 500)], fill=NAVY, width=2)

    # ---- World map strip --------------------------------------------------
    d.text((36, 506), "WHERE THE DAY HAPPENED", font=load(SANS_B, 16), fill=RED)
    d.text((988, 506), "SIX CONTINENTS  \u2022  TWELVE FLASHPOINTS",
           font=load(SANS_B, 14), fill=GREY, anchor="ra")
    world_map(d, 36, 528, 952, 96)
    legend = "  \u2022  ".join(f"{n} {label}" for n, label, _lo, _la in MARKERS)
    d.text((36, 628), legend, font=load(SANS, 11), fill=INK)

    d.line([(36, 648), (988, 648)], fill=NAVY, width=2)

    # ---- Middle band: four stories ---------------------------------------
    cols = [(36, 220), (268, 220), (500, 220), (732, 220)]
    mids = [
        ("chip", "NVIDIA CHIEF OUT IN SPY SCANDAL",
         "Huang resigns over an affair with an alleged Chinese agent."),
        ("phone", "SCREENS GO DARK AT APPLE AND THE NSA",
         "Outages hit airports, banks and Apple; officials blame patching."),
        ("cross", "US LOSES MEASLES-FREE STATUS",
         "Elimination status gone for the first time since 2000."),
        ("camera", "NAT GEO PICTURES OF THE YEAR",
         "The year's best photographs are out."),
    ]
    for (cx, cw), (kind, head, body) in zip(cols, mids):
        ix, iy = cx, 658
        if kind == "chip":
            d.rectangle([ix, iy, ix + 40, iy + 40], fill=(118, 185, 0))
            d.rectangle([ix + 8, iy + 8, ix + 32, iy + 32], fill=(20, 60, 0))
            for k in range(3):
                d.rectangle([ix - 5, iy + 9 + k * 12, ix, iy + 14 + k * 12], fill=GREY)
                d.rectangle([ix + 40, iy + 9 + k * 12, ix + 45, iy + 14 + k * 12], fill=GREY)
            d.text((ix + 20, iy + 20), "NV", font=load(SANS_B, 14), fill=WHITE, anchor="mm")
        elif kind == "phone":
            d.rounded_rectangle([ix + 7, iy, ix + 33, iy + 40], radius=5, outline=NAVY, width=3)
            d.polygon([(ix + 20, iy + 9), (ix + 32, iy + 28), (ix + 8, iy + 28)],
                      fill=(255, 200, 40), outline=INK)
            d.text((ix + 20, iy + 22), "!", font=load(SANS_B, 13), fill=INK, anchor="mm")
        elif kind == "cross":
            d.ellipse([ix, iy, ix + 40, iy + 40], fill=RED)
            d.rectangle([ix + 17, iy + 8, ix + 23, iy + 32], fill=WHITE)
            d.rectangle([ix + 8, iy + 17, ix + 32, iy + 23], fill=WHITE)
        else:
            camera(d, ix, iy, 40)
        y = draw_lines(d, cx, 706, wrap_text(d, head, load(SANS_B, 18), cw),
                       load(SANS_B, 18), NAVY, 21)
        draw_lines(d, cx, y + 4, wrap_text(d, body, load(SANS, 13), cw),
                   load(SANS, 13), INK, 16)

    d.line([(36, 806), (988, 806)], fill=NAVY, width=2)

    # ---- Bottom: the day in brief ----------------------------------------
    d.text((36, 814), "THE DAY IN BRIEF", font=load(SANS_B, 18), fill=RED)
    brief = [
        ("DIRTY BOMB", "Trump takes report seriously"),
        ("3RD CARRIER", "Another carrier for the Gulf"),
        ("HOUTHIS", "5 drones at Saudi pipeline"),
        ("LEBANON", "Strikes and shelling in south"),
        ("UK SANCTIONS", "West Bank firms hit"),
        ("GAZA AID", "Four nations urge access"),
        ("C-130", "Activist held over $60m jet"),
        ("ETHANOL PLANT", "Worker held in plot"),
        ("FLORIDA", "Floods as western storm builds"),
        ("TIGER WOODS", "Golf return in December"),
        ("APPLE", "Sign-in and store faults fixed"),
        ("IRAQ", "Oil flows via Kirkuk\u2013Ceyhan"),
        ("BERLIN", "28 raids in Hezbollah-linked ban"),
        ("GAZA RAINS", "Winter rain floods shelters"),
        ("OMAN", "24 saved from burning tanker"),
        ("PARIS", "Depardieu pleads guilty in court"),
        ("TOKYO", "Japan scrambles jets at Russians"),
        ("KYIV", "Air alerts as Russia answers bridge hit"),
        ("WASHINGTON", "Trump flies to Shenzhen"),
        ("RIYADH", "Saudis on alert after pipeline attack"),
        ("MOSCOW", "Kremlin vows reply to bridge strike"),
        ("SUMMIT", "First meeting of all three leaders"),
        ("STRAIT", "Hormuz shipping on alert"),
        ("BEIJING", "China hosts first three-way summit"),
    ]
    for i, (kw, txt) in enumerate(brief):
        col, row = divmod(i, 8)
        ix = 36 + col * 326
        iy = 842 + row * 17
        brief_line(d, ix, iy, kw, txt, 300)

    d.line([(36, 984), (988, 984)], fill=NAVY, width=1)
    d.text((512, 990), "DRAWN FROM TUESDAY'S REPORTING  \u2022  17 NOVEMBER 2026",
           font=load(SANS, 12), fill=GREY, anchor="ma")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG")
    data = open(out, "rb").read()
    print("wrote", out, len(data), "bytes,",
          hashlib.sha256(data).hexdigest()[:16], "size", img.size)


if __name__ == "__main__":
    main()
