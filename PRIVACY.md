# Privacy

Bekendmakingen werkt zonder account, advertentienetwerk, analyseplatform of
server van de maker. De app verwerkt alleen gegevens die nodig zijn om
officiële publicaties in de buurt te vinden.

## Welke gegevens worden verwerkt

- Postcode, huisnummer en eventuele toevoeging.
- Zoekstraal, terugkijkperiode, verversinterval en meldingsvoorkeur.
- Het kaartpunt en de adresomschrijving die PDOK voor het opgegeven adres
  teruggeeft.
- Openbare bekendmakingen die KOOP binnen de gekozen straal teruggeeft.

De instellingen staan alleen op Toon in
`/mnt/data/tsc/bekendmakingen.json`. Het installatieprogramma zet de
bestandsrechten op `600`. De actuele resultaten, het kaartpunt en lokaal
gemaakte QR-codes staan in het vluchtige bestandssysteem onder
`/var/volatile`; ze verdwijnen bij een herstart.

## Externe diensten

Bij de standaardinstellingen maakt de app rechtstreeks via HTTPS verbinding
met twee officiële overheidsdiensten:

1. Het volledige adres gaat naar de PDOK Locatieserver om één exact BAG-adres
   en kaartpunt te vinden.
2. Het kaartpunt, de zoekstraal en de periode gaan naar de openbare
   KOOP-SRU-interface om bekendmakingen te zoeken. Het adres zelf wordt niet
   meegestuurd in deze zoekvraag.

De app verstuurt niets naar de maker. PDOK en KOOP kunnen technisch
noodzakelijke serverlogboeken bijhouden volgens hun eigen voorwaarden. Een
beheerder kan de bron-URL's handmatig in het configuratiebestand wijzigen; in
dat geval gaan de genoemde gegevens naar die zelfgekozen HTTPS-diensten.

## Zichtbaarheid en verwijderen

Titels van nieuwe openbare bekendmakingen kunnen als melding op het
Toon-scherm verschijnen. Schakel dit uit via **Instellingen** als anderen het
scherm kunnen zien.

Bij verwijderen van de app blijft de persoonlijke configuratie bewaard om een
herinstallatie gemakkelijk te maken. Verwijder die desgewenst via SSH:

```sh
rm -f /mnt/data/tsc/bekendmakingen.json
```

Meld een privacyprobleem via een GitHub-issue, maar plaats daar geen adres,
configuratiebestand of volledig logbestand bij.
