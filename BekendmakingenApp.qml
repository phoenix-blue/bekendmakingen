import QtQuick 2.1
import FileIO 1.0
import qb.components 1.0
import qb.base 1.0

App {
    id: bekendmakingenApp

    property url tileUrl: "BekendmakingenTile.qml"
    property url screenUrl: "BekendmakingenScreen.qml"
    property url detailUrl: "BekendmakingenDetail.qml"
    property url settingsUrl: "BekendmakingenSettings.qml"
    property url popupUrl: "BekendmakingenPopup.qml"

    property BekendmakingenTile bekendmakingenTile
    property BekendmakingenScreen bekendmakingenScreen
    property BekendmakingenDetail bekendmakingenDetail
    property BekendmakingenSettings bekendmakingenSettings
    property Popup bekendmakingenPopup

    property bool configured: false
    property bool online: false
    property string postcode: ""
    property int houseNumber: 0
    property string addition: ""
    property string locationLabel: ""
    property real radiusKM: 5
    property int lookbackDays: 42
    property int publicationCount: 0
    property int sourceCount: 0
    property bool truncated: false
    property variant publications: []
    property string lastError: "Nog niet ingesteld"
    property string lastSuccessAt: ""
    property int alertSequence: 0
    property int observedAlertSequence: -1
    property int selectedIndex: 0

    FileIO {
        id: configFile
        source: "file:///mnt/data/tsc/bekendmakingen.json"
    }

    FileIO {
        id: statusFile
        source: "file:///var/volatile/tmp/bekendmakingen-status.json"
    }

    function init() {
        registry.registerWidget("tile", tileUrl, this, "bekendmakingenTile", {
            thumbCategory: "general",
            thumbLabel: "Bekendmakingen",
            thumbIcon: "qrc:/tsc/button_on.png",
            thumbIconVAlignment: "center",
            thumbWeight: 30,
            baseTileWeight: 10
        })
        registry.registerWidget("screen", screenUrl, this, "bekendmakingenScreen")
        registry.registerWidget("screen", detailUrl, this, "bekendmakingenDetail")
        registry.registerWidget("screen", settingsUrl, this, "bekendmakingenSettings")
        registry.registerWidget("popup", popupUrl, this, "bekendmakingenPopup")
    }

    function numberOr(value, fallback) {
        var parsed = Number(value)
        return isNaN(parsed) ? fallback : parsed
    }

    function parseDutchNumber(value, fallback) {
        return numberOr(String(value).replace(",", "."), fallback)
    }

    function addressText() {
        if (!postcode) return ""
        return postcode + " " + houseNumber + addition
    }

    function statusTitle() {
        if (!configured) return "Adres instellen"
        if (!online) return "Bron niet bereikbaar"
        if (publicationCount === 0) return "Niets nieuws in de buurt"
        return publicationCount + (truncated ? "+" : "") + " bekendmaking" + (publicationCount === 1 ? "" : "en")
    }

    function formatDate(value) {
        var raw = String(value ? value : "")
        if (raw.length < 10) return raw
        return raw.substr(8, 2) + "-" + raw.substr(5, 2) + "-" + raw.substr(0, 4)
    }

    function formatDistance(value, available) {
        if (!available) return "afstand onbekend"
        var distance = numberOr(value, 0)
        if (distance < 1) return Math.round(distance * 1000) + " m"
        return distance.toFixed(1).replace(".", ",") + " km"
    }

    function publicationAt(index) {
        if (index < 0 || index >= publications.length) return ({})
        return publications[index]
    }

    function typeColor(type, title) {
        var value = (String(type) + " " + String(title)).toLowerCase()
        if (value.indexOf("milieu") >= 0 || value.indexOf("natuur") >= 0 || value.indexOf("water") >= 0) return "#2d9671"
        if (value.indexOf("verkeer") >= 0 || value.indexOf("park") >= 0) return "#397bb5"
        if (value.indexOf("evenement") >= 0 || value.indexOf("horeca") >= 0) return "#a76a27"
        if (value.indexOf("bouw") >= 0 || value.indexOf("sloop") >= 0) return "#d26a35"
        return "#6f7780"
    }

    function openPublication(index) {
        selectedIndex = index
        stage.openFullscreen(detailUrl)
    }

    function refreshStatus() {
        try {
            var parsed = JSON.parse(statusFile.read())
            configured = parsed.configured === true
            online = parsed.online === true
            postcode = parsed.postcode ? parsed.postcode : ""
            houseNumber = parseInt(numberOr(parsed.house_number, 0))
            addition = parsed.house_number_addition ? parsed.house_number_addition : ""
            locationLabel = parsed.location_label ? parsed.location_label : ""
            radiusKM = numberOr(parsed.radius_km, 5)
            lookbackDays = parseInt(numberOr(parsed.lookback_days, 42))
            publicationCount = parseInt(numberOr(parsed.count, 0))
            sourceCount = parseInt(numberOr(parsed.source_count, publicationCount))
            truncated = parsed.truncated === true
            publications = parsed.publications ? parsed.publications : []
            lastError = parsed.last_error ? parsed.last_error : ""
            lastSuccessAt = parsed.last_success_at ? parsed.last_success_at : ""
            alertSequence = parseInt(numberOr(parsed.alert_sequence, 0))

            if (observedAlertSequence < 0 || alertSequence < observedAlertSequence) {
                observedAlertSequence = alertSequence
            } else if (alertSequence > observedAlertSequence) {
                observedAlertSequence = alertSequence
                if (bekendmakingenPopup)
                    bekendmakingenPopup.showAlert(parseInt(numberOr(parsed.alert_count, 1)), parsed.alert_title ? parsed.alert_title : "Nieuwe bekendmaking")
            }
        } catch (error) {
            online = false
            lastError = "Lokale Bekendmakingen-service start nog"
        }
    }

    function loadConfig() {
        try {
            var parsed = JSON.parse(configFile.read())
            postcode = parsed.postcode ? parsed.postcode : ""
            houseNumber = parseInt(numberOr(parsed.house_number, 0))
            addition = parsed.house_number_addition ? parsed.house_number_addition : ""
            radiusKM = numberOr(parsed.radius_km, 5)
        } catch (error) {
            postcode = ""
            houseNumber = 0
            addition = ""
            radiusKM = 5
        }
    }

    function saveSettings(newPostcode, newHouseNumber, newAddition, newRadius, newPoll, newLookback, newNotifications) {
        var existing = {}
        try { existing = JSON.parse(configFile.read()) } catch (error) { existing = {} }
        existing.postcode = String(newPostcode).toUpperCase().replace(/\s/g, "")
        existing.house_number = Math.max(0, parseInt(numberOr(newHouseNumber, 0)))
        existing.house_number_addition = String(newAddition).toUpperCase().replace(/\s/g, "")
        existing.radius_km = Math.max(0.25, Math.min(25, parseDutchNumber(newRadius, 5)))
        existing.poll_interval_minutes = Math.max(30, Math.min(1440, parseInt(numberOr(newPoll, 360))))
        existing.lookback_days = Math.max(1, Math.min(90, parseInt(numberOr(newLookback, 42))))
        existing.max_results = existing.max_results ? existing.max_results : 100
        existing.notifications = newNotifications === true
        if (!existing.geocode_url)
            existing.geocode_url = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free"
        if (!existing.publications_url)
            existing.publications_url = "https://repository.overheid.nl/sru"
        configFile.write(JSON.stringify(existing))
        postcode = existing.postcode
        houseNumber = existing.house_number
        addition = existing.house_number_addition
        radiusKM = existing.radius_km
    }

    Timer {
        interval: 2000
        repeat: true
        running: true
        onTriggered: bekendmakingenApp.refreshStatus()
    }

    Component.onCompleted: {
        loadConfig()
        refreshStatus()
    }
}
