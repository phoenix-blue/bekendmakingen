package main

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"math"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"syscall"
	"time"

	qrcode "github.com/skip2/go-qrcode"
)

const (
	version                = "0.1.4"
	defaultConfigPath      = "/mnt/data/tsc/bekendmakingen.json"
	defaultStatusPath      = "/var/volatile/tmp/bekendmakingen-status.json"
	defaultGeocodeURL      = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free"
	defaultPublicationsURL = "https://repository.overheid.nl/sru"
	maximumStatusItems     = 25
)

var (
	postcodePattern = regexp.MustCompile(`^[1-9][0-9]{3}[A-Z]{2}$`)
	additionPattern = regexp.MustCompile(`^[A-Z0-9-]{0,10}$`)
	pointPattern    = regexp.MustCompile(`^POINT\((-?[0-9.]+) (-?[0-9.]+)\)$`)
)

type Config struct {
	Postcode            string  `json:"postcode"`
	HouseNumber         int     `json:"house_number"`
	HouseNumberAddition string  `json:"house_number_addition,omitempty"`
	RadiusKM            float64 `json:"radius_km"`
	PollIntervalMinutes int     `json:"poll_interval_minutes"`
	LookbackDays        int     `json:"lookback_days"`
	MaxResults          int     `json:"max_results"`
	Notifications       *bool   `json:"notifications,omitempty"`
	GeocodeURL          string  `json:"geocode_url,omitempty"`
	PublicationsURL     string  `json:"publications_url,omitempty"`
}

type Location struct {
	Postcode    string
	HouseNumber int
	Addition    string
	Label       string
	Lat         float64
	Lon         float64
}

type Publication struct {
	ID          string  `json:"id"`
	Title       string  `json:"title"`
	Type        string  `json:"type"`
	Date        string  `json:"date"`
	URL         string  `json:"url,omitempty"`
	QRPath      string  `json:"qr_path,omitempty"`
	Authority   string  `json:"authority,omitempty"`
	Location    string  `json:"location,omitempty"`
	DistanceKM  float64 `json:"distance_km,omitempty"`
	HasDistance bool    `json:"has_distance"`
}

type Status struct {
	Configured    bool          `json:"configured"`
	Online        bool          `json:"online"`
	Postcode      string        `json:"postcode,omitempty"`
	HouseNumber   int           `json:"house_number,omitempty"`
	Addition      string        `json:"house_number_addition,omitempty"`
	LocationLabel string        `json:"location_label,omitempty"`
	Latitude      float64       `json:"latitude,omitempty"`
	Longitude     float64       `json:"longitude,omitempty"`
	RadiusKM      float64       `json:"radius_km"`
	LookbackDays  int           `json:"lookback_days"`
	Count         int           `json:"count"`
	SourceCount   int           `json:"source_count"`
	Truncated     bool          `json:"truncated"`
	Publications  []Publication `json:"publications"`
	AlertSequence uint64        `json:"alert_sequence"`
	AlertCount    int           `json:"alert_count,omitempty"`
	AlertTitle    string        `json:"alert_title,omitempty"`
	AlertAt       string        `json:"alert_at,omitempty"`
	LastError     string        `json:"last_error,omitempty"`
	LastSuccessAt string        `json:"last_success_at,omitempty"`
	UpdatedAt     string        `json:"updated_at"`
	Version       string        `json:"version"`
}

type pdokResponse struct {
	Response struct {
		NumFound int `json:"numFound"`
		Docs     []struct {
			Postcode      string `json:"postcode"`
			HouseNumber   int    `json:"huisnummer"`
			HouseLetter   string `json:"huisletter"`
			HouseAddition string `json:"huisnummertoevoeging"`
			DisplayName   string `json:"weergavenaam"`
			CentroidWGS84 string `json:"centroide_ll"`
		} `json:"docs"`
	} `json:"response"`
}

type sruResponse struct {
	SearchRetrieveResponse struct {
		NumberOfRecords int `json:"numberOfRecords"`
		Records         struct {
			Record json.RawMessage `json:"record"`
		} `json:"records"`
	} `json:"searchRetrieveResponse"`
}

type runtime struct {
	client           *http.Client
	config           Config
	location         Location
	status           Status
	seen             map[string]struct{}
	warmed           bool
	configLoaded     bool
	locationResolved bool
	qrDir            string
}

func boolPointer(value bool) *bool { return &value }

func defaultConfig() Config {
	return Config{
		RadiusKM:            5,
		PollIntervalMinutes: 360,
		LookbackDays:        42,
		MaxResults:          100,
		Notifications:       boolPointer(true),
		GeocodeURL:          defaultGeocodeURL,
		PublicationsURL:     defaultPublicationsURL,
	}
}

func normalizePostcode(value string) string {
	return strings.ReplaceAll(strings.ToUpper(strings.TrimSpace(value)), " ", "")
}

func normalizeAddition(value string) string {
	return strings.ReplaceAll(strings.ToUpper(strings.TrimSpace(value)), " ", "")
}

func normalizeConfig(config Config) (Config, error) {
	defaults := defaultConfig()
	config.Postcode = normalizePostcode(config.Postcode)
	config.HouseNumberAddition = normalizeAddition(config.HouseNumberAddition)
	if config.RadiusKM == 0 {
		config.RadiusKM = defaults.RadiusKM
	}
	if config.PollIntervalMinutes == 0 {
		config.PollIntervalMinutes = defaults.PollIntervalMinutes
	}
	if config.LookbackDays == 0 {
		config.LookbackDays = defaults.LookbackDays
	}
	if config.MaxResults == 0 {
		config.MaxResults = defaults.MaxResults
	}
	if config.Notifications == nil {
		config.Notifications = defaults.Notifications
	}
	if config.GeocodeURL == "" {
		config.GeocodeURL = defaults.GeocodeURL
	}
	if config.PublicationsURL == "" {
		config.PublicationsURL = defaults.PublicationsURL
	}
	if config.Postcode == "" {
		if config.HouseNumber != 0 || config.HouseNumberAddition != "" {
			return config, errors.New("vul eerst een postcode in")
		}
	} else {
		if !postcodePattern.MatchString(config.Postcode) {
			return config, errors.New("postcode moet bestaan uit vier cijfers en twee letters")
		}
		if config.HouseNumber < 1 || config.HouseNumber > 99999 {
			return config, errors.New("huisnummer moet tussen 1 en 99999 liggen")
		}
	}
	if !additionPattern.MatchString(config.HouseNumberAddition) {
		return config, errors.New("toevoeging mag alleen letters, cijfers en een streepje bevatten")
	}
	if config.RadiusKM < 0.25 || config.RadiusKM > 25 {
		return config, errors.New("straal moet tussen 0,25 en 25 km liggen")
	}
	if config.PollIntervalMinutes < 30 || config.PollIntervalMinutes > 1440 {
		return config, errors.New("verversinterval moet tussen 30 en 1440 minuten liggen")
	}
	if config.LookbackDays < 1 || config.LookbackDays > 90 {
		return config, errors.New("terugkijkperiode moet tussen 1 en 90 dagen liggen")
	}
	if config.MaxResults < 1 || config.MaxResults > 100 {
		return config, errors.New("maximaal aantal resultaten moet tussen 1 en 100 liggen")
	}
	if err := validHTTPSURL(config.GeocodeURL); err != nil {
		return config, fmt.Errorf("ongeldige adresbron: %w", err)
	}
	if err := validHTTPSURL(config.PublicationsURL); err != nil {
		return config, fmt.Errorf("ongeldige publicatiebron: %w", err)
	}
	return config, nil
}

func validHTTPSURL(value string) error {
	parsed, err := url.Parse(value)
	if err != nil || parsed.Scheme != "https" || parsed.Host == "" {
		return errors.New("alleen een volledige https-url is toegestaan")
	}
	return nil
}

func loadConfig(path string) (Config, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return Config{}, err
	}
	var config Config
	if err := json.Unmarshal(raw, &config); err != nil {
		return Config{}, fmt.Errorf("configuratie lezen: %w", err)
	}
	return normalizeConfig(config)
}

func configKey(config Config) string {
	notifications := config.Notifications != nil && *config.Notifications
	return fmt.Sprintf("%s|%d|%s|%.3f|%d|%d|%d|%t|%s|%s", config.Postcode,
		config.HouseNumber, config.HouseNumberAddition, config.RadiusKM,
		config.PollIntervalMinutes, config.LookbackDays, config.MaxResults,
		notifications, config.GeocodeURL, config.PublicationsURL)
}

func parsePoint(value string) (lat, lon float64, err error) {
	parts := pointPattern.FindStringSubmatch(strings.TrimSpace(value))
	if len(parts) != 3 {
		return 0, 0, errors.New("onbekend coördinaatformaat")
	}
	lon, err = strconv.ParseFloat(parts[1], 64)
	if err != nil {
		return 0, 0, err
	}
	lat, err = strconv.ParseFloat(parts[2], 64)
	if err != nil {
		return 0, 0, err
	}
	if lat < -90 || lat > 90 || lon < -180 || lon > 180 {
		return 0, 0, errors.New("coördinaat ligt buiten het geldige bereik")
	}
	return lat, lon, nil
}

func (r *runtime) resolveAddress(ctx context.Context, config Config) (Location, error) {
	query, err := url.Parse(config.GeocodeURL)
	if err != nil {
		return Location{}, err
	}
	values := query.Query()
	searchText := fmt.Sprintf("%s %d%s", config.Postcode, config.HouseNumber, config.HouseNumberAddition)
	values.Set("q", searchText)
	values.Set("rows", "25")
	values.Add("fq", "type:adres")
	values.Add("fq", "postcode:"+config.Postcode)
	values.Add("fq", "huisnummer:"+strconv.Itoa(config.HouseNumber))
	query.RawQuery = values.Encode()

	var data pdokResponse
	if err := r.getJSON(ctx, query.String(), &data); err != nil {
		return Location{}, fmt.Errorf("adres opzoeken: %w", err)
	}
	for _, doc := range data.Response.Docs {
		addition := normalizeAddition(doc.HouseLetter + doc.HouseAddition)
		if normalizePostcode(doc.Postcode) != config.Postcode ||
			doc.HouseNumber != config.HouseNumber || addition != config.HouseNumberAddition {
			continue
		}
		lat, lon, err := parsePoint(doc.CentroidWGS84)
		if err != nil {
			return Location{}, fmt.Errorf("adrescoördinaat lezen: %w", err)
		}
		return Location{Postcode: config.Postcode, HouseNumber: config.HouseNumber,
			Addition: config.HouseNumberAddition, Label: doc.DisplayName, Lat: lat, Lon: lon}, nil
	}
	if data.Response.NumFound == 0 {
		return Location{}, errors.New("adres is niet gevonden")
	}
	return Location{}, errors.New("postcode, huisnummer en toevoeging leveren geen exacte overeenkomst op")
}

func haversineKM(lat1, lon1, lat2, lon2 float64) float64 {
	const earthRadiusKM = 6371.0088
	toRad := math.Pi / 180
	dLat := (lat2 - lat1) * toRad
	dLon := (lon2 - lon1) * toRad
	a := math.Sin(dLat/2)*math.Sin(dLat/2) +
		math.Cos(lat1*toRad)*math.Cos(lat2*toRad)*math.Sin(dLon/2)*math.Sin(dLon/2)
	return earthRadiusKM * 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))
}

func (r *runtime) fetchPublications(ctx context.Context, config Config, location Location, now time.Time) ([]Publication, int, error) {
	queryURL, err := url.Parse(config.PublicationsURL)
	if err != nil {
		return nil, 0, err
	}
	startDate := now.AddDate(0, 0, -config.LookbackDays).Format("2006-01-02")
	queryText := fmt.Sprintf("c.product-area==officielepublicaties AND dt.modified>=%s AND w.locatiepunt within/etrs89 \"%.6f %.6f %.3f\" sortBy dt.modified /sort.descending",
		startDate, location.Lat, location.Lon, config.RadiusKM)
	values := queryURL.Query()
	values.Set("query", queryText)
	values.Set("maximumRecords", strconv.Itoa(config.MaxResults))
	values.Set("startRecord", "1")
	values.Set("httpAccept", "application/json")
	queryURL.RawQuery = values.Encode()

	var response sruResponse
	if err := r.getJSON(ctx, queryURL.String(), &response); err != nil {
		return nil, 0, fmt.Errorf("bekendmakingen ophalen: %w", err)
	}
	records, err := decodeRecords(response.SearchRetrieveResponse.Records.Record)
	if err != nil {
		return nil, response.SearchRetrieveResponse.NumberOfRecords, err
	}
	publications := make([]Publication, 0, len(records))
	for _, record := range records {
		publication, ok := extractPublication(record, location)
		if ok && !excludedPublication(publication) {
			publications = append(publications, publication)
		}
	}
	sort.SliceStable(publications, func(i, j int) bool { return publications[i].Date > publications[j].Date })
	return publications, response.SearchRetrieveResponse.NumberOfRecords, nil
}

func decodeRecords(raw json.RawMessage) ([]map[string]any, error) {
	if len(raw) == 0 || string(raw) == "null" {
		return nil, nil
	}
	var records []map[string]any
	if err := json.Unmarshal(raw, &records); err == nil {
		return records, nil
	}
	var record map[string]any
	if err := json.Unmarshal(raw, &record); err != nil {
		return nil, fmt.Errorf("publicatierespons lezen: %w", err)
	}
	return []map[string]any{record}, nil
}

func object(value any) map[string]any {
	result, _ := value.(map[string]any)
	return result
}

func child(parent map[string]any, keys ...string) map[string]any {
	current := parent
	for _, key := range keys {
		current = object(current[key])
		if current == nil {
			return nil
		}
	}
	return current
}

func textValue(value any) string {
	switch typed := value.(type) {
	case string:
		return strings.TrimSpace(typed)
	case float64:
		return strconv.FormatFloat(typed, 'f', -1, 64)
	case json.Number:
		return typed.String()
	case map[string]any:
		return textValue(typed["$"])
	case []any:
		for _, item := range typed {
			if result := textValue(item); result != "" {
				return result
			}
		}
	}
	return ""
}

func asObjects(value any) []map[string]any {
	switch typed := value.(type) {
	case map[string]any:
		return []map[string]any{typed}
	case []any:
		result := make([]map[string]any, 0, len(typed))
		for _, item := range typed {
			if entry := object(item); entry != nil {
				result = append(result, entry)
			}
		}
		return result
	}
	return nil
}

func parseLocationPoint(value string) (float64, float64, bool) {
	parts := strings.Fields(value)
	if len(parts) < 2 {
		return 0, 0, false
	}
	first, err1 := strconv.ParseFloat(parts[0], 64)
	second, err2 := strconv.ParseFloat(parts[1], 64)
	if err1 != nil || err2 != nil {
		return 0, 0, false
	}
	if first >= 50 && first <= 54 && second >= 3 && second <= 8 {
		return first, second, true
	}
	if second >= 50 && second <= 54 && first >= 3 && first <= 8 {
		return second, first, true
	}
	return 0, 0, false
}

func extractLocations(tpmeta map[string]any, home Location) (string, float64, bool) {
	bestDistance := math.Inf(1)
	bestLabel := ""
	for _, marker := range asObjects(tpmeta["gebiedsmarkering"]) {
		for _, kind := range []string{"Punt", "Adres"} {
			for _, place := range asObjects(marker[kind]) {
				lat, lon, ok := parseLocationPoint(textValue(place["locatiepunt"]))
				if !ok {
					continue
				}
				distance := haversineKM(home.Lat, home.Lon, lat, lon)
				if distance >= bestDistance {
					continue
				}
				bestDistance = distance
				bestLabel = textValue(place["geometrielabel"])
				if bestLabel == "" {
					street := textValue(place["straatnaam"])
					number := textValue(place["huisnummer"])
					city := textValue(place["woonplaats"])
					bestLabel = strings.TrimSpace(strings.TrimSpace(street+" "+number) + ", " + city)
					bestLabel = strings.Trim(bestLabel, " ,")
				}
			}
		}
	}
	if math.IsInf(bestDistance, 1) {
		return "", 0, false
	}
	return bestLabel, math.Round(bestDistance*10) / 10, true
}

func extractPublication(record map[string]any, home Location) (Publication, bool) {
	meta := child(record, "recordData", "gzd", "originalData", "meta")
	if meta == nil {
		return Publication{}, false
	}
	owms := object(meta["owmskern"])
	mantel := object(meta["owmsmantel"])
	tpmeta := object(meta["tpmeta"])
	title := textValue(mantel["abstract"])
	if title == "" {
		title = textValue(owms["title"])
	}
	if title == "" {
		return Publication{}, false
	}
	publicationType := textValue(tpmeta["activiteit"])
	if publicationType == "" {
		publicationType = textValue(owms["type"])
	}
	id := textValue(owms["identifier"])
	date := textValue(tpmeta["datumTijdstipWijzigingWork"])
	if date == "" {
		date = textValue(owms["modified"])
	}
	if len(date) >= 10 {
		date = date[:10]
	}
	enriched := child(record, "recordData", "gzd", "enrichedData")
	publicationURL := ""
	if enriched != nil {
		publicationURL = textValue(enriched["preferredUrl"])
	}
	locationLabel, distance, hasDistance := extractLocations(tpmeta, home)
	return Publication{
		ID: id, Title: title, Type: publicationType, Date: date,
		URL: publicationURL, Authority: textValue(owms["creator"]),
		Location: locationLabel, DistanceKM: distance, HasDistance: hasDistance,
	}, true
}

func excludedPublication(publication Publication) bool {
	combined := strings.ToLower(publication.Type + " " + publication.Title)
	excluded := []string{
		"echtscheiding", "ontbinding huwelijk", "faillissement",
		"surseance van betaling", "gerechtelijke oproeping",
		"ondercuratelestelling", "handlichting",
	}
	for _, phrase := range excluded {
		if strings.Contains(combined, phrase) {
			return true
		}
	}
	return false
}

func (r *runtime) getJSON(ctx context.Context, endpoint string, target any) error {
	request, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
	if err != nil {
		return err
	}
	request.Header.Set("Accept", "application/json")
	request.Header.Set("User-Agent", "Toon2-Bekendmakingen/"+version)
	response, err := r.client.Do(request)
	if err != nil {
		return err
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		body, _ := io.ReadAll(io.LimitReader(response.Body, 512))
		return fmt.Errorf("bron antwoordt met HTTP %d: %s", response.StatusCode, strings.TrimSpace(string(body)))
	}
	decoder := json.NewDecoder(io.LimitReader(response.Body, 12<<20))
	if err := decoder.Decode(target); err != nil {
		return fmt.Errorf("ongeldig antwoord: %w", err)
	}
	return nil
}

func (r *runtime) summarize(publications []Publication, sourceCount int, now time.Time) {
	newItems := make([]Publication, 0)
	batchSeen := make(map[string]struct{}, len(publications))
	for _, publication := range publications {
		key := publication.ID
		if key == "" {
			key = publication.Date + "|" + publication.Title
		}
		if _, duplicate := batchSeen[key]; duplicate {
			continue
		}
		batchSeen[key] = struct{}{}
		if _, known := r.seen[key]; r.warmed && !known {
			newItems = append(newItems, publication)
		}
		r.seen[key] = struct{}{}
	}
	r.status.Online = true
	r.status.Count = len(publications)
	r.status.SourceCount = sourceCount
	r.status.Truncated = sourceCount > r.config.MaxResults
	if len(publications) > maximumStatusItems {
		publications = publications[:maximumStatusItems]
	}
	r.status.Publications = publications
	r.status.LastError = ""
	r.status.LastSuccessAt = now.Format(time.RFC3339)
	if r.warmed && len(newItems) > 0 && r.config.Notifications != nil && *r.config.Notifications {
		r.status.AlertSequence++
		r.status.AlertCount = len(newItems)
		r.status.AlertTitle = newItems[0].Title
		r.status.AlertAt = now.Format(time.RFC3339)
	}
	r.warmed = true
}

func qrFileName(publication Publication) string {
	key := publication.URL
	if key == "" {
		key = publication.ID
	}
	digest := sha256.Sum256([]byte(key))
	return fmt.Sprintf("%x.png", digest[:16])
}

func (r *runtime) syncQRCodes(publications []Publication) error {
	if r.qrDir == "" {
		return errors.New("QR-map is niet ingesteld")
	}
	if err := os.MkdirAll(r.qrDir, 0755); err != nil {
		return fmt.Errorf("QR-map maken: %w", err)
	}

	expected := make(map[string]struct{})
	limit := len(publications)
	if limit > maximumStatusItems {
		limit = maximumStatusItems
	}
	for index := 0; index < limit; index++ {
		if publications[index].URL == "" {
			continue
		}
		name := qrFileName(publications[index])
		expected[name] = struct{}{}
		path := filepath.Join(r.qrDir, name)
		if _, err := os.Stat(path); errors.Is(err, os.ErrNotExist) {
			png, encodeErr := qrcode.Encode(publications[index].URL, qrcode.Medium, 256)
			if encodeErr != nil {
				return fmt.Errorf("QR-code maken: %w", encodeErr)
			}
			temporary, createErr := os.CreateTemp(r.qrDir, ".bekendmakingen-qr-*")
			if createErr != nil {
				return createErr
			}
			temporaryName := temporary.Name()
			if chmodErr := temporary.Chmod(0644); chmodErr != nil {
				temporary.Close()
				os.Remove(temporaryName)
				return chmodErr
			}
			if _, writeErr := temporary.Write(png); writeErr != nil {
				temporary.Close()
				os.Remove(temporaryName)
				return writeErr
			}
			if closeErr := temporary.Close(); closeErr != nil {
				os.Remove(temporaryName)
				return closeErr
			}
			if renameErr := os.Rename(temporaryName, path); renameErr != nil {
				os.Remove(temporaryName)
				return renameErr
			}
		} else if err != nil {
			return err
		}
		publications[index].QRPath = "file://" + path
	}

	entries, err := os.ReadDir(r.qrDir)
	if err != nil {
		return err
	}
	for _, entry := range entries {
		if entry.IsDir() || filepath.Ext(entry.Name()) != ".png" {
			continue
		}
		if _, keep := expected[entry.Name()]; !keep {
			if err := os.Remove(filepath.Join(r.qrDir, entry.Name())); err != nil {
				return err
			}
		}
	}
	return nil
}

func (r *runtime) poll(ctx context.Context, now time.Time) error {
	publications, sourceCount, err := r.fetchPublications(ctx, r.config, r.location, now)
	if err != nil {
		return err
	}
	if err := r.syncQRCodes(publications); err != nil {
		return err
	}
	r.summarize(publications, sourceCount, now)
	return nil
}

func (r *runtime) applyConfig(ctx context.Context, config Config) (bool, error) {
	changed := !r.configLoaded || configKey(config) != configKey(r.config)
	if !changed {
		return false, nil
	}
	r.config = config
	r.configLoaded = true
	r.locationResolved = false
	r.status.Configured = config.Postcode != ""
	r.status.Postcode = config.Postcode
	r.status.HouseNumber = config.HouseNumber
	r.status.Addition = config.HouseNumberAddition
	r.status.RadiusKM = config.RadiusKM
	r.status.LookbackDays = config.LookbackDays
	r.status.Online = false
	r.status.Count = 0
	r.status.SourceCount = 0
	r.status.Publications = []Publication{}
	r.status.Truncated = false
	r.status.LastError = ""
	r.seen = make(map[string]struct{})
	r.warmed = false
	if config.Postcode == "" {
		r.location = Location{}
		r.status.LocationLabel = ""
		r.status.Latitude = 0
		r.status.Longitude = 0
		r.locationResolved = true
		return true, nil
	}
	location, err := r.resolveAddress(ctx, config)
	if err != nil {
		return true, err
	}
	r.location = location
	r.status.LocationLabel = location.Label
	r.status.Latitude = location.Lat
	r.status.Longitude = location.Lon
	r.locationResolved = true
	return true, nil
}

func newRuntime() *runtime {
	return &runtime{
		client: &http.Client{Timeout: 30 * time.Second},
		status: Status{Publications: []Publication{}, Version: version},
		seen:   make(map[string]struct{}),
		qrDir:  filepath.Join(filepath.Dir(defaultStatusPath), "bekendmakingen-qr"),
	}
}

func writeStatus(path string, status Status) error {
	status.UpdatedAt = time.Now().Format(time.RFC3339)
	status.Version = version
	raw, err := json.Marshal(status)
	if err != nil {
		return err
	}
	if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
		return err
	}
	temporary, err := os.CreateTemp(filepath.Dir(path), ".bekendmakingen-status-*")
	if err != nil {
		return err
	}
	temporaryName := temporary.Name()
	defer os.Remove(temporaryName)
	if err := temporary.Chmod(0644); err != nil {
		temporary.Close()
		return err
	}
	if _, err := temporary.Write(raw); err != nil {
		temporary.Close()
		return err
	}
	if err := temporary.Close(); err != nil {
		return err
	}
	return os.Rename(temporaryName, path)
}

func run(ctx context.Context, configPath, statusPath string, once bool) error {
	r := newRuntime()
	r.qrDir = filepath.Join(filepath.Dir(statusPath), "bekendmakingen-qr")
	nextPoll := time.Time{}
	for {
		now := time.Now()
		config, configErr := loadConfig(configPath)
		if configErr != nil {
			r.status.Online = false
			r.status.LastError = configErr.Error()
		} else {
			if r.configLoaded && !r.locationResolved && configKey(config) == configKey(r.config) &&
				!nextPoll.IsZero() && !now.Before(nextPoll) {
				r.configLoaded = false
			}
			changed, applyErr := r.applyConfig(ctx, config)
			if applyErr != nil {
				r.status.Online = false
				r.status.LastError = applyErr.Error()
				nextPoll = now.Add(5 * time.Minute)
			} else if config.Postcode != "" && r.locationResolved && (changed || nextPoll.IsZero() || !now.Before(nextPoll)) {
				if err := r.poll(ctx, now); err != nil {
					r.status.Online = false
					r.status.LastError = err.Error()
					retry := 15 * time.Minute
					configuredInterval := time.Duration(config.PollIntervalMinutes) * time.Minute
					if configuredInterval < retry {
						retry = configuredInterval
					}
					nextPoll = now.Add(retry)
				} else {
					nextPoll = now.Add(time.Duration(config.PollIntervalMinutes) * time.Minute)
				}
			}
		}
		if err := writeStatus(statusPath, r.status); err != nil {
			return err
		}
		if once {
			if configErr != nil {
				return configErr
			}
			if r.status.LastError != "" {
				return errors.New(r.status.LastError)
			}
			return nil
		}
		select {
		case <-ctx.Done():
			return nil
		case <-time.After(2 * time.Second):
		}
	}
}

func main() {
	configPath := flag.String("config", defaultConfigPath, "pad naar configuratiebestand")
	statusPath := flag.String("status", defaultStatusPath, "pad naar statusbestand")
	once := flag.Bool("once", false, "voer één synchronisatie uit en stop")
	showVersion := flag.Bool("version", false, "toon versie")
	flag.Parse()
	if *showVersion {
		fmt.Println(version)
		return
	}
	ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer cancel()
	if err := run(ctx, *configPath, *statusPath, *once); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
