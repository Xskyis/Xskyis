import os
import urllib.request
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# GitAscii / Dracula-Yoru Contribution Heatmap Palette
PALETTE = [
    "#161b22",  # 0 contributions (Dark slate outline)
    "#1f2937",  # Level 1 (Subtle dark blue/gray)
    "#3b82f6",  # Level 2 (Vibrant blue)
    "#60a5fa",  # Level 3 (Medium light blue)
    "#93c5fd",  # Level 4 (Soft light blue)
    "#c084fc",  # Level 5 (Purple / lavender highlight)
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
            headers={"Authorization": f"Bearer {token.strip()}", "User-Agent": "GitAscii-Heatmap-Generator"}
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
        # Realistic fallback values based on Xskyis profile
        return {
            "total_contributions": 164,
            "weeks": [],
            "days": [],
            "current_streak": 0,
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
    # If today has 0 contributions, streak is evaluated starting from yesterday
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
        return PALETTE[0]
    if max_count <= 0:
        return PALETTE[1]
    ratio = count / max_count
    if ratio <= 0.18:
        return PALETTE[1]
    elif ratio <= 0.38:
        return PALETTE[2]
    elif ratio <= 0.60:
        return PALETTE[3]
    elif ratio <= 0.82:
        return PALETTE[4]
    else:
        return PALETTE[5]

def generate_svg_content(username, stats):
    """Generate SVG markup for the Contribution Highlight terminal window widget."""
    weeks = stats.get("weeks", [])
    max_count = stats.get("best_day_count", 1)

    width = 704
    height = 240
    start_x = 52.0
    start_y = 50.0
    cell_size = 9.545454545454545
    step = 11.93181818181818
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
            # Skip if it is at the very beginning with < 3 weeks duration
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
            delay = f"{col_idx * 0.018 + weekday * 0.045:.3f}s"
            plural = "contribution" if count == 1 else "contributions"
            rect = f'<rect class="c-cell" style="animation-delay:{delay}" x="{c_x:.2f}" y="{c_y:.2f}" width="{cell_size:.2f}" height="{cell_size:.2f}" rx="{rx}" fill="{fill}"><title>{date_str}: {count} {plural}</title></rect>'
            cells_xml.append(rect)

    month_xml = "\n".join([f'<text x="{x:.2f}" y="44" fill="#7d8590" font-size="10">{m}</text>' for x, m in month_labels])
    all_cells_str = "\n".join(cells_xml)

    total_c = stats["total_contributions"]
    start_date = stats["start_date_str"]
    end_date = stats["end_date_str"]
    curr_streak = stats["current_streak"]
    longest_streak = stats["longest_streak"]
    best_count = stats["best_day_count"]
    best_date = stats["best_day_date"]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
<style>
@keyframes cell-anim {{ 0% {{ opacity: 0; transform: translateY(-6px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
.c-cell {{ opacity: 0; animation: cell-anim 0.42s cubic-bezier(.2,.8,.2,1) both; }}
</style>
<defs>
<linearGradient id="heatmap-bg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#0d1420"/>
  <stop offset="1" stop-color="#0d1117"/>
</linearGradient>
</defs>
<rect width="{width}" height="{height}" rx="12" fill="url(#heatmap-bg)"/>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="#30363d" stroke-width="1" stroke-opacity="0.55"/>
<line x1="0" y1="30" x2="{width}" y2="30" stroke="#30363d" stroke-opacity="0.35"/>
<circle cx="22" cy="15" r="5" fill="#ff5f56"/>
<circle cx="38" cy="15" r="5" fill="#ffbd2e"/>
<circle cx="54" cy="15" r="5" fill="#27c93f"/>
<text x="{width / 2:.0f}" y="19" fill="#7d8590" font-size="12" text-anchor="middle">{username}@github: ~/contributions --graph</text>
{month_xml}
<text x="22" y="69.4" fill="#7d8590" font-size="9">Mon</text>
<text x="22" y="93.2" fill="#7d8590" font-size="9">Wed</text>
<text x="22" y="117.1" fill="#7d8590" font-size="9">Fri</text>
{all_cells_str}
<text x="572.8" y="147.2" fill="#7d8590" font-size="10" text-anchor="end">Less</text>
<rect x="578.8" y="139.5" width="9.5" height="9.5" rx="2.2" fill="{PALETTE[0]}"/>
<rect x="590.7" y="139.5" width="9.5" height="9.5" rx="2.2" fill="{PALETTE[1]}"/>
<rect x="602.7" y="139.5" width="9.5" height="9.5" rx="2.2" fill="{PALETTE[2]}"/>
<rect x="614.6" y="139.5" width="9.5" height="9.5" rx="2.2" fill="{PALETTE[3]}"/>
<rect x="626.5" y="139.5" width="9.5" height="9.5" rx="2.2" fill="{PALETTE[4]}"/>
<rect x="638.5" y="139.5" width="9.5" height="9.5" rx="2.2" fill="{PALETTE[5]}"/>
<text x="682" y="147.2" fill="#7d8590" font-size="10" text-anchor="end">More</text>
<line x1="0" y1="163" x2="{width}" y2="163" stroke="#30363d" stroke-opacity="0.25"/>
<text x="22" y="187.1" font-size="13" fill="#39d353"><tspan font-weight="700">{total_c}</tspan><tspan fill="#7d8590"> contributions in the last year</tspan></text>
<text x="682" y="187.1" font-size="12" fill="#7d8590" text-anchor="end">{start_date} &#8594; {end_date}</text>
<text x="22" y="211.1" font-size="13" fill="#7d8590">current streak <tspan fill="#ffa657" font-weight="700">{curr_streak} days</tspan><tspan fill="#7d8590">   &#183;   longest </tspan><tspan fill="#ffa657" font-weight="700">{longest_streak} days</tspan></text>
<text x="682" y="211.1" font-size="12" fill="#7d8590" text-anchor="end">best day <tspan fill="#f2cc60" font-weight="700">{best_count}</tspan> on {best_date}</text>
</svg>"""
    return svg

def generate_and_save_svg(username="Xskyis", token=None, output_path="assets/contributions.svg"):
    """Fetch data, compute stats, and save the SVG card."""
    print(f"INFO: Fetching contribution calendar for {username}...")
    cal = fetch_contribution_data(username=username, token=token)
    stats = compute_stats(cal)
    svg_content = generate_svg_content(username, stats)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"INFO: Successfully generated {output_path} ({os.path.getsize(output_path)} bytes)!")
    return stats

if __name__ == "__main__":
    generate_and_save_svg()
