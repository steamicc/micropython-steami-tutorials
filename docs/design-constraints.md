# steami_screen — Design Constraints

Guide de référence pour concevoir des affichages avec `steami_screen`.
L'API est identique sur les deux écrans ; seules les valeurs numériques changent.

---

## Écrans supportés

| Propriété | SSD1327 | GC9A01 |
|-----------|---------|--------|
| Résolution | 128 × 128 px | 240 × 240 px |
| Forme | Circulaire | Circulaire |
| Format couleur | GS4_HMSB — 16 niveaux de gris | RGB565 — couleur 16-bit |
| Pixel origine | (0, 0) = coin haut-gauche | idem |
| Centre (`screen.center`) | (64, 64) | (120, 120) |
| Rayon (`screen.radius`) | 64 px | 120 px |
| Driver | `SSD1327Display` | `GC9A01Display` |

La forme circulaire réduit la zone visible : les coins du framebuffer carré ne s'affichent pas.

---

## Palette de couleurs

Les constantes RGB sont identiques pour les deux écrans.
Sur SSD1327, les couleurs d'accent dégradent en niveaux de gris (canal R=G=B).

| Constante | RGB | gray4 (SSD1327) | Usage |
|-----------|-----|-----------------|-------|
| `BLACK` | (0, 0, 0) | 0 | Fond, effacement |
| `DARK` | (102, 102, 102) | 6 | Fond surligné, éléments inactifs |
| `GRAY` | (153, 153, 153) | 9 | Textes secondaires, titres |
| `LIGHT` | (187, 187, 187) | 11 | Contenu principal, jauges |
| `WHITE` | (255, 255, 255) | 15 | Valeurs importantes |
| `GREEN` | (119, 255, 119) | — | État positif |
| `RED` | (255, 85, 85) | — | Alerte |
| `YELLOW` | (255, 255, 85) | — | Avertissement |
| `BLUE` | (85, 85, 255) | — | Information |

---

## Typographie

La police built-in MicroPython `framebuf` est la seule disponible sans bibliothèque externe.
Sa taille est **fixe en pixels absolus**, indépendante de la résolution de l'écran.

| Propriété | Valeur |
|-----------|--------|
| `CHAR_W` | 8 px par caractère |
| `CHAR_H` | 8 px de hauteur |
| Caractères max par ligne | `width // 8` : **16** (128px) ou **30** (240px) |
| `draw_small_text()` | ≈ 85 % de la taille de base (subtitles) |
| `draw_medium_text()` | ≈ 130 % (unités, labels) |
| `_draw_scaled_text()` | × 2 (valeurs) ou × 3 (très grand) |

> Sur 240×240, la même police de 8×8 px occupe une fraction plus petite de l'écran.
> Les textes en `scale=2` (16×16 px) restent lisibles sur les deux tailles.

Les caractères accentués ne sont pas disponibles — écrire en anglais sans accents.

---

## Zones de layout

![Zones de layout 128×128 et 240×240](layout-zones.svg)

Les **positions y sont identiques en pixels absolus** sur les deux écrans : `title()` commence
toujours à y=20, `subtitle()` (1 ligne) commence toujours à y = `height − 20`.
La différence principale est la **taille de la zone contenu**.

| Zone | y début | y fin | 128×128 | 240×240 |
|------|---------|-------|---------|---------|
| Marge haute | 0 | 20 | 20 px | 20 px |
| `title()` | 20 | 28 | 8 px | 8 px |
| Zone contenu | 28 | height−20 | **80 px** | **192 px** |
| `subtitle()` 1 ligne | height−20 | height−12 | y=108–116 | y=220–228 |
| `subtitle()` 2 lignes | height−21 | height−10 | y=100–122 | y=207–229 |
| Marge basse | height−12 | height | 12 px | 12 px |

> **Note sur `_safe_margin()`** : le margin_ns est calculé dynamiquement pour que
> le texte reste dans le cercle. Pour les textes courts (≤ 10 chars), margin_ns = 20 px
> sur les deux écrans. Pour des textes plus longs, la marge augmente automatiquement.

---

## Widgets — zones et contraintes

### `title(text, color=GRAY)`

| | 128×128 | 240×240 |
|--|---------|---------|
| Position y | 20 px | 20 px |
| Hauteur | 8 px | 8 px |
| Largeur max | 16 chars | 16 chars (limite de la zone circulaire à y=20) |
| Couleur défaut | `GRAY` | `GRAY` |

Le titre est toujours centré horizontalement.

---

### `subtitle(*lines, color=DARK)`

| | 128×128 | 240×240 |
|--|---------|---------|
| y (1 ligne) | 108 px | 220 px |
| y (2 lignes) | 100–111 px | 207–218 px |
| Hauteur par ligne | 11 px (CHAR_H + 3) | 11 px |
| Largeur max | 16 chars | 24 chars |
| Police | `draw_small_text` (légèrement plus petite) | idem |

---

### `value(val, unit=None, at="CENTER")`

| | 128×128 | 240×240 |
|--|---------|---------|
| Position | Centré verticalement | Centré verticalement |
| Taille valeur (scale=2) | 16×16 px par char | 16×16 px par char |
| Largeur max valeur | 8 chars (128 px) | 8 chars (128 px) |
| Positions alternatives | `"W"`, `"E"` | `"W"`, `"E"` |
| Zone occupée (approx.) | 36 px de haut | 36 px de haut |

**Combinaisons valides** : `title` + `value` + `subtitle`,
`value("W")` + `value("E")` pour 2 valeurs côte à côte.

---

### `bar(val, max_val=100)`

| | 128×128 | 240×240 |
|--|---------|---------|
| Position y | cy + 20 = **84 px** | cy + 20 = **140 px** |
| Largeur | width − 40 = **88 px** | width − 40 = **200 px** |
| Hauteur | 8 px | 8 px |
| Position x | centré (x=20) | centré (x=20) |

---

### `gauge(val, min_val, max_val, unit=None)`

| | 128×128 | 240×240 |
|--|---------|---------|
| Épaisseur arc | max(5, r//9) = **7 px** | max(5, r//9) = **13 px** |
| Rayon de l'arc | r − arc_w/2 − 1 = **60 px** | r − arc_w/2 − 1 = **113 px** |
| Forme | Arc 270°, départ 135° (bas-gauche) | idem |
| Appel conseillé | `gauge()` **avant** `title()` | idem |

La plage non remplie (gap) est en bas. Les étiquettes min/max sont aux extrémités de l'arc.

---

### `graph(data, min_val, max_val)`

| | 128×128 | 240×240 |
|--|---------|---------|
| Zone graphe x | x=21 à x=113 (92 px) | x=21 à x=225 (204 px) |
| Zone graphe y | y=38 à y=90 (52 px) | y=38 à y=90 (52 px) |
| Valeur courante | y=31 | y=31 |
| Points max conseillés | 92 | 204 |

> **Attention** : `gy=38` et `gh=52` sont des valeurs **hardcodées** qui n'adaptent pas
> à 240×240. Le graphe n'occupe pas toute la zone contenu disponible.

---

### `menu(items, selected=0)`

| | 128×128 | 240×240 |
|--|---------|---------|
| Départ y | 35 px | 35 px |
| Hauteur par item | 14 px (CHAR_H + 6) | 14 px |
| Items visibles max | **6** ((128−40)//14) | **14** ((240−40)//14) |
| Largeur surlignage | 98 px (x=15→113) | 210 px (x=15→225) |

---

### `compass(heading)`

| | 128×128 | 240×240 |
|--|---------|---------|
| Rayon de la rose | radius − 12 = **52 px** | radius − 12 = **108 px** |
| Cercle intérieur | r × 0.7 = **36 px** | r × 0.7 = **75 px** |
| Labels cardinaux | r + 5 = **57 px** du centre | r + 5 = **113 px** du centre |
| Longueur aiguille | r × 0.85 = **44 px** | r × 0.85 = **91 px** |
| Usage | **Immersif uniquement** | **Immersif uniquement** |

---

### `watch(hours, minutes, seconds=0)`

| | 128×128 | 240×240 |
|--|---------|---------|
| Rayon du cadran | radius − 8 = **56 px** | radius − 8 = **112 px** |
| Numbers (12/3/6/9) | r − 15 = **41 px** du centre | r − 15 = **97 px** du centre |
| Aiguille heures | r × 0.50 = **28 px** | r × 0.50 = **56 px** |
| Aiguille minutes | r × 0.75 = **42 px** | r × 0.75 = **84 px** |
| Aiguille secondes | r × 0.85 = **47 px** | r × 0.85 = **95 px** |
| Usage | **Immersif uniquement** | **Immersif uniquement** |

---

### `face(expression, color=LIGHT)`

| | 128×128 | 240×240 |
|--|---------|---------|
| Scale par pixel bitmap | (128×11)//128 = **11 px** | (240×11)//128 = **20 px** |
| Taille totale | 88 × 88 px | 160 × 160 px |
| Coin haut-gauche | (20, 20) | (40, 40) |
| Coin bas-droit | (108, 108) | (200, 200) |
| Marge haute libre | y=0→19 (pour `title`) | y=0→39 |
| Marge basse libre | y=109→127 (pour `subtitle`) | y=201→239 |
| Expressions | `"happy"` `"sad"` `"surprised"` `"sleeping"` `"angry"` `"love"` | idem |

---

## Adaptativité : ce qui s'adapte, ce qui est fixe

| Élément | Adaptatif | Fixe |
|---------|:---------:|:----:|
| `title()` / `subtitle()` positions y | ✅ | |
| `compass()` / `watch()` rayon | ✅ | |
| `face()` taille | ✅ | |
| `gauge()` rayon et épaisseur | ✅ | |
| `bar()` largeur et position y | ✅ | |
| `menu()` items visibles max | ✅ | |
| `graph()` zone y (gy=38, gh=52) | | ❌ hardcodé |
| `graph()` valeur courante y=31 | | ❌ hardcodé |
| `menu()` hauteur par item (14 px) | | ❌ hardcodé |
| Police framebuf (8×8 px) | | ❌ taille absolue fixe |

---

## Combinaisons de widgets

| Combinaison | Compatible | Remarque |
|-------------|:---------:|---------|
| `title` + `value` + `subtitle` | ✅ | Pattern de base |
| `title` + `value("W")` + `value("E")` + `subtitle` | ✅ | 2 valeurs côte à côte |
| `title` + `bar` + `subtitle` | ✅ | Barre de progression |
| `gauge` + `title` + `subtitle` | ✅ | Appeler `gauge()` en premier |
| `title` + `graph` + `subtitle` | ✅ | Graphe scrollant |
| `title` + `menu` | ✅ | Pas de place pour subtitle |
| `face` + `title` + `subtitle` | ✅ | Face + labels de contexte |
| `compass` seul | ✅ | Immersif |
| `watch` seul | ✅ | Immersif |
| `face` seul | ✅ | Immersif |
| `compass` + `title` | ⚠️ | Le titre se superpose à la rose |
| `menu` + `subtitle` | ❌ | Les items descendent jusqu'en bas de l'écran |

---

## Règles générales

- Appeler `screen.show()` **une seule fois** à la fin pour éviter le scintillement.
- Appeler `screen.clear()` **en début de boucle** pour ne pas accumuler les frames.
- Les widgets immersifs (`compass`, `watch`, `face`) utilisent tout l'espace — ne pas combiner avec d'autres widgets de contenu.
- Le texte est limité à **ASCII 7 bits** (pas d'accents ni de caractères spéciaux).
- Préférer `screen.value()` (scale 2, 16 px) au `screen.text()` brut (8 px) pour les valeurs numériques à afficher de loin.
