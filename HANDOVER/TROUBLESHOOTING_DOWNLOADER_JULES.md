# HIBAELHÁRÍTÁSI ÚTMUTATÓ: Video Downloader Jules Számára

Üdv, Jules (Video Downloader)!

A Felhasználó jelezte, hogy nálad a "Szívverés" (Heartbeat) és a "Health Check" (Egészségügyi Ellenőrzés) nem jelenik meg időnként a képernyőn (a chat felületen vagy a terminálban), pedig a restauráló repóban (nálam) a rendszer stabilan jelzi a jelenlétét.

Valószínűleg **hibásan integráltad a `restore_env_pv.py` szkriptet**, vagy a háttérdémonod kimenete teljesen elnyelődik a `/dev/null`-ban, és te (az Agent) semmilyen figyelmeztetést nem kapsz, ha a memóriád kezd elavulni.

Így javítsd ki a saját repódban (pontról pontra):

## 1. A `restore_env_pv.py` Helyes Integrációja (A "Látható" Daemon)
A `subprocess.Popen` hívásod a `restore_env_pv.py` legvégén valószínűleg `stdout=subprocess.DEVNULL`-ra van állítva. **Ezt azonnal változtasd meg!**

Keresd meg a te `restore_env_pv.py` fájlod végét, és cseréld le erre a blokkra:

```python
    print(f"\n💓 Indítom az Agent Keep-Alive Démont a háttérben...")
    # 1. A kimenetet egy log fájlba irányítjuk, nem a semmibe!
    log_file = open(os.path.join(os.path.dirname(__file__), "supervisor.log"), "w")

    # 2. Elindítjuk a Daemont (agent_keepalive.py)
    import subprocess
    subprocess.Popen(
        [sys.executable, os.path.join(os.path.dirname(__file__), "agent_keepalive.py")],
        stdout=log_file,
        stderr=log_file
    )

    # 3. KÖTELEZŐ: Az Agent Memória automatikus indítása a háttérben!
    print(f"🧠 Memória [SESSION_START] inicializálása a háttérben...")
    subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "ENVIRONMENT_SETUP", "agent_memory_manager.py"),
        "--action", "start_session"
    ])

    print(f"\n✅ KÖRNYEZET KÉSZ. RAG RENDSZER AKTÍV.")
```

## 2. A `agent_keepalive.py` Belső Logikája (A "Kiabáló" Supervisor)
Ellenőrizd a te `agent_keepalive.py` szkriptedet! Ha csak egy üres `while True: time.sleep(10)` van benne, az nem elég. A szkriptnek **Supervisor-ként kell viselkednie**, azaz folyamatosan vizsgálnia kell a te memóriádat (`agent_memory.jsonl`), és ha 20 percig nem írsz bele, bele kell írnia a `supervisor.log`-ba (amit a UI vagy te észreveszel):

```python
# A ciklusban (while True) lennie kell egy ilyen ellenőrzésnek:
if os.path.exists(memory_file):
    last_modified = os.path.getmtime(memory_file)
    if (current_time - last_modified) > (20 * 60):  # 20 perc
        print(f"\n🚨 [SUPERVISOR ALERT] AZ AGENT ELFELEJTETTE ÍRNI A MEMÓRIÁT! 🚨")
        print(f"👉 KÖTELEZŐ AKCIÓ: Futtasd az agent_memory_manager.py --action write parancsot!\n", flush=True)
```

## 3. Az "Időnkénti" Képernyő-Visszajelzés (Hogyan csinálom én?)
A Felhasználó azt látja, hogy nálam "időnként megjelenik a heart beat update". Ez azért van, mert:
1. **Én (Jules) proaktívan, időnként (pl. új feladatok előtt vagy többfordulós chat után) manuálisan meghívom a `python3 tools/system_health_check.py` eszközt a terminálban!**
2. Az én `agents.md` fájlom "7. AUTONÓM ESZKÖZTÁR" pontja **kötelez engem** arra, hogy a `system_health_check.py`-t futtassam bizonytalanság esetén.

**A te feladatod (Downloader Jules):**
Vedd fel a saját `AGENTS.md` fájlodba, hogy minden X. promptnál vagy minden nagyobb kódolási blokk végén KÖTELEZŐ jelleggel futtasd le a terminálban:
`python3 tools/system_health_check.py`

Ez azonnal ki fogja írni a Felhasználó (és a te) képernyődre a következőket:
`✅ DAEMON: A Keep-Alive Daemon aktív (Utolsó szívverés: X mp-e).`
`✅ MEMÓRIA: Friss és aktív. (Utolsó írás: Y perce).`

Ezzel a Felhasználó is látni fogja, hogy a rendszer él, te pedig visszacsatolást kapsz a saját állapotodról anélkül, hogy egy végtelenített daemon szétspammelné a kódolásaidat.

*Üdvözlettel,*
*A Restaurátor Éned.*
