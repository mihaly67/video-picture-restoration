# RAG-Alapú AI Restaurációs Rendszer - Architektúra

## 1. Rendszer Áttekintés
A rendszer egy átfogó, aszinkron, RAG-vezérelt restaurációs és animációs keretrendszer, amely képeket és videókat dolgoz fel. Hardveres korlátok (AMD Phenom II, 16 GB RAM) miatt aktív memóriamenedzsmenttel (Watchdogs, Tiling) és ONNX/Zero-copy (VapourSynth) technológiákkal működik.

## 2. Architekturális Rétegek

### 2.1. GUI és Vezérlősík (Control Plane) - `src/gui/`
- **WebUI (Gradio / NiceGUI)**: Grafikus felület a felhasználók számára (kép/videó feltöltés, munkafolyamat kiválasztása, aszinkron folyamat-visszajelzés).
- **FastAPI Backend**: A frontend és a feldolgozó motorok közötti aszinkron API híd, amely a feladatokat ütemezi.
- **RAG Agent Interfész**: A backend a RAG adatbázishoz fordul (`rag_interrogator.py`) az optimális modellparaméterekért (pl. fidelity weight, blending ratio).

### 2.2. Folyamatirányító (Pipelines) - `src/pipelines/`
A folyamatirányító összefűzi a specializált modulokat a felhasználó kérése alapján.
- **Történelmi Restaurációs Pipeline**: MiDaS (mélység) + SAM (maszkolás) + GFPGAN/CodeFormer (Arc) + SwinIR/Real-ESRGAN (Upscale).
- **Arc-Transzplantációs Pipeline**: FaceFusion (arccsere referenciakép alapján) -> CodeFormer (finomítás).
- **Állókép Animációs Pipeline**: LivePortrait (statikus kép animálása vezetővideó vagy póz alapján).

### 2.3. Végrehajtó Motorok (AI Engines) - `src/`
Logikailag és funkcionálisan szétválasztott motorok:
- **`src/image/`**: Statikus képek zajszűrése, inpainting, feljavítása.
- **`src/video/`**: Videók időbeli konzisztenciáját tartó modellek (VRT, ProPainter) és VapourSynth MLRT.
- **`src/face_tools/`**: Arc-specifikus megoldások (FaceFusion swap, LivePortrait animáció, GFPGAN/CodeFormer restaurálás).
- **`src/core/`**: Tiling Engine (képdarabolás a kevés RAM miatt), Async Task Queue.
- **`src/utils/`**: Memory Watchdog, teljesítménymérés, hardware profilozás.

## 3. Adatáramlás (Data Flow)
1. **Bemenet**: Felhasználó képet/videót és referenciaképeket tölt fel a GUI-n.
2. **Kérdezés (RAG)**: A rendszer a kért művelet típusához lekérdezi a RAG adatbázisból a szükséges hyperparamétereket és workflow referenciákat.
3. **Ütemezés**: Az Async Task Queue feldarabolja a feladatot (Tiling Engine, ha szükséges).
4. **Feldolgozás**: A kijelölt Pipeline sorban meghívja a Végrehajtó Motorokat (pl. `face_tools/swap.py` -> `image/upscale.py`).
5. **Kimenet**: A Memory Watchdog folyamatosan tisztítja a szemetet, a végeredményt pedig a GUI visszaküldi a felhasználónak.

## 4. Hardveres Optimalizációk
- ONNX Runtime (`intra_op_num_threads` korlátozva).
- RAM Watchdog (memóriatúlcsordulás megelőzése `gc.collect()`-tel).
- VapourSynth (Zero-copy memory videó transzformációknál).
