import os
import glob
import re
import shutil
from datetime import datetime
from PIL import Image

# 1. Load .env BEFORE importing gifos so GITHUB_TOKEN is available at import time
from dotenv import load_dotenv
load_dotenv()

import gifos
from gifos.utils.load_config import gifos_settings
from scripts.generate_contribution_highlight import generate_and_save_svg

# Configure gifos terminal settings
gifos_settings["general"]["user_name"] = "nabilfgrza"
gifos_settings["general"]["color_scheme"] = "yoru"
gifos_settings["general"]["fps"] = 15

FONT_FILE_BITMAP = "./fonts/gohufont-uni-14.pil"

def fallback_gen_gif(fps=15, output_name="output.gif"):
    """Pillow fallback for GIF generation if ffmpeg is not available locally."""
    print("INFO: Assembling frames into GIF via Pillow...")
    frame_files = sorted(
        glob.glob("frames/frame_*.png"),
        key=lambda x: int(re.search(r"frame_(\d+)\.png", x).group(1))
    )
    if not frame_files:
        print("ERROR: No frames found in frames/")
        return
    
    frames = [Image.open(f).convert("P", palette=Image.ADAPTIVE, colors=64) for f in frame_files]
    duration = int(1000 / fps)
    frames[0].save(
        output_name,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=True
    )
    print(f"INFO: Generated {output_name} via Pillow! Size: {os.path.getsize(output_name)} bytes")

def main():
    # Clean previous frames so no stale frames linger
    shutil.rmtree("frames", ignore_errors=True)
    os.makedirs("frames", exist_ok=True)

    print("INFO: Initializing gifos terminal...")
    t = gifos.Terminal(
        width=750,
        height=650,
        xpad=15,
        ypad=15,
        font_file=FONT_FILE_BITMAP,
        font_size=15,
    )
    t.set_prompt(f"\x1b[0;91m{gifos_settings['general']['user_name']}\x1b[0m@\x1b[0;93mthundra-os ~> \x1b[0m")
    year_now = datetime.now().strftime("%Y")

    # Fetch dynamic GitHub stats and contribution highlights for Xskyis
    github_username = "Xskyis"
    token = os.getenv("GITHUB_TOKEN")
    rating = "A+"

    # 1. Fetch live contribution calendar and render both contrib_graph.png and contributions.svg
    try:
        from scripts.generate_contribution_highlight import generate_and_save_all
        contrib_stats = generate_and_save_all(
            username=github_username,
            token=token,
        )
    except Exception as e:
        print(f"WARNING: Could not generate contribution highlight: {e}")
        contrib_stats = {
            "total_contributions": 168,
            "current_streak": 2,
            "longest_streak": 4,
            "best_day_count": 13,
            "best_day_date": "Jun 22, 2026",
            "start_date_short": "Oct 19, 2025",
            "end_date_short": "Oct 24, 2026",
        }

    # 2. Fetch general GitHub stats for user ranking
    if token and token.strip() and not token.startswith("ghp_your"):
        try:
            print(f"INFO: Fetching live GitHub statistics for {github_username}...")
            # Ensure module-level token is updated
            gifos.utils.fetch_github_stats.GITHUB_TOKEN = token.strip()
            stats = gifos.utils.fetch_github_stats(github_username, include_all_commits=True)
            if stats:
                rating = stats.user_rank.level
                print("INFO: Live GitHub stats fetched successfully!")
        except Exception as e:
            print(f"WARNING: Could not fetch live GitHub stats: {e}. Using fallback stats.")
    else:
        print("INFO: GITHUB_TOKEN not found in .env. Using fallback stats.")

    # 1. BIOS Boot Screen
    t.gen_text("", 1, count=5)
    t.toggle_show_cursor(False)
    t.gen_text("THUNDRA_OS Modular BIOS v1.0.11", 1)
    t.gen_text(f"Copyright (C) {year_now}, \x1b[31mXskyis Softwares Inc.\x1b[0m", 2)
    t.gen_text("\x1b[94mGitHub Profile ReadMe Terminal, Rev 1011\x1b[0m", 4)
    t.gen_text("Thundr(tm) TrCPU - 5.6GHz", 5)
    
    # Fast memory test
    for i in range(0, 65653, 16384):
        t.delete_row(7)
        t.gen_text(f"Memory Test: {i}KB", 7, count=1, contin=True)
    t.delete_row(7)
    t.gen_text("Memory Test: 1208394KB OK", 7, count=6, contin=True)

    # 2. Login Phase
    t.clear_frame()
    t.toggle_show_cursor(False)
    t.gen_text("\x1b[93mTHUNDRA_OS v1.0.11 (tty1)\x1b[0m", 1, count=3)
    t.gen_text("login: ", 3, count=2)
    t.toggle_show_cursor(True)
    t.gen_typing_text("nabilfgrza", 3, contin=True)
    t.toggle_show_cursor(False)
    t.gen_text("password: ", 4, count=2)
    t.toggle_show_cursor(True)
    t.gen_typing_text("********", 4, contin=True)
    t.toggle_show_cursor(False)
    t.gen_text("\x1b[92mLast login: " + datetime.now().strftime("%a %b %d") + " on tty1\x1b[0m", 6, count=3)

    # 3. Prompt & Typing fetch.sh
    t.gen_prompt(8, count=3)
    prompt_col = t.curr_col
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[91mfetch.s", 8, contin=True)
    t.delete_row(8, prompt_col)
    t.gen_text("\x1b[92mfetch.sh\x1b[0m", 8, count=2, contin=True)
    t.gen_typing_text(" -u nabilfgrza", 8, contin=True)
    t.clone_frame(4)

    # 4. Fetch Details Display
    t.clear_frame()
    t.toggle_show_cursor(False)

    user_details_lines = f"""\x1b[30;101mnabilfgrza@GitHub\x1b[0m
--------------
\x1b[96mOS:     \x1b[93mCachyOS, Atlas OS\x1b[0m
\x1b[96mHost:   \x1b[93mPoliteknik Negeri Malang (Polinema)\x1b[0m
\x1b[96mKernel: \x1b[93mUndergraduate Informatics Engineering Student\x1b[0m
\x1b[96mUptime: \x1b[93m20 years, 10 months, 7 days\x1b[0m
\x1b[96mIDE:    \x1b[93mVSCode\x1b[0m

\x1b[30;101mContact:\x1b[0m
--------------
\x1b[96mEmail:    \x1b[93mnabilafgareza12@gmail.com\x1b[0m
\x1b[96mLinkedIn: \x1b[93mnabilfgrza\x1b[0m
\x1b[96mGitHub:   \x1b[93mXskyis\x1b[0m

\x1b[40m   \x1b[41m   \x1b[42m   \x1b[43m   \x1b[44m   \x1b[45m   \x1b[46m   \x1b[47m   \x1b[0m"""

    # Top Prompt line after running
    t.gen_prompt(1)
    t.gen_text("\x1b[92mfetch.sh\x1b[0m -u nabilfgrza", 1, contin=True)

    # Paste Cat Mascot on the left
    t.paste_image("./assets/cat_clean.png", 3, 2, 0.85)

    # Print user details on the right
    t.gen_text(user_details_lines, 3, 28, count=3, contin=True)

    # 5. Prompt & Typing contributions --graph
    t.gen_prompt(19, count=2)
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[92mcontributions\x1b[0m --graph", 19, contin=True)
    t.clone_frame(2)
    t.toggle_show_cursor(False)

    # Paste Contribution Heatmap Strip
    t.paste_image("./assets/contrib_graph.png", 20, 1, 1)

    # 6. Footer Command Prompt
    footer_row = 31
    t.gen_prompt(footer_row)
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[92m# Thanks for visiting! :D\x1b[0m", footer_row, contin=True)
    
    # Hold the final screen for 45 frames (~20 seconds)
    t.clone_frame(1200)

    # 7. Generate GIF
    try:
        t.gen_gif()
    except Exception as e:
        print(f"Notice: ffmpeg generation raised: {e}")
    
    if not os.path.exists("output.gif") or os.path.getsize("output.gif") == 0:
        fallback_gen_gif(fps=15, output_name="output.gif")

    # 8. Write single unified README.md
    readme_content = f"""<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./output.gif">
    <source media="(prefers-color-scheme: light)" srcset="./output.gif">
    <img alt="THUNDRA_OS" src="output.gif" width="750">
  </picture>
</div>
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("INFO: Updated README.md (single unified THUNDRA_OS gif)!")

if __name__ == "__main__":
    main()
