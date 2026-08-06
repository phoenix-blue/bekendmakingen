import QtQuick 2.1
import qb.components 1.0

Tile {
    id: root

    property bool dimmed: screenStateController.dimmedColors

    onVisibleChanged: if (visible) app.refreshStatus()
    onClicked: stage.openFullscreen(app.screenUrl)

    Rectangle {
        anchors.fill: parent
        anchors.margins: 6
        radius: 9
        color: dimmed ? "black" : "white"
        border.width: 5
        border.color: app.online ? "#df7b32" : "#9aa1a6"

        Text {
            anchors { top: parent.top; topMargin: 18; horizontalCenter: parent.horizontalCenter }
            text: "IN DE BUURT"
            color: dimmed ? "#dddddd" : "#6a737a"
            font.family: qfont.semiBold.name
            font.pixelSize: isNxt ? 17 : 14
        }

        Image {
            anchors.centerIn: parent
            anchors.verticalCenterOffset: -1
            width: isNxt ? 58 : 46
            height: width
            source: "drawables/BekendmakingenIcon.svg"
            visible: !app.configured || !app.online
            opacity: dimmed ? 0.75 : 1
        }

        Text {
            anchors.centerIn: parent
            anchors.verticalCenterOffset: -1
            text: app.publicationCount + (app.truncated ? "+" : "")
            visible: app.configured && app.online
            color: dimmed ? "white" : "#263238"
            font.family: qfont.semiBold.name
            font.pixelSize: isNxt ? 54 : 43
        }

        Text {
            anchors { bottom: parent.bottom; bottomMargin: 18; horizontalCenter: parent.horizontalCenter }
            width: parent.width - 24
            text: app.statusTitle()
            elide: Text.ElideRight
            horizontalAlignment: Text.AlignHCenter
            color: dimmed ? "#cccccc" : "#65747c"
            font.pixelSize: isNxt ? 15 : 12
        }
    }
}
