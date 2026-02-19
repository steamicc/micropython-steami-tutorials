# CLAUDE.md — Contexte projet tutoriels STeaMi

## Le projet

On crée des tutoriels MicroPython pour la carte **STeaMi** (https://www.steami.cc/), une carte éducative conçue par le L.A.B. (Laboratoire d'Aix-périmentation et de Bidouille) pour enseigner la programmation et l'expérimentation assistée par ordinateur au collège et au lycée.

- Repo d'exemples existants : https://github.com/steamicc/micropython-steami-sample
- Support MicroPython : https://github.com/steamicc/micropython-steami/tree/stm32-steami-rev1d-final
- Drivers : https://github.com/steamicc/micropython-steami-lib
- Design carte : https://github.com/steamicc/steami-reference-design
- Documentation : https://steamicc.notion.site/Documentation-1fd4a41b9b8f4899878e3d42887d2d78?pvs=74

---

## Hardware de la carte STeaMi

- **MCU** : STM32WB55 (Cortex-M4 64MHz + Cortex-M0+ pour BLE)
- **Écran** : SSD1327 OLED 128×128 pixels, niveaux de gris 4-bit (0-15, framebuf GS4_HMSB), bus SPI
- **Capteur température/humidité** : HTS221 (I2C)
- **Capteur distance laser** : VL53L1X — Time of Flight (I2C)
- **Capteur lumière/proximité** : APDS9960 — lumière ambiante + proximité + gestes (I2C, gestes cassés actuellement)
- **Jauge batterie** : BQ27441 (I2C)
- **LED RGB** : 3 LEDs séparées (rouge=pyb.LED(1), verte=pyb.LED(2), bleue=pyb.LED(3)) — aussi accessibles via Pin("LED_RED"), Pin("LED_GREEN"), Pin("LED_BLUE")
- **Speaker/Buzzer** : piézo en bitbang sur Pin("SPEAKER", Pin.OUT_PP)
- **Boutons** : 3 boutons (A_BUTTON, B_BUTTON, MENU_BUTTON) — actifs à l'état bas avec PULL_UP
- **D-PAD** : 4 boutons directionnels (UP/DOWN/LEFT/RIGHT) via MCP23009E expandeur I/O (I2C, addr 0x40), reset sur Pin("RST_EXPANDER"), interruption sur Pin("INT_EXPANDER")
- **BLE** : Bluetooth Low Energy via `aioble`
- **Connecteurs** : 2× Jacdac + 1× micro:bit + 1× Qwiic
- **Bus I2C** : I2C(1) = bus interne (capteurs on-board), I2C(3) = bus externe (connecteurs)
- **Bus SPI** : SPI(1) = bus interne (écran), SPI(2) = bus externe
- **USB** : drag & drop + série (REPL sur LPUART1, 115200 baud)
- **Batterie** : connecteur batterie LiPo

---

## Bibliothèque steami_screen — API haut niveau

**Fichier** : `lib/steami_screen.py`

La bibliothèque fonctionne avec deux backends :
- **SSD1327** (128×128, GS4_HMSB) — écran principal de la carte STeaMi
- **GC9A01** (240×240, RGB565) — écran couleur circulaire optionnel

**CRITICAL** : Appeler `screen.clear()` en début de boucle et `screen.show()` **une seule fois** à la fin.

### Initialisation sur la carte (SSD1327)

```python
from machine import SPI, Pin
import ssd1327
from steami_ssd1327 import SSD1327Display
from steami_screen import Screen

spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")
display = SSD1327Display(ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs))
screen = Screen(display)
```

### Propriétés utiles

```python
screen.center   # (cx, cy) — (64,64) sur 128px, (120,120) sur 240px
screen.radius   # rayon utile — 64 sur 128px, 120 sur 240px
```

### Widgets disponibles

```python
screen.title("Label")                            # texte centré en haut (y=20), max 16 chars
screen.subtitle("Ligne 1", "Ligne 2")            # texte centré en bas, max 1-2 lignes
screen.value(42, unit="mm", at="CENTER")         # grande valeur (scale×2), at="W"/"E" pour 2 valeurs
screen.bar(val, max_val=100)                     # barre de progression horizontale
screen.gauge(val, min_val=0, max_val=100, unit="mm")  # jauge circulaire 270° — APPELER AVANT title()
screen.graph(data, min_val=0, max_val=100)       # graphe scrollant (data = liste de floats)
screen.menu(items, selected=0)                   # liste avec surlignage — PAS de subtitle compatible
screen.compass(heading)                          # rose des vents — widget immersif seul
screen.watch(hours, minutes, seconds=0)          # aiguilles analogiques — widget immersif seul
screen.face(expression, color=LIGHT)             # smiley bitmap 8×8 — immersif (peut avoir title+subtitle)
```

Expressions `face()` valides : `"happy"` `"sad"` `"surprised"` `"sleeping"` `"angry"` `"love"`

### Dessin bas niveau

```python
screen.text("txt", at="CENTER", scale=1)
screen.line(x1, y1, x2, y2)
screen.circle(x, y, r, fill=False)
screen.rect(x, y, w, h, fill=False)
screen.pixel(x, y)
screen.clear()   # efface tout en noir
screen.show()    # envoie le framebuf à l'écran
```

### Couleurs disponibles (steami_screen)

```python
from steami_screen import BLACK, DARK, GRAY, LIGHT, WHITE, GREEN, RED, YELLOW, BLUE
# BLACK=0, DARK~6, GRAY~9, LIGHT~11, WHITE=15 (valeurs GS4 pour SSD1327)
# GREEN/RED/YELLOW/BLUE : couleurs accentuées (dégradent en gris sur SSD1327)
```

---

## Tooling — workflow de développement

### Commandes principales

```bash
# Valider tous les tutoriels (SSIM ≥ 0.85 requis)
~/venv/bin/python3 validate.py

# Valider un seul tutoriel
~/venv/bin/python3 validate.py 04_circular_gauge

# Régénérer le rapport galerie (docs/mockups/README.md)
~/venv/bin/python3 generate_report.py

# Générer le screenshot d'un tutoriel
~/venv/bin/python3 tutorials/04_circular_gauge/screenshot.py
```

**ALWAYS** : après avoir modifié un SVG ou un `screenshot.py`, relancer `validate.py` pour vérifier le SSIM.

### Fichiers outils

| Fichier | Rôle |
|---------|------|
| `validate.py` | Lance chaque `screenshot.py`, rasterise le SVG, calcule le SSIM |
| `generate_report.py` | Génère `docs/mockups/README.md` — galerie HTML 2 colonnes |
| `sim/sim_backend.py` | Backend Pillow pour simuler l'écran sur PC |
| `lib/steami_screen.py` | Bibliothèque haute niveau partagée carte + sim |
| `lib/steami_ssd1327.py` | Wrapper SSD1327 pour la carte |
| `lib/steami_gc9a01.py` | Wrapper GC9A01 pour la carte |
| `lib/steami_colors.py` | Constantes couleurs |
| `docs/design-constraints.md` | Zones de layout, contraintes widgets (2 écrans) |
| `docs/layout-zones.svg` | Schéma SVG comparatif 128×128 vs 240×240 |
| `docs/mockups/README.md` | Galerie générée — NE PAS ÉDITER MANUELLEMENT |

### Pattern screenshot.py — REQUIRED pour chaque tutoriel

**CRITICAL** : tout nouveau tutoriel doit avoir ce fichier `screenshot.py`.

```python
METADATA = {
    "title": "Nom affiché dans la galerie",
    "widget": "screen.gauge(val, min_val, max_val, unit)",
    "description": "Description courte en anglais",
}

import sys, os
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(root, "lib"))
sys.path.insert(0, os.path.join(root, "sim"))

from steami_screen import Screen, GREEN   # importer les couleurs nécessaires
from sim_backend import SimBackend

backend = SimBackend(128, 128, scale=3)   # scale=3 pour PNG lisible
screen = Screen(backend)

# --- Même code que main.py, avec des valeurs fixes ---
screen.clear()
screen.title("Title")
screen.value(42, unit="mm")
screen.show()

out_dir = os.path.join(root, "docs", "mockups")
out_path = os.path.join(out_dir, "04_circular_gauge_sim.png")
backend.save(out_path)
print("Saved:", out_path)
```

### Pattern mockup SVG — REQUIRED pour chaque tutoriel

**CRITICAL** : le fichier `docs/mockups/{name}.svg` est la référence de validation SSIM.
- Viewbox 200×200, clipPath sur cercle r=95, cx=cy=100
- Couleurs : `#000` fond, `#999` GRAY, `#bbb` LIGHT, `#fff` WHITE, `#7f7` GREEN, `#f55` RED, etc.
- **Facteur SVG** : les coordonnées écran 128px → coordonnées SVG via `(coord_px / 128) × 200`
- Titre positionné à `y=43` (≈ y=20 px écran × 200/128 + 12 pour baseline)

---

## Tutoriels réalisés (15/15 PASS)

| Dossier | Widget principal | Capteur/composant |
|---------|-----------------|-------------------|
| `01_temperature` | `value()` + `bar()` | HTS221 température |
| `02_battery` | `value()` + `gauge()` | BQ27441 état de charge |
| `03_comfort_dual` | `value("W")` + `value("E")` | HTS221 temp + humidité |
| `04_circular_gauge` | `gauge()` | VL53L1X distance |
| `05_scrolling_graph` | `graph()` | VL53L1X historique |
| `06_dpad_menu` | `menu()` | MCP23009E D-PAD navigation |
| `07_compass` | `compass()` | heading simulé |
| `08_smiley_angry` | `face("angry")` | — |
| `08_smiley_happy` | `face("happy")` | — |
| `08_smiley_love` | `face("love")` | — |
| `08_smiley_reactive` | `face(expr)` | VL53L1X distance → expression |
| `08_smiley_sad` | `face("sad")` | — |
| `08_smiley_sleeping` | `face("sleeping")` | — |
| `08_smiley_surprised` | `face("surprised")` | — |
| `09_watch` | `watch()` | RTC / horloge |

---

## Ce qu'il reste à faire

### Série "Projets combinés" (PAS ENCORE CODÉS)

| # | Projet | Composants |
|---|--------|-----------|
| 1 | Theremin lumineux | Distance → fréquence buzzer + `bar()` |
| 2 | Feux tricolores | LED RGB + boutons + distance → machine à états |
| 3 | Gardien de salle | Distance + LED + buzzer → alarme avec seuil |
| 4 | Station confort | Temp + humidité → indice de confort + `gauge()` |
| 5 | Luxmètre scientifique | Lumière → `graph()` scrollant + série |
| 6 | Talkie-Walkie Morse | BLE + boutons + buzzer |
| 7 | Radar de poche | Servo + distance → vue radar |
| 8 | Robot expressif | KS4034F + `face()` + sons |

### Série "Explorations" — patterns non couverts (PAS ENCORE CODÉS)

| # | Sujet | Lacune comblée |
|---|-------|---------------|
| 1 | Proximité APDS9960 | Mode proximité (0-255) jamais montré |
| 2 | GPIO extension | Pins P0-P16, ADC jamais exploités |
| 3 | Capteur externe Qwiic | I2C(3) jamais illustré |
| 4 | Multitâche asyncio | `async/await`, `asyncio.gather()` |
| 5 | Interruptions (IRQ) | `Pin.irq()`, `mcp.interrupt_on_change()` |
| 6 | Machine à états | enum d'états, transitions |
| 7 | Enregistreur de données | `open()`/`write()` flash + CSV + timestamps RTC |
| 8 | Console série bidirectionnelle | `sys.stdin`/`input()` depuis le PC |
| 9 | Palette de gris | 16 niveaux, `display.lookup()` |

---

## API MicroPython — Patterns vérifiés

### Capteurs I2C
```python
from machine import I2C
i2c = I2C(1)

from hts221 import HTS221
capteur = HTS221(i2c)
capteur.temperature()  # float °C
capteur.humidity()     # float %

from vl53l1x import VL53L1X
capteur = VL53L1X(i2c)
capteur.read()  # int mm

from apds9960 import uAPDS9960 as APDS9960
capteur = APDS9960(i2c)
capteur.enableLightSensor()
capteur.readAmbientLight()   # int lux
capteur.enableProximitySensor()
capteur.readProximity()      # int 0-255

from bq27441 import BQ27441
capteur = BQ27441(i2c)
capteur.state_of_charge()    # int %
capteur.voltage()            # int mV
capteur.current_average()    # float mA
capteur.capacity_remaining() # int mAh
capteur.capacity_full()      # int mAh
```

### Boutons et D-PAD
```python
from machine import Pin
bouton_a = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)   # value() == 0 = appuyé
bouton_b = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)
bouton_menu = Pin("MENU_BUTTON", Pin.IN, Pin.PULL_UP)

from mcp23009e import MCP23009E
from mcp23009e.const import *
reset = Pin("RST_EXPANDER", Pin.OUT)
mcp = MCP23009E(i2c, address=MCP23009_I2C_ADDR, reset_pin=reset)
mcp.setup(MCP23009_BTN_UP, MCP23009_DIR_INPUT, pullup=MCP23009_PULLUP)
mcp.get_level(MCP23009_BTN_UP)  # MCP23009_LOGIC_LOW = appuyé
# Interruptions (optionnel)
mcp.interrupt_on_change(MCP23009_BTN_UP, callback)
```

### LED RGB et Speaker
```python
import pyb
led_rouge = pyb.LED(1)  # pyb.LED(2)=vert, pyb.LED(3)=bleu
led_rouge.on() ; led_rouge.off()

from machine import Pin
from time import sleep_us, ticks_us, ticks_add, ticks_diff
speaker = Pin("SPEAKER", Pin.OUT_PP)

def tone(pin, freq, duration_ms):
    if freq == 0:
        from time import sleep
        sleep(duration_ms / 1000)
        return
    period_us = 1_000_000 // freq
    half_period = period_us // 2
    end_time = ticks_add(ticks_us(), duration_ms * 1000)
    while ticks_diff(end_time, ticks_us()) > 0:
        pin.on(); sleep_us(half_period)
        pin.off(); sleep_us(half_period)
```

### Écran — fonctions bas niveau (sans steami_screen)
```python
display.fill(0)
display.text("texte", x, y, couleur)
display.framebuf.fill_rect(x, y, w, h, couleur)
display.framebuf.hline(x, y, w, couleur)
display.framebuf.vline(x, y, h, couleur)
display.show()
```

---

## Conventions de code

- **Langue du code** : anglais pour les commentaires et noms de fonctions
- **Langue des textes écran** : anglais sans accents (limitation ASCII 7-bit du driver)
- **Fichiers autonomes** : chaque `main.py` contient tout (pas de module partagé)
- **Pattern capteur** : étape 1 (écran) → 2 (capteur) → 3 (lire) → 4 (afficher) → 5 (boucle)
- **Sleep** : 0.5s par défaut, 0.1s pour les boutons, 2s pour la batterie
- **Print série** : toujours en parallèle de l'affichage écran

## Contenu existant dans le repo upstream (ne pas dupliquer)

| Dossier | Contenu |
|---------|---------|
| LED/blink | Cycle RGB avec affichage texte |
| BUTTON/set_led_on | Bouton → LED |
| SCREEN/steami_faces | Smileys bitmap 8×8 scalés |
| SCREEN/steami_animation | Animation |
| SENSOR/show_distance | VL53L1X → écran |
| SENSOR/show_luminosity | APDS9960 → écran |
| SENSOR/show_temp_humidity | HTS221 → écran |
| SENSOR/show_fuel_gauge | BQ27441 → écran |
| GAME/snake | Snake dans cercle |
| BLE/STeaMi_adv | Advertising BLE |
| BLE/STeaMi_talk | Communication bidirectionnelle |
| DEMO/ | Menu combiné (sensors, buzzer, LED, screen, button) |
| ROBOT/KS4034F/ | Moteurs, suivi de ligne, ultrason |

## Commandes utiles

```bash
# Copier un script sur la carte
mpremote connect auto fs cp tutorials/01_temperature/main.py :main.py
mpremote connect auto reset

# Ouvrir le REPL
mpremote connect auto

# Lister les fichiers sur la carte
mpremote connect auto fs ls
```
