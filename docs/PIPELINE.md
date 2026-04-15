# Csővezetékek (Pipelines) - Kivitelezési Stratégia

A rendszer csővezetékei történelmi korszakokra, és most már egyéni transzformációkra is vannak bontva. Minden lépés aszinkron ONNX szálakon fut, `VapourSynth` optimalizációkkal.

## 1. I-II. Világháborús és Pre-1960 Fekete-Fehér Fotók
1. **Physical Damage Assessment**: Karcolások és gyűrődések észlelése, majd `ProPainter` / inpainting kitöltése.
2. **Face Transplant (Opcionális)**: Ha a főszereplő arca felismerhetetlen (homályos, letépték), de van alternatív korabeli vagy jó minőségű fotó róla, a `FaceFusion` modullal behelyettesítjük.
3. **Face Restoration**: A `CodeFormer` futtatása, RAG-vezérelt `fidelity weight`-tel (erősen védve a rögzített identitást).
4. **Colorization**: `DeOldify` futtatása (No-GAN mód a konzisztencia végett, halvány "szépia/hiteles" színpalettával).
5. **Animation (Opcionális)**: `LivePortrait` segítségével a karaktert finoman életre keltjük.

## 2. 70-es, 80-as Évek Analóg Színes (VHS, Fotó)
1. **Color Shift Correction**: Fakulás, vörös eltolódás javítása tradicionális OpenCV és VapourSynth szűrőkkel.
2. **Denoising**: `RVRT` (videó) vagy `SwinIR` (fotó) a szemcsézettség csökkentésére.
3. **Upsampling**: `HAT` alapú felskálázás.

## 3. Korai Digitális Kamera (Erős Tömörítési Kockásodás)
1. **Deblocking**: Speciális VapourSynth MLRT háló a JPEG/MPEG zaj csökkentésére.
2. **Super Resolution**: `Real-ESRGAN` textúragenerálás (finomított ringing és halo effect védelemmel).
