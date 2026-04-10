# Képfeldolgozó Rendszer Architektúra (AM3 / Phenom II Optimalizált)

Ez a dokumentum a kép- és videó-restaurációs alkalmazás felépítését és a lépésenkénti fejlesztési ütemtervét rögzíti, figyelembe véve a hardveres korlátokat (AVX utasításkészlet hiánya, 16 GB RAM limit, CPU melegedés).

## Rendszerarchitektúra

A rendszer három fő rétegből áll:

### 1. Feldolgozó Réteg (AI Engine)
- **Futtatókörnyezet:** `onnxruntime` használata a hagyományos (és AVX-et gyakran megkövetelő) PyTorch helyett. Az ONNX modellek kompatibilisebbek a régebbi SSE utasításkészletekkel.
- **Modellek:** Könnyített ("light") modellek használata (pl. Real-ESRGAN light verziók, YOLOv8-nano).
- **Hardveres megfontolások:** Alapvetően CPU alapú inferencia, elkerülve a memóriaszivárgást és a kompatibilitási hibákat.

### 2. Logikai és Vezérlő Réteg (The "Brain")
- **Batch Manager (Kötegelő):** Az I/O műveleteket generátorfüggvényekkel és feldolgozási sorokkal (queue) kezeli. A multiprocessing helyett a threading (vagy szekvenciális végrehajtás) javasolt, hogy elkerüljük az OS lefagyasztását.
- **Memória-őr (Watchdog):** Aktívan figyeli a szabad RAM-ot. Ha a felhasználás eléri a ~80%-ot (kb. 12.8 GB), kényszerített memóriatisztítást (`gc.collect()`) végez. Ezenkívül a CPU túlmelegedésének elkerülése végett opcionális pihenőidőt (sleep) iktat be a műveletek közé.
- **Tiling Engine:** Nagyobb felbontású képeket feldolgozás előtt kisebb csempékre (tiles) vágja, a darabokat egyesével küldi be az AI Engine-nek, majd összefűzi a végeredményt. Ezzel elkerülhető a RAM túltöltése.

### 3. GUI Réteg (Felhasználói Felület)
- **Keretrendszer:** Web-alapú felhasználói felület (`Gradio` vagy hasonló technológia), amely lehetővé teszi a könnyű hozzáférést a helyi és a távoli VPS környezetből is.
- **Funkciók:**
  - Fájl és mappa kiválasztása.
  - Vizuális csővezeték (pipeline) összeállító.
  - Valós idejű erőforrás-monitorozás (RAM/CPU kijelzés).
  - "Low-resource" (Alacsony erőforrású) mód: Kép-előnézetek generálásának letiltása futás közben a memória megtakarítása érdekében.

n### Képfeldolgozási Csővezeték (Pipeline)
A részletes, történelmi korszakokra bontott (I-II. világháborús fekete-fehér, 70-es évekbeli analóg színes, és korai digitális) képfeldolgozási és restaurációs lépéseket a [PIPELINE.md](PIPELINE.md) dokumentum tartalmazza.

---

## Fejlesztési Lépések (Roadmap)

A fejlesztés során az "elefántot kisebb falatokban esszük meg":

- **Fázis 1: Alap Infastruktúra és Biztonság (Jelenlegi fázis)**
  - Projekt architektúra rögzítése, mappastruktúra véglegesítése.
  - Alapvető csomagkövetelmények (`requirements.txt`) meghatározása.
  - A *Memória-őr (Watchdog)* modul implementálása, amely az alkalmazás legalsó, védelmi szintje lesz.

- **Fázis 2: Menedzsment és Adatáramlás**
  - A *Batch Manager* implementálása generátorokkal a biztonságos, OOM (Out-of-Memory) nélküli I/O eléréshez.
  - A *Tiling Engine* logikájának (darabolás és összefűzés) megírása, még valós AI modellek nélkül (képmanipulációk tesztelése OpenCV-vel).

- **Fázis 3: AI Engine Integráció**
  - Az első "light" ONNX modellek integrálása.
  - Zajszűrő és Inpainting (behelyettesítő) csővezetékek kialakítása, amelyek már a Tiling Engine-t és a Watchdog-ot használják.

- **Fázis 4: GUI Kifejlesztése**
  - A `Gradio` felület elkészítése.
  - A végpontok összekötése a Batch Managerrel.
  - Erőforrás-monitor beépítése a webes felületre.
