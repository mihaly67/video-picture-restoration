import faiss
import sqlite3
import numpy as np
import os
import sys
import argparse
import warnings
from sentence_transformers import SentenceTransformer

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def main():
    parser = argparse.ArgumentParser(description="AI PICTURE & VIDEO RESTORATION - RAG Query Deep Drill Edition")
    parser.add_argument("--query", type=str, required=True, help="A koncepcionális kérdés (pl. 'How to upsample video frames')")
    parser.add_argument("--repo", type=str, default="", help="Szűrés forrás repóra (pl. 'BasicSR-master')")
    parser.add_argument("--lang", type=str, default="", help="Szűrés programnyelvre (pl. 'Python', 'C++', 'Vue')")
    parser.add_argument("--type", type=str, default="", help="Szűrés fájltípusra (pl. 'Code', 'Documentation')")
    parser.add_argument("--filepath", type=str, default="", help="Szűrés adott fájlnévre vagy útvonalra")
    parser.add_argument("--limit", type=int, default=5, help="Hány találatot adjon vissza")
    parser.add_argument("--neighborhood", type=int, default=0, help="Hány előző és következő blokkot fűzzön hozzá a találathoz (pl. 2)")
    parser.add_argument("--expand_file", action="store_true", help="KASZKÁD FÚRÁS: Újraépíti az egész fájlt, amelyben a találat szerepel")
    args = parser.parse_args()

    work_dir = os.path.dirname(get_script_dir())

    db_paths = [
        ("Knowledge_Base/RAG_DB", "video_picture_restoration_compressed.index", "video_picture_restoration_knowledge.db"),
        ("Knowledge_Base/RAG_DB", "video_picture_restoration_compressed.index", "video_picture_restoration.db"),
    ]

    index_path = None
    sqlite_path = None

    for rel_dir, idx_file, db_file in db_paths:
        full_dir = os.path.join(work_dir, rel_dir)
        if os.path.exists(os.path.join(full_dir, idx_file)) and os.path.exists(os.path.join(full_dir, db_file)):
            index_path = os.path.join(full_dir, idx_file)
            sqlite_path = os.path.join(full_dir, db_file)
            break

    if not index_path or not sqlite_path:
        print(f"❌ Error: Nem találtam érvényes RAG adatbázist a szokásos mappákban.")
        print("💡 Próbáld meg lefuttatni a 'python3 tools/restore_env_pv.py' scriptet!")
        sys.exit(1)

    model_name = "all-MiniLM-L6-v2"
    print(f"🧠 Modell betöltése ({model_name})...")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = SentenceTransformer(model_name)

    print(f"📂 FAISS Index: {index_path}")
    index = faiss.read_index(index_path)

    print(f"🔌 SQLite DB: {sqlite_path}")
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    print(f"🎯 Query kódolása: '{args.query}'")
    query_vector = model.encode([args.query]).astype('float32')

    k_search = max(1000, args.limit * 50) # Nagyobb merítés kell a sok metadata szűrés miatt
    print(f"🔍 Vektoros keresés top {k_search} jelöltre...")
    distances, indices = index.search(query_vector, k_search)

    results = []

    # Dinamikus SQL felépítése a szűrőkhöz
    sql_base = "SELECT id, source_repo, filepath, language, file_type, content FROM rag_data WHERE id=?"
    sql_params = []

    if args.repo:
        sql_base += " AND source_repo LIKE ?"
        sql_params.append(f"%{args.repo}%")
    if args.lang:
        sql_base += " AND language LIKE ?"
        sql_params.append(f"%{args.lang}%")
    if args.type:
        sql_base += " AND file_type LIKE ?"
        sql_params.append(f"%{args.type}%")
    if args.filepath:
        sql_base += " AND filepath LIKE ?"
        sql_params.append(f"%{args.filepath}%")

    for i in range(k_search):
        idx = int(indices[0][i])
        dist = distances[0][i]

        if idx == -1: continue

        cursor.execute(sql_base, [idx] + sql_params)
        row = cursor.fetchone()

        if row:
            db_id, source_repo, filepath, language, file_type, content = row

            if args.expand_file and any(r['filepath'] == filepath and r['repo'] == source_repo for r in results):
                continue

            results.append({
                "id": db_id,
                "distance": dist,
                "repo": source_repo,
                "filepath": filepath,
                "language": language,
                "type": file_type,
                "content": content
            })
            if len(results) >= args.limit:
                break

    print("\n" + "═"*80)
    print("🎯 RAG INTEL REPORT - DEEP DRILL EDITION 🎯")
    print("═"*80 + "\n")

    if not results:
        print("⚠️ Nem találtam egyezést a megadott vektoros és metaadat szűrőkkel.")
    else:
        for i, res in enumerate(results):
            print(f"[{i+1}] 📄 FÁJL: {res['filepath']}")
            print(f"    📦 REPO: {res['repo']} | 🔤 NYELV: {res['language']} | 📋 TÍPUS: {res['type']}")
            print(f"    📏 TÁVOLSÁG: {res['distance']:.4f} | 🔑 CÉL-ROWID: {res['id']}")
            print("-" * 80)

            # ---------------------------------------------------------
            # 1. KASZKÁD / EXPAND_FILE MÓD (A teljes fájl visszaállítása)
            # ---------------------------------------------------------
            if args.expand_file and res['filepath'] != 'Unknown':
                print(f"🔄 KASZKÁD FÚRÁS AKTÍV: A teljes '{res['filepath']}' fájl rekonstruálása...")
                cursor.execute("SELECT content FROM rag_data WHERE filepath = ? AND source_repo = ? ORDER BY id ASC",
                               (res['filepath'], res['repo']))

                all_chunks = cursor.fetchall()

                if all_chunks:
                    print(f"   ✓ {len(all_chunks)} adatbázis blokk összefűzve.\n")
                    print("⬇️ --- [REKONSTRUÁLT FÁJL KEZDETE] --- ⬇️\n")

                    full_text = ""
                    for chunk in all_chunks:
                        full_text += chunk[0] + "\n...[CHUNK_BOUNDARY]...\n"

                    print(full_text)
                    print("⬆️ --- [REKONSTRUÁLT FÁJL VÉGE] --- ⬆️\n")
                else:
                    print("⚠️ Hiba a fájl rekonstruálása közben.")

            # ---------------------------------------------------------
            # 2. SZOMSZÉDSÁG / NEIGHBORHOOD MÓD (Kibővített kontextus)
            # ---------------------------------------------------------
            elif args.neighborhood > 0:
                print(f"🔍 SZOMSZÉDSÁG AKTÍV (±{args.neighborhood} blokk)")

                # Előző blokkok lekérdezése
                cursor.execute("SELECT id, content FROM rag_data WHERE id >= ? AND id < ? ORDER BY id ASC",
                               (res['id'] - args.neighborhood, res['id']))
                prev_rows = cursor.fetchall()

                for pr_id, pr_content in prev_rows:
                    print(f"--- [ELŐZŐ KONTEXTUS (ROWID: {pr_id})] ---")
                    print(pr_content + "\n")

                print(f"--- [🎯 CÉL KONTEXTUS (ROWID: {res['id']})] ---")
                print(res['content'] + "\n")

                # Következő blokkok lekérdezése
                cursor.execute("SELECT id, content FROM rag_data WHERE id > ? AND id <= ? ORDER BY id ASC",
                               (res['id'], res['id'] + args.neighborhood))
                next_rows = cursor.fetchall()

                for nx_id, nx_content in next_rows:
                    print(f"--- [KÖVETKEZŐ KONTEXTUS (ROWID: {nx_id})] ---")
                    print(nx_content + "\n")

            # ---------------------------------------------------------
            # 3. NORMÁL MÓD (Csak a cél chunk)
            # ---------------------------------------------------------
            else:
                print("--- [CÉL KONTEXTUS] ---")
                print(res['content'] + "\n")
                print("💡 Tipp: Használd a '--neighborhood 2' vagy '--expand_file' kapcsolókat a teljesebb képért!")

            print("═"*80 + "\n")

    conn.close()

if __name__ == "__main__":
    main()
