import requests
import questionary
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz
from pathlib import Path
import subprocess, os, re, sys
from githubupdater import github_updater

def resource_path(filename):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, "resources", "windows", filename)

# Example usage:
animepahe_cli = resource_path("animepahe-cli-beta.exe")
ffmpeg_exe = resource_path("ffmpeg.exe")

os.system(f"\"{animepahe_cli}\" --upgrade")
try:
    from version import VERSION
    print(f"[Updater] Current version: {VERSION}")
    github_updater("zhiftyDK/animepahe-gui", VERSION)
except ImportError:
    pass  # VERSION not found, skip update check
except Exception as e:
    print(f"[Updater] Update check failed: {e}")

os.system('cls' if os.name == 'nt' else 'clear')

cookies = {
    '__ddg9_': '80.208.100.192',
    '__ddgid_': 'ABmiCUaATsAIHTTF',
    '__ddgmark_': 'iBUkxSbHEnjoYNsY',
    '__ddg2_': 'umr2NNwRpWsO9pDi',
    '__ddg1_': 'SmguJNFGE0AajRM0ymy8',
    'ddg_last_challenge': '1766357252660',
    'latest': '6374',
    'res': '1080',
    'aud': 'jpn',
    'av1': '0',
    'ann-fakesite': '0',
}

response = requests.get('https://animepahe.si/anime', cookies=cookies)

# Parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Find the div with class "tab-content"
tab_content_div = soup.find("div", class_="tab-content")

# Extract all a tags
a_tags = tab_content_div.find_all("a")

# Save link and text in a list of dictionaries
links_data = [{"href": a['href'], "text": a.text} for a in a_tags]

texts = [entry["text"] for entry in links_data]

# Function to perform fuzzy search and return top N matches
def fuzzy_search(query, choices, top_n=5):
    results = process.extract(query, choices, scorer=fuzz.WRatio, limit=top_n)
    # results is a list of tuples: (match_text, score, index)
    top_matches = []
    for match_text, score, idx in results:
        top_matches.append({
            "text": match_text,
            "href": links_data[idx]["href"],
            "score": score
        })
    return top_matches

try:
    query = input("🔍 Enter search query: ")
    matches = fuzzy_search(query, texts, top_n=5)

    animes = [f"{m['text']}" for m in matches]
except KeyboardInterrupt:
    print("\nSearch cancelled...")
    exit(0)

selected_anime = questionary.select(
    "Select anime",
    choices=animes
).ask()

languages = ["jp", "zh", "en"]
selected_languages = questionary.checkbox(
    "Select language",
    choices=languages
).ask()

if "jp" in selected_languages and len(selected_languages) > 1:
    merge_audio = questionary.confirm("Merge audio tracks into single .mkv file?").ask()

if not selected_anime or not selected_languages:
    print("No anime or language selected. Exiting...")
    exit(0)

def remove_ansi_codes(s):
    return re.sub(r'\x1b\[[0-9;]*m', '', s)

def rename_episode(prev_name, current_episode):
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in filenames:
            if prev_name in filename:
                old_path = os.path.join(dirpath, filename)
                new_path = os.path.join(dirpath, f"Episode {current_episode}.mp4")
                os.rename(old_path, new_path)

def download_anime(selected_anime, language, command, rename_episodes=True):
    prev_name = None
    current_episode = 1
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    try:
        for line in process.stdout:
            if "Episodes:" in line:
                print(f"Downloading {selected_anime}, Language: {language}, {int(line.split(': ')[1].strip())} episodes found.")
            if "Downloading" in line:
                if prev_name:
                    if(rename_episodes):
                        rename_episode(prev_name, current_episode)
                    current_episode += 1
                prev_name = remove_ansi_codes(line.split("Downloading : ")[1].strip())
                print(f"\r{line.strip():<120}")
            if "%" in line:
                print(line.strip(), end="\r")
        if(rename_episodes):
            rename_episode(prev_name, current_episode)
        print(f"\r{'Download completed!':<120}\n", end="")
    except KeyboardInterrupt:
        print("\nInterrupted! Terminating subprocess...")
    finally:
        process.terminate()
        process.wait()

EP_REGEX = re.compile(r"_-_([0-9]{2})_")
DUB_LANG_REGEX = re.compile(r"_([A-Za-z]{2,})_Dub")

LANG_MAP = {
    "Eng": "eng",
    "English": "eng",
    "Jap": "jpn",
    "Jpn": "jpn",
    "Ger": "deu",
    "German": "deu",
    "Spa": "spa",
    "Spanish": "spa",
    "Fra": "fra",
    "French": "fra",
    "Ita": "ita",
    "Italian": "ita",
    "Por": "por",
    "Portuguese": "por",
    "Rus": "rus",
    "Russian": "rus",
    "Zho": "zho",
    "Chinese": "zho",
}

def detect_dub_language(filename: str) -> tuple[str, str]:
    """
    Returns (iso639_code, human_readable_name)
    """
    match = DUB_LANG_REGEX.search(filename)
    if not match:
        return ("und", "Dub")

    raw = match.group(1)
    iso = LANG_MAP.get(raw, raw.lower())
    return (iso, raw)

def merge_folder(folder_path: str):
    folder = Path(folder_path)

    jp_files = {}
    dub_files = {}

    for file in folder.iterdir():
        if not file.is_file() or file.suffix.lower() != ".mp4":
            continue

        ep_match = EP_REGEX.search(file.name)
        if not ep_match:
            continue

        ep = int(ep_match.group(1))

        if "_Dub" in file.name:
            dub_files[ep] = file
        else:
            jp_files[ep] = file

    episodes = sorted(jp_files.keys() & dub_files.keys())
    if not episodes:
        raise RuntimeError("No matching JP/Dub episode pairs found")

    print(f"Found {len(episodes)} episode pairs")

    for ep in episodes:
        jp = jp_files[ep]
        dub = dub_files[ep]

        iso_lang, lang_name = detect_dub_language(dub.name)
        output = folder / f"Episode {ep}.mkv"

        print(f"\nMerging Episode {ep}")
        print(f" JP  : {jp.name}")
        print(f" Dub : {dub.name} ({lang_name})")

        cmd = [
            ffmpeg_exe,
            "-i", str(jp),
            "-i", str(dub),
            "-map", "0:v:0",     # Video from JP
            "-map", "0:a:0",     # JP audio
            "-map", "1:a:0",     # Dub audio
            "-c:v", "copy",      # Copy video (no re-encode)
            "-c:a", "copy",      # Copy audio (no re-encode)
            "-metadata:s:a:0", "language=jpn",
            "-metadata:s:a:1", f"language={iso_lang}",
            "-metadata:s:a:0", "title=Japanese",
            "-metadata:s:a:1", f"title={lang_name}",
            "-disposition:a:0", "default",
            str(output)
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f" ✔ Created {output.name}")

            # Delete original files after successful merge
            jp.unlink()
            dub.unlink()
            print(f" ✔ Deleted original files: {jp.name}, {dub.name}")

        except subprocess.CalledProcessError as e:
            print(f" ✖ Failed to merge Episode {ep}: {e}")
            continue

    print("\nAll episodes processed successfully.")

def find_folder(original_title: str, score_threshold: int = 80) -> Path | None:
    """
    Finds the anime folder based on original title using RapidFuzz.
    Base folder is the same folder as this script.
    """
    base_folder = Path(__file__).parent  # Folder where the script is located
    dirs = [f for f in base_folder.iterdir() if f.is_dir()]
    if not dirs:
        return None

    folder_names = [f.name for f in dirs]

    match = process.extractOne(
        query=original_title,
        choices=folder_names,
        scorer=fuzz.token_sort_ratio
    )

    if match and match[1] >= score_threshold:
        return base_folder / match[0]
    return None

if len(selected_languages) > 1:
    link = f"https://animepahe.si{matches[animes.index(selected_anime)]['href']}"
    for lang in selected_languages:
        command = f"{animepahe_cli} -q 0 -a {lang} -l {link}"
        download_anime(selected_anime, lang, command, rename_episodes=False)
    if merge_audio:
        folder = find_folder(selected_anime)
        if folder is None:
            print("Could not find downloaded anime folder for merging.")
        else:
            merge_folder(folder)
else:
    lang = selected_languages[0]
    link = f"https://animepahe.si{matches[animes.index(selected_anime)]['href']}"
    command = f"{animepahe_cli} -q 0 -a {lang} -l {link}"
    download_anime(selected_anime, lang, command)