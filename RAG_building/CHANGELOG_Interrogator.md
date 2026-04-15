# RAG Interrogator - Changelog

## Deep Drill Edition (A referencia szkript alapján)

### Hozzáadott funkciók és változtatások a `rag_interrogator.py` fájlban:
- **Kaszkád fúrás (`--expand_file`)**: Képes egy találatot adó fájl teljes tartalmát adatbázis blokkról blokkra (`id` sorrendben) rekonstruálni, ezzel vizuálisan összefűzve az egész fájlt. Automatikusan deduplikálja az azonos fájlra mutató találatokat a limit túllépése elkerülése végett.
- **Kiterjesztett szomszédság vizsgálat (`--neighborhood N`)**: Az eddigi boolean érték helyett most egy `int` alapú változó, ami megadja, hogy egy pontos találat köré mekkora keretet fűzzön hozzá a kontextus érdekében (pl. `N=2` esetén két előző és két rákövetkező blokkot is kinyer az SQLite-ból).
- **Fájl elérési út szűrés (`--filepath`)**: Egy új paraméterrel kiegészült a szkript, amely lehetővé teszi, hogy adott mappára, fájlra vagy kiterjesztésre szűkítsük a RAG-ban történő vektoros keresést.
- **Dinamikus Adatbázis Keresés**: A szkript immáron rugalmasabban kezeli az SQLite adatbázis neveket. Támogatja mind a `video_picture_restoration.db` mind a `video_picture_restoration_knowledge.db` elnevezést a `Knowledge_Base/RAG_DB` mappán belül, igazodva az új rendszer környezetéhez.
- **Dinamikus SQL szűrők**: A kategória (`--category`) helyett - mivel az új RAG adatbázis sémája más metaadatokat is tartalmaz -, a lekérdezés dinamikusan a programnyelv (`language`) és fájltípus (`file_type`) értékekre van felépítve.
