import os
import glob
import re
from datetime import datetime
from PIL import Image

# 1. Load .env BEFORE importing gifos so GITHUB_TOKEN is available at import time
from dotenv import load_dotenv
load_dotenv()

import gifos
from gifos.utils.load_config import gifos_settings

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
    print("INFO: Initializing gifos terminal...")
    t = gifos.Terminal(
        width=750,
        height=500,
        xpad=15,
        ypad=15,
        font_file=FONT_FILE_BITMAP,
        font_size=15,
    )

    year_now = datetime.now().strftime("%Y")

    # Fetch dynamic GitHub stats for Xskyis
    github_username = "Xskyis"
    rating = "A+"
    stars = "0"
    commits = "342"
    prs = "7 (Merged: 100%)"
    contribs = "1"
    top_langs = "Jupyter, JS, CSS, HTML"

    token = os.getenv("GITHUB_TOKEN")
    if token and token.strip() and not token.startswith("ghp_your"):
        try:
            print(f"INFO: Fetching live GitHub statistics for {github_username}...")
            # Ensure module-level token is updated
            gifos.utils.fetch_github_stats.GITHUB_TOKEN = token.strip()
            stats = gifos.utils.fetch_github_stats(github_username, include_all_commits=True)
            if stats:
                rating = stats.user_rank.level
                stars = str(stats.total_stargazers)
                commits = str(stats.total_commits_all_time or stats.total_commits_last_year)
                prs = f"{stats.total_pull_requests_made} (Merged: {stats.pull_requests_merge_percentage:.0f}%)"
                contribs = str(stats.total_repo_contributions)
                if stats.languages_sorted:
                    top_langs = ", ".join([l[0] for l in stats.languages_sorted[:4]])
                print("INFO: Live GitHub stats fetched successfully!")
        except Exception as e:
            print(f"WARNING: Could not fetch live GitHub stats: {e}. Using fallback stats.")
    else:
        print("INFO: GITHUB_TOKEN not found in .env. Using fallback stats.")

    # 1. BIOS Boot Screen
    t.gen_text("", 1, count=5)
    t.toggle_show_cursor(False)
    t.gen_text("GIF_OS Modular BIOS v1.0.11", 1)
    t.gen_text(f"Copyright (C) {year_now}, \x1b[31mXskyis Softwares Inc.\x1b[0m", 2)
    t.gen_text("\x1b[94mGitHub Profile ReadMe Terminal, Rev 1011\x1b[0m", 4)
    t.gen_text("Krypton(tm) GIFCPU - 250Hz", 5)
    
    # Fast memory test
    for i in range(0, 65653, 16384):
        t.delete_row(7)
        t.gen_text(f"Memory Test: {i}KB", 7, count=1, contin=True)
    t.delete_row(7)
    t.gen_text("Memory Test: 64KB OK", 7, count=6, contin=True)

    # 2. Login Phase
    t.clear_frame()
    t.toggle_show_cursor(False)
    t.gen_text("\x1b[93mGIF OS v1.0.11 (tty1)\x1b[0m", 1, count=3)
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

\x1b[30;101mGitHub Stats:\x1b[0m
--------------
\x1b[96mUser Rating:         \x1b[92m{rating}\x1b[0m
\x1b[96mTotal Stars Earned:  \x1b[93m{stars}\x1b[0m
\x1b[96mTotal Commits:       \x1b[93m{commits}\x1b[0m
\x1b[96mTotal PRs:           \x1b[93m{prs}\x1b[0m
\x1b[96mTotal Contributions: \x1b[93m{contribs}\x1b[0m
\x1b[96mTop Languages:       \x1b[93m{top_langs}\x1b[0m

\x1b[40m   \x1b[41m   \x1b[42m   \x1b[43m   \x1b[44m   \x1b[45m   \x1b[46m   \x1b[47m   \x1b[0m"""

    # Top Prompt line after running
    t.gen_prompt(1)
    t.gen_text("\x1b[92mfetch.sh\x1b[0m -u nabilfgrza", 1, contin=True)

    # Paste Cat Mascot on the left
    t.paste_image("./assets/cat_clean.png", 3, 2, 0.85)

    # Print user details on the right
    t.gen_text(user_details_lines, 3, 28, count=5, contin=True)

    # 5. Footer Command Prompt
    footer_row = 25
    t.gen_prompt(footer_row)
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[92m# Thanks for visiting! :D\x1b[0m", footer_row, contin=True)
    
    # Hold the final screen for 45 frames (~3 seconds)
    t.clone_frame(45)

    # 6. Generate GIF
    try:
        t.gen_gif()
    except Exception as e:
        print(f"Notice: ffmpeg generation raised: {e}")
    
    if not os.path.exists("output.gif") or os.path.getsize("output.gif") == 0:
        fallback_gen_gif(fps=15, output_name="output.gif")

    # 7. Write minimalist README.md (pure x0rzavi gifos style)
    readme_content = f"""<div align="center">
<picture>
    <source media="(prefers-color-scheme: dark)" srcset="./output.gif">
    <source media="(prefers-color-scheme: light)" srcset="./output.gif">
    <img alt="GIFOS" src="output.gif" width="750">
</picture>

<br />
<sub><i>Generated automatically using <a href="https://github.com/x0rzavi/github-readme-terminal">x0rzavi/github-readme-terminal</a></i></sub>
</div>
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("INFO: Updated README.md (clean gifos style)!")

if __name__ == "__main__":
    main()
