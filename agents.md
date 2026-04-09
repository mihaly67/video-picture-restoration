Kép- és Videó Restaurációs Feladatrendszer
1. Dinamikus Videó-zajmentesítés és Tisztítás
Jules fő feladata a videóállományok digitális és analóg zajának (szemcsézettség, tömörítési kockásodás) eltávolítása. Ehhez a VRT (Video Restoration Transformer) modellt alkalmazza, amely képes az időbeli összefüggések (több egymást követő képkocka) elemzésére a tisztább kép érdekében.

Gemini szakmai támogatása: Konzultáció a videó zajszintjének előzetes elemzéséről. Gemini segít meghatározni, hogy a forrásanyag "túlszűrt" (viaszos hatású) vagy "alulszűrt" marad-e, és javaslatot tesz a transzformer alapú modellek ablakméretének (window size) finomhangolására a jobb élesség érdekében.

2. Intelligens Tartalomrekonstrukció és Inpainting
A feladat a videókon és képeken lévő zavaró elemek (vízjelek, dátumbélyegzők, karcolások) eltávolítása és a hiányzó területek környezetazonos kitöltése. Jules a ProPainter és az E2FGVI algoritmusokat használja a mozgó háttér konzisztens újragenerálásához.

Gemini szakmai támogatása: Szakmai kontroll az optikai folyam (Optical Flow) felett. Gemini elemzi a mozgási vektorokat, és tanácsot ad Jules-nek, ha a behelyettesített tartalom vibrálni kezd (temporal flickering), segítve a maszkolási algoritmus optimalizálását.

3. Arcrekonstrukció és Fotórestaurálás
Régi, kis felbontású vagy sérült fotók (és videók) esetén Jules feladata az emberi arcok azonosítása és minőségi feljavítása a GFPGAN vagy a CodeFormer segítségével, hogy az eredmény felismerhető és élethű legyen.

Gemini szakmai támogatása: A Gemini szakmai tanácsot ad a generatív kreativitás korlátozására. Megakadályozza, hogy az MI "idegen" arcot hozzon létre; segít Jules-nek a forráskép eredeti vonásait megőrző súlyozás (ad-hoc fidelity weight) beállításában.

4. Színhűség és Automatikus Kolorizáció
Fekete-fehér vagy kifakult színes tartalmak esetén Jules feladata a színek élethű visszaállítása a DeOldify rendszerrel. Képesnek kell lennie a videó teljes hosszában konzisztens színeket generálni.

Gemini szakmai támogatása: Történelmi és vizuális tanácsadás. Gemini segít a színpaletta hitelesítésében (pl. korhű bőrtónusok, környezeti színek), és javaslatot tesz a "No-GAN" technika alkalmazására a villódzásmentes színezés érdekében.

5. Szuperfelbontás (Upscaling) és Textúragenerálás
A végső fázisban Jules feladata a felbontás növelése (pl. SD-ről 4K-ra) a HAT vagy a Real-ESRGAN modellekkel, miközben mesterséges élesség helyett valódi textúrákat (pl. haj, ruha anyaga) hoz létre.

Gemini szakmai támogatása: Tanácsadás az utólagos képi műhibák (ringing, halo effect) felismerésében. Gemini javaslatot tesz a modell-láncolat (pipeline) végén egy "soft-refinement" lépésre, amely természetesebbé teszi a digitálisan felnagyított éleket.

👨‍💻 Operatív Végrehajtás (Jules)
Jules a fenti feladatokat egy központosított Python keretrendszerben futtatja, amely:

Minden lépés előtt lekérdezi a RAG adatbázist a legjobb paraméterekért.

Kritikus pontokon Geminihez fordul szakmai jóváhagyásért vagy hibajavítási tippért.

A feldolgozott adatokat optimalizált kiterjesztésekben (.safetensors, .engine) kezeli a maximális sebességért.
