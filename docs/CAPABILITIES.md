# AI RAG Adatbázis Képességtérkép

A `rag_interrogator.py` futtatása során feltérképeztük a csatolt RAG (Retrieval-Augmented Generation) adatbázis tartalmát. A repók (pl. mmcv, DepictQA, VapourSynth, CodeFormer) széleskörű beépített és algoritmikus megoldásokat kínálnak a klasszikus és gépi tanulásos képmódosításhoz.

Ezek a funkciók egyaránt alkalmazhatók adat-előkészítésként (augmentation) és a végső kimenet utófeldolgozásaként (post-processing).

## 1. Alacsony szintű / Alapvető képmanipulációk
A rendszer jelentősen támaszkodik a nyílt forráskódú számítógépes látás könyvtárakra (pl. OpenCV, MMCV `photometric` és `geometric` modulok).

- **Színterek és Csatornák kezelése (RGB / HSV / HLS / YCbCr):**
  A repók tartalmaznak direkt csatorna transzformációkat és szeparációt. Képesek vagyunk egy képet HSV térbe konvertálni, majd izoláltan csak a Value (Fényesség) vagy Hue (Színezet) csatornát módosítani, ezután visszaalakítani RGB-be.
- **Kontraszt és Fényesség (Brightness / Contrast):**
  - OpenCV szintű matematikai eltolások (shift) a pixelek értékein.
  - Automatikus kontraszt növelés (Auto-contrast).
  - Hisztogram kiegyenlítés és CLAHE (Contrast Limited Adaptive Histogram Equalization) a sötét/világos területek (árnyékok és fénypontok) kiegyensúlyozására.
- **Vágás és Átméretezés (Cropping / Scaling):**
  - Fix és relatív vágás (Crop / CropAbs a VapourSynthből).
  - Skálázó algoritmusok (`imrescale`, `imresize_like` az MMCV-ből).
  - Patch-alapú feldolgozás (a memórialimit miatt kritikus `paired_random_crop` és `mod_crop` funkciók, pl. a CodeFormerből).

## 2. Középszintű transzformációk (Színek és Fények)
- **Fehéregyensúly és Színkorrekció:**
  Bár dedikált "Photoshop-szintű" fehéregyensúly gomb nincs beépítve a modellekbe, a meglévő "adjust_color", "adjust_lighting" (MMCV) modulok segítségével RGB egyensúlyozás könnyen elérhető algoritmikusan.
- **Gamma Korrekció és Fekete/Fehér pontok:**
  - A DepictQA repó tartalmaz explicit `brightness_brighten_gamma_HSV/RGB` implementációkat.
  - A gamma eltolásával módosítható a "mid-tone" kontraszt és szabályozhatók a sötét (árnyék) pontok kimosódása.
- **Árnyalat és Szaturáció (Hue / Saturation):**
  Az MMCV `adjust_hue` és az HSV csatornás matematikai szorzások (augmentation részeként) teljes kontrollt adnak a színtelítettség felett.
- **Speciális effektusok:**
  - Vignetta hozzáadása/eltávolítása (`brightness_vignette`).
  - Posterization és Solarization.

## 3. Magas szintű / AI Alapú funkciók (Restauráció)
- **Zajmentesítés (Denoising) és Szuperfelbontás (Upscaling):**
  Real-ESRGAN, BasicSR, HAT modellek állnak rendelkezésre.
- **Maszkolás és Inpainting (Behelyettesítés):**
  - VapourSynth `MaskedMerge` (Alpha blending / pre-multiplied alpha). Ezzel megoldható a kép specifikus rétegeinek (pl. csak a háttér, vagy csak a hibás részek) módosítása és újraintegrálása az eredeti képre.

## Összegzés a Fejlesztéshez
Nem kell "Photoshopot" újraírnunk. A 16GB RAM limitünkön belül is biztonságosan használhatjuk a már rendelkezésre álló **MMCV** és **OpenCV** algoritmusokat (amelyek az `opencv-python-headless` csomagunk részei). A GUI-ban létre tudunk hozni csúszkákat a kontrasztra, gamma-korrekcióra, HSV-re, amelyek a RAG-ban talált optimalizált, CPU-n is rendkívül gyors matematikai funkciókat hívják meg a képcsempéken (tiles), mielőtt vagy miután azokat átengedjük az AI modellen.
