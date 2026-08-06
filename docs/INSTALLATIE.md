# Installatie op Toon 2

## Via een Toon repository

Gebruik `dist/bekendmakingen-0.1.4.tar.gz` als app-pakket en
`ToonRepo-entry.xml` als repository-item. De installer zet symlinks voor de
achtergrondservice in `/qmf/bin` en `/etc/rc5.d` en start de service meteen.

Na installatie:

1. voeg de tegel **Bekendmakingen** toe;
2. open de tegel en kies **Instellingen**;
3. vul postcode en huisnummer in, plus de toevoeging indien van toepassing;
4. kies straal, verversinterval en terugkijkperiode;
5. sla op en wacht enkele seconden op de eerste synchronisatie.

## Handmatige controle via SSH

```sh
/qmf/bin/bekendmakingen-service.sh status
/qmf/bin/bekendmakingen-service.sh test
cat /var/volatile/tmp/bekendmakingen-status.json
tail -n 50 /var/volatile/log/bekendmakingen.log
```

Een testactie gebruikt de actuele configuratie en schrijft meteen een nieuw
statusbestand. Fouten zoals een onbekend adres of onbereikbare bron verschijnen
zowel in dit bestand als op het instellingenscherm.

## Verwijderen

De Toon-installer roept `bekendmakingen.sh uninstall` aan. De service en
symlinks worden verwijderd. De persoonlijke configuratie in
`/mnt/data/tsc/bekendmakingen.json` blijft bewust bewaard voor een eventuele
herinstallatie. Verwijder dit bestand handmatig als de instellingen niet
bewaard mogen blijven:

```sh
rm -f /mnt/data/tsc/bekendmakingen.json
```

Het statusbestand en de lokaal gemaakte QR-codes staan onder `/var/volatile`
en verdwijnen bij een herstart van Toon.
