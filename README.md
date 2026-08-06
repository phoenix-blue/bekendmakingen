# Bekendmakingen voor Toon 2

> Testversie 0.1.4. Deze branch is bedoeld om de app en Store-vermelding te
> controleren voordat een officiële TSC Store-aanvraag wordt gedaan.

Bekendmakingen toont officiële Nederlandse overheidspublicaties rond een exact
adres. Denk aan aanvragen en besluiten over bouwen, slopen, milieu, verkeer,
water, horeca en evenementen. De tegel toont het aantal publicaties binnen de
ingestelde periode; tikken opent een lijst en daarna een detailweergave.

## Werking

1. PDOK zet postcode, huisnummer en een eventuele toevoeging om naar één exact
   BAG-adres en een kaartpunt.
2. De lokale ARM-service vraagt via de officiële KOOP-SRU-interface publicaties
   binnen de ingestelde straal op.
3. Toon leest alleen het lokale statusbestand. Er is geen Home Assistant,
   account of API-sleutel nodig.
4. De eerste synchronisatie geeft bewust geen melding. Alleen later nieuw
   verschenen publicaties kunnen tien seconden bovenin Toon verschijnen.

Standaard zoekt de app binnen 5 km, kijkt hij 42 dagen terug en synchroniseert
hij iedere zes uur. Instelbare grenzen zijn 0,25–25 km, 1–90 dagen en
30–1440 minuten. Privacygevoelige categorieën zoals faillissementen,
echtscheidingen en gerechtelijke oproepingen worden lokaal uitgefilterd.

## Privacy

De app heeft geen account, advertenties, telemetrie of server van de maker.
Het adres staat lokaal op Toon en gaat via HTTPS naar PDOK om het kaartpunt te
bepalen; KOOP ontvangt vervolgens het kaartpunt en de gekozen zoekstraal. Lees
[PRIVACY.md](PRIVACY.md) voor de volledige uitleg en verwijderinstructies.

## Bouwen

```sh
make test
make build
make package
```

De ARMv7-binary is statisch en gebruikt alleen de Go-standaardbibliotheek. Het
installatiearchief komt in `dist/bekendmakingen-0.1.4.tar.gz`.

## Grenzen

De resultaten zijn afhankelijk van de locatiegegevens die de publicerende
overheid aan de officiële publicatie toevoegt. Een publicatie zonder bruikbare
geografische markering kan niet in de straalzoekactie verschijnen. Toon toont
een samenvatting; de tekst op Officiëlebekendmakingen.nl is de officiële bron.

Zie [docs/INSTALLATIE.md](docs/INSTALLATIE.md) voor installatie,
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) voor technische details en
[store/README.md](store/README.md) voor het TSC Store-materiaal.

De app is een onafhankelijk communityproject en is niet verbonden aan of
goedgekeurd door Eneco, Quby, PDOK, KOOP, het Kadaster of de Nederlandse
overheid.
