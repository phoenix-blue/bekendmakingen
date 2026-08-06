import QtQuick 2.1
import qb.base 1.0
import qb.components 1.0

Popup {
    id: alertPopup

    property int newCount: 1
    property string titleText: ""

    function showAlert(count, title) {
        newCount = count
        titleText = title
        show()
        dismissTimer.restart()
    }

    Timer {
        id: dismissTimer
        interval: 10000
        repeat: false
        onTriggered: alertPopup.hide()
    }

    Rectangle {
        width: isNxt ? 700 : 560
        height: isNxt ? 116 : 93
        anchors { top: parent.top; topMargin: isNxt ? 24 : 19; horizontalCenter: parent.horizontalCenter }
        radius: 12
        color: "#fffaf5"
        border.width: 3
        border.color: "#df7b32"

        Image {
            width: isNxt ? 58 : 46
            height: width
            anchors { left: parent.left; leftMargin: 22; verticalCenter: parent.verticalCenter }
            source: "drawables/BekendmakingenIcon.svg"
        }
        Column {
            anchors { left: parent.left; leftMargin: isNxt ? 100 : 80; right: parent.right; rightMargin: 20; verticalCenter: parent.verticalCenter }
            spacing: 5
            Text {
                width: parent.width
                text: newCount + " nieuwe bekendmaking" + (newCount === 1 ? "" : "en") + " in de buurt"
                color: "#263238"
                font.family: qfont.semiBold.name
                font.pixelSize: isNxt ? 21 : 17
            }
            Text {
                width: parent.width
                text: titleText
                elide: Text.ElideRight
                color: "#65747c"
                font.pixelSize: isNxt ? 15 : 12
            }
        }
        MouseArea { anchors.fill: parent; onClicked: alertPopup.hide() }
    }
}
