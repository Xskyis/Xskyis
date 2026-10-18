import os
from PIL import Image, ImageDraw, ImageFont

# 8-bit Color Palette for the Terminal & Mascot
PALETTE = {
    '.': (0, 0, 0, 0),             # Transparent
    '#': (18, 22, 30, 255),        # Deep Charcoal Outline
    'D': (42, 48, 62, 255),        # Dark Charcoal Body
    'M': (58, 66, 84, 255),        # Mid Charcoal / Shading
    'L': (90, 102, 126, 255),      # Light Slate Highlight
    'W': (236, 241, 248, 255),     # Crisp White (chest/paws)
    'P': (255, 121, 198, 255),     # Pink (inner ear, nose, blush)
    'E': (80, 250, 123, 255),      # Emerald / Neon Green Eye
    'B': (14, 17, 24, 255),        # Black pupil
    'S': (139, 233, 253, 255),     # Cyan Sparkle
    'H': (255, 85, 85, 255),       # Heart Coral Red
}

# 24 wide x 21 high pixel art cat mascot
# 1. Neutral pose: Eyes wide open with emerald glow, looking forward
SPRITE_NEUTRAL = [
    "........................",
    "...##..............##...",
    "..#DD#............#DD#..",
    "..#DPD#..........#DPD#..",
    "..#DPPD#........#DPPD#..",
    "..#DMPPD########DPPMD#..",
    ".#DDMMDDDDDDDDDDDDMMDD#.",
    ".#DMMDDDDDDDDDDDDDDMMD#.",
    "#DDMDDEEBBDDDDBBEEDMDDD#",
    "#DDDDDEEBBDDDDBBEEDDDDD#",
    "#DDDDDDBBBDDDDBBBDDDDDD#",
    "#DDDDDDDPPWWWWPPDDDDDDD#",
    ".#DDDDDDDPPWPPPDDDDDDD#.",
    ".#DDDDDDDWWWWWDDDDDDDD#.",
    "..#DDDDDDDWWDDDDDDDDD#..",
    "..#DDDDDDDDDDDDDDDDDD#..",
    ".#DDMMDDDDDDDDDDDDMMDD#.",
    ".#DDDDDDDDDDDDDDDDDDDD##",
    ".#DDDDWWDDDDDDWWDDDDD#D#",
    "..#DDD##DDDDDD##DDDD#DD#",
    "...####.######.#####..##"
]

# 2. Glance pose: Pupils shift right towards stats, tail sways up
SPRITE_GLANCE = [
    "........................",
    "...##..............##...",
    "..#DD#............#DD#..",
    "..#DPD#..........#DPD#..",
    "..#DPPD#........#DPPD#..",
    "..#DMPPD########DPPMD#..",
    ".#DDMMDDDDDDDDDDDDMMDD#.",
    ".#DMMDDDDDDDDDDDDDDMMD#.",
    "#DDMDDDBBEEDDDDBBEEDDDD#",
    "#DDDDDDBBEEDDDDBBEEDDDD#",
    "#DDDDDDBBBDDDDBBBDDDDDD#",
    "#DDDDDDDPPWWWWPPDDDDDDD#",
    ".#DDDDDDDPPWPPPDDDDDDD#.",
    ".#DDDDDDDWWWWWDDDDDDDD#.",
    "..#DDDDDDDWWDDDDDDDDD#.#",
    "..#DDDDDDDDDDDDDDDDDD#DD",
    ".#DDMMDDDDDDDDDDDDMMD#DD",
    ".#DDDDDDDDDDDDDDDDDD##D#",
    ".#DDDDWWDDDDDDWWDDDD#D#.",
    "..#DDD##DDDDDD##DDDD##..",
    "...####.######.#####...."
]

# 3. Happy blink: Eyes close into happy arches ^ ^
SPRITE_BLINK = [
    "........................",
    "...##..............##...",
    "..#DD#............#DD#..",
    "..#DPD#..........#DPD#..",
    "..#DPPD#........#DPPD#..",
    "..#DMPPD########DPPMD#..",
    ".#DDMMDDDDDDDDDDDDMMDD#.",
    ".#DMMDDDDDDDDDDDDDDMMD#.",
    "#DDMDD.####DD####.MDDDD#",
    "#DDDDD##DDDD##DDDD#DDDD#",
    "#DDDDDDDDDDDDDDDDDDDDDD#",
    "#DDDDDDDPPWWWWPPDDDDDDD#",
    ".#DDDDDDDPPWPPPDDDDDDD#.",
    ".#DDDDDDDWWWWWDDDDDDDD#.",
    "..#DDDDDDDWWDDDDDDDDD#..",
    "..#DDDDDDDDDDDDDDDDDD#..",
    ".#DDMMDDDDDDDDDDDDMMDD#.",
    ".#DDDDDDDDDDDDDDDDDDDD##",
    ".#DDDDWWDDDDDDWWDDDDD#D#",
    "..#DDD##DDDDDD##DDDD#DD#",
    "...####.######.#####..##"
]

# 4. Heart pose: Glowing red pixel heart floats above ear, slight bounce down
SPRITE_HEART = [
    "..................##....",
    ".................#HH##..",
    "...##...........#HHHH#..",
    "..#DD#...........#HH#...",
    "..#DPD#...........##.##.",
    "..#DPPD#.........#DPD#..",
    "..#DMPPD########DPPD#...",
    ".#DDMMDDDDDDDDDDMMDD#...",
    ".#DMMDDDDDDDDDDDDMMD#...",
    "#DDMDDEEBBDDDDBBEEDMDD#.",
    "#DDDDDEEBBDDDDBBEEDDDD#.",
    "#DDDDDDBBBDDDDBBBDDDDD#.",
    "#DDDDDDDPPWWWWPPDDDDDD#.",
    ".#DDDDDDDPPWPPPDDDDDDD#.",
    ".#DDDDDDDWWWWWDDDDDDDD#.",
    "..#DDDDDDDWWDDDDDDDDD#..",
    "..#DDDDDDDDDDDDDDDDDD#..",
    ".#DDMMDDDDDDDDDDDDMMDD#.",
    ".#DDDDDDDDDDDDDDDDDDDD##",
    ".#DDDDWWDDDDDDWWDDDDD#D#",
    "..#DDD##DDDDDD##DDDD#DD#",
    "...####.######.#####..##"
]

def render_sprite(matrix, scale=7):
    rows = len(matrix)
    cols = max(len(row) for row in matrix)
    img = Image.new("RGBA", (cols * scale, rows * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for r in range(rows):
        line = matrix[r].ljust(cols, '.')
        for c in range(cols):
            ch = line[c]
            color = PALETTE.get(ch, (0, 0, 0, 0))
            if color[3] > 0:
                draw.rectangle([c * scale, r * scale, (c + 1) * scale - 1, (r + 1) * scale - 1], fill=color)
    return img

def render_terminal_frame(
    sprite_img=None,
    cat_y_offset=0,
    header_cmd="Fetch.sh -u nabilfgrza",
    header_cursor=True,
    show_content=True,
    footer_cursor=True,
    active_color_idx=-1
):
    W, H = 840, 520
    im = Image.new("RGBA", (W, H), (15, 17, 23, 255))
    draw = ImageDraw.Draw(im)

    # Window border & shadow
    draw.rounded_rectangle([0, 0, W-1, H-1], radius=10, fill=(18, 21, 28, 255), outline=(59, 66, 82, 255), width=1)
    
    # Title bar
    draw.rounded_rectangle([0, 0, W-1, 34], radius=10, fill=(24, 28, 38, 255))
    draw.rectangle([0, 24, W-1, 34], fill=(24, 28, 38, 255))
    draw.line([0, 34, W-1, 34], fill=(46, 52, 64, 255), width=1)

    # Window control dots
    draw.ellipse([14, 11, 26, 23], fill=(255, 95, 86, 255))  # Red (Close)
    draw.ellipse([34, 11, 46, 23], fill=(255, 189, 46, 255)) # Yellow (Minimize)
    draw.ellipse([54, 11, 66, 23], fill=(39, 201, 63, 255))  # Green (Maximize)

    # Window title (ricer style)
    font_title = ImageFont.truetype("fonts/JetBrainsMono-Bold.ttf", 12)
    title_text = "nabilfgrza@gifos: ~ (zsh)"
    tbox = draw.textbbox((0, 0), title_text, font=font_title)
    tw = tbox[2] - tbox[0]
    draw.text(((W - tw) // 2, 9), title_text, fill=(140, 150, 170, 255), font=font_title)

    # Fonts
    font_code = ImageFont.truetype("fonts/JetBrainsMono-Bold.ttf", 13)
    font_bold = ImageFont.truetype("fonts/JetBrainsMono-Bold.ttf", 14)

    # Top Prompt line
    y = 48
    draw.text((22, y), "nabilfgrza", fill=(80, 250, 123, 255), font=font_code)
    draw.text((105, y), "@gifos", fill=(139, 233, 253, 255), font=font_code)
    draw.text((158, y), " ~> ", fill=(255, 184, 108, 255), font=font_code)
    
    cmd_x = 192
    draw.text((cmd_x, y), header_cmd, fill=(248, 248, 242, 255), font=font_code)
    if header_cursor:
        cbox = draw.textbbox((0, 0), header_cmd, font=font_code)
        cw = cbox[2] - cbox[0] if header_cmd else 0
        draw.text((cmd_x + cw, y), "▋", fill=(80, 250, 123, 255), font=font_code)

    if not show_content:
        return im

    # Left Box for Mascot
    draw.rounded_rectangle([20, 80, 236, 462], radius=8, fill=(20, 24, 33, 255), outline=(46, 52, 64, 255), width=1)
    draw.text((32, 92), "┌─ [ CONSOLE PET ]", fill=(98, 114, 164, 255), font=font_code)
    
    if sprite_img:
        im.paste(sprite_img, (44, 125 + cat_y_offset), sprite_img)

    # Mascot status block
    draw.text((32, 305), "├─ STATUS: ONLINE", fill=(80, 250, 123, 255), font=font_code)
    draw.text((32, 325), "├─ MOOD:   PURRING", fill=(255, 121, 198, 255), font=font_code)
    draw.text((32, 345), "├─ LVL:    v2.1", fill=(139, 233, 253, 255), font=font_code)
    draw.text((32, 365), "└─ BYTES:  8-BIT MEOW", fill=(241, 250, 140, 255), font=font_code)

    # Right Column info
    rx = 256
    ry = 78

    # User Info Block
    draw.text((rx, ry), "nabilfgrza@GitHub", fill=(255, 121, 198, 255), font=font_bold)
    draw.line([rx, ry + 20, rx + 160, ry + 20], fill=(98, 114, 164, 255), width=1)

    info_items = [
        ("OS", "CachyOS, Parrot OS, Windows 11"),
        ("Host", "Politeknik Negeri Malang (Polinema)"),
        ("Kernel", "Freelance Software Developer"),
        ("Uptime", "21 years, 5 months, 4 days"),
        ("IDE", "neovim, VSCode"),
    ]

    cur_y = ry + 28
    for label, val in info_items:
        draw.text((rx, cur_y), f"{label}:", fill=(139, 233, 253, 255), font=font_code)
        draw.text((rx + 72, cur_y), val, fill=(248, 248, 242, 255), font=font_code)
        cur_y += 18

    # Contact Block
    cur_y += 6
    draw.text((rx, cur_y), "Contact:", fill=(255, 184, 108, 255), font=font_bold)
    cur_y += 20
    contact_items = [
        ("Email", "nabilfgrza@web.id"),
        ("LinkedIn", "nabilfgrza"),
        ("GitHub", "Xskyis"),
    ]
    for label, val in contact_items:
        draw.text((rx, cur_y), f"{label}:", fill=(189, 147, 249, 255), font=font_code)
        draw.text((rx + 72, cur_y), val, fill=(248, 248, 242, 255), font=font_code)
        cur_y += 18

    # GitHub Stats Block
    cur_y += 6
    draw.text((rx, cur_y), "GitHub Stats:", fill=(80, 250, 123, 255), font=font_bold)
    cur_y += 20
    stats_items = [
        ("Rating", "A+"),
        ("Stars Earned", "142"),
        ("Commits", "748"),
        ("PRs", "36  (Merged: 89.2%)"),
        ("Total Contribs", "912"),
        ("Top Languages", "JS, PHP, Python, HTML, CSS"),
    ]
    for label, val in stats_items:
        draw.text((rx, cur_y), f"{label}:", fill=(241, 250, 140, 255), font=font_code)
        if label == "Rating":
            draw.text((rx + 130, cur_y), val, fill=(80, 250, 123, 255), font=font_bold)
        else:
            draw.text((rx + 130, cur_y), val, fill=(248, 248, 242, 255), font=font_code)
        cur_y += 18

    # Color palette blocks
    cur_y += 8
    palette_colors = [
        (40, 42, 54),   # Black
        (255, 85, 85),  # Red
        (80, 250, 123), # Green
        (241, 250, 140),# Yellow
        (189, 147, 249),# Purple
        (255, 121, 198),# Pink
        (139, 233, 253),# Cyan
        (248, 248, 242),# White
    ]
    bx = rx
    for idx, c in enumerate(palette_colors):
        if idx == active_color_idx:
            draw.rectangle([bx - 1, cur_y - 2, bx + 29, cur_y + 14], outline=(255, 255, 255, 220), width=1)
        draw.rectangle([bx, cur_y, bx + 28, cur_y + 12], fill=c)
        bx += 34

    # Footer Line
    fy = H - 28
    draw.text((22, fy), "nabilfgrza", fill=(80, 250, 123, 255), font=font_code)
    draw.text((105, fy), "@gifos", fill=(139, 233, 253, 255), font=font_code)
    draw.text((158, fy), " ~> ", fill=(255, 184, 108, 255), font=font_code)
    
    footer_text = "# Have a nice day kin"
    draw.text((192, fy), footer_text, fill=(189, 147, 249, 255), font=font_code)
    if footer_cursor:
        cbox = draw.textbbox((0, 0), footer_text, font=font_code)
        cw = cbox[2] - cbox[0]
        draw.text((192 + cw, fy), "_", fill=(255, 255, 255, 255), font=font_code)

    return im

def generate_assets():
    print("[1/3] Rendering pixel mascot sprites...")
    s_neutral = render_sprite(SPRITE_NEUTRAL)
    s_glance = render_sprite(SPRITE_GLANCE)
    s_blink = render_sprite(SPRITE_BLINK)
    s_heart = render_sprite(SPRITE_HEART)

    os.makedirs("assets", exist_ok=True)

    print("[2/3] Rendering static high-res preview PNG...")
    preview_img = render_terminal_frame(
        sprite_img=s_neutral,
        cat_y_offset=0,
        header_cmd="Fetch.sh -u nabilfgrza",
        header_cursor=True,
        show_content=True,
        footer_cursor=True,
        active_color_idx=2
    )
    preview_img.save("assets/terminal_preview.png")

    print("[3/3] Compiling animated GIF timeline...")
    frames = []
    durations = []

    # Intro typing sequence (~0.5s)
    typing_steps = [
        ("", True, 180),
        ("Fetch.sh", True, 120),
        ("Fetch.sh -u nabil", True, 120),
        ("Fetch.sh -u nabilfgrza", False, 180),
    ]

    for cmd, cur, dur in typing_steps:
        fr = render_terminal_frame(
            sprite_img=None,
            header_cmd=cmd,
            header_cursor=cur,
            show_content=False,
            footer_cursor=False
        )
        fr_p = fr.convert("P", palette=Image.ADAPTIVE, colors=64)
        frames.append(fr_p)
        durations.append(dur)

    # Live console interactive loop (~3.2s)
    # Cat breathes, glances right at stats, blinks happily, heart floats, tail wags!
    # Blinking cursors at top and bottom, color swatches pulse!
    main_loop = [
        (s_neutral, 0, True,  True,  0, 200),
        (s_neutral, 0, True,  False, 1, 200),
        (s_glance,  0, False, True,  2, 200),
        (s_glance,  0, False, False, 3, 200),
        (s_blink,   0, True,  True,  4, 150),
        (s_blink,   0, True,  False, 5, 150),
        (s_heart,   1, False, True,  6, 220), # Breath down 1px
        (s_heart,   1, False, False, 7, 220),
        (s_neutral, 0, True,  True,  0, 200), # Breath up
        (s_neutral, 0, True,  False, 1, 200),
        (s_glance,  0, False, True,  2, 200),
        (s_glance,  0, False, False, 3, 200),
        (s_neutral, 0, True,  True,  4, 200),
        (s_blink,   0, True,  False, 5, 150),
        (s_neutral, 0, False, True,  6, 200),
        (s_neutral, 0, False, False, 7, 200),
    ]

    for sprite, y_off, h_cur, f_cur, col_idx, dur in main_loop:
        fr = render_terminal_frame(
            sprite_img=sprite,
            cat_y_offset=y_off,
            header_cmd="Fetch.sh -u nabilfgrza",
            header_cursor=h_cur,
            show_content=True,
            footer_cursor=f_cur,
            active_color_idx=col_idx
        )
        fr_p = fr.convert("P", palette=Image.ADAPTIVE, colors=64)
        frames.append(fr_p)
        durations.append(dur)

    gif_path = "assets/terminal.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"Generated {gif_path}! Size: {os.path.getsize(gif_path)} bytes")

if __name__ == "__main__":
    generate_assets()
