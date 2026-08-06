package main

import (
	"context"
	"encoding/json"
	"errors"
	"image/png"
	"math"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func TestNormalizeConfig(t *testing.T) {
	config, err := normalizeConfig(Config{Postcode: " 3511 aa ", HouseNumber: 20, HouseNumberAddition: " a "})
	if err != nil {
		t.Fatal(err)
	}
	if config.Postcode != "3511AA" || config.HouseNumberAddition != "A" || config.RadiusKM != 5 || config.LookbackDays != 42 {
		t.Fatalf("onverwachte configuratie: %#v", config)
	}
	if config.Notifications == nil || !*config.Notifications {
		t.Fatal("meldingen staan niet standaard aan")
	}
	if _, err := normalizeConfig(Config{Postcode: "0123AA", HouseNumber: 1}); err == nil {
		t.Fatal("ongeldige postcode is geaccepteerd")
	}
	if _, err := normalizeConfig(Config{Postcode: "3511AA"}); err == nil {
		t.Fatal("ontbrekend huisnummer is geaccepteerd")
	}
}

func TestParsePointAndHaversine(t *testing.T) {
	lat, lon, err := parsePoint("POINT(5.1155496 52.09260622)")
	if err != nil {
		t.Fatal(err)
	}
	if math.Abs(lat-52.09260622) > 1e-8 || math.Abs(lon-5.1155496) > 1e-8 {
		t.Fatalf("onverwacht punt: %.8f, %.8f", lat, lon)
	}
	distance := haversineKM(52.0894, 5.1103, 52.3780, 4.9003)
	if distance < 34 || distance > 36 {
		t.Fatalf("afstand = %.2f km", distance)
	}
}

func TestResolveAddressRequiresExactAddition(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.URL.Query().Get("q") != "3511AA 20A" {
			t.Errorf("onverwachte zoektekst: %q", request.URL.Query().Get("q"))
		}
		filters := request.URL.Query()["fq"]
		if len(filters) != 3 {
			t.Errorf("onverwachte filters: %#v", filters)
		}
		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte(`{"response":{"numFound":2,"docs":[
			{"postcode":"3511AA","huisnummer":20,"weergavenaam":"Zakkendragerssteeg 20","centroide_ll":"POINT(5.116 52.092)"},
			{"postcode":"3511AA","huisnummer":20,"huisletter":"A","weergavenaam":"Zakkendragerssteeg 20A","centroide_ll":"POINT(5.117 52.093)"}
		]}}`))
	}))
	defer server.Close()

	r := newRuntime()
	location, err := r.resolveAddress(context.Background(), Config{
		Postcode: "3511AA", HouseNumber: 20, HouseNumberAddition: "A", GeocodeURL: server.URL,
	})
	if err != nil {
		t.Fatal(err)
	}
	if location.Label != "Zakkendragerssteeg 20A" || math.Abs(location.Lon-5.117) > 0.0001 {
		t.Fatalf("verkeerd adres gekozen: %#v", location)
	}
}

func fixtureRecord(id, title string) map[string]any {
	raw := `{
		"recordData":{"gzd":{
			"originalData":{"meta":{
				"owmskern":{"identifier":"` + id + `","title":"Lange titel","type":{"$":"omgevingsvergunning"},"creator":{"$":"Utrecht"},"modified":"2026-08-04"},
				"owmsmantel":{"abstract":"` + title + `"},
				"tpmeta":{"activiteit":{"$":"bouwen"},"datumTijdstipWijzigingWork":"2026-08-04T10:00:00+02:00","gebiedsmarkering":{"Adres":{"locatiepunt":"52.092645 5.115155","straatnaam":"Teststraat","huisnummer":40,"woonplaats":"Utrecht"}}}
			}},
			"enrichedData":{"preferredUrl":"https://zoek.officielebekendmakingen.nl/` + id + `.html"}
		}}
	}`
	var record map[string]any
	if err := json.Unmarshal([]byte(raw), &record); err != nil {
		panic(err)
	}
	return record
}

func TestExtractPublication(t *testing.T) {
	publication, ok := extractPublication(fixtureRecord("gmb-2026-1", "Aanvraag dakkapel"), Location{Lat: 52.0926, Lon: 5.1155})
	if !ok {
		t.Fatal("publicatie niet gelezen")
	}
	if publication.Title != "Aanvraag dakkapel" || publication.Type != "bouwen" || publication.Date != "2026-08-04" {
		t.Fatalf("onverwachte publicatie: %#v", publication)
	}
	if !publication.HasDistance || publication.DistanceKM > 0.1 || !strings.Contains(publication.Location, "Teststraat 40") {
		t.Fatalf("locatie niet goed verwerkt: %#v", publication)
	}
}

func TestDecodeSingleRecord(t *testing.T) {
	raw, _ := json.Marshal(fixtureRecord("gmb-2026-2", "Test"))
	records, err := decodeRecords(raw)
	if err != nil || len(records) != 1 {
		t.Fatalf("enkel record niet verwerkt: %v, %d", err, len(records))
	}
}

func TestSummarizeWarmsThenAlerts(t *testing.T) {
	r := newRuntime()
	r.config = defaultConfig()
	now := time.Date(2026, 8, 5, 12, 0, 0, 0, time.UTC)
	first := Publication{ID: "one", Title: "Eerste", Date: "2026-08-05"}
	r.summarize([]Publication{first}, 1, now)
	if r.status.AlertSequence != 0 {
		t.Fatal("eerste synchronisatie gaf een melding")
	}
	second := Publication{ID: "two", Title: "Tweede", Date: "2026-08-05"}
	r.summarize([]Publication{second, first}, 2, now.Add(time.Hour))
	if r.status.AlertSequence != 1 || r.status.AlertCount != 1 || r.status.AlertTitle != "Tweede" {
		t.Fatalf("nieuwe publicatie niet gemeld: %#v", r.status)
	}
	r.summarize([]Publication{second}, 1, now.Add(2*time.Hour))
	r.summarize([]Publication{second, first}, 2, now.Add(3*time.Hour))
	if r.status.AlertSequence != 1 {
		t.Fatal("tijdelijk verdwenen publicatie is ten onrechte opnieuw gemeld")
	}
}

func TestSyncQRCodes(t *testing.T) {
	r := newRuntime()
	r.qrDir = t.TempDir()
	stalePath := filepath.Join(r.qrDir, "stale.png")
	if err := os.WriteFile(stalePath, []byte("oud"), 0644); err != nil {
		t.Fatal(err)
	}
	publications := []Publication{{
		ID: "gmb-2026-1", URL: "https://zoek.officielebekendmakingen.nl/gmb-2026-1.html",
	}}
	if err := r.syncQRCodes(publications); err != nil {
		t.Fatal(err)
	}
	if publications[0].QRPath == "" || !strings.HasPrefix(publications[0].QRPath, "file://") {
		t.Fatalf("QR-pad ontbreekt: %#v", publications[0])
	}
	qrPath := strings.TrimPrefix(publications[0].QRPath, "file://")
	file, err := os.Open(qrPath)
	if err != nil {
		t.Fatal(err)
	}
	defer file.Close()
	config, err := png.DecodeConfig(file)
	if err != nil {
		t.Fatalf("QR-bestand is geen geldige PNG: %v", err)
	}
	if config.Width != 256 || config.Height != 256 {
		t.Fatalf("onverwachte QR-afmeting: %dx%d", config.Width, config.Height)
	}
	if _, err := os.Stat(stalePath); !errors.Is(err, os.ErrNotExist) {
		t.Fatalf("oude QR-code is niet verwijderd: %v", err)
	}
}

func TestPrivacyFilter(t *testing.T) {
	if !excludedPublication(Publication{Type: "Bekendmakingen faillissement"}) {
		t.Fatal("faillissement is niet gefilterd")
	}
	if excludedPublication(Publication{Title: "Aanvraag omgevingsvergunning"}) {
		t.Fatal("normale vergunning is ten onrechte gefilterd")
	}
}
