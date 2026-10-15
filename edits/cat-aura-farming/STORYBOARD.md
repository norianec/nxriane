# CAT AURA FARMING — édit TikTok sur « PURR OF DEATH »

Format 1080×1920, 30 fps, **45,03 s** (1351 images). La durée est calée pour que le
prochain coup de 808 tombe pile au redémarrage de la boucle. La dernière image retombe
sur la première (noir + deux yeux dorés), donc la boucle est raccord.

Analyse du son (`analysis/`) : ~117 BPM, montée 0–16,5 s, **drop à 16,54 s**,
cassure 31–33 s, **second drop à 33,07 s**. Les miaulements sont les glissandos repérés
sur les spectrogrammes (`analysis/zoom_*.jpg`).

| Temps | Phase | Plans | Ce qui se passe sur le son |
|---|---|---|---|
| 0–8,1 s | **Mystérieux** | yeux seuls dans le noir → silhouette sous la lune de sang (pluie) → profil dans les braises → macro de l'œil | chaque miaulement = éclat des yeux (flare anamorphique) + micro-zoom |
| 8,1–16,5 s | **Charismatique** | marche au ralenti dans la fumée → regard fixe (distorsion de chaleur) → contre-plongée royale → trône | un plan par mesure, sur les miaulements 10,15 / 12,05 / 14,30 ; plongée dans la pupille avec tremblement montant jusqu'au drop |
| 16,25 s | pré-drop | miaulement face caméra, lignes de vitesse anime | miaulement |
| 16,54–31 s | **Dominant** | contre-plongée foudre, cri vers le ciel, regard fixe, trône, profil… | **coupe ou impact sur chaque 808** (zoom punch, secousse, aberration RVB, flash rouge) ; miaulements = gueule ouverte + lignes de vitesse ; flashs négatifs à 22,00 et 30,25 ; éclairs |
| 31–33 s | calme avant la tempête | yeux fermés, bandes cinéma | glissandos descendants, tremblement qui monte |
| 33,07–44 s | **Aura cosmique** | aura de feu violette, chat sur astéroïde, chat-dieu au-dessus d'une planète… | onde de choc + flash violet au drop, coupes sur les 808 (toutes les ~0,5 s), étoiles en hyperespace ; miaulements = rayons des yeux / flashs négatifs |
| 44–45 s | boucle | plongée dans la pupille → noir → retour aux yeux de l'image 1 | |

Palette : noir profond / rouge sang / or (yeux), puis violet-magenta pour la phase cosmique.
Aucun texte à l'écran.

## Refaire le rendu

```bash
pip install numpy opencv-python-headless librosa
cp /chemin/PURR_OF_DEATH.wav assets/purr_of_death.wav
python3 scripts/render.py preview 0 16.6 33.1     # images-clés dans out/preview/
python3 scripts/render.py video --workers 4       # out/cat_aura_farming.mp4 (master)
ffmpeg -i out/cat_aura_farming.mp4 -c:v libx264 -preset slow -crf 19 -maxrate 14M -bufsize 28M \
  -c:a copy -movflags +faststart out/CAT_AURA_FARMING_tiktok.mp4
```

Le découpage se règle dans `scripts/timeline.py` (plans, miaulements, basses, événements) ;
les effets sont dans `scripts/fx.py`.

Les 15 images fixes (`assets/stills/`) viennent de Higgsfield Soul 2.0 (plan gratuit).
