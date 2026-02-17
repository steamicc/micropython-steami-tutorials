# CLAUDE.md — Contexte projet tutoriels STeaMi

## Le projet

On crée des tutoriels MicroPython pour la carte **STeaMi** (https://www.steami.cc/), une carte éducative conçue par le L.A.B. (Laboratoire d'Aix-périmentation et de Bidouille) pour enseigner la programmation et l'expérimentation assistée par ordinateur au collège et au lycée.

Le repo d'exemples existants est ici : https://github.com/steamicc/micropython-steami-sample

Le support micropython de la carte est ici : https://github.com/steamicc/micropython-steami/tree/stm32-steami-rev1d-final

Les drivers sont situés ici : https://github.com/steamicc/micropython-steami-lib

L'ensemble du design de la carte est disponible dans ce repo : https://github.com/steamicc/steami-reference-design

La documentation est présente ici : https://steamicc.notion.site/Documentation-1fd4a41b9b8f4899878e3d42887d2d78?pvs=74

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

## API MicroPython — Patterns vérifiés dans le repo existant

### Initialisation écran (identique partout)
```python
from machine import SPI, Pin
import ssd1327

spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")
display = ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs)
```

### Capteurs I2C
```python
from machine import I2C
i2c = I2C(1)

# Température / Humidité
from hts221 import HTS221
capteur = HTS221(i2c)
capteur.temperature()  # float en °C
capteur.humidity()     # float en %

# Distance
from vl53l1x import VL53L1X
capteur = VL53L1X(i2c)
capteur.read()  # int en mm

# Luminosité
from apds9960 import uAPDS9960 as APDS9960
capteur = APDS9960(i2c)
capteur.enableLightSensor()  # NÉCESSAIRE avant lecture
capteur.readAmbientLight()   # int en lux

# Proximité (même capteur APDS9960)
capteur.enableProximitySensor()  # NÉCESSAIRE avant lecture
capteur.readProximity()          # int (0-255, plus c'est grand plus c'est proche)

# Batterie
from bq27441 import BQ27441
capteur = BQ27441(i2c)
capteur.state_of_charge()     # int en %
capteur.voltage()             # int en mV
capteur.current_average()     # float en mA
capteur.capacity_remaining()  # int en mAh
capteur.capacity_full()       # int en mAh
```

### Boutons
```python
from machine import Pin
bouton_a = Pin("A_BUTTON", Pin.IN, Pin.PULL_UP)
bouton_b = Pin("B_BUTTON", Pin.IN, Pin.PULL_UP)
bouton_menu = Pin("MENU_BUTTON", Pin.IN, Pin.PULL_UP)
# Appuyé = value() == 0
```

### LED RGB
```python
import pyb
led_rouge = pyb.LED(1)
led_verte = pyb.LED(2)
led_bleue = pyb.LED(3)
led_rouge.on() / led_rouge.off()
```

### Speaker (bitbang)
```python
from machine import Pin
from time import sleep_us, ticks_us, ticks_add, ticks_diff

speaker = Pin("SPEAKER", Pin.OUT_PP)

def tone(pin, freq, duration_ms):
    if freq == 0:
        sleep(duration_ms / 1000)
        return
    period_us = 1_000_000 // freq
    half_period = period_us // 2
    end_time = ticks_add(ticks_us(), duration_ms * 1000)
    while ticks_diff(end_time, ticks_us()) > 0:
        pin.on()
        sleep_us(half_period)
        pin.off()
        sleep_us(half_period)
```

### Écran — fonctions de dessin
```python
# Couleurs : 0 (noir) à 15 (blanc) — GS4_HMSB 4-bit
display.fill(0)                                         # efface tout
display.text("texte", x, y, couleur)                    # texte (8px par char, col=15 par défaut)
display.pixel(x, y, couleur)                            # 1 pixel
display.line(x1, y1, x2, y2, couleur)                   # ligne quelconque
display.scroll(dx, dy)                                  # scroll software
display.framebuf.fill_rect(x, y, w, h, couleur)         # rectangle plein
display.framebuf.rect(x, y, w, h, couleur)              # rectangle vide
display.framebuf.hline(x, y, w, couleur)                # ligne horizontale
display.framebuf.vline(x, y, h, couleur)                # ligne verticale
display.framebuf.blit(framebuffer, x, y)                # blitter un framebuf
display.show()                                          # rafraîchir l'écran

# Contrôle écran
display.contrast(0-255)                                 # luminosité
display.rotate(True/False)                              # rotation 180°
display.invert(True/False)                              # inverser couleurs
display.poweroff() / display.poweron()                  # veille écran
```

### PWM / Servo
```python
from pyb import Pin, Timer
pin = Pin("P11", Pin.OUT_PP)
timer = Timer(timer_id, freq=50)
channel = timer.channel(channel_id, Timer.PWM, pin=pin)
channel.pulse_width_percent(duty)  # 5% à 10% pour servo standard
```

### BLE (aioble)
```python
import bluetooth
import aioble
ble = bluetooth.BLE()
ble.active(True)
# Voir BLE/STeaMi_talk/ et BLE/STeaMi_adv/ pour les patterns complets
```

### D-PAD (MCP23009E via I2C)
```python
from machine import I2C, Pin
from mcp23009e import MCP23009E
from mcp23009e.const import *

i2c = I2C(1)
reset = Pin("RST_EXPANDER", Pin.OUT)
mcp = MCP23009E(i2c, address=MCP23009_I2C_ADDR, reset_pin=reset)

# Configuration des boutons (entrée + pull-up)
mcp.setup(MCP23009_BTN_UP, MCP23009_DIR_INPUT, pullup=MCP23009_PULLUP)
mcp.setup(MCP23009_BTN_DOWN, MCP23009_DIR_INPUT, pullup=MCP23009_PULLUP)
mcp.setup(MCP23009_BTN_LEFT, MCP23009_DIR_INPUT, pullup=MCP23009_PULLUP)
mcp.setup(MCP23009_BTN_RIGHT, MCP23009_DIR_INPUT, pullup=MCP23009_PULLUP)

# Lecture (actif bas comme les boutons A/B/MENU)
mcp.get_level(MCP23009_BTN_UP)  # MCP23009_LOGIC_LOW = appuyé

# Interruptions (optionnel, nécessite interrupt_pin=Pin("INT_EXPANDER", Pin.IN))
mcp.interrupt_on_falling(MCP23009_BTN_UP, callback)
mcp.interrupt_on_raising(MCP23009_BTN_UP, callback)
mcp.interrupt_on_change(MCP23009_BTN_UP, callback)  # reçoit le niveau en paramètre
```

## Contenu existant dans le repo (ne pas dupliquer)

| Dossier | Contenu |
|---------|---------|
| LED/blink | Cycle RGB avec affichage texte |
| LED/basic_toggle | Toggle simple |
| BUTTON/set_led_on | Bouton → LED |
| SCREEN/text | Affichage texte |
| SCREEN/steami_faces | Smileys bitmap 8×8 scalés |
| SCREEN/steami_animation | Animation |
| SENSOR/show_distance | VL53L1X → écran |
| SENSOR/show_luminosity | APDS9960 → écran |
| SENSOR/show_temp_humidity | HTS221 → écran |
| SENSOR/show_fuel_gauge | BQ27441 → écran |
| GAME/snake | Snake dans cercle |
| GAME/dinoSteam | Dino runner |
| GAME/ticTacToe | Morpion |
| BLE/STeaMi_adv | Advertising BLE |
| BLE/STeaMi_talk | Communication bidirectionnelle peripheral/central |
| BLE/Thermometer_Scanner | Scanner BLE thermomètre |
| DEMO/ | Menu combiné (sensors, buzzer, LED, screen, button, gesture) |
| SCENARIO/1,2,3 | Multi-cartes BLE avec rôles peripheral/relay |
| BASIC/PWM/Servo_Sweep | Balayage servo avec auto-détection timer |
| ROBOT/KS4034F/ | Moteurs, suivi de ligne, ultrason, servo scanner |
| BATTERY/ | Profiling consommation par périphérique |

## Ce qu'il reste à faire

### Série "Un capteur à la fois" (9 tutoriels)

Principe : **un pattern identique décliné pour chaque capteur/actionneur**. Même structure en 5 étapes, mêmes noms de fonctions, même layout écran.

| Fichier | Composant | Fonction clé |
|---------|-----------|-------------|
| 01_temperature/main.py | HTS221 | `lire()` → `capteur.temperature()` |
| 02_humidite/main.py | HTS221 | `lire()` → `capteur.humidity()` |
| 03_distance/main.py | VL53L1X | `lire()` → `capteur.read()` |
| 04_luminosite/main.py | APDS9960 | `lire()` → `capteur.readAmbientLight()` |
| 05_batterie/main.py | BQ27441 | `lire()` → `capteur.state_of_charge()` |
| 06_boutons/main.py | Boutons A/B/MENU | `lire()` → test `value() == 0` |
| 07_led_rgb/main.py | LED RGB | `actionner(led)` → `on()`/`off()` |
| 08_buzzer/main.py | Speaker | `actionner(freq, duree)` → bitbang |
| 09_ecran/main.py | SSD1327 | 4 fonctions de dessin (texte, rect, cercle, damier) |

Chaque tutoriel a un `README.md` avec objectif, composant, structure, sortie série et "Pour aller plus loin".

### Série "Projets combinés" (proposés, PAS ENCORE CODÉS)



Projets qui combinent plusieurs capteurs/actionneurs :

1. **Smiley réactif** — Boutons + distance + lumière → expression sur écran
2. **Theremin lumineux** — Distance → fréquence buzzer + barre visuelle
3. **Feux tricolores** — LED RGB + boutons + distance → machine à états
4. **Gardien de salle** — Distance + LED + buzzer → alarme avec seuil
5. **Station confort** — Temp + humidité → indice de confort + jauge circulaire
6. **Luxmètre scientifique** — Lumière → graphe temporel scrolling + série
7. **Talkie-Walkie Morse** — BLE + boutons + buzzer → communication Morse
8. **Radar de poche** — Servo + distance → vue radar sur écran circulaire
9. **Podomètre connecté** — Distance/accéléromètre + BLE → compteur de pas
10. **Escape Game** — Tous capteurs → scénario narratif multi-énigmes
11. **Réseau de capteurs** — Multi-cartes BLE → centralisation données
12. **Robot expressif** — KS4034F + smileys + sons → robot avec émotions

### Série "Explorations" — hardware et patterns non couverts (PAS ENCORE CODÉS)

Tutoriels qui comblent les lacunes : hardware inexploité, patterns logiciels absents, capacités écran sous-utilisées.

**Hardware inexploité :**

1. **D-PAD navigation** — MCP23009E, polling I2C, menu directionnel sur écran → premier usage du D-PAD
2. **Proximité** — APDS9960 mode proximité (0-255), barre graphique réactive → mode capteur jamais montré
3. **Horloge / chronomètre** — RTC (`pyb.RTC()`), formatage temps, affichage persistant → RTC jamais utilisé
4. **GPIO extension** — Pins P0-P16, ADC (`pyb.ADC()`), lecture analogique → connecteurs jamais exploités
5. **Capteur externe Qwiic** — I2C(3), scan bus, protocole I2C générique → bus externe jamais illustré

**Patterns logiciels :**

6. **Multitâche asyncio** — `async/await`, `asyncio.gather()`, tâches capteur + écran + boutons en parallèle → pattern fondamental jamais enseigné
7. **Interruptions (IRQ)** — `Pin.irq()` sur boutons, `mcp.interrupt_on_change()` sur D-PAD, réveil sur événement → tout est en polling actuellement
8. **Machine à états** — enum d'états, transitions, pattern réactif → structure de base des programmes interactifs
9. **Enregistreur de données** — `open()`/`write()`/`read()` sur flash interne, format CSV, timestamps RTC → filesystem jamais utilisé
10. **Console série bidirectionnelle** — `sys.stdin`/`input()`, commandes depuis le PC, protocole texte → seul `print()` est montré

**Capacités écran :**

11. **Palette de gris** — 16 niveaux, dégradés, `display.lookup()` pour remapper la palette → tout est en noir/blanc actuellement
12. **Grapheur de capteur** — graphe scrolling, barre horizontale/verticale, jauge circulaire, axes gradués → aucune visualisation de données

### Améliorations possibles de la série "Un capteur à la fois"

- Version "avec barre graphique" : même pattern mais avec une jauge visuelle en plus du texte
- Version "avec historique" : graphe des N dernières valeurs qui scrolle
- Versions Arduino et MakeCode des mêmes tutoriels

## Conventions de code

- **Langue du code** : anglais pour les commentaires et noms de fonctions
- **Langue des textes écran** : anglais sans accents (limitation du driver SSD1327)
- **Fichiers autonomes** : chaque `main.py` contient tout (pas de `pins.py` partagé)
- **Pattern capteur** : étape 1 (écran) → 2 (capteur) → 3 (lire) → 4 (afficher) → 5 (boucle)
- **Pattern actionneur** : même chose mais (actionner) au lieu de (lire)
- **Print série** : toujours en parallèle de l'affichage écran
- **Sleep** : 0.5s par défaut, 0.1s pour les boutons, 2s pour la batterie

## Commandes utiles

```bash
# Copier un script sur la carte
mpremote connect auto fs cp 01_temperature/main.py :main.py
mpremote connect auto reset

# Ouvrir le REPL
mpremote connect auto

# Lister les fichiers sur la carte
mpremote connect auto fs ls
```