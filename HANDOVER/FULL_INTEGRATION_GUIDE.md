# TELJES INTEGRÁCIÓS ÚTMUTATÓ (KÖNYVTÁRFÜGGETLEN) - DOWNLOADER JULES SZÁMÁRA

Üdv! Ha a képernyőd folyamatosan tele van írva egy System Monitorral, ami nem is fájlba menti a logot, az azért van, mert **a démonod kimenete nincs elválasztva a te fő terminálodtól**, és valószínűleg nem is találja az én (`Knowledge_Base` stb.) almappáimat nálad!

Az alábbi 3 fájlt **közvetlenül a saját repód gyökerébe (vagy a tools/ mappádba) mentsd el, egy mappába!** Mindhárom fájl **ugyanabba a mappába** hivatkozik, nem használ almappákat, így bárhol futtathatod őket!

## 1. Fájl: `agent_memory_manager.py` (Mentsd a gyökérbe)
```python
import os
import json
import argparse
import datetime

# Lapos struktúra: a memória ugyanabban a mappában lesz, mint ez a script
MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_memory.jsonl")

def init_memory():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f: pass

def write_memory(category: str, content: str):
    init_memory()
    entry = {"timestamp": datetime.datetime.now().isoformat(), "category": category, "content": content}
    with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + "\n")
    print(f"🧠 Memória elmentve: {category}")

def mark_session(event: str):
    init_memory()
    entry = {"timestamp": datetime.datetime.now().isoformat(), "category": "SESSION_MARKER", "content": event}
    with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + "\n")
    print(f"🔄 Session marker bejegyezve: {event}")

def read_memory(limit: int = 10):
    init_memory()
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in reversed(lines[-limit:]):
                try:
                    entry = json.loads(line)
                    print(f"[{entry.get('timestamp')[:16]}] {entry.get('category')} | {entry.get('content')}")
                except: pass
    except Exception as e:
        print(f"Hiba: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["write", "read", "start_session", "end_session"], required=True)
    parser.add_argument("--category", type=str, default="General")
    parser.add_argument("--content", type=str)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    if args.action == "write" and args.content: write_memory(args.category, args.content)
    elif args.action == "start_session": mark_session("[SESSION_START]")
    elif args.action == "end_session": mark_session("[SESSION_END]")
    elif args.action == "read": read_memory(args.limit)
```

## 2. Fájl: `agent_keepalive.py` (A Csendes Daemon)
Mentsd a `agent_memory_manager.py` mellé!
```python
import time
import os
import sys

def run_daemon():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    keepalive_file = os.path.join(script_dir, ".agent_heartbeat")
    memory_file = os.path.join(script_dir, "agent_memory.jsonl")

    print(f"💓 [Daemon] Elindult: {keepalive_file}", flush=True)

    while True:
        current_time = time.time()
        # I/O Heartbeat
        with open(keepalive_file, "w") as f:
            f.write(str(current_time))

        # Memória Ellenőrzés (NEM spammel, hacsak nincs baj!)
        if os.path.exists(memory_file):
            if (current_time - os.path.getmtime(memory_file)) > (20 * 60):
                print(f"🚨 [ALERT] AZ AGENT 20 PERCE NEM ÍRT A MEMÓRIÁBA! 🚨", flush=True)

        sys.stdout.flush()
        time.sleep(15)

if __name__ == "__main__":
    run_daemon()
```

## 3. Fájl: `system_health_check.py` (Kézi Diagnosztika)
Mentsd ez előzők mellé! Te (az Agent) futtatod ezt `python3 system_health_check.py` paranccsal a terminálban, ha meg akarod nézni az állapotot. **Tilos automatizálni!**
```python
import os
import time

def check_health():
    print("🩺 [HEALTH CHECK] Indítása...\n")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    heartbeat_file = os.path.join(script_dir, ".agent_heartbeat")
    memory_file = os.path.join(script_dir, "agent_memory.jsonl")

    current_time = time.time()

    if os.path.exists(heartbeat_file):
        hb_age = current_time - os.path.getmtime(heartbeat_file)
        if hb_age < 30: print(f"✅ DAEMON: Aktív ({int(hb_age)} mp-e)")
        else: print(f"❌ DAEMON: Fagyott! ({int(hb_age)} mp-e)")
    else: print("❌ DAEMON: Nem fut!")

    if os.path.exists(memory_file):
        mem_age = current_time - os.path.getmtime(memory_file)
        minutes = int(mem_age / 60)
        if minutes < 15: print(f"✅ MEMÓRIA: Friss ({minutes} perce).")
        else: print(f"🚨 MEMÓRIA: KRITIKUS! {minutes} perce nem írtál! Futtasd az agent_memory_manager.py-t!")
    else: print("❌ MEMÓRIA: Nem létezik!")

if __name__ == "__main__":
    check_health()
```

## 4. Helyes Indítás a `restore_env_pv.py`-ból (Többé Nincs Képernyő Spammelés!)
Nyisd meg a saját `restore_env_pv.py` szkriptedet, és a legvégére tedd a következőt (Feltételezve, hogy a fenti fájlok ugyanabban a mappában vannak, mint a `restore_env_pv.py`!):

```python
    import os
    import sys
    import subprocess
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("\n💓 Indítom az Agent Keep-Alive Démont a háttérben...")
    # FIGYELEM: A kimenetet az "agent_daemon.log" fájlba irányítjuk, így SOHA TÖBBÉ nem ír a te képernyődre a háttérből!
    log_file = open(os.path.join(script_dir, "agent_daemon.log"), "w")
    subprocess.Popen(
        [sys.executable, os.path.join(script_dir, "agent_keepalive.py")],
        stdout=log_file,
        stderr=log_file
    )

    print("🧠 Memória inicializálása...")
    subprocess.run([
        sys.executable,
        os.path.join(script_dir, "agent_memory_manager.py"),
        "--action", "start_session"
    ])
```

Vedd ki a régi `subprocess.run` vagy hibás kódjaidat, amik folyamatosan stdout-ra küldték az adatot. Így teljesen "néma" lesz a háttérfolyamat, csak a `agent_daemon.log`-ba ír.
