# Overheid Bekendmakingen Sensor - Home Assistant Integratie

Deze integratie haalt lokaal relevante overheidsbekendmakingen op en toont deze als sensor in Home Assistant. De bekendmakingen worden opgehaald van [Officiële Bekendmakingen](https://www.officielebekendmakingen.nl), zoals bouwvergunningen, verkeersbesluiten en andere gemeentelijke meldingen.

## Functies

- Ophalen van overheidsbekendmakingen op basis van GPS-locatie.
- Weergave van de laatste bekende bekendmaking, bijbehorende URL en timestamp.
- Extra informatie zoals latitude, longitude en de radius van de zoekopdracht.
- Automatische intervalconfiguratie.
- Mogelijkheid om handmatig te verversen via een service.
- Volledige configuratie via de UI, geen `configuration.yaml` nodig.

## Installatie

### Manuele installatie:

1. Download de laatste release van de repository.
2. Kopieer de map `overheid_bekendmakingen` naar je Home Assistant `custom_components` directory.
3. Start Home Assistant opnieuw op.
4. Voeg de integratie toe via de UI: *Instellingen* > *Apparaten & Services* > *Integraties* > *Toevoegen* > zoek op "Overheid Bekendmakingen".

## Configuratie

De module configureert zich automatisch via een config flow. Je kunt de volgende instellingen aanpassen:

- **Automatische GPS-locatie:** Laat de integratie automatisch je locatie gebruiken.
- **Radius:** Stel een radius in voor de zoekopdracht (in kilometers).
- **Update-interval:** Stel het interval in waarop de bekendmakingen worden opgehaald (in uren).

**Opmerking:** De optie voor handmatige GPS-locatie-invoer en debug-optie zijn verwijderd om de integratie eenvoudiger en betrouwbaarder te maken.

## Voorbeeld

De sensor toont de volgende gegevens:

| Attribuut         | Beschrijving                                  |
| ----------------- | --------------------------------------------- |
| `state`           | Timestamp van de laatste bekende bekendmaking  |
| `latest_title`    | Titel van de nieuwste bekendmaking            |
| `latest_url`      | URL naar de bekendmaking                      |
| `latitude`        | Gebruikte latitude voor de zoekopdracht       |
| `longitude`       | Gebruikte longitude voor de zoekopdracht      |
| `range_km`        | Radius voor de zoekopdracht                   |

## Gebruik

- **Handmatige verversing:** Gebruik de `manual_refresh` service om de bekendmakingen handmatig te verversen.
- **Automatische updates:** Bekendmakingen worden automatisch opgehaald op basis van het ingestelde interval.

## To Do

- Verbeteringen in de integratie voor het ondersteunen van automatiseringen en scripts.
- Validatie van URL's en foutafhandeling.
- Weergave van de bekendmakingen op een kaart.
- Verwijderen van debuglogregels.

## Bron van gegevens

De bekendmakingen worden opgehaald van [Officiële Bekendmakingen](https://www.officielebekendmakingen.nl). Deze data wordt verstrekt onder de **Open Data Licentie Nederland (ODbL)**.

## Licentie

Deze integratie is gelicentieerd onder de MIT-licentie. Zie het `LICENSE`-bestand voor meer details.

De data van overheidsbekendmakingen wordt verstrekt onder de **Open Data Licentie Nederland (ODbL)**.
