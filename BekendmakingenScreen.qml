import QtQuick 2.1
import qb.components 1.0

Screen {
    id: root
    screenTitle: "Bekendmakingen"

    onVisibleChanged: {
        if (visible) {
            addCustomTopRightButton("Instellingen")
            app.refreshStatus()
        }
    }
    onCustomButtonClicked: stage.openFullscreen(app.settingsUrl)

    Rectangle {
        id: summary
        anchors { top: parent.top; topMargin: 16; left: parent.left; leftMargin: 34; right: parent.right; rightMargin: 34 }
        height: isNxt ? 82 : 66
        radius: 9
        color: "#fff7ef"
        border.width: 2
        border.color: "#e5b17f"

        Text {
            anchors { left: parent.left; leftMargin: 22; verticalCenter: parent.verticalCenter }
            text: app.statusTitle()
            color: "#303b40"
            font.family: qfont.semiBold.name
            font.pixelSize: isNxt ? 24 : 19
        }
        Text {
            anchors { right: parent.right; rightMargin: 22; verticalCenter: parent.verticalCenter }
            width: parent.width * 0.55
            text: app.configured ? (app.locationLabel || app.addressText()) + " · " + app.radiusKM.toString().replace(".", ",") + " km" : "Open Instellingen om je adres in te vullen"
            elide: Text.ElideMiddle
            horizontalAlignment: Text.AlignRight
            color: "#65747c"
            font.pixelSize: isNxt ? 15 : 12
        }
    }

    Text {
        id: errorText
        anchors { top: summary.bottom; topMargin: 20; horizontalCenter: parent.horizontalCenter }
        width: parent.width - 80
        visible: !app.online || app.publications.length === 0
        text: !app.configured ? "Vul eerst je postcode en huisnummer in." :
              (!app.online ? app.lastError : "Geen openbare bekendmakingen gevonden in de gekozen periode en straal.")
        wrapMode: Text.WordWrap
        horizontalAlignment: Text.AlignHCenter
        color: app.online ? "#65747c" : "#a2473c"
        font.pixelSize: isNxt ? 17 : 14
    }

    Flickable {
        id: list
        anchors { top: summary.bottom; topMargin: 13; left: parent.left; leftMargin: 34; right: parent.right; rightMargin: 34; bottom: parent.bottom; bottomMargin: 18 }
        visible: app.online && app.publications.length > 0
        contentWidth: width
        contentHeight: listColumn.height
        clip: true

        Column {
            id: listColumn
            width: list.width
            spacing: 8

            Repeater {
                model: app.publications

                Rectangle {
                    width: listColumn.width
                    height: isNxt ? 92 : 74
                    radius: 7
                    color: itemMouse.pressed ? "#edf1f2" : "#ffffff"
                    border.width: 1
                    border.color: "#cbd2d5"

                    Rectangle {
                        width: 7
                        height: parent.height
                        radius: 3
                        color: app.typeColor(modelData.type, modelData.title)
                    }

                    Column {
                        anchors { left: parent.left; leftMargin: 20; right: parent.right; rightMargin: 18; verticalCenter: parent.verticalCenter }
                        spacing: isNxt ? 7 : 5
                        Text {
                            width: parent.width
                            text: modelData.title
                            elide: Text.ElideRight
                            color: "#263238"
                            font.family: qfont.semiBold.name
                            font.pixelSize: isNxt ? 17 : 14
                        }
                        Text {
                            width: parent.width
                            text: app.formatDate(modelData.date) + "  ·  " + (modelData.type || "bekendmaking") + "  ·  " + app.formatDistance(modelData.distance_km, modelData.has_distance)
                            elide: Text.ElideRight
                            color: "#65747c"
                            font.pixelSize: isNxt ? 14 : 11
                        }
                    }

                    MouseArea {
                        id: itemMouse
                        anchors.fill: parent
                        onClicked: app.openPublication(index)
                    }
                }
            }
        }
    }
}
