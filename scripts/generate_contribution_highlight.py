import os
import urllib.request
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Yoru / THUNDRA_OS Terminal Palette (Aligned with gifos yoru theme)
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

# Yoru-themed heatmap levels (seamless dark forest to emerald green)
YORU_HEATMAP = [
    "#202325",  # 0 contributions (Subtle visible dark slate cell)
    "#1e3e2e",  # Level 1 (1-2)
    "#2d6347",  # Level 2 (3-5)
    "#448e65",  # Level 3 (6-8)
    "#78b892",  # Level 4 (9-11)
    "#81c19b",  # Level 5 (12+)
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
            "total_contributions": 166,
            "weeks": [],
            "days": [],
            "current_streak": 1,
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

def generate_svg_content(username, stats):
    """Generate SVG markup for the Contribution Highlight terminal window widget in Yoru theme."""
    weeks = stats.get("weeks", [])
    max_count = stats.get("best_day_count", 1)

    width = 750
    height = 240
    start_x = 76.0
    start_y = 52.0
    cell_size = 9.8
    step = 12.0
    rx = 2.5

    # Month labels calculation - skip very short initial partial month so it matches reference
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

    # Cells generation
    cells_xml = []
    for col_idx, week in enumerate(weeks):
        for day in week["contributionDays"]:
            weekday = day["weekday"]  # 0=Sunday, 1=Monday, ..., 6=Saturday
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

<!-- Window Controls (Yoru Red, Yellow, Green) -->
<circle cx="22" cy="16" r="5" fill="{YORU_RED}"/>
<circle cx="38" cy="16" r="5" fill="{YORU_YELLOW}"/>
<circle cx="54" cy="16" r="5" fill="{YORU_GREEN}"/>

<!-- Terminal Title Prompt matching THUNDRA_OS -->
<text x="{width / 2:.0f}" y="20" font-size="12" font-weight="600" text-anchor="middle">
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

def generate_and_save_svg(username="Xskyis", token=None, output_path="assets/contributions.svg"):
    """Fetch data, compute stats, and save the SVG card in Yoru theme."""
    print(f"INFO: Fetching contribution calendar for {username}...")
    cal = fetch_contribution_data(username=username, token=token)
    stats = compute_stats(cal)
    svg_content = generate_svg_content(username, stats)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"INFO: Successfully generated {output_path} ({os.path.getsize(output_path)} bytes) in Yoru theme!")
    return stats

if __name__ == "__main__":
    generate_and_save_svg()
