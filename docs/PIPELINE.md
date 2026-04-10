# Képfeldolgozási Csővezetékek (Történelmi Korszakok Alapján)

Mivel a cél a dédnagyapák, nagyapák generációjától a korai digitális korszakig terjedő családi archívum megmentése, a képrestorációs folyamatot (Pipeline) nem lehet egyetlen "mágikus" gombbal megoldani. Különböző történelmi korszakok fotói más-más kémiai, fizikai és digitális bomláson mentek keresztül, így eltérő megközelítést igényelnek.

A RAG adatbázisunk és a nyílt forráskódú könyvtáraink (OpenCV, MMCV, ONNX modellek) birtokában az alábbi három specifikus csővezetéket (Pipeline) alakítjuk ki.

---

## 1. Archív Fekete-Fehér Korszak (1910-es – 1960-as évek)
*Ide tartoznak: Az I. és II. világháború képei, valamint a háború utáni hétköznapi, gyakran sérült fekete-fehér fotók.*

**Tipikus hibák:** Szakakadások, karcolások, ezüstösödés (silvering), nagyon alacsony kontraszt, elmosódott (out-of-focus) arcok.

**Feldolgozási Csővezeték:**
1. **Pre-processing (Alapozás):**
   - **Gamma és Feketepont korrekció:** A beszürkült képek feketéinek és fehéreinek helyreállítása (`adjust_gamma`, `auto_contrast`).
   - **CLAHE (Hisztogram kiegyenlítés):** A lokális kontraszt javítása, hogy a sötét egyenruhák és a túlvilágosított egek részletei előjöjjenek.
2. **AI Inferencia (Restaurálás):**
   - **Inpainting (Behelyettesítés):** A karcolások és szakadások automatikus eltüntetése maszkolás segítségével.
   - **Arcrekonstrukció:** A felismerhetetlen arcok fókuszba hozása (CodeFormer / GFPGAN light modellek), ügyelve az *ad-hoc fidelity weight* beállításra, hogy az ősök arca ne váljon "idegenné".
3. **Post-processing (Befejezés):**
   - **Opcionális Kolorizáció:** Ha a cél a kép kiszínezése, a DeOldify-szerű algoritmus hívása a már helyreállított fekete-fehér alapon.

---

## 2. Analóg Színes Korszak (1970-es – 1980-as évek)
*Ide tartoznak: A családi albumok első színes képei.*

**Tipikus hibák:** Drasztikus fakulás, kémiai elszíneződés (sárgás vagy bíbor/magenta köd), színzaj (color noise).

**Feldolgozási Csővezeték:**
1. **Pre-processing (Kémiai helyreállítás):**
   - **RGB/HSV Csatorna Szeparáció:** Az eltolódott színek (pl. túl sok sárga) manuális vagy automatikus kompenzálása az adott színcsatorna eltolásával (RGB shift).
   - **Fehéregyensúly és Színkorrekció:** A `adjust_color` és a Saturation (színezet) növelése a kifakult pigmentek "felélesztésére".
2. **AI Inferencia (Tisztítás):**
   - **Színzaj-szűrés (Denoising):** Az analóg film finom szemcsézettségének megtartása, de a durva színfoltok (chroma noise) eltüntetése.
   - **Szuperfelbontás (Upscaling):** A gyakran kicsi vagy homályos papírképek felbontásának megnövelése (Real-ESRGAN).
3. **Post-processing (Szín-maszkolás):**
   - **VapourSynth MaskedMerge logika:** A restaurált és túlságosan "mesterséges" színek finomítása úgy, hogy csak bizonyos területek (pl. bőrtónusok) legyenek védve a túl-szaturálástól.

---

## 3. Korai Digitális Korszak (1990-es évektől)
*Ide tartoznak: A korai digitális fényképezőgépek és mobiltelefonok képei.*

**Tipikus hibák:** JPEG tömörítési kockásodás (blocking artifacts), szenzorzaj (főleg sötétben lőtt képeknél), alacsony felbontás (pl. 640x480).

**Feldolgozási Csővezeték:**
1. **Pre-processing (Előkészítés):**
   - Fényerő korrekció a sötét (alul-exponált) képeken.
2. **AI Inferencia (Digitális javítás):**
   - **JPEG Artifact Removal:** Kifejezetten a tömörítési hibák eltüntetésére edzett modellek.
   - **Erős Szuperfelbontás (HAT / ESRGAN):** A pixeles (SD) képek felhúzása élvezhető, nyomtatható (HD/4K) felbontásra, valódi textúrák generálásával.
3. **Post-processing (Élesítés):**
   - Enyhe élesítés (`adjust_sharpness`), valamint a mesterséges élek "finomítása" (soft-refinement), hogy a kép ne nézzen ki túlságosan "műanyagnak" (ringing / halo effect megelőzése).

---

A GUI-n (Felhasználói felületen) ezek a korszakok **Profilokként (Presets)** is kiválaszthatók lesznek, amelyek automatikusan beállítják a megfelelő csővezetéket és a csúszkák (kontraszt, gamma, RGB) kezdőértékeit.
