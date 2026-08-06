import QtQuick 2.1
import FileIO 1.0
import qb.components 1.0

Screen {
    id: root
    screenTitle: "Bekendmakingen instellingen"

    property string editorKey: ""
    property bool returningFromKeyboard: false
    property bool notificationsEnabled: true

    function beginEdit(key, title, value) {
        editorKey = key
        returningFromKeyboard = true
        qkeyboard.open(title, String(value), keyboardSaved)
    }

    function keyboardSaved(text) {
        if (text === undefined || text === null) return
        var value = String(text)
        if (editorKey === "postcode") postcodeField.prefilledText = value
        else if (editorKey === "house") houseField.prefilledText = value
        else if (editorKey === "addition") additionField.prefilledText = value
        else if (editorKey === "radius") radiusField.prefilledText = value
        else if (editorKey === "poll") pollField.prefilledText = value
        else if (editorKey === "lookback") lookbackField.prefilledText = value
    }

    function loadSettings() {
        var config = {}
        try { config = JSON.parse(appConfig.read()) } catch (error) { config = {} }
        postcodeField.prefilledText = config.postcode ? config.postcode : app.postcode
        houseField.prefilledText = String(config.house_number ? config.house_number : app.houseNumber)
        additionField.prefilledText = config.house_number_addition ? config.house_number_addition : app.addition
        radiusField.prefilledText = String(config.radius_km ? config.radius_km : app.radiusKM).replace(".", ",")
        pollField.prefilledText = String(config.poll_interval_minutes ? config.poll_interval_minutes : 360)
        lookbackField.prefilledText = String(config.lookback_days ? config.lookback_days : 42)
        notificationsEnabled = config.notifications === undefined ? true : config.notifications === true
    }

    function normalizedPostcode() {
        return String(postcodeField.inputText).toUpperCase().replace(/\s/g, "")
    }

    function saveAndClose() {
        var postcode = normalizedPostcode()
        var houseNumber = parseInt(houseField.inputText)
        var radius = app.parseDutchNumber(radiusField.inputText, 0)
        var poll = parseInt(pollField.inputText)
        var lookback = parseInt(lookbackField.inputText)

        if (!/^[1-9][0-9]{3}[A-Z]{2}$/.test(postcode)) {
            qdialog.showDialog(qdialog.SizeLarge, "Adres controleren",
                               "Vul een geldige postcode in, bijvoorbeeld 3511 AA.", "Sluiten")
            return
        }
        if (isNaN(houseNumber) || houseNumber < 1 || houseNumber > 99999) {
            qdialog.showDialog(qdialog.SizeLarge, "Adres controleren",
                               "Vul een geldig huisnummer in.", "Sluiten")
            return
        }
        if (radius < 0.25 || radius > 25) {
            qdialog.showDialog(qdialog.SizeLarge, "Instellingen controleren",
                               "De straal moet tussen 0,25 en 25 km liggen.", "Sluiten")
            return
        }
        if (isNaN(poll) || poll < 30 || poll > 1440) {
            qdialog.showDialog(qdialog.SizeLarge, "Instellingen controleren",
                               "Verversen moet tussen 30 en 1440 minuten liggen.", "Sluiten")
            return
        }
        if (isNaN(lookback) || lookback < 1 || lookback > 90) {
            qdialog.showDialog(qdialog.SizeLarge, "Instellingen controleren",
                               "De periode moet tussen 1 en 90 dagen liggen.", "Sluiten")
            return
        }

        app.saveSettings(postcode, houseNumber, additionField.inputText,
                         radius, poll, lookback, notificationsEnabled)
        statusText.text = "Instellingen opgeslagen; adres wordt gecontroleerd..."
        statusText.color = "#187a58"
        hide()
    }

    onShown: {
        addCustomTopRightButton("Opslaan")
        if (returningFromKeyboard) {
            returningFromKeyboard = false
        } else {
            loadSettings()
            statusText.text = app.lastError.length > 0 ? app.lastError :
                              "Na Opslaan controleert de lokale service het adres."
            statusText.color = app.lastError.length > 0 ? "#a63b32" : "#607d8b"
        }
    }

    onCustomButtonClicked: saveAndClose()

    FileIO {
        id: appConfig
        source: "file:///mnt/data/tsc/bekendmakingen.json"
    }

    Column {
        id: fieldsColumn
        width: isNxt ? 660 : 528
        spacing: isNxt ? 8 : 6
        anchors {
            top: parent.top
            topMargin: isNxt ? 15 : 12
            horizontalCenter: parent.horizontalCenter
        }

        Text {
            width: parent.width
            text: "Vul je adres en het gewenste zoekgebied in. Tik op een regel om het standaard Toon-toetsenbord te openen."
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            color: "#455a64"
            font.pixelSize: isNxt ? 15 : 12
        }

        EditTextLabel {
            id: postcodeField
            width: parent.width
            height: isNxt ? 44 : 35
            labelText: "Postcode"
            placeholder: "3511 AA"
            MouseArea {
                anchors.fill: parent
                onClicked: root.beginEdit("postcode", postcodeField.labelText, postcodeField.inputText)
            }
        }

        EditTextLabel {
            id: houseField
            width: parent.width
            height: isNxt ? 44 : 35
            labelText: "Huisnummer"
            inputHints: Qt.ImhDigitsOnly
            MouseArea {
                anchors.fill: parent
                onClicked: root.beginEdit("house", houseField.labelText, houseField.inputText)
            }
        }

        EditTextLabel {
            id: additionField
            width: parent.width
            height: isNxt ? 44 : 35
            labelText: "Toevoeging (optioneel)"
            placeholder: "bijvoorbeeld A of -1"
            MouseArea {
                anchors.fill: parent
                onClicked: root.beginEdit("addition", additionField.labelText, additionField.inputText)
            }
        }

        EditTextLabel {
            id: radiusField
            width: parent.width
            height: isNxt ? 44 : 35
            labelText: "Straal in km (0,25–25)"
            MouseArea {
                anchors.fill: parent
                onClicked: root.beginEdit("radius", radiusField.labelText, radiusField.inputText)
            }
        }

        EditTextLabel {
            id: pollField
            width: parent.width
            height: isNxt ? 44 : 35
            labelText: "Verversen in minuten (30–1440)"
            inputHints: Qt.ImhDigitsOnly
            MouseArea {
                anchors.fill: parent
                onClicked: root.beginEdit("poll", pollField.labelText, pollField.inputText)
            }
        }

        EditTextLabel {
            id: lookbackField
            width: parent.width
            height: isNxt ? 44 : 35
            labelText: "Terugkijken in dagen (1–90)"
            inputHints: Qt.ImhDigitsOnly
            MouseArea {
                anchors.fill: parent
                onClicked: root.beginEdit("lookback", lookbackField.labelText, lookbackField.inputText)
            }
        }

        Item {
            width: parent.width
            height: isNxt ? 42 : 34

            Text {
                text: "Popup bij nieuwe bekendmaking"
                anchors.verticalCenter: parent.verticalCenter
                color: "#263238"
                font.pixelSize: isNxt ? 16 : 13
            }

            OnOffToggle {
                id: notificationsToggle
                height: isNxt ? 38 : 30
                isSwitchedOn: root.notificationsEnabled
                anchors {
                    right: parent.right
                    verticalCenter: parent.verticalCenter
                }
                onIsSwitchedOnChanged: root.notificationsEnabled = isSwitchedOn
            }
        }

        Text {
            id: statusText
            width: parent.width
            text: ""
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            color: "#607d8b"
            font.pixelSize: isNxt ? 14 : 11
        }
    }
}
