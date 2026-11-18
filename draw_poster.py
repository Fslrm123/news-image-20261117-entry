#!/usr/bin/env python3
"""Draw the 17 November 2026 world-news front page as a 1024x1024 PNG.

The poster is a newspaper front page: masthead, lead story on the
Trump-Xi-Putin summit in Shenzhen, side panels on the US strikes on Iran
and the Kerch Bridge hit, a middle row on NVIDIA, the Apple/NSA outages
and the lost measles status, plus an "Also today" strip.

Deterministic: same input, same bytes. Run: python3 draw_poster.py
Writes entry.png beside this file.
"""
import math
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
CREAM = (250, 247, 238)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
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


def text_block(draw, x, y, lines, fnt, fill, leading=None):
    """Draw lines starting at (x, y); returns y after the last line."""
    lh = leading or int(fnt.size * 1.22)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def star_points(cx, cy, r_out, r_in, points=5, rot=-90):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_us_flag(draw, x, y, w, h):
    stripe = h / 13.0
    for i in range(13):
        c = (179, 34, 52) if i % 2 == 0 else WHITE
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe], fill=c)
    cw, ch = w * 0.4, stripe * 7
    draw.rectangle([x, y, x + cw, y + ch], fill=(30, 51, 101))
    for r in range(5):
        for cidx in range(6):
            sx = x + 6 + cidx * (cw - 10) / 5.0
            sy = y + 5 + r * (ch - 8) / 4.0
            draw.ellipse([sx - 1.6, sy - 1.6, sx + 1.6, sy + 1.6], fill=WHITE)


def draw_cn_flag(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    draw.polygon(star_points(x + w * 0.18, y + h * 0.30, h * 0.20, h * 0.08), fill=(255, 222, 0))
    for sx, sy in [(0.42, 0.14), (0.52, 0.26), (0.52, 0.44), (0.42, 0.56)]:
        draw.polygon(star_points(x + w * sx, y + h * sy, h * 0.07, h * 0.03), fill=(255, 222, 0))


def draw_ru_flag(draw, x, y, w, h):
    for i, c in enumerate([WHITE, (0, 57, 166), (213, 0, 50)]):
        draw.rectangle([x, y + i * h / 3.0, x + w, y + (i + 1) * h / 3.0], fill=c)


def draw_skyline(draw, x, y, w, h, color):
    """Dark skyline silhouette with a few lit windows, inside (x, y, w, h)."""
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
            draw.polygon([(tx + tw / 2 - 3, base - th), (tx + tw / 2 + 3, base - th),
                          (tx + tw / 2, base - th - 26)], fill=color)
    for i in range(46):  # lit windows, fixed pattern
        wx = x + 8 + (i * 37) % int(w - 16)
        wy = base - 14 - (i * 53) % int(h * 0.7)
        draw.rectangle([wx, wy, wx + 4, wy + 6], fill=GOLD)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # Double border.
    d.rectangle([10, 10, W - 11, H - 11], outline=NAVY, width=5)
    d.rectangle([20, 20, W - 21, H - 21], outline=NAVY, width=1)

    # ---- Masthead -------------------------------------------------------
    d.text((512, 30), "THE WORLD", font=font(SERIF_B, 78), fill=NAVY, anchor="ma")
    d.line([(36, 118), (988, 118)], fill=NAVY, width=2)
    d.text((36, 126), "TUESDAY, 17 NOVEMBER 2026", font=font(SANS_B, 19), fill=INK)
    d.text((988, 126), "ONE DAY  \u2022  ONE IMAGE", font=font(SANS_B, 19), fill=INK, anchor="ra")
    d.line([(36, 156), (988, 156)], fill=NAVY, width=2)

    # ---- Lead story: Trump-Xi-Putin summit ------------------------------
    lx, lw = 36, 636
    d.text((lx, 172), "APEC SUMMIT  \u2022  SHENZHEN, CHINA", font=font(SANS_B, 20), fill=RED)
    head = wrap(d, "TRUMP, XI & PUTIN TO MEET IN SHENZHEN", font(SERIF_B, 46), lw)
    y = 200
    for line in head:
        d.text((lx, y), line, font=font(SERIF_B, 46), fill=NAVY)
        y += 56
    sub = ("Trump lands in China for the first three-way summit with "
           "Xi Jinping and Vladimir Putin \u2014 as war in the Gulf and a "
           "spy scandal hang over the talks.")
    y = text_block(d, lx, 332, wrap(d, sub, font(SANS, 22), lw), font(SANS, 22), INK, 30)

    # Visual: skyline with three flags.
    vx, vy, vw, vh = lx, 428, lw, 128
    d.rectangle([vx, vy, vx + vw, vy + vh], fill=(223, 232, 240))
    draw_skyline(d, vx, vy + 34, vw, vh - 34, NAVY)
    for i, flag in enumerate([draw_us_flag, draw_cn_flag, draw_ru_flag]):
        fx = vx + 56 + i * 210
        d.line([(fx + 44, vy + 6), (fx + 44, vy + 96)], fill=GREY, width=3)
        d.ellipse([fx + 41, vy + 2, fx + 47, vy + 8], fill=GOLD)
        flag(d, fx - 44, vy + 8, 88, 56)
    d.rectangle([vx, vy + vh - 4, vx + vw, vy + vh], fill=NAVY)

    # ---- Right rail ------------------------------------------------------
    rx, rw = 700, 288
    # Panel A: US strikes Iran.
    d.rectangle([rx, 172, rx + rw, 330], fill=TEAL)
    d.text((rx + 14, 184), "US STRIKES IRAN", font=font(SANS_B, 22), fill=WHITE)
    d.text((rx + 14, 212), "HORMUZ STANDOFF", font=font(SANS_B, 22), fill=(255, 214, 130))
    # Sea, ship, burst.
    d.rectangle([rx, 252, rx + rw, 330], fill=(16, 90, 110))
    for k in range(4):
        d.arc([rx - 40 + k * 80, 300, rx + 40 + k * 80, 336], 200, 340, fill=(120, 190, 205), width=3)
    d.rectangle([rx + 96, 292, rx + 200, 312], fill=(225, 225, 225))  # hull
    d.rectangle([rx + 116, 272, rx + 180, 292], fill=(150, 150, 150))  # containers
    d.polygon(star_points(rx + 148, 268, 22, 9), fill=(255, 170, 40))
    d.polygon(star_points(rx + 148, 268, 12, 5), fill=(255, 220, 120))
    cap = ("US hits missile sites; Iran drones a Bahrain base "
           "a third time.")
    text_block(d, rx + 14, 338, wrap(d, cap, font(SANS, 17), rw - 28),
               font(SANS, 17), INK, 22)
    # Panel B: Kerch Bridge hit.
    by = 414
    d.rectangle([rx, by, rx + rw, by + 104], fill=(64, 58, 74))
    d.text((rx + 14, by + 10), "KERCH BRIDGE HIT", font=font(SANS_B, 22), fill=WHITE)
    d.line([(rx, by + 62), (rx + 110, by + 62)], fill=(230, 230, 230), width=4)
    d.line([(rx + 178, by + 62), (rx + rw, by + 62)], fill=(230, 230, 230), width=4)
    d.line([(rx + 110, by + 62), (rx + 150, by + 84)], fill=(230, 230, 230), width=4)
    for cx, cy, r in [(rx + 128, by + 48, 8), (rx + 144, by + 40, 11), (rx + 160, by + 50, 7)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 150, 150))
    d.rectangle([rx, by + 92, rx + rw, by + 104], fill=(30, 44, 66))
    cap2 = ("Drones hit the Crimea link; Russia hits Kyiv back.")
    text_block(d, rx + 14, by + 112, wrap(d, cap2, font(SANS, 17), rw - 28),
               font(SANS, 17), INK, 22)

    d.line([(36, 596), (988, 596)], fill=NAVY, width=2)

    # ---- Middle band: three stories --------------------------------------
    cols = [(36, 300), (362, 300), (688, 300)]
    mids = [
        ("chip",
         "NVIDIA CHIEF OUT IN SPY SCANDAL",
         "Huang resigns over an affair with an alleged Chinese agent; "
         "the board says no return."),
        ("phone",
         "SCREENS GO DARK AT APPLE AND THE NSA",
         "A week of outages hits airports, banks and Microsoft; officials "
         "insist it is patching, not hacking."),
        ("cross",
         "US LOSES MEASLES-FREE STATUS",
         "Elimination status gone for the first time since 2000 as "
         "vaccination rates fall."),
    ]
    for (cx, cw), (kind, head, body) in zip(cols, mids):
        ix, iy = cx, 612
        if kind == "chip":
            d.rectangle([ix, iy, ix + 64, iy + 64], fill=(118, 185, 0))
            d.rectangle([ix + 12, iy + 12, ix + 52, iy + 52], fill=(20, 60, 0))
            for k in range(3):
                d.rectangle([ix - 8, iy + 14 + k * 18, ix, iy + 22 + k * 18], fill=GREY)
                d.rectangle([ix + 64, iy + 14 + k * 18, ix + 72, iy + 22 + k * 18], fill=GREY)
            d.text((ix + 32, iy + 32), "NV", font=font(SANS_B, 22), fill=WHITE, anchor="mm")
        elif kind == "phone":
            d.rounded_rectangle([ix + 10, iy, ix + 54, iy + 64], radius=8, outline=NAVY, width=3)
            d.polygon([(ix + 32, iy + 14), (ix + 50, iy + 44), (ix + 14, iy + 44)],
                      fill=(255, 200, 40), outline=INK)
            d.text((ix + 32, iy + 34), "!", font=font(SANS_B, 20), fill=INK, anchor="mm")
        else:
            d.ellipse([ix, iy, ix + 64, iy + 64], fill=RED)
            d.rectangle([ix + 28, iy + 12, ix + 36, iy + 52], fill=WHITE)
            d.rectangle([ix + 12, iy + 28, ix + 52, iy + 36], fill=WHITE)
        y = text_block(d, cx, 684, wrap(d, head, font(SANS_B, 22), cw),
                       font(SANS_B, 22), NAVY, 27)
        text_block(d, cx, y + 6, wrap(d, body, font(SANS, 17), cw),
                   font(SANS, 17), INK, 20)

    d.line([(36, 808), (988, 808)], fill=NAVY, width=2)

    # ---- Bottom strip: also today -----------------------------------------
    d.text((36, 822), "ALSO TODAY", font=font(SANS_B, 20), fill=RED)
    items = [
        ("GAZA", "Four nations urge Israel to open aid crossings."),
        ("PARIS", "Depardieu pleads guilty to sexual assault."),
        ("TOKYO", "Japan scrambles jets as Russian planes enter its airspace."),
        ("SPORT", "Tiger Woods returns in December; Waymo pulls its robotaxis."),
    ]
    for i, (kw, txt) in enumerate(items):
        ix = 36 + i * 242
        iw = 226
        d.text((ix, 852), kw, font=font(SANS_B, 16), fill=RED)
        text_block(d, ix, 876, wrap(d, txt, font(SANS, 15), iw),
                   font(SANS, 15), INK, 19)

    d.line([(36, 962), (988, 962)], fill=NAVY, width=1)
    d.text((512, 970), "DRAWN FROM TUESDAY'S REPORTING  \u2022  17 NOVEMBER 2026",
           font=font(SANS, 15), fill=GREY, anchor="ma")

    import hashlib
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG")
    data = open(out, "rb").read()
    print("wrote", out, len(data), "bytes,",
          hashlib.sha256(data).hexdigest()[:16], "size", img.size)


if __name__ == "__main__":
    main()
