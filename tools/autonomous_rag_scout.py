import os
import sqlite3
import re
import sys

# Hozzáférés az Agent Memória Menedzserhez
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ENVIRONMENT_SETUP.agent_memory_manager import write_memory

def run_autonomous_scout():
    """
    A Skill RAG (RAG_CHATBOT_CSV_DATA_LLM_github.db) mélyfúrása.
    Felderíti a repositorykat (pl. pandas-ai, LLaMA-agents), kigyűjti
    a fő README leírásokat, valamint a python fájlok docstringjeit.
    """
    print("🤖 AUTONÓM FELDERÍTŐ INDÍTÁSA (Deep Drill a Skill RAG-on)...")

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Knowledge_Base", "RAG_DB", "RAG_CHATBOT_CSV_DATA_LLM_github.db")

    if not os.path.exists(db_path):
        print(f"❌ Adatbázis nem található: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT source_repo, filepath, file_type, content FROM rag_data ORDER BY source_repo, filepath")
        rows = cursor.fetchall()
    except Exception as e:
        print(f"Hiba az SQL lekérdezésben: {e}")
        conn.close()
        return

    print(f"📂 {len(rows)} fájldarab kinyerve az adatbázisból feldolgozásra.")

    repo_insights = {}

    for repo, filepath, file_type, content in rows:
        if not content: continue

        if repo not in repo_insights:
            repo_insights[repo] = {"description": "Nincs elérhető README összegzés.", "files": {}}

        if filepath not in repo_insights[repo]["files"]:
            repo_insights[repo]["files"][filepath] = ""

        # 1. Repo szintű leírás kinyerése (README.md)
        if filepath.endswith("README.md") and file_type.lower() == "documentation":
            match = re.search(r"#(.*?)(?:\n\n|\Z)", content, re.DOTALL)
            if match:
                desc = match.group(0).strip().replace('\n', ' ')
                if len(desc) < 50:
                    lines = content.split('\n')
                    desc = " ".join([l.strip() for l in lines[:10] if l.strip() and not l.startswith('[')])

                repo_insights[repo]["description"] = desc[:500] + ("..." if len(desc) > 500 else "")

        # 2. Fájl szintű docstring
        if filepath.endswith(".py"):
            doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if doc_match:
                file_desc = doc_match.group(1).strip().replace('\n', ' ')
                repo_insights[repo]["files"][filepath] = file_desc[:200] + ("..." if len(file_desc) > 200 else "")

    conn.close()

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Knowledge_Base", "KNOWLEDGE_MAPS")
    os.makedirs(out_dir, exist_ok=True)
    report_file = os.path.join(out_dir, "skill_rag_deep_drill.md")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 🔬 AUTONÓM MÉLYFÚRÁS (Skill RAG Deep Drill Report)\n")
        f.write("Adatbázis: RAG_CHATBOT_CSV_DATA_LLM_github.db\n")
        f.write("Ezek azok a fejlett AI Agent, Adatbázis elemző és MCP eszközök, amiket a videomunka automatizálására/támogatására használhatunk.\n\n")

        for repo in sorted(repo_insights.keys()):
            f.write(f"## 📦 REPO: {repo}\n")
            f.write(f"**Funkció / Leírás:** {repo_insights[repo]['description']}\n\n")
            f.write("**Kritikus Fájlok és Szerepük:**\n")

            file_count = 0
            for filepath in sorted(repo_insights[repo]["files"].keys()):
                desc = repo_insights[repo]["files"][filepath]
                if desc:
                    f.write(f"  - 📄 `{filepath}`: *{desc}*\n")
                    file_count += 1
                elif "agent" in filepath or "model" in filepath or "bot" in filepath or "server" in filepath:
                     f.write(f"  - 📄 `{filepath}`: (Fő feldolgozó / LLM modul)\n")
                     file_count += 1

            if file_count == 0:
                f.write("  - *(Nincs specifikus dokumentált Python script, vizsgáld kézzel az iterrogatorral)*\n")

            f.write("\n" + "-"*40 + "\n\n")

    print(f"\n✅ Autonóm Felderítés befejezve. A teljes térkép a KNOWLEDGE_MAPS mappában: {report_file}")

    write_memory("Auto_Scout_Report", f"A Skill RAG (RAG_CHATBOT_CSV_DATA_LLM_github.db) mélyfúrása lefutott. {len(repo_insights)} repository-t elemeztem ki, a teljes jelentés a KNOWLEDGE_MAPS/skill_rag_deep_drill.md fájlban van.")

if __name__ == "__main__":
    run_autonomous_scout()
