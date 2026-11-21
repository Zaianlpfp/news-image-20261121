#!/usr/bin/env python3
"""Build THE WORLD TODAY - Saturday, 21 November 2026 (1024x1024).

Composes the newspaper from three AI-illustrated lead photos
(work/media-generation-lead-*.webp) plus text drawn with PIL.
Deterministic: same inputs -> same bytes (fixed quality, no metadata).
Run: python3 build.py  -> writes entry.png (JPEG bytes in a .png name,
allowed by the competition rules: file type is told by its first bytes).
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")
W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (178, 34, 34)
GREY = (90, 86, 78)
RULE = (60, 58, 52)
OCEAN = (191, 217, 232)
LAND = (232, 220, 192)
LAND_EDGE = (150, 138, 105)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_I = "/usr/share/fonts/truetype/noto/NotoSans-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    lh = leading or int(fnt.size * 1.22)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def fit_headline(draw, x, y, text, max_w, size=19, max_lines=2):
    fnt = font(SERIF_B, size)
    lines = wrap(draw, text, fnt, max_w)
    while len(lines) > max_lines and size > 14:
        size -= 1
        fnt = font(SERIF_B, size)
        lines = wrap(draw, text, fnt, max_w)
    lh = int(size * 1.18)
    for ln in lines[:max_lines]:
        draw.text((x, y), ln, font=fnt, fill=INK)
        y += lh
    return y


# ---------------- world map (rough equirectangular polygons, lon/lat) -------
CONTINENTS = {
    "N America": [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-65, 60),
                  (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
                  (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-145, 60), (-165, 60)],
    "S America": [(-80, 10), (-77, 4), (-80, -4), (-81, -6), (-77, -12), (-70, -18),
                  (-70, -30), (-72, -40), (-70, -52), (-66, -55), (-60, -45), (-55, -35),
                  (-48, -28), (-40, -20), (-35, -8), (-45, -3), (-52, 4), (-60, 8), (-70, 11)],
    "Africa": [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
               (43, 12), (51, 11), (48, 2), (40, -10), (35, -20), (32, -29), (25, -34),
               (18, -35), (12, -18), (9, 4), (-8, 5)],
    "Europe": [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
               (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (40, 68), (45, 68),
               (40, 60), (35, 55), (30, 50), (28, 45), (23, 40), (19, 42), (12, 44),
               (8, 44), (3, 42), (-2, 37), (-9, 37)],
    "Asia": [(40, 68), (60, 70), (80, 73), (100, 76), (120, 73), (140, 72), (160, 70),
             (178, 66), (170, 60), (162, 56), (158, 52), (142, 50), (140, 40), (130, 35),
             (122, 30), (120, 22), (110, 20), (105, 10), (100, 8), (95, 15), (90, 22),
             (85, 20), (80, 15), (77, 8), (72, 20), (66, 25), (60, 25), (56, 26),
             (50, 29), (48, 30), (43, 35), (40, 40), (35, 45), (40, 55)],
    "Australia": [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (136, -35),
                  (140, -38), (146, -39), (150, -37), (153, -27), (146, -19), (142, -11),
                  (136, -12), (132, -11), (126, -14), (122, -17), (118, -20)],
}
# (lon, lat, label, dx, dy) label offsets in px
PINS = [
    (19, 52, "POLAND", 6, -13),
    (-76, -10, "PERU", 6, -3),
    (-74, 41, "NEW YORK", 6, -13),
    (79, 21, "INDIA", -6, 12),
    (34, 31, "GAZA", 6, -13),
    (47, 25, "RIYADH", 6, -13),
    (10, 56, "DENMARK", -62, -13),
    (33, 48, "UKRAINE", 6, 11),
    (2, 47, "FRANCE", -52, 11),
]


def draw_map(draw, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=OCEAN, outline=RULE, width=1)
    lon_min, lon_max, lat_max, lat_min = -180, 180, 75, -55

    def px(lon, lat):
        return (x0 + (lon - lon_min) / (lon_max - lon_min) * w,
                y0 + (lat_max - lat) / (lat_max - lat_min) * h)

    for poly in CONTINENTS.values():
        pts = [px(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    fnt = font(SANS_B, 10)
    for lon, lat, label, dx, dy in PINS:
        cx, cy = px(lon, lat)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED, outline=(255, 255, 255))
        draw.text((cx + dx, cy + dy), label, font=fnt, fill=INK,
                  stroke_width=2, stroke_fill=(247, 243, 232))


LEADS = [
    ("media-generation-lead-poland-missile-0-8f7a8f4d-c83a-434a-b92e-2692d2b2e11e.webp",
     "RUSSIAN MISSILES HIT POLAND",
     "Two Russian cruise missiles and a jet-powered drone came down in "
     "south-east Poland. PM Donald Tusk called it a deliberate "
     "provocation, timed to allied war games nearby. NATO jets scrambled; "
     "no one was hurt.",
     "Debris in a field near Nowy Lipowiec. (Illustration)"),
    ("media-generation-lead-peru-quake-0-ec4e4118-fe65-4bd0-bc5c-d0c3066ce421.webp",
     "6.8 QUAKE SHAKES PERU",
     "A magnitude 6.8 earthquake struck the Andean region of Junin in "
     "central Peru, with tremors felt in Lima, 320 km away. Rescue teams "
     "searched damaged adobe towns as aftershocks rattled the region.",
     "Rescue workers in a damaged Andean town. (Illustration)"),
    ("media-generation-lead-markets-plunge-0-425a392d-7d6c-44c7-8deb-b2e4927ded10.webp",
     "WALL ST SLUMPS INTO CORRECTION",
     "US stocks fell about 3.7% as an AI-chip sell-off dragged the S&P 500 "
     "and the Dow into correction territory. Traders blamed stretched AI "
     "valuations and new curbs on chip exports to China.",
     "Traders watch red boards in New York. (Illustration)"),
]

NUMBERED = [
    ("Trump urges Nvidia to bring back Huang",
     "The US president called on Nvidia to reinstate 'brilliant' former CEO Jensen Huang and urged him to 'make a big apology'."),
    ("COP31 climate deal stalls",
     "Negotiators in Turkiye struggled to agree a climate plan as the UN summit entered its final stage."),
    ("Gen Z protests sweep Europe",
     "Thousands rallied in 25 countries over living costs, military spending and climate."),
    ("Denmark expels Russian diplomat",
     "Copenhagen accused Moscow of plotting to kill a US-Ukrainian rapper; Russia denied the claim."),
    ("Houthi missiles downed over Riyadh",
     "The Saudi-led coalition intercepted three missiles; Iran's IRGC said it shot down a US drone."),
    ("Rahul completes the SENA set",
     "KL Rahul became the first Indian opener with Test hundreds in South Africa, England, New Zealand and Australia."),
    ("Rikers Island to close by 2032",
     "New York Mayor Mamdani unveiled a plan to shut the jail complex, five years past the legal deadline."),
    ("Record foreign cash into India",
     "A record \u20b91.22 lakh crore flowed into Indian shares in November, depository data showed."),
    ("Nepal PM heads to Delhi",
     "Balendra Shah begins his first foreign visit, a two-day trip to India starting Sunday."),
    ("UK and EU sign three deals",
     "Food trade, carbon markets and youth mobility were agreed at a Brussels summit."),
    ("French officers convicted over Zecler beating",
     "Three police were convicted, with racism ruled an aggravating factor in the 2020 attack."),
    ("Four nations urge aid into flooded Gaza",
     "Australia, Canada, Italy and the UK called on Israel to allow immediate humanitarian access."),
]

# 21 one-line briefs, 3 columns x 7 rows; keep each <= ~58 chars
BRIEFS = [
    "US sanctions four Iranians over oil revenues.",
    "Kryvyi Rih strike kills 2, injures 42.",
    "EU adopts \u20ac1bn military aid package for Ukraine.",
    "Tanker hit and ablaze in Strait of Hormuz.",
    "US approves ~900,000 AI chip exports to China.",
    "Russian military plane crashes in Siberia; 19 dead.",
    "Nvidia probes CEO's alleged China spy link.",
    "US details $12bn in Venezuelan oil revenue.",
    "France: fourth weekend of cost-of-living protests.",
    "Israel's president taps Eisenkot to form government.",
    "Nigeria lets states run their own police.",
    "Two helicopters collide over Everest; 1 killed.",
    "Court freezes assets after Binance's $6.3bn hack.",
    "Robert Pattinson named the next James Bond.",
    "Zelensky: US floated Donbas-for-NATO swap.",
    "UN warns of growing global hunger.",
    "NSE becomes world's 5th-largest exchange.",
    "Cheetah gives birth to four cubs at Kuno.",
    "JPMorgan, Visa, Mastercard hit by vendor hack.",
    "Hyundai unveils 2027 Elantra at LA Auto Show.",
    "Sensex rallies 898 points to 83,920.",
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 16  # margin

    # ---- masthead ----
    title = "THE WORLD TODAY"
    tf = font(SERIF_B, 62)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, 6), title, font=tf, fill=INK)
    d.line([(mx, 84), (W - mx, 84)], fill=RULE, width=2)
    df = font(SANS_B, 20)
    date = "SATURDAY, 21 NOVEMBER 2026"
    d.text((mx, 92), date, font=df, fill=RED)
    rf = font(SANS, 15)
    right = "ONE DAY  \u2022  ONE PAGE  \u2022  THE WORLD IN BRIEF"
    d.text((W - mx - d.textlength(right, font=rf), 95), right, font=rf, fill=GREY)
    d.line([(mx, 118), (W - mx, 118)], fill=RULE, width=1)

    # ---- three leads ----
    col_w, gap = 320, 16
    y_photo, photo_h = 126, 158
    lead_bottom = 0
    for i, (fname, head, body, cap) in enumerate(LEADS):
        x = mx + i * (col_w + gap)
        im = Image.open(os.path.join(WORK, fname)).convert("RGB")
        tw_, th_ = im.size
        target = col_w / photo_h
        if tw_ / th_ > target:
            nw = int(th_ * target)
            off = (tw_ - nw) // 2
            im = im.crop((off, 0, off + nw, th_))
        else:
            nh = int(tw_ / target)
            off = (th_ - nh) // 2
            im = im.crop((0, off, tw_, off + nh))
        im = im.resize((col_w, photo_h), Image.LANCZOS)
        img.paste(im, (x, y_photo))
        d.rectangle([x, y_photo, x + col_w - 1, y_photo + photo_h - 1], outline=RULE, width=1)
        cy = y_photo + photo_h + 4
        cf = font(SANS_I, 11)
        cy = draw_wrapped(d, x, cy, cap, cf, col_w, fill=GREY, leading=13, max_lines=1) + 2
        cy = fit_headline(d, x, cy, head, col_w, size=19, max_lines=2)
        cy += 4
        bf = font(SANS, 13)
        cy = draw_wrapped(d, x, cy, body, bf, col_w, leading=14, max_lines=5)
        lead_bottom = max(lead_bottom, cy)
        if i < 2:
            d.line([(x + col_w + gap // 2, y_photo),
                    (x + col_w + gap // 2, lead_bottom)], fill=(200, 194, 178), width=1)

    # ---- numbered stories ----
    y0 = lead_bottom + 12
    d.line([(mx, y0), (W - mx, y0)], fill=RULE, width=2)
    sf = font(SANS_B, 15)
    d.text((mx, y0 + 6), "THE DAY IN BRIEF", font=sf, fill=INK)
    d.line([(mx, y0 + 28), (W - mx, y0 + 28)], fill=RULE, width=1)
    ncol_w = 492
    y_top = y0 + 36
    rows = 6
    col_ends = []
    for col in range(2):
        yy = y_top
        for r in range(rows):
            idx = col * rows + r
            title, body = NUMBERED[idx]
            x = mx + col * (ncol_w + 8)
            nf = font(SERIF_B, 15)
            d.text((x, yy), f"{idx + 1}.", font=nf, fill=RED)
            tx = x + 26
            yy2 = draw_wrapped(d, tx, yy, title, font(SANS_B, 13), ncol_w - 26,
                               leading=15, max_lines=1)
            yy2 = draw_wrapped(d, tx, yy2, body, font(SANS, 12), ncol_w - 26,
                               leading=13, max_lines=2)
            yy = yy2 + 3
        col_ends.append(yy)
    y = max(col_ends)

    # ---- world map ----
    d.line([(mx, y + 4), (W - mx, y + 4)], fill=RULE, width=2)
    d.text((mx, y + 10), "AROUND THE WORLD", font=sf, fill=INK)
    d.line([(mx, y + 32), (W - mx, y + 32)], fill=RULE, width=1)
    draw_map(d, mx, y + 40, W - 2 * mx, 84)
    y = y + 40 + 84

    # ---- briefs ----
    yb = y + 10
    d.line([(mx, yb), (W - mx, yb)], fill=RULE, width=2)
    d.text((mx, yb + 6), "ALSO TODAY", font=sf, fill=INK)
    d.line([(mx, yb + 28), (W - mx, yb + 28)], fill=RULE, width=1)
    bcol_w = 320
    bf = font(SANS, 11)
    y_start = yb + 36
    col_ends = []
    for col in range(3):
        yyy = y_start
        for r in range(7):
            idx = col * 7 + r
            x = mx + col * (bcol_w + 16)
            yyy = draw_wrapped(d, x, yyy, "\u2022  " + BRIEFS[idx], bf,
                               bcol_w, leading=12, max_lines=1)
        col_ends.append(yyy)
    y = max(col_ends)

    # ---- footer ----
    yf = y + 6
    d.line([(mx, yf), (W - mx, yf)], fill=RULE, width=1)
    ff = font(SANS, 9)
    foot = ("Sources: AP \u2022 Reuters \u2022 BBC \u2022 The Times \u2022 Al Jazeera \u2022 The Guardian "
            "\u2022 NDTV \u2014 all reported 21 Nov 2026. Lead photos are AI illustrations. "
            "make.fun \u2014 news-image-20261121")
    draw_wrapped(d, mx, yf + 5, foot, ff, W - 2 * mx, leading=12, max_lines=1)
    print("layout bottom y =", yf + 17, "of", H)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="JPEG", quality=88, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
