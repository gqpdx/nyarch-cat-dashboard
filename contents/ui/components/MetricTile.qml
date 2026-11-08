import QtQuick
import QtQuick.Layouts
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

Rectangle {
    id: tile

    property string name: "METRIC"
    property string value: "--"
    property string icon: "◈"
    property int tileHeight: 65

    Layout.fillWidth: true
    Layout.preferredHeight: tile.tileHeight

    radius: 12

    color: Qt.rgba(
        Kirigami.Theme.textColor.r,
        Kirigami.Theme.textColor.g,
        Kirigami.Theme.textColor.b,
        0.07
    )

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 9
        spacing: 3

        RowLayout {
            spacing: 6

            PlasmaComponents.Label {
                text: tile.icon
                color: Kirigami.Theme.highlightColor
                font.pixelSize: 15
            }

            PlasmaComponents.Label {
                text: tile.name
                color: Kirigami.Theme.textColor
                font.pixelSize: 10
                font.bold: true
            }
        }

        PlasmaComponents.Label {
            Layout.fillWidth: true
            text: tile.value
            color: Kirigami.Theme.disabledTextColor
            font.pixelSize: 10
            elide: Text.ElideRight
        }
    }
}
