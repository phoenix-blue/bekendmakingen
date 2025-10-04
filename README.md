# 🏛️ Overheid Bekendmakingen voor Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/phoenix-blue/bekendmakingen.svg)](https://github.com/phoenix-blue/bekendmakingen/releases)
[![License](https://img.shields.io/github/license/phoenix-blue/bekendmakingen.svg)](LICENSE)

> ## ⚠️ **BETA VERSIE** - v2024.10.04.3
> 
> 🧪 **Dit is een bètaversie** met veel nieuwe functies! Help ons verbeteren:
> - 🐛 **Bug gevonden?** → [Meld het hier](https://github.com/phoenix-blue/bekendmakingen/issues)
> - 💡 **Suggestie/feedback?** → [Open een discussion](https://github.com/phoenix-blue/bekendmakingen/discussions)
> - ⭐ **Werkt goed?** → Laat een ⭐ achter op GitHub!
>
> **Nieuw in deze versie:** Dynamische configuratie, archief functie, map integratie en veel meer!

---

**🇳🇱 Nederlandse overheidsbekendmakingen direct in je Home Assistant!**

Houd lokale bekendmakingen van de Nederlandse overheid bij via een complete sensor suite. Van bouwvergunningen tot verkeersmaatregelen - alles netjes georganiseerd in Home Assistant met kaartweergave, archief functie en realtime configuratie.

## ✨ **Overzicht van Functies**

### 🎛️ **Complete Sensor Suite (7 sensoren)**
- 📊 **Hoofd sensor** - Overzicht met alle bekendmakingen  
- 📋 **Recent (24h)** - Laatste bekendmakingen met mooie tekst formatting
- 📚 **Archief** - Volledige geschiedenis configureerbaar bewaren
- 🎯 **Range config** - Realtime zoekbereik aanpassen (100-10000m)
- ⏰ **Interval config** - Realtime scan interval (1-24h)
- 📄 **Latest title** + 🔗 **Latest URL** sensoren

### 🗺️ **Map Integratie**  
- **Oranje markers** op de kaart voor alle bekendmakingen
- **Configureerbare weergaveduur** (hoeveel dagen markers blijven)
- **Klikbare markers** met directe link naar officiele documenten

### ⚙️ **Geavanceerde Configuratie**
- **� Services** voor automatie (`set_range`, `set_interval`, `manual_refresh`)
- **📱 Input helpers** automatisch aangemaakt voor eenvoudige bediening
- **⚡ Realtime updates** - geen herstart Home Assistant nodig!
- **📊 Live statistieken** in sensor attributen

### 📱 **Perfect Home Assistant Integratie**
- **🏠 Device grouping** - alle sensoren netjes onder 1 apparaat
- **🎨 Dashboard ready** - mooie tekst formatting voor cards
- **🔔 Automation friendly** - events en services voor slimme acties
- **🌐 HACS compatible** - eenvoudige installatie en updates

### 🏛️ **Welke bekendmakingen zie je?**

| Type | Voorbeelden |
|------|-------------|
| 🏗️ **Bouw** | Bouwvergunningen, sloopvergunningen, monumentenstatus |
| 🚗 **Verkeer** | Wegafsluitingen, parkeerregels, verkeerslichten |
| 🌳 **Omgeving** | Kapvergunningen, bestemmingsplannen, milieuvergunningen |  
| 🎪 **Evenementen** | Marktvergunningen, evenementenvergunningen, terrassen |
| 📋 **Bestuur** | Gemeenteraad besluiten, inspraakprocedures, subsidies |

---

## 🚀 **Installatie**

### 📦 **Via HACS (Aanbevolen)**

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Phoenix-Blue&repository=https%3A%2F%2Fgithub.com%2Fphoenix-blue%2Fbekendmakingen)

1. 🏠 Open **HACS** in je Home Assistant
2. 🔧 Ga naar **"Integrations"**  
3. ⚙️ Klik op de **drie puntjes** rechtsboven
4. 📁 Selecteer **"Custom repositories"**
5. 🌐 Voeg toe: `https://github.com/phoenix-blue/bekendmakingen`
6. 📂 Categorie: **"Integration"**
7. 🔍 Zoek **"Overheid Bekendmakingen"** en installeer
8. 🔄 **Herstart Home Assistant** (volledig vereist voor beta!)

### 💻 **Handmatige Installatie**

```bash
# Download naar custom_components directory
cd /config/custom_components/
git clone https://github.com/phoenix-blue/bekendmakingen.git overheid_bekendmakingen
```

1. 📁 Download de `overheid_bekendmakingen` map naar `custom_components/`
2. 🔄 **Herstart Home Assistant** 
3. ⚙️ Ga naar **Instellingen** → **Apparaten & Services** → **Integraties**
4. ➕ Klik **"Toevoegen"** en zoek **"Overheid Bekendmakingen"**

### ✅ **Vereisten**

- 🏠 **Home Assistant** ≥ 2024.1.0
- 🌐 **Internet verbinding** voor overheidsdatabase
- 📍 **Locatie ingesteld** in HA (of handmatig invoeren)

---

## ⚙️ **Configuratie**

### 🔧 **Basis Setup**

Na installatie configureer je via: **Instellingen** → **Apparaten & Services** → **Overheid Bekendmakingen** → **Configureren**

| 🎛️ Instelling | 📝 Beschrijving | ⚙️ Standaard | 🔄 Realtime |
|---------------|-----------------|---------------|---------------|
| **📍 Locatie** | Gebruik HA locatie of handmatig | Automatisch | - |
| **🎯 Zoekradius** | Bereik in meters (100-10000) | 1000m | ✅ |
| **⏰ Scan interval** | Update frequentie (1-24h) | 12h | ✅ |  
| **🗺️ Map weergave** | Hoeveel dagen markers tonen (1-30) | 7d | ✅ |
| **📚 Archief** | Hoeveel dagen bewaren (7-365) | 30d | ✅ |
| **🔍 Debug** | Uitgebreide logging | Uit | ✅ |

### 🔧 **Realtime Aanpassen (NIEUW!)**

#### Via Services (Developer Tools)
```yaml
# Zoekbereik aanpassen  
service: overheid_bekendmakingen.set_range
data:
  range_meters: 2000

# Scan interval aanpassen
service: overheid_bekendmakingen.set_interval  
data:
  interval_hours: 6

# Handmatige refresh
service: overheid_bekendmakingen.manual_refresh
```

#### Via Input Helpers (Automatisch aangemaakt)
```yaml
# Deze helpers worden automatisch aangemaakt:
input_number.bekendmakingen_range_[id]     # Bereik instellen
input_number.bekendmakingen_interval_[id]  # Interval instellen  
input_number.bekendmakingen_map_days_[id]  # Map weergave dagen
```

#### Via Configuration Options  
- ⚙️ **Instellingen** → **Apparaten & Services** → **Overheid Bekendmakingen** → **Configureren**
- 🔄 Changes worden **direct toegepast** zonder herstart!

---

## � **Sensoren & Entiteiten**

### 🏠 **Device Grouping**
Alle sensoren verschijnen netjes gegroepeerd onder **"Overheid Bekendmakingen"** apparaat:

```
📱 Overheid Bekendmakingen
├── 📊 Hoofd Sensor (overheid_bekendmakingen)
├── 📋 Recent 24h (overheid_bekendmakingen_recent_24h)  
├── 📚 Archief (overheid_bekendmakingen_archive)
├── 🎯 Range Config (overheid_bekendmakingen_range_config)
├── ⏰ Interval Config (overheid_bekendmakingen_interval_config)  
├── 📄 Latest Title (overheid_bekendmakingen_latest_title)
└── 🌐 Latest URL (overheid_bekendmakingen_latest_url)
```

### 📊 **Hoofd Sensor**
```yaml
sensor.overheid_bekendmakingen
```

**State:** Aantal gevonden bekendmakingen  
**Attributen:**
```yaml
latitude: 52.3676              # Zoeklocatie
longitude: 4.9041  
range_km: 2.0                  # Bereik in kilometers
radius_meters: 2000            # Bereik in meters
update_interval_hours: 6.0     # Scan frequentie
debug_mode: false              # Debug status
total_records: 8               # Aantal bekendmakingen
latest_title: "Omgevingsvergunning..."  # Laatste titel
latest_url: "https://..."     # Laatste URL  
records: [...]                 # Volledige lijst
```

### 📋 **Recent Sensor (NIEUW!)**
```yaml
sensor.overheid_bekendmakingen_recent_24h
```

**State:** Aantal bekendmakingen laatste 24h  
**Speciale attributen:**
```yaml
display_text: |              # Mooie tekstweergave voor dashboard
  📋 Recente Bekendmakingen (24u):
  1. Omgevingsvergunning Hoofdstraat 123
  2. Verkeersmaatregel Dorpsplein  
  3. Bouwvergunning Kerkstraat 45
count: 3                     # Aantal recent
last_update: "2024-10-04T14:30:00"
```

### 📚 **Archief Sensor (NIEUW!)**  
```yaml
sensor.overheid_bekendmakingen_archive
```

**State:** Totaal aantal gearchiveerde bekendmakingen
**Speciale attributen:**
```yaml
display_text: |              # Volledig archief overzicht
  📚 Archief Bekendmakingen:
  1. Omgevingsvergunning Hoofdstraat 123
  2. Verkeersmaatregel Dorpsplein
  ...
  ... en 20 meer (totaal: 25)
count: 25                    # Totaal archief
```

### 🎯 **Config Sensoren (NIEUW!)**
```yaml
sensor.overheid_bekendmakingen_range_config    # Huidige range in meters
sensor.overheid_bekendmakingen_interval_config # Huidige interval in uren
```

### 🗺️ **Map Markers**  
```yaml
geo_location.bekendmaking_map_*    # 0-10 markers op kaart
```
- **🟠 Oranje markers** voor Nederlandse overheid styling
- **📍 Klikbaar** met directe link naar officiele documenten  
- **⏱️ Configureerbare weergaveduur** (1-30 dagen)
- **🎯 Smart positioning** met kleine offset voor zichtbaarheid

---

## 🤖 **Automatie & Dashboard**

### 🔔 **Basis Notificaties**
```yaml
# Nieuwe bekendmaking alert
automation:
  - alias: "📢 Nieuwe Bekendmaking"
    trigger:
      - platform: state
        entity_id: sensor.overheid_bekendmakingen_recent_24h
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state|int > trigger.from_state.state|int }}"
    action:
      - service: notify.mobile_app_jouw_telefoon
        data:
          title: "🏛️ Nieuwe bekendmaking in je buurt!"
          message: "{{ state_attr('sensor.overheid_bekendmakingen', 'latest_title') }}"
          data:
            url: "{{ state_attr('sensor.overheid_bekendmakingen', 'latest_url') }}"
            icon: "https://www.overheid.nl/favicon.ico"
```

### 🎯 **Slimme Range Automatie**  
```yaml
# Groter bereik overdag, kleiner 's avonds
automation:
  - alias: "🌅 Ochtend: Groter bereik"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: overheid_bekendmakingen.set_range
        data:
          range_meters: 3000

  - alias: "🌙 Avond: Kleiner bereik"  
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: overheid_bekendmakingen.set_range
        data:
          range_meters: 1000
```

### 🏠 **Dashboard Cards**

#### **Overzichtskaart**
```yaml
type: entities
title: 📋 Bekendmakingen Overzicht
entities:
  - sensor.overheid_bekendmakingen_recent_24h
  - sensor.overheid_bekendmakingen_archive  
  - sensor.overheid_bekendmakingen_range_config
  - sensor.overheid_bekendmakingen_interval_config
```

#### **Tekst Overzicht** 
```yaml
type: markdown
title: 📰 Laatste Bekendmakingen
content: |
  {{ state_attr('sensor.overheid_bekendmakingen_recent_24h', 'display_text') }}
  
  ---
  
  📊 **Statistieken:**
  - Bereik: {{ states('sensor.overheid_bekendmakingen_range_config') }}m
  - Interval: {{ states('sensor.overheid_bekendmakingen_interval_config') }}h  
  - Archief: {{ states('sensor.overheid_bekendmakingen_archive') }} bekendmakingen
```

#### **Quick Actions**
```yaml
type: horizontal-stack
cards:
  - type: button
    name: "🔄 Refresh"
    tap_action:
      action: call-service
      service: overheid_bekendmakingen.manual_refresh
      
  - type: button  
    name: "🎯 Groot bereik"
    tap_action:
      action: call-service
      service: overheid_bekendmakingen.set_range
      service_data:
        range_meters: 5000
```

#### **Map Kaart**
```yaml
type: map
title: 🗺️ Bekendmakingen Kaart  
entities:
  - geo_location.bekendmaking_map
dark_mode: false
hours_to_show: 168  # 1 week
```

---

## 📡 **Data & Bron**

### 🏛️ **Officiële Overheidsdata**
Alle informatie komt van [repository.overheid.nl](https://repository.overheid.nl):
- ✅ **100% Officieel** - Direct van overheidsbronnen
- 🇳🇱 **Compleet** - Alle Nederlandse gemeenten en overheidsorganisaties  
- 🔄 **Realtime** - Live updates via SRU API
- 📊 **Betrouwbaar** - Gecertificeerde overheids-API
- 🆓 **Open Data** - Vrij beschikbaar onder ODBL licentie

### � **API Details**
- **Endpoint:** `https://repository.overheid.nl/sru`
- **Protocol:** Search/Retrieve via URL (SRU 2.0)  
- **Format:** XML met standardized metadata
- **Coverage:** Lokale bekendmakingen van alle Nederlandse gemeenten

---

## 🔧 **Troubleshooting**

### 🚫 **Geen bekendmakingen gevonden?**

| 🔍 Probleem | 💡 Oplossing |
|-------------|--------------|
| **Lege sensor** | Vergroot zoekradius via config of service |
| **Verkeerde locatie** | Check coördinaten in configuratie |
| **Oude data** | Gebruik `manual_refresh` service |
| **Geen internet** | Controleer HA internetverbinding |

### ⚠️ **Integratie laadt niet?** 

| 🚨 Error | 🛠️ Fix |
|----------|---------|
| **"Integration not found"** | Herstart HA na installatie (volledig!) |
| **"Cannot import"** | HA versie ≥ 2024.1.0 vereist |
| **"Setup failed"** | Check logs voor details |
| **"404 errors"** | Update naar v2024.10.04.3+ |

### 🔍 **Debug Logging**
```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.overheid_bekendmakingen: debug
```

### � **Beta Issues**
- 🐛 **Onverwacht gedrag?** → [Open een issue](https://github.com/phoenix-blue/bekendmakingen/issues)
- 💬 **Vragen?** → [Start een discussion](https://github.com/phoenix-blue/bekendmakingen/discussions)  
- ⚡ **Feature request?** → [Feature request](https://github.com/phoenix-blue/bekendmakingen/issues/new?template=feature_request.md)

---

## 🤝 **Support & Community**

### 📞 **Hulp Nodig?**

| 🎯 Type | 📍 Waar |  
|---------|---------|
| 🐛 **Bug Report** | [GitHub Issues](https://github.com/phoenix-blue/bekendmakingen/issues) |
| 💡 **Feature Ideas** | [GitHub Discussions](https://github.com/phoenix-blue/bekendmakingen/discussions) |  
| ❓ **Vragen** | [Home Assistant Community](https://community.home-assistant.io) |
| 📚 **Documentatie** | [Deze README](README.md) + [CONTRIBUTING.md](CONTRIBUTING.md) |

### 💻 **Bijdragen Welkom!**

```bash
# Development setup
git clone https://github.com/phoenix-blue/bekendmakingen.git
cd bekendmakingen
# Maak je wijzigingen en open een Pull Request!
```

**Ideeën voor bijdragen:**
- 🎨 UI verbeteringen  
- 🔧 Bug fixes
- 📊 Nieuwe sensor types
- 🌐 Meertalige support  
- 📱 Mobile app integratie

### ⭐ **Vind je het nuttig?**
- ⭐ **Star** het project op GitHub
- � **Share** met andere HA gebruikers  
- 💬 **Review** op HACS of Community forum

---

## �📄 **Licenties & Credits**

### 📋 **Software Licentie**
```
MIT License - Zie LICENSE bestand voor details
Copyright (c) 2024 Phoenix-Blue
```

### 🏛️ **Overheidsdata Licentie**  
```
Open Data Licentie Nederland (ODBL)
Bron: repository.overheid.nl
Copyright: Nederlandse Overheid
```

### 🙏 **Credits**
- 🏠 **Home Assistant** team voor het geweldige platform
- 🏛️ **Nederlandse Overheid** voor open data beleid  
- 👥 **Community** voor feedback en suggesties
- 🧪 **Beta testers** voor hulp met deze versie

---

### 🚀 **Changelog v2024.10.04.3**

| ✨ Nieuw | 🔧 Verbeterd | 🐛 Fixed |
|----------|--------------|----------|
| + 7 sensor types | Realtime config | 404 API errors |
| + Map integratie | Device grouping | Range configuratie |  
| + Services API | Tekst formatting | Options handling |
| + Input helpers | Error handling | Live updates |

**Van basis sensor naar complete suite!** 🎉

---

<div align="center">

**🇳🇱 Made with ❤️ for the Dutch Home Assistant community**

[![GitHub](https://img.shields.io/badge/GitHub-phoenix--blue-blue?logo=github)](https://github.com/phoenix-blue/bekendmakingen)
[![HACS](https://img.shields.io/badge/HACS-Compatible-orange?logo=home-assistant)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-blue?logo=home-assistant)](https://home-assistant.io)

</div>
