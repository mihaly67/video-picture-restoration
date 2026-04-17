# Autonomous Subagent Skill: Restoration Codebase Architect
# Az Ördög Ügyvédje Protokoll alapján: ez a script végigmegy a
# video_picture_restoration_knowledge.db adatbázison, kigyűjti a fontos
# repókat (GFPGAN, BasicSR, CodeFormer, VapourSynth), és
# KIZÁRÓLAG AZ ARCHITEKTURÁLIS VÁZAT (Osztályok, Fő Metódusok, Importok)
# menti le egy JSONL fájlba.
# Így OOM nélkül, tisztán látja a LLM, hogy "hogyan kell megépíteni egy restaurálót".

import sqlite3
import os
import re
import json
import argparse
import sys

def parse_python_architecture(content: str):
    """RegEx alapú, memóriakímélő architektúra kivonó (Parser)."""
    architecture = {
        "imports": [],
        "classes": {},
        "functions": []
    }

    current_class = None

    for line in content.splitlines():
        line = line.strip()

        # 1. Importok (Csak a legfontosabb AI/CV könyvtárak érdekelnek)
        if line.startswith("import ") or line.startswith("from "):
            if any(k in line for k in ["torch", "cv2", "numpy", "vapoursynth", "basicsr", "mmcv"]):
                architecture["imports"].append(line)

        # 2. Osztályok
        class_match = re.match(r"^class\s+([A-Za-z0-9_]+)[\(:]", line)
        if class_match:
            current_class = class_match.group(1)
            architecture["classes"][current_class] = []

        # 3. Osztály metódusai (Kritikusak: __init__, forward)
        if current_class and line.startswith("def "):
            method_match = re.match(r"^def\s+([A-Za-z0-9_]+)\s*(\(.*\))", line)
            if method_match:
                m_name = method_match.group(1)
                m_args = method_match.group(2)
                # Csak az infrastruktúrát építő metódusokat tartjuk meg
                if m_name in ["__init__", "forward", "process", "enhance", "run"]:
                    architecture["classes"][current_class].append(f"{m_name}{m_args}")

        # 4. Globális Főfüggvények
        elif not current_class and line.startswith("def "):
            func_match = re.match(r"^def\s+([A-Za-z0-9_]+)\s*(\(.*\))", line)
            if func_match:
                 architecture["functions"].append(f"{func_match.group(1)}{func_match.group(2)}")

    return architecture

def run_restoration_analysis():
    print("🤖 [Restoration Architect Subagent] Mélyfúrás és Kód Kivonatolás Indítása...")

    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Knowledge_Base", "RAG_DB", "video_picture_restoration_knowledge.db")
    out_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Knowledge_Base", "KNOWLEDGE_MAPS", "restoration_architectures.jsonl")

    if not os.path.exists(db_path):
        print(f"❌ Hiba: Nem találom a RAG adatbázist: {db_path}")
        return

    # Azok a repók, amikből a "kész restaurátorokat" megérthetjük
    target_repos = [
        "BasicSR-master", "CodeFormer-master", "GFPGAN-master",
        "VRT-main", "vs-mlrt-master", "Real-ESRGAN-master"
    ]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    placeholders = ','.join(['?'] * len(target_repos))
    query = f"SELECT source_repo, filepath, content FROM rag_data WHERE source_repo IN ({placeholders}) AND filepath LIKE '%.py'"

    try:
        cursor.execute(query, target_repos)
        rows = cursor.fetchall()
    except Exception as e:
        print(f"Hiba az SQL lekérdezésben: {e}")
        conn.close()
        return

    print(f"📂 {len(rows)} Python forrásfájl feldolgozása a {len(target_repos)} kulcsfontosságú repóból...")

    # Ha volt előző fájl, felülírjuk, hogy ne duzzadjon a végtelenségig
    with open(out_file, "w", encoding="utf-8") as f:
        pass

    extracted_count = 0

    with open(out_file, "a", encoding="utf-8") as f:
        for repo, filepath, content in rows:
            if not content: continue

            # Kinyerjük az architekturális vázat
            arch = parse_python_architecture(content)

            # Csak akkor mentjük, ha találtunk valami érdemlegeset (osztályt vagy AI importot)
            if arch["classes"] or arch["functions"] or arch["imports"]:
                entry = {
                    "repo": repo,
                    "file": filepath,
                    "architecture": arch
                }
                f.write(json.dumps(entry) + "\n")
                extracted_count += 1

    conn.close()
    print(f"✅ [Restoration Architect Subagent] Kész! {extracted_count} fájl Architektúrája (OOM-Safe JSONL formátumban) kimentve ide: {out_file}")

    # Hívjuk meg a Memória Menedzsert, hogy a Fő Agent tudjon róla!
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from ENVIRONMENT_SETUP.agent_memory_manager import write_memory
    write_memory("Subagent_Report", f"A restoration_analyzer_subagent.py kigyűjtötte a {', '.join(target_repos)} architekturális vázát a restoration_architectures.jsonl fájlba. Ebből kell megépítenem a mi restaurátorunkat.")

if __name__ == "__main__":
    run_restoration_analysis()
