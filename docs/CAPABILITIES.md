# RAG Integrált Képességek

A felmérések alapján a Rendszer az alábbi külső modulokat és technológiákat képes integrálni és vezérelni:

## AI Modellek és Technikák
- **FaceFusion**: Csúcsminőségű arccsere (Face Swap) referenciaképek alapján. Beépített Frame Enhancer és Face Enhancer (GFPGAN/CodeFormer).
- **LivePortrait**: Állóképek élethű animálása mozgásvideókkal vagy póz-sablonokkal. Retargeting control.
- **GFPGAN / CodeFormer**: Vak archarmonizáció és feljavítás.
- **VRT / RVRT**: Időbeli konzisztenciával rendelkező videó zajmentesítés.
- **ProPainter / E2FGVI**: Intelligens tartalomkitöltés és eltüntetés (Inpainting) videókhoz.
- **DeOldify / DDColor**: Automatikus, villódzásmentes színezés.
- **SwinIR / HAT / Real-ESRGAN**: Szuperfelbontás mesterséges textúrázás nélkül.
- **MiDaS / Segment Anything (SAM)**: Mélység- és maszkfelismerés a nem "beautification" (hamisító) környezettartó beavatkozásokhoz.

## Rendszer és Keretrendszer (Framework)
- **FastAPI**: Aszinkron task menedzsment a háttérben futó nehéz ONNX inferenciák köré.
- **VapourSynth**: A videó keretek zéró-kópiás transzformációs motorja, amely az MLRT kiterjesztéssel Python interfészen keresztül hajtja végre az optimalizált feladatokat.
- **Gradio / NiceGUI**: Különböző komplexitású WebUI interakciók biztosítása (egyszerű gombnyomásostól a "Node-based" workflow szerkesztésig).
- **Tiling Engine & RAM Watchdog**: Az alacsony hardver (16GB RAM) megóvása a feldarabolt képszámításokkal és explicit szemétgyűjtéssel.
