# Hardver-Szintű Optimalizációk (AM3 / 16GB RAM)

A `CAPABILITIES.md` és `PIPELINE.md` dokumentumokban leírt képrestorációs folyamatok a hagyományos architektúrákon (NVIDIA GPU + 32GB+ RAM) gyorsan lefutnak. Azonban az AMD Phenom II processzor (AVX utasításkészlet hiánya) és a 16 GB RAM miatt **mély, futtatókörnyezet-szintű trükköket** kell alkalmaznunk a stabilitás és a lefagyások elkerülése érdekében.

A kibővített RAG adatbázisunk (ONNX, FastAPI, Starlette, VapourSynth) elemzése alapján az alábbi mechanizmusokat fogjuk implementálni az `src/core/` és `src/utils/` mappákba:

## 1. ONNX Runtime CPU Szálkezelés (Threading)
PyTorch futtatása helyett az összes ML modellt (Real-ESRGAN, CodeFormer) `.onnx` formátumba kell konvertálnunk. Az ONNX Runtime indításakor explicit módon korlátoznunk kell a szálakat:
- **`intra_op_num_threads`**: Az egyetlen csomóponton (node) belüli párhuzamosítást szabályozza. Phenom II (4 mag) esetén ezt nem érdemes 4 fölé vinni. Olyan értéket kell beállítani, ami hagy levegőt a rendszer többi részének (pl. `intra_op_num_threads = 2` vagy `3`).
- **`inter_op_num_threads`**: Hány csomópont fusson egyszerre. Szintén szigorúan korlátozni kell.
- **Execution Provider**: Kizárólag a `CPUExecutionProvider` vagy az (esetlegesen optimalizált) `OpenVINOExecutionProvider` használata az AVX-alapú crashek megelőzésére.

## 2. Aszinkron Feladat- és Kapacitáskezelés (FastAPI / Starlette)
Ha a UI (Gradio) közvetlenül hívná meg az ML modellt, a felület teljesen lefagyna, a rendszer pedig OOM (Out Of Memory) hibával leállna, amint a felhasználó két képet tölt fel egyszerre.
A RAG adatbázis `fastapi/concurrency.py` és `curio` repóiból átemelt minták alapján:
- **Capacity Limiter (AnyIO / Starlette):** A feldolgozó szálakat egy szigorú (pl. limit=1) korláton (limiteren) keresztül engedjük csak futni a `run_in_threadpool` segítségével. Ez biztosítja, hogy egyszerre fizikailag is csak 1 kép (vagy csempe) legyen a memóriában feldolgozás alatt.
- **Universal Queue / Task Queue:** A képek nem kerülnek be azonnal a memóriába; egy aszinkron, lemezen várakozó (disk-backed) vagy korlátozott memóriájú LIFO/FIFO sorba (Queue) kerülnek, ahonnan a feldolgozó motor csak akkor vesz ki újat, ha az előző lefutott és a `MemoryWatchdog` is "Zöld" jelzést adott.

## 3. VapourSynth MLRT (Kizárólag Videókhoz)
A fotók esetében a standard Python + OpenCV Tiling logika kiváló, de videóknál az I/O (másodpercenként 24-60 db 4K képkocka) azonnal megölné a Python memóriakezelőjét.
A `vs-mlrt` (Machine Learning Runtime for VapourSynth) plugin:
- Lehetővé teszi, hogy az ONNX modelleket egyenesen a VapourSynth C++ (native) pipeline-jába fűzzük be.
- **Memória-cserélés nélküli (Zero-copy) feldolgozás:** A képkockák nyers adatai nem lépnek be a Python memóriatérbe, hanem lent a backendben maradnak. Ezzel a 16 GB RAM videórestauráláshoz is elég lehet, ha a chunk/batch méret minimális.

## Összegzés a Kódoláshoz
A fejlesztés során az ML modelleket "Sötét Dobozként" kell kezelnünk, amiket egy aszinkron **Queue Manager** etet apró darabokkal (Tiling), szigorú **Thread Limit**ek mellett, miközben a **MemoryWatchdog** folyamatosan figyeli a psutil-lal a memóriafogyasztást, és szükség esetén kikényszeríti a `gc.collect()` futását.
