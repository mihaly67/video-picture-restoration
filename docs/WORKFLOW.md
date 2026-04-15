# Munkafolyamatok (Workflows)

Ez a dokumentum a felhasználó által kezdeményezhető főbb munkafolyamatokat (workflow-kat) és a RAG-ból származó integrációkat (FaceFusion, LivePortrait) tartalmazza.

## 1. Komplex Történelmi Fotó Restauráció & Arccsere (Face Swap)
**Mikor használjuk:** Amikor a régi fotó annyira sérült (pl. elmosódott arc), hogy a hagyományos restaurálás (GFPGAN/CodeFormer) nem elegendő, de van egy másik, tisztább referenciakép ugyanarról a személyről.

**Lépések:**
1. **Zaj- és Karceltávolítás**: Alapvető fizikai sérülések javítása hagyományos (OpenCV) és neurális (SwinIR) módszerekkel.
2. **Környezeti Maszkolás**: Segment Anything (SAM) felismeri a hátteret, elválasztja a ruházatot és a sérült arcot.
3. **Referencia Arccsere (FaceFusion)**:
   - A rendszer beolvassa a jól látható referenciaképet.
   - Kicseréli a sérült fotón lévő arcot az éles referenciára.
   - *RAG Integráció:* `facefusion` modulok alkalmazása, a "blend" és "fidelity" paraméterek lekérése a RAG adatbázisból, hogy az illesztés hiteles legyen (ne "műanyag").
4. **Globális Színharmonizáció**: Színezés (DeOldify) és színharmonizáció, hogy az új arc bőrtónusa megegyezzen az eredeti környezettel.
5. **Végső Szuperfelbontás**: Teljes kép (arc + háttér) 4K feljavítása Real-ESRGAN / HAT modellekkel.

## 2. Állókép Animálás (Portré Animáció)
**Mikor használjuk:** Egy sikeresen restaurált vagy színezett történelmi/régi fotó "életre keltéséhez".

**Lépések:**
1. **Bemenet Ellenőrzése**: A restaurált állókép és egy (opcionális) vezetővideó (driving video) vagy arcpóz profil (driving profile `.pkl`) betöltése.
2. **Animációs Motor (LivePortrait)**:
   - A `LivePortrait` betöltése és a képkockák szintézise.
   - *RAG Integráció:* `--flag_crop_driving_video` és `--driving_smooth_observation_variance` paraméterek RAG alapú konfigurálása a lágyabb, természetes mozgásért (kerülve a robotos hatást).
3. **Időbeli Simítás (Temporal Smoothing)**: VRT alkalmazása, ha a generált videón villódzás (flickering) tapasztalható.
4. **Exportálás**: VapourSynth csővezetéken keresztül a memóriahatékony videó (mp4) előállítása.

## 3. Dinamikus Videó Tisztítás & Zajmentesítés
**Mikor használjuk:** Régi, zajos VHS, vagy korai digitális tömörített felvételek feljavítására.
- Analízis -> VRT (Video Restoration Transformer) / ProPainter (Inpainting) -> Szuperfelbontás -> Export.
