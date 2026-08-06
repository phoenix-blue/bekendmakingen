# Architectuur

## Lokale service

`toon2_bekendmakingen` leest `/mnt/data/tsc/bekendmakingen.json`. Bij een nieuw
adres vraagt de service maximaal 25 adreskandidaten bij PDOK op en accepteert
alleen een exacte overeenkomst van postcode, huisnummer en toevoeging. De
coördinaten en het adreslabel worden alleen in geheugen en het vluchtige
statusbestand bewaard.

Daarna wordt de collectie `officielepublicaties` via KOOP SRU doorzocht met:

```text
c.product-area==officielepublicaties
AND dt.modified>=YYYY-MM-DD
AND w.locatiepunt within/etrs89 "latitude longitude radius_km"
```

De service leest maximaal 100 recente records, extraheert titel, datum, type,
instantie, officiële URL en het dichtstbijzijnde locatiepunt en publiceert
atomair naar `/var/volatile/tmp/bekendmakingen-status.json`. De QML-app leest
dit bestand iedere twee seconden. Configuratiewijzigingen worden zonder
herstart binnen dezelfde periode opgepakt.

## Meldingen en privacy

De eerste succesvolle synchronisatie vult alleen de deduplicatielijst. Bij een
latere synchronisatie verhoogt een nieuw publicatie-ID `alert_sequence`. QML
opent bij een stijgend volgnummer de korte popup. Een herstart van service of
QML herhaalt oude meldingen niet.

Publicaties over echtscheiding, faillissement, surseance van betaling,
gerechtelijke oproepingen, ondercuratelestelling en handlichting worden niet in
het lokale statusbestand opgenomen. Het statusbestand bevat maximaal 25
publicaties en staat op een vluchtig bestandssysteem.

## Externe koppelingen

- PDOK Locatieserver v3.1: officiële, open Nederlandse geocodeerservice.
- KOOP SRU 2.0: officiële zoekinterface voor de collectie Officiële
  Publicaties.

Er worden geen sleutels, Toon-cloudgegevens of externe accounts gebruikt.
