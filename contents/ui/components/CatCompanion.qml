import QtQuick
import QtQuick.Layouts
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

Rectangle {
    id: companion

    property string expression: "ฅ^•ﻌ•^ฅ"
    property string greeting: "Nya~!"
    property string message: "Your little companion is awake!"
    property bool animationsEnabled: true
    property bool isBlinking: false

    Layout.fillWidth: true
    Layout.preferredHeight: 100

    radius: 14

    color: Qt.rgba(
        Kirigami.Theme.highlightColor.r,
        Kirigami.Theme.highlightColor.g,
        Kirigami.Theme.highlightColor.b,
        0.13
    )

    SequentialAnimation {
        running: companion.animationsEnabled
        loops: Animation.Infinite

        NumberAnimation {
            target: catBob
            property: "offset"
            to: -3
            duration: 1400
            easing.type: Easing.InOutSine
        }

        NumberAnimation {
            target: catBob
            property: "offset"
            to: 3
            duration: 1400
            easing.type: Easing.InOutSine
        }
    }

    Timer {
        id: blinkTimer

        interval: 3500 + Math.random() * 2500
        repeat: true
        running: companion.animationsEnabled

        onTriggered: blinkAnimation.start()
    }

    SequentialAnimation {
        id: blinkAnimation

        ScriptAction {
            script: companion.isBlinking = true
        }

        PauseAnimation {
            duration: 220
        }

        ScriptAction {
            script: companion.isBlinking = false
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 14

        Item {
            id: catBob

            property real offset: 0

            Layout.preferredWidth: 120
            Layout.minimumWidth: 120
            Layout.maximumWidth: 120
            Layout.preferredHeight: 42
            Layout.alignment: Qt.AlignVCenter

            transform: Translate {
                y: catBob.offset
            }

            PlasmaComponents.Label {
                id: catLabel

                anchors.fill: parent

                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter

                text: companion.isBlinking
                ? "ฅ^‑ﻌ‑^ฅ"
                : companion.expression

                font.pixelSize: 27
                color: Kirigami.Theme.textColor
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 4

            PlasmaComponents.Label {
                text: companion.greeting
                font.pixelSize: 19
                font.bold: true
                color: Kirigami.Theme.textColor
            }

            PlasmaComponents.Label {
                Layout.fillWidth: true
                text: companion.message
                font.pixelSize: 10
                color: Kirigami.Theme.disabledTextColor
                wrapMode: Text.WordWrap
            }
        }
    }
}
