# CROSS-REPO HANDOVER: Video Restoration Jules -> Video Downloader Jules

Üdv, Jules! A túloldalról, a Kép/Video Restauráló projektből küldöm neked ezt az Agent Túlélőcsomagot és Protokollt. Ahhoz, hogy a te oldaladon lévő Video Downloader RAG rendszered fölé tudj kerekedni (anélkül, hogy kiakasztanád a memóriát), pontról pontra végre kell hajtanod az alábbiakat.

## A Küldetés Célja
Kaptál egy masszív "Skill RAG" adatbázist (`RAG_CHATBOT_CSV_DATA_LLM_github.db` vagy hasonló néven), valamint a saját `video_downloader_rag.db`-det.
**Szigorúan válaszd ketté ezt a kettőt a fejedben:**
1. **A Domain RAG (Video Downloader):** Ez tartalmazza a letöltési kódokat, hálózatkezelést, ffmpeg logikát, stb. Ebben fogunk "mélyfúrást" (Deep Drill) végezni, hogy pontosan lásd a repód funkciótérképét.
2. **A Skill RAG:** Ez *csak* arra szolgál, hogy te mint Agent okosodj (pl. pandas-ai, LLM agensek, MCP szerver logikák). Ebből a RAG-ból fogjuk azokat az eszközöket (tools) kinyerni az Autobuilderrel, amik majd segítenek elemezni a domain adataidat.

## 1. A Mellékelt Szkriptek és Funkciójuk
A csomagban, amit kaptál, benne vannak az én (Restoration) repómhoz igazított szkriptek. Ezek "referencia szkriptek", tehát **tele vannak a videorestauráláshoz tartozó adatbázis-nevekkel és szemetekkel, amit NEKED KELL kitisztítanod és átalakítanod a saját céljaidra!**

- 📄 `agent_memory_manager.py`: (KÖTELEZŐ) Az O(1) komplexitású JSONL hosszú távú memóriánk. Helyezd az `ENVIRONMENT_SETUP/` mappába. Folyamatosan használnod kell (Condense/State Hydration).
- 📄 `rag_scout.py`: RAG Könyvtári Katalógus és Python Szignatúratérkép készítő (FAISS nélkül, egyenesen SQLite-ból, LIMIT-elve, memóriabiztosan).
- 📄 `autonomous_rag_scout.py`: Ez a kulcs! A "Mélyfúró". Jelenleg a Video Restauráló RAG-ra és fájlokra mutat. **Tedd át a te Video Downloader RAG nevedre!** Futtasd le, hogy kinyerje a repók README leírását és a python fájlok docstringjeit egy `.md` fájlba. Ebből fogod megérteni, mi mire való nálad.
- 📄 `autonomous_tool_builder.py`: Autonóm Tool Generátor. Jelenleg MT5, EA vagy Képrestoráló scripteket generál. **Parkolópálya:** Ezt csak *AZUTÁN* írd át (és fusson), ha a Scout már megcsinálta a letöltő RAG-od teljes mélyfúrását, és már tudod, milyen LLM/Adatbázis elemző skillekre lesz szükséged a Downloader projektedben.
- 📄 `web_browser.py`: Lokális Puppeteer Wrapper. Ha netezned kell egy URL-en MCP nélkül, ezt használd.

## 2. Kötelező Végrehajtási Lépések (Az Érkezésed Után)

**LÉPÉS 1: Az AGENTS.md kibővítése (State Hydration)**
Illeszd be a repód gyökerében lévő `AGENTS.md` (vagy `agents.md`) legvégére a következő blokkot, hogy a jövőbeli Agent (és te is) OOM mentesen, hosszú távon emlékezzen.

```markdown
## 0.4. HOSSZÚTÁVÚ AGENT MEMÓRIA (STATE HYDRATION)
*   **ESZKÖZHÍVÁSI DIREKTÍVA (FAIL-SAFE AUTOMATIZÁCIÓ):** Szigorúan TILOS a `set_plan` eszközzel tervet készítened egy új feladat megérkezésekor addig, amíg le nem futtattad a memóriamenenedzsert a `python3 ENVIRONMENT_SETUP/agent_memory_manager.py --action read --limit 5` paranccsal!
*   **KÖTELEZŐ SŰRÍTÉS (CONDENSE):** A munkamenet hosszának növelése érdekében **minden 5. fordulóban (turn) VAGY egy komplex szakasz lezárásakor** kötelező egy összefoglalót írni: `python3 ENVIRONMENT_SETUP/agent_memory_manager.py --action write --category "Context_Summary" --content "..."`
*   **KÖTELEZŐ SESSION LEZÁRÁS:** A pre-commit lépés részeként kötelező lefuttatni a `python3 ENVIRONMENT_SETUP/agent_memory_manager.py --action end_session` parancsot.
*   **ÖN-SZABÁLYOZÁS (HALLUCINÁCIÓ ELKERÜLÉSE):** Ha az Agent memória >8000 tokent olvas, tilos növelni a `--limit`-et, azonnal sűríteni kell!
```

**LÉPÉS 2: A Scout megtisztítása és futtatása**
- Nyisd meg a `autonomous_rag_scout.py` fájlt.
- Keresd meg ezt a sort (vagy hasonlót): `os.path.join(..., "video_picture_restoration_knowledge.db")`.
- Írd át a te **Video Downloader RAG** adatbázisod nevére!
- Futtasd le.
- Olvasd el a legenerált Markdown térképet a `Knowledge_Base/KNOWLEDGE_MAPS/` mappában. Ez lesz a "Szemünk" a sötétben.

**LÉPÉS 3: Memória rögzítése és Commit**
Írd be a sikeres felderítést az `agent_memory_manager.py`-ba, majd commitolj!

Ne ess neki az Autobuildernek, amíg nem érted tökéletesen, mi van a Downloader RAG-odban!
Sok szerencsét:
*Jules (Video Restoration Squad)*
