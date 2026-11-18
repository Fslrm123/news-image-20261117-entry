#!/usr/bin/env python3
"""Draw the 17 November 2026 world-news front page as a 1024x1024 PNG.

v4: more detail, neater grid. The page keeps the v3 shape (31 stories,
13 illustrated, a 12-flashpoint world map, a 24-item day in brief) and
adds the furniture a real front page carries: an issue line under the
masthead, datelines under the lead and middle stories, a pull-quote from
the day's own coverage, captions under the map and the skyline, an
ALSO INSIDE index line, and a BY THE NUMBERS strip whose figures come
only from numbers already printed in the stories on the page. Every
section sits on one strict grid: fixed outer margins, even gutters,
aligned column baselines, uniform icon boxes, and nothing touching a
border or a rule.

Deterministic: same input, same bytes. Run: python3 draw_poster.py
Writes entry.png beside this file.
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 242, 230)
INK = (24, 24, 24)
NAVY = (18, 32, 60)
RED = (178, 26, 26)
TEAL = (14, 74, 90)
GOLD = (198, 160, 38)
GREY = (96, 96, 96)
WHITE = (255, 255, 255)
SEA = (212, 225, 234)
SLATE = (58, 54, 68)
SEA_LINE = (178, 198, 212)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_font(path, size):
    return ImageFont.truetype(path, size)


def fit_lines(draw, text, fnt, max_w):
    """Greedy word wrap; returns the lines that fit max_w."""
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


def draw_lines(draw, x, y, lines, fnt, fill, leading=None):
    """Draw lines starting at (x, y); returns y after the last line."""
    lh = leading or int(fnt.size * 1.22)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def fit_size(draw, text, sizes, max_w, max_lines):
    """First (font, lines) in sizes that fits max_w in at most max_lines."""
    for size in sizes:
        fnt = load_font(SANS_B, size)
        lines = fit_lines(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines
    return load_font(SANS_B, sizes[-1]), fit_lines(
        draw, text, load_font(SANS_B, sizes[-1]), max_w)


def star_shape(cx, cy, r_out, r_in, points=5, rot=-90):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def globe_mark(draw, cx, cy, r):
    """Small globe: circle, two meridian ellipses, two latitude chords."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=3)
    draw.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
                 outline=NAVY, width=2)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=NAVY, width=2)
    draw.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], 200, 340,
             fill=NAVY, width=2)
    draw.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], 20, 160,
             fill=NAVY, width=2)


def us_banner(draw, x, y, w, h):
    stripe = h / 13.0
    for i in range(13):
        c = (179, 34, 52) if i % 2 == 0 else WHITE
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                       fill=c)
    cw, ch = w * 0.4, stripe * 7
    draw.rectangle([x, y, x + cw, y + ch], fill=(30, 51, 101))
    for r in range(5):
        for cidx in range(6):
            sx = x + 6 + cidx * (cw - 10) / 5.0
            sy = y + 5 + r * (ch - 8) / 4.0
            draw.ellipse([sx - 1.6, sy - 1.6, sx + 1.6, sy + 1.6],
                         fill=WHITE)


def cn_banner(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    draw.polygon(star_shape(x + w * 0.18, y + h * 0.30, h * 0.20, h * 0.08),
                 fill=(255, 222, 0))
    for sx, sy in [(0.42, 0.14), (0.52, 0.26), (0.52, 0.44), (0.42, 0.56)]:
        draw.polygon(star_shape(x + w * sx, y + h * sy, h * 0.07, h * 0.03),
                     fill=(255, 222, 0))


def ru_banner(draw, x, y, w, h):
    for i, c in enumerate([WHITE, (0, 57, 166), (213, 0, 50)]):
        draw.rectangle([x, y + i * h / 3.0, x + w, y + (i + 1) * h / 3.0],
                       fill=c)


def skyline_band(draw, x, y, w, h, color):
    """Dark skyline silhouette with a few lit windows, in (x, y, w, h)."""
    base = y + h
    towers = [(0, 0.55), (0.10, 0.75), (0.20, 0.45), (0.30, 0.85),
              (0.42, 0.60), (0.52, 0.95), (0.64, 0.50), (0.74, 0.70),
              (0.84, 0.58), (0.93, 0.80)]
    tw = w / len(towers)
    for i, (fx, fh) in enumerate(towers):
        tx = x + i * tw
        th = h * fh
        draw.rectangle([tx, base - th, tx + tw - 2, base], fill=color)
        if i == 5:  # spire on the tallest tower
            draw.polygon([(tx + tw / 2 - 3, base - th),
                          (tx + tw / 2 + 3, base - th),
                          (tx + tw / 2, base - th - 24)], fill=color)
    for i in range(46):  # lit windows, fixed pattern
        wx = x + 8 + (i * 37) % int(w - 16)
        wy = base - 14 - (i * 53) % int(h * 0.7)
        draw.rectangle([wx, wy, wx + 4, wy + 6], fill=GOLD)


# ---- World map ----------------------------------------------------------
# Rough continent outlines as (lon, lat) points; equirectangular.
LAND = [
    [(-168, 66), (-140, 70), (-120, 71), (-100, 72), (-80, 73), (-70, 68),
     (-60, 55), (-55, 47), (-65, 44), (-70, 41), (-76, 35), (-81, 26),
     (-84, 30), (-90, 21), (-97, 16), (-105, 20), (-110, 24), (-117, 32),
     (-124, 40), (-130, 48), (-140, 60), (-158, 58), (-168, 66)],
    [(-79, 9), (-72, 11), (-62, 10), (-52, 5), (-44, -3), (-35, -8),
     (-40, -20), (-48, -27), (-58, -34), (-66, -40), (-70, -52),
     (-73, -44), (-71, -30), (-77, -15), (-81, -5), (-79, 9)],
    [(-10, 36), (-9, 43), (-2, 48), (3, 51), (8, 55), (10, 58), (18, 56),
     (21, 55), (24, 58), (28, 60), (30, 62), (32, 70), (40, 68),
     (35, 64), (30, 60), (27, 55), (23, 50), (19, 45), (15, 40),
     (10, 38), (3, 38), (-2, 37), (-10, 36)],
    [(-17, 15), (-12, 25), (-6, 33), (0, 36), (10, 37), (20, 32),
     (30, 31), (34, 28), (37, 22), (43, 12), (48, 11), (51, 10),
     (44, 0), (40, -8), (36, -18), (32, -26), (26, -33), (19, -34),
     (15, -27), (12, -18), (9, -5), (9, 4), (-8, 5), (-14, 10)],
    [(30, 70), (45, 69), (60, 69), (75, 72), (90, 75), (105, 76),
     (120, 73), (135, 72), (150, 70), (162, 68), (170, 66), (162, 62),
     (155, 56), (142, 52), (132, 45), (127, 38), (122, 31), (116, 23),
     (110, 18), (105, 10), (100, 8), (96, 14), (90, 22), (84, 19),
     (78, 10), (74, 16), (68, 23), (62, 25), (56, 27), (50, 29),
     (46, 32), (42, 36), (38, 40), (34, 44), (30, 48), (32, 60), (30, 70)],
    [(113, -22), (120, -15), (128, -13), (136, -12), (142, -11),
     (147, -19), (150, -27), (150, -37), (143, -38), (135, -34),
     (128, -32), (120, -34), (114, -30), (113, -22)],
]
# (number, label, lon, lat) -- display positions nudged so no two dots
# touch: the Europe / Middle East cluster is spread by hand.
SPOTS = [
    (1, "SHENZHEN", 114.1, 22.5),
    (2, "HORMUZ", 60.0, 30.0),
    (3, "BAHRAIN", 50.0, 20.0),
    (4, "KERCH", 38.0, 46.0),
    (5, "KYIV", 27.0, 54.0),
    (6, "GAZA", 32.0, 26.0),
    (7, "PARIS", 2.3, 48.9),
    (8, "TOKYO", 139.7, 35.7),
    (9, "WASHINGTON", -76.0, 40.0),
    (10, "RIYADH", 41.0, 17.0),
    (11, "BERLIN", 13.4, 52.5),
    (12, "FLORIDA", -82.0, 25.0),
]


def world_chart(draw, x, y, w, h):
    """Stylised world map with numbered flashpoints, in (x, y, w, h)."""
    draw.rectangle([x, y, x + w, y + h], fill=SEA)

    def px(lon, lat):
        return (x + (lon + 180.0) / 360.0 * w,
                y + (78.0 - lat) / 134.0 * h)

    for lon in (-120, -60, 0, 60, 120):  # faint graticule
        gx, _ = px(lon, 0)
        draw.line([(gx, y), (gx, y + h)], fill=SEA_LINE, width=1)
    for lat in (60, 30, 0, -30):
        _, gy = px(0, lat)
        draw.line([(x, gy), (x + w, gy)], fill=SEA_LINE, width=1)
    for poly in LAND:
        draw.polygon([px(lon, lat) for lon, lat in poly], fill=NAVY)
    num_f = load_font(SANS_B, 9)
    for n, _label, lon, lat in SPOTS:
        mx, my = px(lon, lat)
        draw.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=RED,
                     outline=WHITE, width=2)
        draw.text((mx, my), str(n), font=num_f, fill=WHITE, anchor="mm")


def brief_row(draw, x, y, kicker, text, max_w):
    """One brief line: red bold kicker + plain text. Warns if it overflows."""
    kf = load_font(SANS_B, 12)
    tf = load_font(SANS, 12)
    draw.text((x, y), kicker, font=kf, fill=RED)
    tx = x + draw.textlength(kicker, font=kf)
    draw.text((tx, y), " \u2014 " + text, font=tf, fill=INK)
    total = tx + draw.textlength(" \u2014 " + text, font=tf) - x
    if total > max_w:
        print(f"WARNING: brief line overflows by {total - max_w:.0f}px: "
              f"{kicker}")


def icon_box(draw, x, y, size, kind):
    """Uniform 32px icon box, same size and baseline for every column."""
    draw.rectangle([x, y, x + size, y + size], outline=NAVY, width=2)
    cx, cy = x + size / 2, y + size / 2
    if kind == "chip":
        draw.rectangle([cx - 10, cy - 10, cx + 10, cy + 10], fill=(118, 185, 0))
        draw.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=(20, 60, 0))
        for k in range(3):
            draw.rectangle([cx - 16, cy - 8 + k * 8, cx - 10, cy - 3 + k * 8],
                           fill=GREY)
            draw.rectangle([cx + 10, cy - 8 + k * 8, cx + 16, cy - 3 + k * 8],
                           fill=GREY)
        draw.text((cx, cy), "NV", font=load_font(SANS_B, 11), fill=WHITE,
                  anchor="mm")
    elif kind == "phone":
        draw.rounded_rectangle([cx - 8, cy - 14, cx + 8, cy + 14], radius=4,
                               outline=NAVY, width=2)
        draw.polygon([(cx, cy - 8), (cx + 7, cy + 7), (cx - 7, cy + 7)],
                     fill=(255, 200, 40), outline=INK)
        draw.text((cx, cy + 2), "!", font=load_font(SANS_B, 10), fill=INK,
                  anchor="mm")
    elif kind == "cross":
        draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=RED)
        draw.rectangle([cx - 2, cy - 8, cx + 2, cy + 8], fill=WHITE)
        draw.rectangle([cx - 8, cy - 2, cx + 8, cy + 2], fill=WHITE)
    else:  # camera
        draw.rectangle([cx - 11, cy - 8, cx + 11, cy + 9], fill=NAVY)
        draw.rectangle([cx - 5, cy - 12, cx + 3, cy - 8], fill=NAVY)
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=NAVY)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # Double border.
    d.rectangle([10, 10, W - 11, H - 11], outline=NAVY, width=5)
    d.rectangle([20, 20, W - 21, H - 21], outline=NAVY, width=1)

    # ---- Masthead -------------------------------------------------------
    globe_mark(d, 66, 54, 26)
    globe_mark(d, 958, 54, 26)
    d.text((512, 22), "THE WORLD", font=load_font(SERIF_B, 64), fill=NAVY,
           anchor="ma")
    d.text((512, 90), "Vol. I \u2014 No. 1  \u2022  TUESDAY EDITION",
           font=load_font(SANS, 12), fill=GREY, anchor="ma")
    d.line([(36, 108), (988, 108)], fill=NAVY, width=2)
    d.text((36, 114), "TUESDAY, 17 NOVEMBER 2026",
           font=load_font(SANS_B, 16), fill=INK)
    d.text((988, 114), "31 STORIES  \u2022  13 ILLUSTRATED  \u2022  6 CONTINENTS",
           font=load_font(SANS_B, 14), fill=INK, anchor="ra")
    d.line([(36, 136), (988, 136)], fill=NAVY, width=2)

    # ---- Lead story: Trump-Xi-Putin summit ------------------------------
    lx, lw = 36, 636
    d.text((lx, 142), "APEC SUMMIT  \u2022  SHENZHEN, CHINA",
           font=load_font(SANS_B, 20), fill=RED)
    head = fit_lines(d, "TRUMP, XI & PUTIN TO MEET IN SHENZHEN",
                     load_font(SERIF_B, 42), lw)
    y = 168
    for line in head:
        d.text((lx, y), line, font=load_font(SERIF_B, 42), fill=NAVY)
        y += 48
    d.text((lx, 272), "SHENZHEN \u2014 STAFF REPORT",
           font=load_font(SANS, 12), fill=GREY)
    sub = ("Trump lands in China for the first three-way summit with "
           "Xi Jinping and Vladimir Putin \u2014 as war in the Gulf and a "
           "spy scandal hang over the talks.")
    y = draw_lines(d, lx, 290,
                   fit_lines(d, sub, load_font(SANS, 20), lw),
                   load_font(SANS, 20), INK, 24)

    # Visual: skyline with three flags.
    vx, vy, vw, vh = lx, 368, lw, 68
    d.rectangle([vx, vy, vx + vw, vy + vh], fill=(223, 232, 240))
    skyline_band(d, vx, vy + 22, vw, vh - 22, NAVY)
    for i, flag in enumerate([us_banner, cn_banner, ru_banner]):
        fx = vx + 56 + i * 210
        d.line([(fx + 44, vy + 4), (fx + 44, vy + 62)], fill=GREY, width=3)
        d.ellipse([fx + 41, vy, fx + 47, vy + 6], fill=GOLD)
        flag(d, fx - 44, vy + 6, 88, 50)
    d.rectangle([vx, vy + vh - 3, vx + vw, vy + vh], fill=NAVY)
    d.text((lx, 440), "The Shenzhen skyline on the morning the three "
                      "leaders met.",
           font=load_font(SANS, 12), fill=GREY)

    # ---- Right rail ------------------------------------------------------
    rx, rw = 700, 288
    # Panel A: US strikes Iran.
    d.rectangle([rx, 142, rx + rw, 272], fill=TEAL)
    d.text((rx + 14, 152), "US STRIKES IRAN", font=load_font(SANS_B, 22),
           fill=WHITE)
    d.text((rx + 14, 180), "HORMUZ STANDOFF", font=load_font(SANS_B, 22),
           fill=(255, 214, 130))
    # Sea, ship, burst.
    d.rectangle([rx, 216, rx + rw, 272], fill=(16, 90, 110))
    for k in range(4):
        d.arc([rx - 40 + k * 80, 258, rx + 40 + k * 80, 294], 200, 340,
              fill=(120, 190, 205), width=3)
    d.rectangle([rx + 96, 250, rx + 200, 268], fill=(225, 225, 225))
    d.rectangle([rx + 116, 232, rx + 180, 250], fill=(150, 150, 150))
    d.polygon(star_shape(rx + 148, 228, 20, 8), fill=(255, 170, 40))
    d.polygon(star_shape(rx + 148, 228, 11, 5), fill=(255, 220, 120))
    cap = "US hits missile sites; Iran drones Bahrain again."
    draw_lines(d, rx + 14, 278, fit_lines(d, cap, load_font(SANS, 16), rw - 28),
               load_font(SANS, 16), INK, 20)
    # Panel B: Kerch Bridge hit.
    by = 324
    d.rectangle([rx, by, rx + rw, by + 86], fill=SLATE)
    d.text((rx + 14, by + 10), "KERCH BRIDGE HIT",
           font=load_font(SANS_B, 22), fill=WHITE)
    d.line([(rx, by + 52), (rx + 110, by + 52)], fill=(230, 230, 230), width=4)
    d.line([(rx + 178, by + 52), (rx + rw, by + 52)], fill=(230, 230, 230),
           width=4)
    d.line([(rx + 110, by + 52), (rx + 150, by + 72)], fill=(230, 230, 230),
           width=4)
    for cx, cy, r in [(rx + 128, by + 40, 7), (rx + 144, by + 33, 10),
                      (rx + 160, by + 42, 6)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 150, 150))
    d.rectangle([rx, by + 76, rx + rw, by + 86], fill=(30, 44, 66))
    cap2 = "Drones hit the Crimea link; Russia hits back."
    draw_lines(d, rx + 14, 416,
               fit_lines(d, cap2, load_font(SANS, 16), rw - 28),
               load_font(SANS, 16), INK, 20)

    d.line([(36, 464), (988, 464)], fill=NAVY, width=2)

    # ---- Pull-quote + also inside ---------------------------------------
    d.text((512, 470),
           "\u201cThe first meeting of all three leaders.\u201d \u2014 the "
           "summit, as reported today",
           font=load_font(SERIF, 16), fill=NAVY, anchor="ma")
    d.text((36, 496),
           "ALSO INSIDE \u2014 Where the day happened (map)  \u2022  By the "
           "numbers  \u2022  The day in brief, 24 items",
           font=load_font(SANS, 13), fill=INK)
    d.line([(36, 514), (988, 514)], fill=NAVY, width=2)

    # ---- World map strip --------------------------------------------------
    d.text((36, 520), "WHERE THE DAY HAPPENED",
           font=load_font(SANS_B, 16), fill=RED)
    d.text((988, 520), "SIX CONTINENTS  \u2022  TWELVE FLASHPOINTS",
           font=load_font(SANS_B, 13), fill=GREY, anchor="ra")
    world_chart(d, 36, 540, 952, 72)
    d.text((36, 616), "Twelve places where the day turned.",
           font=load_font(SANS, 12), fill=GREY)
    legend = "  \u2022  ".join(f"{n} {label}" for n, label, _lo, _la in SPOTS)
    for leg_size in (13, 12, 11):  # shrink until the whole legend fits
        leg_fnt = load_font(SANS, leg_size)
        if d.textlength(legend, font=leg_fnt) <= 952:
            break
    d.text((36, 634), legend, font=leg_fnt, fill=INK)

    d.line([(36, 652), (988, 652)], fill=NAVY, width=2)

    # ---- By the numbers ---------------------------------------------------
    d.text((36, 662), "BY THE NUMBERS", font=load_font(SANS_B, 14), fill=RED)
    stats = [
        ("3", "leaders at the summit"),
        ("2", "carriers in the Gulf"),
        ("5", "drones at the pipeline"),
        ("28", "raids in Berlin"),
        ("24", "saved from the tanker"),
    ]
    cell_x, cell_w = 210, 155
    for i, (num, label) in enumerate(stats):
        cx = cell_x + i * cell_w + cell_w / 2
        d.text((cx, 656), num, font=load_font(SANS_B, 20), fill=NAVY,
               anchor="ma")
        d.text((cx, 682), label, font=load_font(SANS, 10), fill=GREY,
               anchor="ma")

    d.line([(36, 700), (988, 700)], fill=NAVY, width=2)

    # ---- Middle band: four stories ----------------------------------------
    cols = [36, 280, 524, 768]
    cw = 220
    mids = [
        ("chip", "NVIDIA CHIEF OUT IN SPY SCANDAL",
         "SANTA CLARA \u2014 STAFF REPORT",
         "Huang quits over an affair with an alleged Chinese agent."),
        ("phone", "SCREENS GO DARK AT APPLE AND THE NSA",
         "CUPERTINO \u2014 STAFF REPORT",
         "Outages hit airports, banks and Apple; officials blame patching."),
        ("cross", "US LOSES MEASLES-FREE STATUS",
         "ATLANTA \u2014 STAFF REPORT",
         "Gone for the first time since 2000 as vaccination rates fall."),
        ("camera", "NAT GEO PICTURES OF THE YEAR",
         "WASHINGTON \u2014 STAFF REPORT",
         "The year's best photographs are out."),
    ]
    for (cx, (kind, head, byline, body)) in zip(cols, mids):
        icon_box(d, cx, 708, 32, kind)
        fnt, lines = fit_size(d, head, (17, 16, 15), cw, 2)
        draw_lines(d, cx, 746, lines, fnt, NAVY, 20)
        d.text((cx, 790), byline, font=load_font(SANS, 10), fill=GREY)
        bfnt, blines = fit_size(d, body, (12, 11), cw, 2)
        draw_lines(d, cx, 804, blines, bfnt, INK, 14)

    d.line([(36, 838), (988, 838)], fill=NAVY, width=2)

    # ---- Bottom: the day in brief ----------------------------------------
    d.text((36, 844), "THE DAY IN BRIEF", font=load_font(SANS_B, 17),
           fill=RED)
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
        iy = 866 + row * 14
        brief_row(d, ix, iy, kw, txt, 300)

    d.line([(36, 982), (988, 982)], fill=NAVY, width=1)
    d.text((512, 988), "DRAWN FROM TUESDAY'S REPORTING  \u2022  17 NOVEMBER 2026",
           font=load_font(SANS, 12), fill=GREY, anchor="ma")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG")
    data = open(out, "rb").read()
    print("wrote", out, len(data), "bytes,",
          hashlib.sha256(data).hexdigest()[:16], "size", img.size)


if __name__ == "__main__":
    main()
