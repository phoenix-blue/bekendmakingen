# Overheid Bekendmakingen Sensor - Home Assistant Integratie
BUG - ERROR in Sensor.py, not stable at this moment.

Deze integratie haalt lokaal relevante overheidsbekendmakingen op en toont deze als sensor in Home Assistant. De bekendmakingen worden opgehaald van [Officiële Bekendmakingen](https://www.officielebekendmakingen.nl), zoals bouwvergunningen, verkeersbesluiten en andere gemeentelijke meldingen.

## Functies

- Ophalen van overheidsbekendmakingen op basis van GPS-locatie.
- Weergave van de laatste bekende bekendmaking en bijbehorende URL.
- Extra informatie zoals latitude, longitude en de radius van de zoekopdracht.
- Handmatige vernieuwing via een button.
- Automatische intervalconfiguratie.
- Geen configuratie via `configuration.yaml` nodig; volledige configuratie via de UI.

## Installatie

### Manuele installatie:

1. Download de laatste release van de repository.
2. Kopieer de map `overheid_bekendmakingen` naar je Home Assistant `custom_components` directory.
3. Start Home Assistant opnieuw op.
4. Voeg de integratie toe via de UI: *Instellingen* > *Apparaten & Services* > *Integraties* > *Toevoegen* > zoek op "Overheid Bekendmakingen".

## Configuratie

De module configureert zich automatisch via een config-flow. Je kunt de volgende instellingen aanpassen:

- **Automatische GPS-locatie:** Laat de integratie automatisch je locatie gebruiken.
- **Handmatige GPS-locatie:** Voer handmatig een locatie in.
- **Radius:** Stel een radius in voor de zoekopdracht (in kilometers).
- **Update-interval:** Stel het interval in waarop de bekendmakingen worden opgehaald (in uren).

## Voorbeeld

De sensor toont de volgende gegevens:

| Attribuut         | Beschrijving                                 |
| ----------------- | -------------------------------------------- |
| `state`           | Titel van de laatste bekende bekendmaking    |
| `latest_title`    | Titel van de nieuwste bekendmaking           |
| `latest_url`      | URL naar de bekendmaking                     |
| `latitude`        | Gebruikte latitude voor de zoekopdracht      |
| `longitude`       | Gebruikte longitude voor de zoekopdracht     |
| `range_km`        | Radius voor de zoekopdracht                  |

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

---

# Government Announcements Sensor - Home Assistant Integration

This integration fetches locally relevant government announcements and displays them as a sensor in Home Assistant. The announcements are retrieved from [Official Announcements](https://www.officielebekendmakingen.nl), such as building permits, traffic decisions, and other municipal notifications.

## Features

- Fetch government announcements based on GPS location.
- Display the latest known announcement and associated URL.
- Extra information such as latitude, longitude, and the radius of the search query.
- Manual refresh via a button.
- Automatic interval configuration.
- No configuration via `configuration.yaml` needed; full configuration via the UI.

## Installation

### Manual Installation:

1. Download the latest release from the repository.
2. Copy the `overheid_bekendmakingen` folder to your Home Assistant `custom_components` directory.
3. Restart Home Assistant.
4. Add the integration via the UI: *Settings* > *Devices & Services* > *Integrations* > *Add* > search for "Overheid Bekendmakingen".

## Configuration

The module configures itself automatically via a config flow. You can adjust the following settings:

- **Automatic GPS Location:** Let the integration automatically use your location.
- **Manual GPS Location:** Manually enter a location.
- **Radius:** Set a radius for the search query (in kilometers).
- **Update Interval:** Set the interval at which the announcements are fetched (in hours).

## Example

The sensor displays the following data:

| Attribute         | Description                                   |
| ----------------- | --------------------------------------------- |
| `state`           | Title of the latest known announcement        |
| `latest_title`    | Title of the newest announcement              |
| `latest_url`      | URL to the announcement                       |
| `latitude`        | Latitude used for the search query            |
| `longitude`       | Longitude used for the search query           |
| `range_km`        | Radius for the search query                   |

## To Do

- Improvements in the integration to support automations and scripts.
- URL validation and error handling.
- Display announcements on a map.
- Remove debug log lines.

## Data Source

The announcements are retrieved from [Official Announcements](https://www.officielebekendmakingen.nl). This data is provided under the **Open Data License Netherlands (ODbL)**.

## License

This integration is licensed under the MIT license. See the `LICENSE` file for more details.

The data of government announcements is provided under the **Open Data License Netherlands (ODbL)**.
