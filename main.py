#!/usr/bin/env python3
"""The World Today - 24 November 2026 in one image.
Python stdlib only. Draws a 1024x1024 newspaper front page,
fully deterministic, writes entry.png to the output dir.
"""
import os, struct, zlib

W = 1024
H = 1024
PX = bytearray(W * H * 3)

# palette
PAPER = (247, 243, 232)
INK = (22, 22, 28)
RED = (178, 34, 42)
BLUE = (28, 74, 140)
TEAL = (18, 116, 110)
GOLD = (198, 142, 28)
LIGHT = (232, 226, 208)
GREY = (105, 102, 96)
WHITE = (255, 255, 255)
SKY = (172, 205, 228)
SEA = (46, 110, 160)
ORANGE = (226, 110, 38)
GREEN = (52, 130, 62)
BROWN = (120, 78, 44)

def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PX[i] = c[0]; PX[i+1] = c[1]; PX[i+2] = c[2]

def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        base = yy * W
        for xx in range(x, x + w):
            if 0 <= xx < W and 0 <= yy < H:
                i = (base + xx) * 3
                PX[i] = c[0]; PX[i+1] = c[1]; PX[i+2] = c[2]

def frame(x, y, w, h, c, t=3):
    rect(x, y, w, t, c); rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c); rect(x + w - t, y, t, h, c)

def hline(x, y, w, c, t=2):
    rect(x, y, w, t, c)

def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                set_px(xx, yy, c)

def tri(x1, y1, x2, y2, x3, y3, c):
    lo_x = max(0, min(x1, x2, x3)); hi_x = min(W - 1, max(x1, x2, x3))
    lo_y = max(0, min(y1, y2, y3)); hi_y = min(H - 1, max(y1, y2, y3))
    d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    if d == 0:
        return
    for yy in range(lo_y, hi_y + 1):
        for xx in range(lo_x, hi_x + 1):
            a = ((y2 - y3) * (xx - x3) + (x3 - x2) * (yy - y3)) / d
            b = ((y3 - y1) * (xx - x3) + (x1 - x3) * (yy - y3)) / d
            g = 1 - a - b
            if a >= 0 and b >= 0 and g >= 0:
                set_px(xx, yy, c)

# 5x7 bitmap font, rows top to bottom
FONT = {
'A':("01110","10001","10001","11111","10001","10001","10001"),
'B':("11110","10001","10001","11110","10001","10001","11110"),
'C':("01110","10001","10000","10000","10000","10001","01110"),
'D':("11100","10010","10001","10001","10001","10010","11100"),
'E':("11111","10000","10000","11110","10000","10000","11111"),
'F':("11111","10000","10000","11110","10000","10000","10000"),
'G':("01110","10001","10000","10111","10001","10001","01111"),
'H':("10001","10001","10001","11111","10001","10001","10001"),
'I':("01110","00100","00100","00100","00100","00100","01110"),
'J':("00111","00010","00010","00010","00010","10010","01100"),
'K':("10001","10010","10100","11000","10100","10010","10001"),
'L':("10000","10000","10000","10000","10000","10000","11111"),
'M':("10001","11011","10101","10101","10001","10001","10001"),
'N':("10001","11001","10101","10011","10001","10001","10001"),
'O':("01110","10001","10001","10001","10001","10001","01110"),
'P':("11110","10001","10001","11110","10000","10000","10000"),
'Q':("01110","10001","10001","10001","10101","10010","01101"),
'R':("11110","10001","10001","11110","10100","10010","10001"),
'S':("01111","10000","10000","01110","00001","00001","11110"),
'T':("11111","00100","00100","00100","00100","00100","00100"),
'U':("10001","10001","10001","10001","10001","10001","01110"),
'V':("10001","10001","10001","10001","10001","01010","00100"),
'W':("10001","10001","10001","10101","10101","10101","01010"),
'X':("10001","01010","00100","00100","00100","01010","10001"),
'Y':("10001","01010","00100","00100","00100","00100","00100"),
'Z':("11111","00001","00010","00100","01000","10000","11111"),
'0':("01110","10001","10011","10101","11001","10001","01110"),
'1':("00100","01100","00100","00100","00100","00100","01110"),
'2':("01110","10001","00001","00110","01000","10000","11111"),
'3':("11110","00001","00001","01110","00001","00001","11110"),
'4':("00010","00110","01010","10010","11111","00010","00010"),
'5':("11111","10000","11110","00001","00001","10001","01110"),
'6':("00110","01000","10000","11110","10001","10001","01110"),
'7':("11111","00001","00010","00100","01000","01000","01000"),
'8':("01110","10001","10001","01110","10001","10001","01110"),
'9':("01110","10001","10001","01111","00001","00010","01100"),
' ':("00000","00000","00000","00000","00000","00000","00000"),
'.':("00000","00000","00000","00000","00000","01100","01100"),
',':("00000","00000","00000","00000","01100","00100","01000"),
"'":("00100","00100","01000","00000","00000","00000","00000"),
':':("00000","01100","01100","00000","01100","01100","00000"),
'-':("00000","00000","00000","01110","00000","00000","00000"),
'+':("00000","00100","00100","01110","00100","00100","00000"),
'/':("00001","00010","00010","00100","01000","01000","10000"),
'%':("11001","11010","00010","00100","01000","01011","10011"),
'!':("00100","00100","00100","00100","00100","00000","00100"),
'?':("01110","10001","00001","00110","00100","00000","00100"),
'(':("00010","00100","01000","01000","01000","00100","00010"),
')':("01000","00100","00010","00010","00010","00100","01000"),
'&':("01100","10010","10100","01000","10101","10010","01101"),
}

def text(x, y, s, scale, c, spacing=1):
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = glyph[r]
            for col in range(5):
                if row[col] == '1':
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
        cx += (5 + spacing) * scale
    return cx

def text_w(s, scale, spacing=1):
    return len(s) * (5 + spacing) * scale - spacing * scale

def centered(y, s, scale, c):
    x = (W - text_w(s, scale)) // 2
    text(x, y, s, scale, c)
    return x

def wrapped(x, y, lines, scale, c, leading=12):
    yy = y
    for ln in lines:
        text(x, yy, ln, scale, c)
        yy += 7 * scale + leading
    return yy


def draw_chip(cx, cy, size, body, pin):
    rect(cx - size // 2, cy - size // 2, size, size, body)
    frame(cx - size // 2, cy - size // 2, size, size, INK, 4)
    inner = size // 2
    rect(cx - inner // 2, cy - inner // 2, inner, inner, GOLD)
    step = size // 5
    for k in range(-2, 3):
        off = k * step
        rect(cx + off - 3, cy - size // 2 - 22, 6, 22, pin)
        rect(cx + off - 3, cy + size // 2, 6, 22, pin)
        rect(cx - size // 2 - 22, cy + off - 3, 22, 6, pin)
        rect(cx + size // 2, cy + off - 3, 22, 6, pin)

def draw_ship(cx, cy, hull, accent):
    tri(cx - 90, cy, cx + 90, cy, cx + 55, cy + 34, hull)
    rect(cx - 90, cy - 8, 180, 10, hull)
    rect(cx - 28, cy - 42, 62, 34, accent)
    rect(cx + 8, cy - 62, 10, 22, INK)
    for i in range(4):
        circle(cx - 55 + i * 32, cy + 12, 5, WHITE)

def draw_small_ship(cx, cy, hull, accent):
    # compact ship icon, about 84 wide and 36 tall, centred on cx, cy
    tri(cx - 42, cy, cx + 42, cy, cx + 26, cy + 16, hull)
    rect(cx - 42, cy - 4, 84, 5, hull)
    rect(cx - 12, cy - 22, 28, 18, accent)
    rect(cx + 2, cy - 32, 5, 10, INK)
    for i in range(3):
        circle(cx - 22 + i * 22, cy + 6, 3, WHITE)

def draw_flame(cx, cy, s, c1, c2):
    tri(cx, cy - s, cx - s // 2, cy + s // 2, cx + s // 2, cy + s // 2, c1)
    tri(cx, cy - s // 3, cx - s // 4, cy + s // 2, cx + s // 4, cy + s // 2, c2)
    circle(cx, cy + s // 3, s // 4, c2)

def build():
    rect(0, 0, W, H, PAPER)
    # masthead
    rect(0, 0, W, 118, INK)
    centered(18, "THE WORLD TODAY", 11, WHITE)
    rect(0, 118, W, 8, RED)
    centered(134, "TUESDAY 24 NOVEMBER 2026", 4, RED)
    hline(24, 168, W - 48, INK, 3)

    # LEAD: Huawei verdict
    rect(24, 182, 976, 318, WHITE)
    frame(24, 182, 976, 318, INK, 3)
    rect(24, 182, 976, 44, RED)
    text(44, 192, "LEAD  -  US TRIAL VERDICT", 3, WHITE)
    wrapped(44, 242, ["HUAWEI", "GUILTY OF"], 7, INK, 10)
    wrapped(44, 356, ["TRADE THEFT", "AND FRAUD"], 6, RED, 8)
    wrapped(44, 458, ["ACQUITTED ON RACKETEERING,", "THE GRAVER CHARGE"], 2, GREY, 5)
    # lead visual: courthouse + chip + gavel bar
    rect(650, 242, 310, 190, SKY)
    frame(650, 242, 310, 190, INK, 3)
    rect(674, 268, 262, 14, WHITE)
    tri(662, 268, 948, 268, 805, 236 + 10, WHITE)
    for col in range(4):
        rect(690 + col * 64, 282, 22, 92, WHITE)
    rect(674, 374, 262, 14, WHITE)
    rect(674, 402, 262, 18, BROWN)
    draw_chip(805, 328, 50, INK, GOLD)

    # middle row: two panels
    # Panel A Hormuz
    rect(24, 516, 480, 236, WHITE)
    frame(24, 516, 480, 236, INK, 3)
    rect(24, 516, 480, 38, BLUE)
    text(40, 526, "STRAIT OF HORMUZ", 3, WHITE)
    wrapped(40, 568, ["TANKERS HIT MINES,", "IRAN REFUSES TALKS"], 4, INK, 8)
    wrapped(40, 652, ["IRGC SAYS 4 TANKERS STRUCK", "MINES, CONTAINER SHIP HIT.", "TEHRAN: NO TALKS UNTIL US", "BLOCKADE IS LIFTED"], 2, GREY, 5)
    rect(392, 700, 96, 44, SEA)
    draw_small_ship(440, 720, INK, ORANGE)
    draw_flame(472, 712, 16, ORANGE, GOLD)

    # Panel B Ukraine at sea
    rect(520, 516, 480, 236, WHITE)
    frame(520, 516, 480, 236, INK, 3)
    rect(520, 516, 480, 38, TEAL)
    text(536, 526, "UKRAINE - WAR AT SEA", 3, WHITE)
    wrapped(536, 568, ["DRONES HIT RUSSIAN", "SHIPS ON TWO SEAS"], 4, INK, 8)
    wrapped(536, 652, ["CARGO SHIP SPARTA II HIT IN", "GULF OF FINLAND, AFTER THE", "LIBYA STRIKE. POLAND RAISES", "NEW AIRSPACE CLAIM"], 2, GREY, 5)
    rect(888, 700, 96, 44, SEA)
    draw_small_ship(936, 720, INK, RED)
    circle(904, 712, 6, GOLD)

    # bottom row: three panels
    panels = [
        (24, "MALAYSIA - ROHINGYA", RED,
         ["MALAYSIA SENDS", "6,500 BACK"],
         ["RETURNS TO MYANMAR BY SHIP", "AND PLANE FROM DECEMBER,", "DAYS AFTER ICJ GENOCIDE", "RULING AGAINST MYANMAR"]),
        (352, "SPACE - SHENZHOU-24", GOLD,
         ["FIRST FOREIGNER", "TO TIANGONG"],
         ["PAKISTAN'S ZEESHAN ALI NAMED", "TO SHENZHOU-24 CREW - FIRST", "NON-CHINESE VISITOR TO", "CHINA'S SPACE STATION"]),
        (680, "INDONESIA - FIRE", ORANGE,
         ["FIRE TOLL RISES", "TO 26 DEAD"],
         ["BANTEN CANDY FACTORY: 28", "STILL MISSING AS RESCUERS", "SEARCH UNSTABLE WRECKAGE.", "WORKERS TRAPPED INSIDE"]),
    ]
    for x, head, col, title, body in panels:
        wdt = 320 if x != 680 else 320
        rect(x, 768, wdt, 176, WHITE)
        frame(x, 768, wdt, 176, INK, 3)
        rect(x, 768, wdt, 34, col)
        text(x + 14, 777, head, 2, WHITE)
        wrapped(x + 14, 814, title, 3, INK, 6)
        wrapped(x + 14, 884, body, 1, GREY, 4)

    # ticker
    rect(0, 960, W, 64, INK)
    text(20, 974, "ALSO: SENEGAL REGAIN AFCON TITLE ON APPEAL", 2, GOLD)
    text(20, 996, "DEMOCRATS REACH 259 HOUSE SEATS - UK SANCTIONS HOUTHIS", 2, WHITE)

def save_png(path):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        start = yy * W * 3
        raw.extend(PX[start:start + W * 3])
    comp = zlib.compress(bytes(raw), 9)
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
        return out
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)

def main():
    build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    save_png(os.path.join(out_dir, "entry.png"))

if __name__ == "__main__":
    main()
