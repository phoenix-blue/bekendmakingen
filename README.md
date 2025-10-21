# Overheid Bekendmakingen - Home Assistant Integratie

Een Home Assistant integratie voor het ophalen van officiële bekendmakingen van Nederlandse gemeenten via de overheids-API.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=phoenix-blue&repository=bekendmakingen)

## Wat doet deze integratie?

Deze integratie haalt automatisch bekendmakingen op van Nederlandse gemeenten zoals:
- Bouwvergunningen 
- Sloopvergunningen
- Milieumeldingen
- APV vergunningen
- Evenementenmeldingen
- En meer...

De bekendmakingen worden weergegeven als sensors in Home Assistant met locatie-informatie op de kaart.

## Installatie

### Via HACS (Aanbevolen)

1. Voeg deze repository toe aan HACS als custom repository
2. Zoek naar "Overheid Bekendmakingen" in HACS
3. Installeer de integratie
4. Herstart Home Assistant
5. Ga naar Instellingen  Apparaten & Services  Integratie toevoegen
6. Zoek naar "Overheid Bekendmakingen"

### Handmatige installatie

1. Download alle bestanden uit de custom_components/overheid_bekendmakingen map
2. Plaats deze in <config>/custom_components/overheid_bekendmakingen/
3. Herstart Home Assistant
4. Voeg de integratie toe via Instellingen  Apparaten & Services

## Configuratie

Bij het instellen van de integratie kun je opgeven:

- **Locatie**: GPS-coördinaten (gebruikt Home Assistant locatie standaard)
- **Zoekradius**: Afstand in meters rond de locatie (1000-50000m)
- **Update interval**: Hoe vaak er nieuwe data wordt opgehaald (1-24 uur)
- **Debug**: Voor probleemoplossing en uitgebreide logging

## Wat krijg je?

### Sensors

- **Hoofdsensor**: Totaal aantal bekendmakingen met laatste melding
- **Type sensors**: Per type bekendmaking (bouwen, milieu, etc.) met clickable links
- **Individuele sensors**: Voor elke bekendmaking apart
- **Geschiedenis sensors**: Historisch overzicht per type

### Kaartweergave 

- Bekendmakingen worden getoond op de Home Assistant kaart
- Elk type krijgt een passend icoon (hamer voor bouwen, blad voor milieu, etc.)
- Clickable locaties met details

### Bedieningselementen

- **Update knop**: Handmatig data verversen
- **Zoekradius instelling**: Aanpasbare radius via number entity
- **Update interval**: Aanpasbaar interval via number entity

## Kenmerken

- **Clickable links**: URLs in attributes zijn direct klikbaar
- **GPS integratie**: Automatische Google Maps links voor locaties
- **Slimme iconen**: Verschillende iconen per type bekendmaking
- **Nederlandse gemeenten**: Werkt met alle Nederlandse gemeenten
- **Real-time data**: Gebruikt officiële overheids-API
- **Gebruiksvriendelijk**: Eenvoudige configuratie via UI
- **Locatie filtering**: Radius-gebaseerde filtering met Haversine-formule
- **Privacy-vriendelijk**: Filtert automatisch AVG-gevoelige publicaties uit

## API Bron

Deze integratie gebruikt de officiële Nederlandse overheids-API:
- **Bron**: 
epository.overheid.nl
- **Protocol**: SRU (Search/Retrieve via URL)
- **Data**: Officiële bekendmakingen van alle Nederlandse gemeenten

## Inspiratie

Deze integratie is geïnspireerd door het uitstekende werk van [@basgroot](https://github.com/basgroot/bekendmakingen). Veel dank voor de inspiratie en referentie-implementatie.

## Versie 2.1.3 - Nieuwe Features

✅ **Locatie filtering**: Accurate radius-gebaseerde filtering geïmplementeerd  
✅ **Privacy filtering**: Bepaalde publicatietypen worden automatisch uitgefilterd  
✅ **Verbeterde coordinaat verwerking**: Gebaseerd op basgroot referentie-implementatie

## TODO / Roadmap

- [ ] Icoontjes maps toewijzen
- [x] Locatie filtering verbeteren (✅ v2.1.3)
- [x] Privacy-gevoelige publicaties filteren (✅ v2.1.3)
- [ ] Performance optimalisaties voor grote datasets

## Ondersteuning

Voor vragen, suggesties of problemen:
- Maak een [GitHub Issue](https://github.com/phoenix-blue/bekendmakingen/issues)
- Check de Home Assistant logs voor foutmeldingen

## Licentie

Dit project is gelicentieerd onder de MIT Licentie.

---

**Disclaimer**: Deze integratie is niet officieel verbonden aan de Nederlandse overheid. Het gebruikt publieke API's voor het ophalen van openbare bekendmakingen.
