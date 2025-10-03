# Overheid Bekendmakingen voor Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/phoenix-blue/bekendmakingen.svg)](https://github.com/phoenix-blue/bekendmakingen/releases)
[![License](https://img.shields.io/github/license/phoenix-blue/bekendmakingen.svg)](LICENSE)

**Nederlandse overheidsbekendmakingen direct in je Home Assistant!**

Deze integratie toont lokale bekendmakingen van de Nederlandse overheid als sensoren in Home Assistant. Bekendmakingen verschijnen ook als **oranje balletjes op de kaart** zodat je precies kunt zien waar ze zich bevinden.

## 🎯 Wat doet deze integratie?

- **📍 Kaartweergave**: Bekendmakingen verschijnen als oranje balletjes op je Home Assistant kaart
- **📊 Sensor**: Tekstsensor met details van de laatste bekendmaking  
- **🔔 Meldingen**: Automatische notificaties bij nieuwe bekendmakingen in jouw buurt
- **⚙️ Configureerbaar**: Stel zelf je zoekradius in (100m tot 10km)

### Welke bekendmakingen krijg je te zien?

- Bouwvergunningen
- Verkeersbesluiten  
- Omgevingsvergunningen
- Bestemmingsplanwijzigingen
- Gemeentelijke meldingen
- En nog veel meer overheidszaken

## 🚀 Installatie

### Via HACS (Aanbevolen)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Phoenix-Blue&repository=https%3A%2F%2Fgithub.com%2Fphoenix-blue%2Fbekendmakingen)

1. Ga naar HACS in je Home Assistant
2. Klik op "Integrations"
3. Klik op de drie puntjes rechtsboven
4. Selecteer "Custom repositories" 
5. Voeg deze URL toe: `https://github.com/phoenix-blue/bekendmakingen`
6. Categorie: "Integration"
7. Zoek naar "Overheid Bekendmakingen" en installeer
8. Herstart Home Assistant

### Handmatige installatie

1. Download de `overheid_bekendmakingen` map naar je `custom_components` directory
2. Herstart Home Assistant
3. Ga naar Instellingen → Apparaten & Services → Integraties
4. Klik "Toevoegen" en zoek "Overheid Bekendmakingen"

## ⚙️ Configuratie

Na installatie configureer je de integratie via de Home Assistant interface:

| Instelling | Beschrijving | Standaard |
|------------|--------------|-----------|
| **Automatische locatie** | Gebruik je HA locatie | Aan |
| **Handmatige coördinaten** | Voer eigen locatie in | Uit |
| **Zoekradius** | Afstand in meters | 1000m |
| **Update interval** | Uren tussen updates | 12 uur |

## 📍 Kaart en sensoren

### Op de kaart
- **Oranje balletjes** tonen locaties van bekendmakingen
- Klik op een balletje voor details
- Zoom in/uit om meer of minder details te zien

### Sensor informatie
```
sensor.overheid_bekendmakingen
```

**Attributen:**
- `state`: Aantal gevonden bekendmakingen
- `laatste_titel`: Titel van nieuwste bekendmaking  
- `laatste_url`: Link naar volledige tekst
- `laatste_datum`: Publicatiedatum
- `bekendmakingen`: Lijst met alle gevonden bekendmakingen
- `breedtegraad` / `lengtegraad`: Gebruikte zoeklocatie
- `radius_meters`: Gebruikte zoekradius

## 🔔 Automatisering voorbeeld

Krijg een melding bij nieuwe bekendmakingen:

```yaml
automation:
  - alias: "Nieuwe bekendmaking in de buurt"
    trigger:
      - platform: state
        entity_id: sensor.overheid_bekendmakingen
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state|int > trigger.from_state.state|int }}"
    action:
      - service: notify.mobile_app_jouw_telefoon
        data:
          title: "🏛️ Nieuwe bekendmaking"
          message: "{{ state_attr('sensor.overheid_bekendmakingen', 'laatste_titel') }}"
          data:
            url: "{{ state_attr('sensor.overheid_bekendmakingen', 'laatste_url') }}"
```

## 📡 Data bron

Alle informatie komt van [Officiële Bekendmakingen](https://www.officielebekendmakingen.nl):
- **Realtime**: Direct van overheidsbronnen
- **Compleet**: Alle Nederlandse gemeenten en overheidsorganisaties  
- **Betrouwbaar**: Officiële overheids-API
- **Open data**: Vrij beschikbaar onder ODBL licentie

## 🔧 Probleemoplossing

**Geen bekendmakingen gevonden?**
- Controleer je coördinaten
- Vergroot de zoekradius
- Check je internetverbinding

**Integratie laadt niet?**
- Home Assistant versie ≥ 2024.1.0 vereist
- Controleer de logs voor foutmeldingen

**Debug logging inschakelen:**
```yaml
logger:
  logs:
    custom_components.overheid_bekendmakingen: debug
```

## 🤝 Bijdragen

Bijdragen zijn welkom! Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor meer informatie.

## 📄 Licentie

MIT License - zie [LICENSE](LICENSE) bestand voor details.

Overheidsdata valt onder de [Open Data Licentie Nederland (ODBL)](https://data.overheid.nl/licenties-voor-hergebruik).
