import os
import urllib.request
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()

# Yoru / THUNDRA_OS Terminal Palette (Hex for SVG & RGB for Pillow)
YORU_BG = "#0c0e0f"       # Pure dark terminal background
YORU_BAR = "#141719"      # Window header bar
YORU_BORDER = "#232628"   # Subtle terminal border
YORU_DIVIDER = "#1e2123"  # Divider line
YORU_FG = "#edeff0"       # White text
YORU_MUTED = "#7a8288"    # Muted gray text
YORU_CYAN = "#70b8ca"     # Cyan labels
YORU_GREEN = "#81c19b"    # Emerald green numbers & accents
YORU_YELLOW = "#de8f78"   # Peach / yellow numbers & prompt
YORU_RED = "#df5b61"      # Red prompt username

YORU_BG_RGB = (12, 14, 15, 255)
YORU_MUTED_RGB = (122, 130, 136, 255)
YORU_CYAN_RGB = (112, 184, 202, 255)
YORU_GREEN_RGB = (129, 193, 155, 255)
YORU_YELLOW_RGB = (222, 143, 120, 255)
YORU_DIVIDER_RGB = (30, 33, 35, 255)

# Yoru-themed heatmap levels (seamless dark forest to emerald green)
YORU_HEATMAP = [
    "#202325",  # 0 contributions (Subtle visible dark slate cell)
    "#1e3e2e",  # Level 1 (1-2)
    "#2d6347",  # Level 2 (3-5)
    "#448e65",  # Level 3 (6-8)
    "#78b892",  # Level 4 (9-11)
    "#81c19b",  # Level 5 (12+)
]

HEATMAP_COLORS_RGB = [
    (32, 35, 37, 255),   # Level 0 (empty #202325)
    (30, 62, 46, 255),   # Level 1 (#1e3e2e)
    (45, 99, 71, 255),   # Level 2 (#2d6347)
    (68, 142, 101, 255), # Level 3 (#448e65)
    (120, 184, 146, 255),# Level 4 (#78b892)
    (129, 193, 155, 255),# Level 5 (#81c19b)
]

def fetch_contribution_data(username="Xskyis", token=None):
    """Fetch GitHub contribution calendar data via GraphQL API."""
    if not token:
        token = os.getenv("GITHUB_TOKEN")

    if not token or token.startswith("ghp_your"):
        print("WARNING: GITHUB_TOKEN not provided or invalid. Using fallback data.")
        return None

    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
                weekday
              }
            }
          }
        }
      }
    }
    """
    try:
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": query, "variables": {"login": username}}).encode("utf-8"),
            headers={"Authorization": f"Bearer {token.strip()}", "User-Agent": "THUNDRA-Heatmap-Generator"}
        )
        res = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8"))
        if "data" in res and res["data"] and "user" in res["data"] and res["data"]["user"]:
            cal = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]
            return cal
        else:
            print(f"WARNING: GraphQL returned unexpected structure: {res}")
            return None
    except Exception as e:
        print(f"WARNING: GraphQL contribution fetch failed ({e}). Using fallback data.")
        return None

def compute_stats(cal):
    """Compute contribution totals, streaks, best day, and date ranges."""
    if not cal or not cal.get("weeks"):
        return {
            "total_contributions": 168,
            "weeks": [],
            "days": [],
            "current_streak": 2,
            "longest_streak": 4,
            "best_day_count": 13,
            "best_day_date": "Jun 22, 2026",
            "start_date_str": "Oct 19, 2025",
            "end_date_str": "Oct 24, 2026",
            "start_date_short": "Oct 19, 2025",
            "end_date_short": "Oct 24, 2026",
        }

    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    total_contributions = cal.get("totalContributions", sum(d["contributionCount"] for d in days))

    # Calculate streaks
    longest_streak = 0
    temp_streak = 0
    for d in days:
        if d["contributionCount"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    curr_streak = 0
    rev_days = list(reversed(days))
    idx = 0
    if rev_days and rev_days[0]["contributionCount"] == 0:
        idx = 1
    while idx < len(rev_days) and rev_days[idx]["contributionCount"] > 0:
        curr_streak += 1
        idx += 1

    best_day = max(days, key=lambda d: d["contributionCount"]) if days else {"contributionCount": 0, "date": "2026-01-01"}
    try:
        best_day_date = datetime.strptime(best_day["date"], "%Y-%m-%d").strftime("%b %d, %Y")
        start_date_str = datetime.strptime(days[0]["date"], "%Y-%m-%d").strftime("%b %d, %Y")
        end_date_str = datetime.strptime(days[-1]["date"], "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        best_day_date = best_day["date"]
        start_date_str = "Oct 19, 2025"
        end_date_str = "Oct 24, 2026"

    return {
        "total_contributions": total_contributions,
        "weeks": weeks,
        "days": days,
        "current_streak": curr_streak,
        "longest_streak": longest_streak,
        "best_day_count": best_day["contributionCount"],
        "best_day_date": best_day_date,
        "start_date_str": start_date_str,
        "end_date_str": end_date_str,
        "start_date_short": start_date_str,
        "end_date_short": end_date_str,
    }

def get_fill_color(count, max_count):
    if count == 0:
        return YORU_HEATMAP[0]
    if max_count <= 0:
        return YORU_HEATMAP[1]
    ratio = count / max_count
    if ratio <= 0.18:
        return YORU_HEATMAP[1]
    elif ratio <= 0.38:
        return YORU_HEATMAP[2]
    elif ratio <= 0.60:
        return YORU_HEATMAP[3]
    elif ratio <= 0.82:
        return YORU_HEATMAP[4]
    else:
        return YORU_HEATMAP[5]

def get_fill_color_rgb(count, max_count):
    if count == 0:
        return HEATMAP_COLORS_RGB[0]
    if max_count <= 0:
        return HEATMAP_COLORS_RGB[1]
    ratio = count / max_count
    if ratio <= 0.18:
        return HEATMAP_COLORS_RGB[1]
    elif ratio <= 0.38:
        return HEATMAP_COLORS_RGB[2]
    elif ratio <= 0.60:
        return HEATMAP_COLORS_RGB[3]
    elif ratio <= 0.82:
        return HEATMAP_COLORS_RGB[4]
    else:
        return HEATMAP_COLORS_RGB[5]

def render_contribution_strip(stats, output_path="assets/contrib_graph.png"):
    """Render the contribution heatmap strip to PNG for direct pasting inside gifos."""
    weeks = stats.get("weeks", [])
    max_count = stats.get("best_day_count", 1)

    width = 696
    height = 175
    im = Image.new("RGBA", (width, height), YORU_BG_RGB)
    draw = ImageDraw.Draw(im)

    font_path = "./fonts/JetBrainsMono-Bold.ttf"
    try:
        font_sm = ImageFont.truetype(font_path, 10)
        font_xs = ImageFont.truetype(font_path, 9)
        font_md = ImageFont.truetype(font_path, 11)
    except Exception:
        font_sm = ImageFont.load_default()
        font_xs = font_sm
        font_md = font_sm

    start_x = 34
    start_y = 22
    cell_size = 9.5
    step = 12.0
    rx = 2

    # 1. Month Labels
    col_months = []
    for week in weeks:
        day = week["contributionDays"][min(3, len(week["contributionDays"]) - 1)]
        dt = datetime.strptime(day["date"], "%Y-%m-%d")
        col_months.append(dt.strftime("%b"))

    last_label_col = -10
    for col_idx in range(len(col_months)):
        m = col_months[col_idx]
        prev_m = col_months[col_idx - 1] if col_idx > 0 else None
        if m != prev_m:
            month_len = 0
            for future_col in range(col_idx, len(col_months)):
                if col_months[future_col] == m:
                    month_len += 1
                else:
                    break
            if col_idx == 0 and month_len < 3:
                continue
            if (col_idx - last_label_col) >= 3:
                mx = start_x + col_idx * step
                draw.text((mx, 4), m, fill=YORU_CYAN_RGB, font=font_sm)
                last_label_col = col_idx

    # 2. Weekday Labels
    draw.text((8, start_y + 1 * step - 2), "Mon", fill=YORU_MUTED_RGB, font=font_xs)
    draw.text((8, start_y + 3 * step - 2), "Wed", fill=YORU_MUTED_RGB, font=font_xs)
    draw.text((8, start_y + 5 * step - 2), "Fri", fill=YORU_MUTED_RGB, font=font_xs)

    # 3. Cells
    for col_idx, week in enumerate(weeks):
        for day in week["contributionDays"]:
            weekday = day["weekday"]
            cx = start_x + col_idx * step
            cy = start_y + weekday * step
            count = day["contributionCount"]
            color = get_fill_color_rgb(count, max_count)
            draw.rounded_rectangle([cx, cy, cx + cell_size, cy + cell_size], radius=rx, fill=color)

    # 4. Legend
    legend_y = start_y + 7 * step + 5
    draw.text((530, legend_y - 2), "Less", fill=YORU_MUTED_RGB, font=font_sm)
    for i, c in enumerate(HEATMAP_COLORS_RGB):
        lx = 562 + i * 12
        draw.rounded_rectangle([lx, legend_y - 1, lx + cell_size, legend_y - 1 + cell_size], radius=rx, fill=c)
    draw.text((638, legend_y - 2), "More", fill=YORU_MUTED_RGB, font=font_sm)

    # 5. Divider Line
    line_y = legend_y + 18
    draw.line([(8, line_y), (width - 8, line_y)], fill=YORU_DIVIDER_RGB, width=1)

    # 6. Summary Rows
    total_c = stats["total_contributions"]
    curr_strk = stats["current_streak"]
    lng_strk = stats["longest_streak"]
    best_c = stats["best_day_count"]
    best_d = stats["best_day_date"]
    start_d = stats["start_date_str"]
    end_d = stats["end_date_str"]

    row1_y = line_y + 6
    draw.text((8, row1_y), f"{total_c}", fill=YORU_GREEN_RGB, font=font_md)
    t_w = draw.textlength(f"{total_c} ", font=font_md)
    draw.text((8 + t_w, row1_y), "contributions in the last year", fill=YORU_MUTED_RGB, font=font_md)
    range_str = f"{start_d} -> {end_d}"
    range_w = draw.textlength(range_str, font=font_md)
    draw.text((width - 8 - range_w, row1_y), range_str, fill=YORU_CYAN_RGB, font=font_md)

    row2_y = row1_y + 16
    draw.text((8, row2_y), "current streak ", fill=YORU_MUTED_RGB, font=font_md)
    w1 = draw.textlength("current streak ", font=font_md)
    draw.text((8 + w1, row2_y), f"{curr_strk} days", fill=YORU_YELLOW_RGB, font=font_md)
    w2 = draw.textlength(f"{curr_strk} days", font=font_md)
    draw.text((8 + w1 + w2, row2_y), "  \u00b7  longest ", fill=YORU_MUTED_RGB, font=font_md)
    w3 = draw.textlength("  \u00b7  longest ", font=font_md)
    draw.text((8 + w1 + w2 + w3, row2_y), f"{lng_strk} days", fill=YORU_YELLOW_RGB, font=font_md)

    best_str_prefix = "best day "
    best_val = f"{best_c}"
    best_suffix = f" on {best_d}"
    bw1 = draw.textlength(best_str_prefix, font=font_md)
    bw2 = draw.textlength(best_val, font=font_md)
    bw3 = draw.textlength(best_suffix, font=font_md)
    total_bw = bw1 + bw2 + bw3
    bx = width - 8 - total_bw
    draw.text((bx, row2_y), best_str_prefix, fill=YORU_MUTED_RGB, font=font_md)
    draw.text((bx + bw1, row2_y), best_val, fill=YORU_YELLOW_RGB, font=font_md)
    draw.text((bx + bw1 + bw2, row2_y), best_suffix, fill=YORU_MUTED_RGB, font=font_md)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    im.save(output_path)
    print(f"INFO: Rendered {output_path} ({im.size}) for gifos integration")
    return im

def generate_svg_content(username, stats):
    """Generate SVG markup for Contribution Highlight terminal card without Apple buttons."""
    weeks = stats.get("weeks", [])
    max_count = stats.get("best_day_count", 1)

    width = 750
    height = 240
    start_x = 76.0
    start_y = 52.0
    cell_size = 9.8
    step = 12.0
    rx = 2.5

    col_months = []
    for week in weeks:
        day = week["contributionDays"][min(3, len(week["contributionDays"]) - 1)]
        dt = datetime.strptime(day["date"], "%Y-%m-%d")
        col_months.append(dt.strftime("%b"))

    month_labels = []
    last_label_col = -10
    for col_idx in range(len(col_months)):
        m = col_months[col_idx]
        prev_m = col_months[col_idx - 1] if col_idx > 0 else None
        if m != prev_m:
            month_len = 0
            for future_col in range(col_idx, len(col_months)):
                if col_months[future_col] == m:
                    month_len += 1
                else:
                    break
            if col_idx == 0 and month_len < 3:
                continue
            if (col_idx - last_label_col) >= 3:
                col_x = start_x + col_idx * step
                month_labels.append((col_x, m))
                last_label_col = col_idx

    cells_xml = []
    for col_idx, week in enumerate(weeks):
        for day in week["contributionDays"]:
            weekday = day["weekday"]
            c_x = start_x + col_idx * step
            c_y = start_y + weekday * step
            count = day["contributionCount"]
            date_str = day["date"]
            fill = get_fill_color(count, max_count)
            delay = f"{col_idx * 0.016 + weekday * 0.04:.3f}s"
            plural = "contribution" if count == 1 else "contributions"
            rect = f'<rect class="c-cell" style="animation-delay:{delay}" x="{c_x:.2f}" y="{c_y:.2f}" width="{cell_size:.2f}" height="{cell_size:.2f}" rx="{rx}" fill="{fill}"><title>{date_str}: {count} {plural}</title></rect>'
            cells_xml.append(rect)

    month_xml = "\n".join([f'<text x="{x:.2f}" y="45" fill="{YORU_CYAN}" font-size="10" font-weight="600">{m}</text>' for x, m in month_labels])
    all_cells_str = "\n".join(cells_xml)

    total_c = stats["total_contributions"]
    start_date = stats["start_date_str"]
    end_date = stats["end_date_str"]
    curr_streak = stats["current_streak"]
    longest_streak = stats["longest_streak"]
    best_count = stats["best_day_count"]
    best_date = stats["best_day_date"]

    # Clean terminal header without Apple traffic light buttons
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
<style>
@keyframes cell-anim {{ 0% {{ opacity: 0.3; transform: translateY(-4px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
.c-cell {{ opacity: 1; animation: cell-anim 0.38s cubic-bezier(.2,.8,.2,1) both; }}
</style>

<!-- Terminal Window Background (Yoru Theme #0c0e0f) -->
<rect width="{width}" height="{height}" rx="10" fill="{YORU_BG}"/>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="none" stroke="{YORU_BORDER}" stroke-width="1"/>

<!-- Header Bar -->
<path d="M 0.5 10.5 A 10 10 0 0 1 10.5 0.5 L {width - 10.5} 0.5 A 10 10 0 0 1 {width - 0.5} 10.5 L {width - 0.5} 32 L 0.5 32 Z" fill="{YORU_BAR}"/>
<line x1="0" y1="32" x2="{width}" y2="32" stroke="{YORU_BORDER}" stroke-width="1"/>

<!-- Clean Linux Terminal Prompt Header (No Apple Buttons) -->
<text x="24" y="20" font-size="12" font-weight="600">
  <tspan fill="{YORU_RED}">nabilfgrza</tspan><tspan fill="{YORU_MUTED}">@</tspan><tspan fill="{YORU_YELLOW}">thundra-os</tspan><tspan fill="{YORU_CYAN}">: </tspan><tspan fill="{YORU_GREEN}">~/contributions</tspan><tspan fill="{YORU_FG}"> --graph</tspan>
</text>

<!-- Month Labels -->
{month_xml}

<!-- Weekday Labels -->
<text x="32" y="70" fill="{YORU_MUTED}" font-size="9" font-weight="600">Mon</text>
<text x="32" y="94" fill="{YORU_MUTED}" font-size="9" font-weight="600">Wed</text>
<text x="32" y="118" fill="{YORU_MUTED}" font-size="9" font-weight="600">Fri</text>

<!-- Contribution Cells -->
{all_cells_str}

<!-- Legend -->
<text x="618" y="149" fill="{YORU_MUTED}" font-size="10" text-anchor="end">Less</text>
<rect x="624" y="141" width="9.5" height="9.5" rx="2.2" fill="{YORU_HEATMAP[0]}"/>
<rect x="636" y="141" width="9.5" height="9.5" rx="2.2" fill="{YORU_HEATMAP[1]}"/>
<rect x="648" y="141" width="9.5" height="9.5" rx="2.2" fill="{YORU_HEATMAP[2]}"/>
<rect x="660" y="141" width="9.5" height="9.5" rx="2.2" fill="{YORU_HEATMAP[3]}"/>
<rect x="672" y="141" width="9.5" height="9.5" rx="2.2" fill="{YORU_HEATMAP[4]}"/>
<rect x="684" y="141" width="9.5" height="9.5" rx="2.2" fill="{YORU_HEATMAP[5]}"/>
<text x="726" y="149" fill="{YORU_MUTED}" font-size="10" text-anchor="end">More</text>

<!-- Divider Line -->
<line x1="16" y1="165" x2="{width - 16}" y2="165" stroke="{YORU_DIVIDER}" stroke-width="1"/>

<!-- Summary Bottom Row 1 -->
<text x="24" y="189" font-size="13"><tspan fill="{YORU_GREEN}" font-weight="700">{total_c}</tspan><tspan fill="{YORU_MUTED}"> contributions in the last year</tspan></text>
<text x="{width - 24}" y="189" font-size="12" fill="{YORU_CYAN}" text-anchor="end">{start_date} &#8594; {end_date}</text>

<!-- Summary Bottom Row 2 -->
<text x="24" y="213" font-size="13" fill="{YORU_MUTED}">current streak <tspan fill="{YORU_YELLOW}" font-weight="700">{curr_streak} days</tspan><tspan fill="{YORU_MUTED}">   &#183;   longest </tspan><tspan fill="{YORU_YELLOW}" font-weight="700">{longest_streak} days</tspan></text>
<text x="{width - 24}" y="213" font-size="12" fill="{YORU_MUTED}" text-anchor="end">best day <tspan fill="{YORU_YELLOW}" font-weight="700">{best_count}</tspan> on {best_date}</text>
</svg>"""
    return svg

def generate_and_save_all(username="Xskyis", token=None):
    """Fetch data, compute stats, and save both contrib_graph.png and contributions.svg."""
    print(f"INFO: Fetching contribution calendar for {username}...")
    cal = fetch_contribution_data(username=username, token=token)
    stats = compute_stats(cal)

    # 1. Render PNG strip for gifos terminal
    render_contribution_strip(stats, output_path="assets/contrib_graph.png")

    # 2. Render clean SVG (no Apple buttons)
    svg_content = generate_svg_content(username, stats)
    os.makedirs("assets", exist_ok=True)
    with open("assets/contributions.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("INFO: Successfully saved assets/contributions.svg (pure Linux terminal style, no Apple buttons)!")

    return stats

# Compatibility helper
def generate_and_save_svg(username="Xskyis", token=None, output_path="assets/contributions.svg"):
    return generate_and_save_all(username=username, token=token)

if __name__ == "__main__":
    generate_and_save_all()
