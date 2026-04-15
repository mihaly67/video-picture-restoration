import sqlite3
import os
import sys

def get_db_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_paths = [
        os.path.join(base_dir, "Knowledge_Base/RAG_DB/video_picture_restoration_knowledge.db"),
        os.path.join(base_dir, "Knowledge_Base/RAG_DB/video_picture_restoration.db")
    ]
    for path in db_paths:
        if os.path.exists(path):
            return path
    return None

def main():
    db_path = get_db_path()
    if not db_path:
        print("❌ RAG adatbázis nem található.")
        sys.exit(1)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo_list_path = os.path.join(base_dir, "RAG_building/repo_list.txt")
    output_path = os.path.join(base_dir, "docs/REPO_OVERVIEW.md")

    if not os.path.exists(repo_list_path):
        print(f"❌ A {repo_list_path} fájl nem található.")
        sys.exit(1)

    with open(repo_list_path, 'r', encoding='utf-8') as f:
        repos = [line.strip() for line in f if line.strip()]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    overview_content = "# RAG Repository Overview\n\nEz a dokumentum a RAG adatbázisban tárolt repozitóriumok rövid funkcionális leírását tartalmazza a README fájlok alapján.\n\n"

    for repo in repos:
        # Próbáljuk meg kinyerni a README-k bevezető részét. A README-k általában a filepath-ban a repo gyökerében vannak, mint 'repo_name/README.md' vagy csak 'README.md' ha a source_repo a mappa neve.
        # Mivel a RAG feldolgozta őket chunkokra, próbáljuk megtalálni az első chunkot a README.md-ből.
        cursor.execute("SELECT content FROM rag_data WHERE source_repo = ? AND filepath LIKE '%README.md' ORDER BY id ASC LIMIT 2", (repo,))
        rows = cursor.fetchall()

        overview_content += f"## {repo}\n"

        if rows:
            # Csak a szöveges részt próbáljuk megtartani, de egyszerűbb, ha csak az első kb. 500-1000 karaktert vesszük, ahol a leírás szokott lenni.
            combined_content = "\n".join([row[0] for row in rows])

            # Kicsit megtisztítjuk a badge-ektől ha lehetséges, vagy egyszerűen csak bevesszük az első 600 karaktert.
            # Egy okosabb megoldás, ha a "# " vagy "## " címsorok utáni első pár mondatot vesszük ki.
            lines = combined_content.split('\n')
            description_lines = []
            char_count = 0
            for line in lines:
                if line.startswith('[!') or line.startswith('![') or line.startswith('<'):
                    continue # Kép vagy HTML valószínűleg
                if line.strip() == "":
                    continue
                description_lines.append(line.strip())
                char_count += len(line)
                if char_count > 400 and len(description_lines) > 2:
                    break

            summary = " ".join(description_lines)
            if len(summary) > 800:
                 summary = summary[:797] + "..."
            overview_content += f"{summary}\n\n"
        else:
            # Ha nincs README.md, megpróbálunk bármilyen kódot/fájlt találni, csak hogy jelezzük
            cursor.execute("SELECT file_type, count(id) FROM rag_data WHERE source_repo = ? GROUP BY file_type", (repo,))
            stats = cursor.fetchall()
            if stats:
                stat_str = ", ".join([f"{s[1]} {s[0]} blokk" for s in stats])
                overview_content += f"*(Nincs README.md)* Tartalom: {stat_str}\n\n"
            else:
                overview_content += "*Nincs adat a repóról a RAG adatbázisban.*\n\n"

    conn.close()

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(overview_content)

    print(f"✅ Sikeresen legenerálva: {output_path}")

if __name__ == "__main__":
    main()
