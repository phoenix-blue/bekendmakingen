# Overheid Bekendmakingen Sensor

Met de **Overheid Bekendmakingen Sensor** kun je lokaal relevante overheidsbekendmakingen ophalen en weergeven in Home Assistant. Deze integratie maakt gebruik van GPS-locaties (automatisch of handmatig ingesteld) om bekendmakingen op te halen uit de database van [Officiële Bekendmakingen](https://www.officielebekendmakingen.nl).

### Functies
- **Laatste bekendmakingen:** Haal de nieuwste bekendmakingen op, inclusief details zoals de titel en URL van de bekendmaking.
- **GPS-integratie:** Gebruik automatisch je huidige Home Assistant GPS-locatie of stel handmatig een locatie in.
- **Radius en interval configuratie:** Stel een zoekradius in kilometers in, evenals een interval voor automatische updates.
- **Handmatige updates:** Start handmatig een update met een simpele druk op een knop in de interface.

### Hoe te gebruiken
Na installatie en configuratie van de integratie via de Home Assistant UI, maakt deze automatisch een sensor aan die de meest recente bekendmaking toont. De sensor bevat verschillende attributen, zoals de laatste titel, URL, locatie en meer.

### Voordelen
- **Automatische updates:** De integratie haalt periodiek nieuwe bekendmakingen op zonder dat je handmatig hoeft in te grijpen.
- **Handmatige controle:** Je kunt op elk moment de gegevens verversen via de Home Assistant interface.
- **Gebruiksvriendelijke configuratie:** Volledig configureerbaar via de Home Assistant UI, zonder dat `configuration.yaml` nodig is.

### Toekomstige Verbeteringen
- Ondersteuning voor automatiseringen en scripts.
- Validatie en controle van opgehaalde URL's.
- Weergave van bekendmakingen op een kaartweergave.
- Verwijderen van debug-logregels voor productieversies.

Bekijk de volledige documentatie in de `README.md` voor meer details.

---

# Government Announcements Sensor

With the **Government Announcements Sensor**, you can fetch and display locally relevant government announcements in Home Assistant. This integration uses GPS locations (automatically or manually set) to retrieve announcements from the [Official Announcements](https://www.officielebekendmakingen.nl) database.

### Features
- **Latest Announcements:** Fetch the latest announcements, including details such as the title and URL of the announcement.
- **GPS Integration:** Automatically use your current Home Assistant GPS location or manually set a location.
- **Radius and Interval Configuration:** Set a search radius in kilometers, as well as an interval for automatic updates.
- **Manual Updates:** Manually trigger an update with a simple press of a button in the interface.

### How to Use
After installing and configuring the integration via the Home Assistant UI, it will automatically create a sensor that displays the most recent announcement. The sensor contains various attributes, such as the latest title, URL, location, and more.

### Benefits
- **Automatic Updates:** The integration periodically fetches new announcements without requiring manual intervention.
- **Manual Control:** You can refresh the data at any time via the Home Assistant interface.
- **User-Friendly Configuration:** Fully configurable via the Home Assistant UI, without needing `configuration.yaml`.

### Future Improvements
- Support for automations and scripts.
- Validation and checking of retrieved URLs.
- Display of announcements on a map view.
- Removal of debug log lines for production versions.

See the full documentation in the `README.md` for more details.
