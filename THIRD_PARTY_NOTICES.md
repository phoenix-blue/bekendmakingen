# Bronnen en attributie

- Het app-idee is gebaseerd op de MIT-gelicentieerde Home Assistant-integratie
  [phoenix-blue/bekendmakingen](https://github.com/phoenix-blue/bekendmakingen).
  De Toon-implementatie en Go-service zijn zelfstandig geschreven en nemen geen
  Home Assistant-code mee.
- Adressen worden geocodeerd met de open PDOK Locatieserver van het Kadaster.
  PDOK vermeldt onder meer de BAG als gegevensbron; de dienst en brongegevens
  hebben hun eigen gebruiksvoorwaarden en licenties.
- Bekendmakingen komen uit de openbare SRU-interface van KOOP op
  `repository.overheid.nl`. De volledige officiële tekst blijft beschikbaar via
  `zoek.officielebekendmakingen.nl`.
- QR-codes worden lokaal gemaakt met de MIT-gelicentieerde Go-bibliotheek
  [skip2/go-qrcode](https://github.com/skip2/go-qrcode).

Deze app is niet verbonden aan of goedgekeurd door PDOK, KOOP, het Kadaster of
de Nederlandse overheid.
