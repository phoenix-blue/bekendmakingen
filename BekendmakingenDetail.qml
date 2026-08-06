import QtQuick 2.1
import qb.components 1.0

Screen {
    id: root
    screenTitle: "Bekendmaking"

    property variant item: app.publicationAt(app.selectedIndex)
    property color accentColor: app.typeColor(root.item.type, root.item.title)

    onVisibleChanged: if (visible) item = app.publicationAt(app.selectedIndex)

    Flickable {
        anchors { fill: parent; margins: isNxt ? 34 : 27 }
        contentWidth: width
        contentHeight: detailColumn.height
        clip: true

        Column {
            id: detailColumn
            width: parent.width
            spacing: isNxt ? 18 : 14

            Rectangle {
                width: parent.width
                height: isNxt ? 10 : 8
                radius: 4
                color: root.accentColor
            }
            Text {
                width: parent.width
                text: root.item.title || "Bekendmaking"
                wrapMode: Text.WordWrap
                color: "#263238"
                font.family: qfont.semiBold.name
                font.pixelSize: isNxt ? 25 : 20
            }
            Row {
                width: parent.width
                spacing: isNxt ? 10 : 8

                Rectangle {
                    width: dateChipText.paintedWidth + (isNxt ? 24 : 20)
                    height: isNxt ? 32 : 26
                    radius: height / 2
                    color: "#eef2f4"
                    Text {
                        id: dateChipText
                        anchors.centerIn: parent
                        text: app.formatDate(root.item.date)
                        color: "#53636b"
                        font.pixelSize: isNxt ? 14 : 12
                    }
                }
                Rectangle {
                    width: typeChipText.paintedWidth + (isNxt ? 24 : 20)
                    height: isNxt ? 32 : 26
                    radius: height / 2
                    color: root.accentColor
                    Text {
                        id: typeChipText
                        anchors.centerIn: parent
                        text: root.item.type || "Type onbekend"
                        color: "white"
                        font.family: qfont.semiBold.name
                        font.pixelSize: isNxt ? 14 : 12
                    }
                }
                Rectangle {
                    width: distanceChipText.paintedWidth + (isNxt ? 24 : 20)
                    height: isNxt ? 32 : 26
                    radius: height / 2
                    color: "#eef2f4"
                    Text {
                        id: distanceChipText
                        anchors.centerIn: parent
                        text: app.formatDistance(root.item.distance_km, root.item.has_distance)
                        color: "#53636b"
                        font.pixelSize: isNxt ? 14 : 12
                    }
                }
            }
            Rectangle { width: parent.width; height: 1; color: "#ccd4d7" }
            Row {
                width: parent.width
                spacing: isNxt ? 26 : 20
                height: Math.max(infoColumn.height, qrPanel.height)

                Column {
                    id: infoColumn
                    width: parent.width - (qrPanel.visible ? qrPanel.width + parent.spacing : 0)
                    spacing: isNxt ? 18 : 14

                    Row {
                        width: parent.width
                        height: authorityText.height
                        spacing: isNxt ? 12 : 9

                        Image {
                            width: isNxt ? 26 : 21
                            height: width
                            source: "drawables/InstitutionIcon.svg"
                            fillMode: Image.PreserveAspectFit
                            smooth: true
                        }
                        Text {
                            id: authorityText
                            width: parent.width - (isNxt ? 38 : 30)
                            text: "Instantie\n" + (root.item.authority || "Onbekend")
                            wrapMode: Text.WordWrap
                            color: "#34434a"
                            font.pixelSize: isNxt ? 16 : 13
                            lineHeight: 1.2
                        }
                    }
                    Row {
                        width: parent.width
                        visible: root.item.location ? true : false
                        height: locationText.height
                        spacing: isNxt ? 12 : 9

                        Image {
                            width: isNxt ? 26 : 21
                            height: width
                            source: "drawables/LocationIcon.svg"
                            fillMode: Image.PreserveAspectFit
                            smooth: true
                        }
                        Text {
                            id: locationText
                            width: parent.width - (isNxt ? 38 : 30)
                            text: "Locatie\n" + root.item.location
                            wrapMode: Text.WordWrap
                            color: "#34434a"
                            font.pixelSize: isNxt ? 16 : 13
                            lineHeight: 1.2
                        }
                    }
                    Rectangle {
                        visible: root.item.url ? true : false
                        width: isNxt ? 230 : 184
                        height: isNxt ? 44 : 36
                        radius: isNxt ? 7 : 6
                        color: "white"
                        border { width: 2; color: root.accentColor }

                        Text {
                            anchors.centerIn: parent
                            text: "Officiële publicatie  ›"
                            color: root.accentColor
                            font.family: qfont.semiBold.name
                            font.pixelSize: isNxt ? 16 : 13
                        }
                    }
                    Text {
                        width: parent.width
                        text: root.item.url ? "Scan de QR-code om de volledige, juridisch geldende tekst te openen." : "Voor deze melding is geen officiële link beschikbaar."
                        wrapMode: Text.WordWrap
                        color: "#65747c"
                        font.pixelSize: isNxt ? 14 : 11
                    }
                }

                Item {
                    id: qrPanel
                    visible: root.item.qr_path ? true : false
                    width: isNxt ? 224 : 180
                    height: isNxt ? 272 : 218

                    Rectangle {
                        anchors {
                            fill: parent
                            leftMargin: 1
                            rightMargin: 1
                            topMargin: 1
                            bottomMargin: isNxt ? 6 : 5
                        }
                        color: "white"
                        radius: isNxt ? 11 : 9
                        border { width: 2; color: root.accentColor }

                        Rectangle {
                            anchors { top: parent.top; left: parent.left; right: parent.right }
                            height: isNxt ? 9 : 7
                            radius: parent.radius
                            color: root.accentColor
                        }

                        Image {
                            anchors { top: parent.top; topMargin: isNxt ? 16 : 13; horizontalCenter: parent.horizontalCenter }
                            width: isNxt ? 194 : 154
                            height: width
                            source: root.item.qr_path || ""
                            fillMode: Image.PreserveAspectFit
                            smooth: false
                            cache: false
                        }

                        Text {
                            anchors { bottom: parent.bottom; bottomMargin: isNxt ? 12 : 9; left: parent.left; leftMargin: 8; right: parent.right; rightMargin: 8 }
                            text: "Scan voor de officiële melding"
                            horizontalAlignment: Text.AlignHCenter
                            wrapMode: Text.WordWrap
                            color: "#34434a"
                            font.family: qfont.semiBold.name
                            font.pixelSize: isNxt ? 15 : 12
                        }
                    }
                }
            }
            Item { width: 1; height: isNxt ? 8 : 6 }
        }
    }
}
