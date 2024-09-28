# Overheid Bekendmakingen Sensor - Home Assistant Integratie

Deze integratie haalt lokaal relevante overheidsbekendmakingen op en toont deze als sensor in Home Assistant. De bekendmakingen worden opgehaald van [Officiële Bekendmakingen](https://www.officielebekendmakingen.nl), zoals bouwvergunningen, verkeersbesluiten en andere gemeentelijke meldingen.

## Functies

- Ophalen van overheidsbekendmakingen op basis van GPS-locatie.
- Weergave van de laatste bekende bekendmaking en bijbehorende URL.
- Extra informatie zoals latitude, longitude en de radius van de zoekopdracht.
- Handmatige vernieuwing via een button.
- Automatische intervalconfiguratie.
- Geen configuratie via `configuration.yaml` nodig; volledige configuratie via de UI.

## Installatie

1. ** Installatie via HACS (aanbevolen):**

Open je Home Assistant instance en open een repository in de Home Assistant Community Store.

[![Open je Home Assistant instance en toon het dialoogvenster om een repository toe te voegen met een vooraf ingevulde URL.](https://camo.githubusercontent.com/8cec5af6ba93659beb5352741334ef3bbee70c4cb725f20832a1b897dfb8fc5f/68747470733a2f2f6d792e686f6d652d617373697374616e742e696f2f6261646765732f686163735f7265706f7369746f72792e737667)](https://my.home-assistant.io/redirect/hacs_repository/?owner=phoenix-blue&repository=bekendmakingen)

1. Gebruik de custom repo link: `https://github.com/phoenix-blue/bekendmakingen`
2. Selecteer het categorietype: Integratie
3. Zodra het daar is (nog steeds in HACS), klik op de INSTALL-knop
4. Herstart Home Assistant
5. Na het herstarten, ga in de HA UI naar Configuratie (het ⚙️ linksonder) -> Apparaten en Diensten, klik op + Integratie toevoegen en zoek naar "Overheid Bekendmakingen"

2. **Manuele installatie:**
   - Download de laatste release van de repository.
   - Kopieer de map `overheid_bekendmakingen` naar je Home Assistant `custom_components` directory.
   - Start Home Assistant opnieuw op.
   - Voeg de integratie toe via de UI: *Instellingen* > *Apparaten & Services* > *Integraties* > *Toevoegen* > zoek op "Overheid Bekendmakingen".

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
| `state`           | Titel van de laatste bekende bekendmaking     |
| `latest_title`    | Titel van de nieuwste bekendmaking            |
| `latest_url`      | URL naar de bekendmaking                      |
| `latitude`        | Gebruikte latitude voor de zoekopdracht       |
| `longitude`       | Gebruikte longitude voor de zoekopdracht      |
| `range_km`        | Radius voor de zoekopdracht                   |

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

1. ** Installation via HACS (recommended): **

Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.

[![Open your Home Assistant instance and show the add repository dialog with a specific repository URL pre-filled.](https://camo.githubusercontent.com/8cec5af6ba93659beb5352741334ef3bbee70c4cb725f20832a1b897dfb8fc5f/68747470733a2f2f6d792e686f6d652d617373697374616e742e696f2f6261646765732f686163735f7265706f7369746f72792e737667)](https://my.home-assistant.io/redirect/hacs_repository/?owner=phoenix-blue&repository=bekendmakingen)

1. Use the custom repo link: `https://github.com/phoenix-blue/bekendmakingen`
2. Select the category type: Integration
3. Once it's there (still in HACS), click the INSTALL button
4. Restart Home Assistant
5. Once restarted, in the HA UI go to Configuration (the ⚙️ in the lower left) -> Devices and Services, click + Add Integration and search for "Overheid Bekendmakingen"

2. **Manual Installation:**
   - Download the latest release from the repository.
   - Copy the `overheid_bekendmakingen` folder to your Home Assistant `custom_components` directory.
   - Restart Home Assistant.
   - Add the integration via the UI: *Settings* > *Devices & Services* > *Integrations* > *Add* > search for "Overheid Bekendmakingen".

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
