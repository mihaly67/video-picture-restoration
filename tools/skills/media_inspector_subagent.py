# Autonomous Subagent Skill: Media & Metadata Inspector
# Egy olyan eszköz az Agentnek, ami helyettesít egy MCP szervert (pl. ffprobe wrapper).
# Meg tudja vizsgálni a feldolgozandó videók / képek paramétereit (FPS, Codec, Felbontás)
# még a restaurációs pipeline indítása előtt (Memory Watchdog előtt kötelező lépés).

import argparse
import subprocess
import os

def inspect_media(filepath: str):
    print(f"🎬 [Media Inspector] Fájl vizsgálata: {filepath}")
    if not os.path.exists(filepath):
        print(f"❌ [Media Inspector] A fájl nem létezik: {filepath}")
        return

    # Mivel egy konténerben vagyunk, megpróbáljuk használni a fájlparancsot vagy az ffprobe-t, ha van
    try:
        # Alap Linux "file" parancs a kiterjesztés megállapítására
        result_file = subprocess.run(["file", filepath], capture_output=True, text=True, timeout=5)
        print(f"🔍 [Alap Info]: {result_file.stdout.strip()}")

        # Ha van ffprobe (Videókhoz)
        result_ffprobe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=width,height,r_frame_rate,codec_name", "-of", "default=noprint_wrappers=1", filepath],
            capture_output=True, text=True, timeout=10
        )
        if result_ffprobe.returncode == 0 and result_ffprobe.stdout.strip():
            print("\n🎞️ [Video/Kép Paraméterek]:")
            print(result_ffprobe.stdout.strip())
        else:
             print("⚠️ [Media Inspector] Az FFprobe nem elérhető vagy nem adott vissza videó adatot.")

    except Exception as e:
        print(f"❌ [Media Inspector] Rendszerhiba a lekérdezés során: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Media Inspector Subagent (MCP Emulator)")
    parser.add_argument("--file", required=True, help="A vizsgálandó kép vagy videó elérési útja")
    args = parser.parse_args()

    inspect_media(args.file)
