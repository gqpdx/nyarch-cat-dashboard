
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components as PlasmaComponents
import org.kde.plasma.plasma5support as Plasma5Support
import org.kde.kirigami as Kirigami

import "components"

PlasmoidItem {
    id: root

    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    property var systemStats: ({})
    property string monitorStatus: "Waiting for system data..."
    property string monitorScriptPath: decodeURIComponent(
        Qt.resolvedUrl("../scripts/linux_monitor.py").toString().replace("file://", "")
    )

    property string monitorCommand: "/usr/bin/python3 \"" +
    monitorScriptPath + "\" --gpu-backend " +
    ["auto", "amd", "nvidia", "disabled"][plasmoid.configuration.gpuBackend]

    property string gpuText: {
        const gpu = systemStats.gpu
        if (!gpu)
            return plasmoid.configuration.gpuBackend === 3 ? "Disabled" : "Unavailable"

        const parts = []
        if (gpu.temperature !== null && gpu.temperature !== undefined)
            parts.push(gpu.temperature + "°C")
        if (gpu.utilization !== null && gpu.utilization !== undefined)
            parts.push(gpu.utilization + "%")
        if (gpu.memory_used !== null && gpu.memory_total !== null &&
            gpu.memory_used !== undefined && gpu.memory_total !== undefined)
            parts.push((gpu.memory_used / 1024).toFixed(1) + "/" +
                       (gpu.memory_total / 1024).toFixed(1) + " GB VRAM")
        return (gpu.name ? gpu.name + " · " : "") +
               (parts.length ? parts.join(" · ") : "Readings unavailable")
    }

    property string cpuText: {
        if (!systemStats.cpu)
            return "Waiting..."

            const usage = systemStats.cpu.usage
            const frequency = systemStats.cpu.frequency

            return usage + "% · " +
            (frequency !== null && frequency !== undefined
            ? frequency + " MHz"
            : "Frequency unavailable")
    }

    property string memoryText: systemStats.memory
    ? systemStats.memory.usage + "% · " +
    (systemStats.memory.used / 1024).toFixed(1) + " GB used"
    : "Waiting..."

    property string batteryText: {
        if (!systemStats.battery)
            return "Unavailable"

            if (systemStats.battery.charge === null ||
                systemStats.battery.charge === undefined)
                return "Charge unavailable"

                const health = systemStats.battery.health

                return systemStats.battery.charge + "% · " +
                (health !== null && health !== undefined
                ? health + "% health"
                : "Health unavailable")
    }

    property string temperatureText: {
        if (!systemStats.thermals)
            return "Waiting..."

            const cpu = systemStats.thermals.cpu
            const nvme = systemStats.thermals.nvme

            const cpuText = cpu !== null && cpu !== undefined
            ? cpu + "°C CPU"
            : "CPU unavailable"

            const nvmeText = nvme !== null && nvme !== undefined
            ? nvme + "°C NVMe"
            : "NVMe unavailable"

            return cpuText + " · " + nvmeText
    }

    property string fanText: {
        if (!systemStats.thermals ||
            systemStats.thermals.fan === null ||
            systemStats.thermals.fan === undefined)
            return "Unavailable"

            const rpm = systemStats.thermals.fan

            return rpm > 0 ? rpm + " RPM" : "Stopped"
    }

    property string storageText: {
        if (!systemStats.storage)
            return "Waiting..."

            return systemStats.storage.usage + "% · " +
            systemStats.storage.free.toFixed(1) + " GB free"
    }

    property var metricModel: {
        let metrics = []

        if (plasmoid.configuration.showCpu) {
            metrics.push({
                name: "CPU",
                value: root.cpuText,
                icon: "◈"
            })
        }

        if (plasmoid.configuration.showMemory) {
            metrics.push({
                name: "MEMORY",
                value: root.memoryText,
                icon: "▤"
            })
        }

        if (plasmoid.configuration.showBattery) {
            metrics.push({
                name: "BATTERY",
                value: root.batteryText,
                icon: "♡"
            })
        }

        if (plasmoid.configuration.showTemperature) {
            metrics.push({
                name: "TEMPERATURE",
                value: root.temperatureText,
                icon: "♨"
            })
        }

        if (plasmoid.configuration.showFan) {
            metrics.push({
                name: "FAN",
                value: root.fanText,
                icon: "✧"
            })
        }

        if (plasmoid.configuration.showStorage) {
            metrics.push({
                name: "STORAGE",
                value: root.storageText,
                icon: "▣"
            })
        }

        if (plasmoid.configuration.showGpu) {
            metrics.push({
                name: "GPU",
                value: root.gpuText,
                icon: "▰"
            })
        }

        return metrics
    }

    // Effective number of grid columns.
    property int effectiveColumns: Math.max(
        1,
        Math.min(
            plasmoid.configuration.columns,
            Math.max(1, metricModel.length)
        )
    )

    // Number of rows required by enabled metrics.
    property int metricRows: Math.ceil(
        metricModel.length / effectiveColumns
    )

    // Tile height based on layout mode and density.
    property int effectiveTileHeight: {
        const mode = plasmoid.configuration.layoutMode
        const compact = plasmoid.configuration.tileDensity === 1

        if (mode === 1 || compact)
            return 48

            return 65
    }

    // Space required by the metric grid.
    property int metricGridHeight: {
        if (metricRows === 0)
            return 0

            return metricRows * effectiveTileHeight
            + (metricRows - 1) * 8
    }

    // Dashboard height follows the actual content layout.
    property int dashboardHeight: contentLayout.implicitHeight + 40

    width: 370
    height: dashboardHeight

    Layout.minimumWidth: 370
    Layout.minimumHeight: dashboardHeight
    Layout.preferredWidth: 370
    Layout.preferredHeight: dashboardHeight


    property string currentTime: Qt.formatTime(new Date(), "hh:mm")
    property string currentDate: Qt.formatDate(new Date(), "dddd, MMMM d")

    property string catMood: {
        const thermals = systemStats.thermals
        const cpu = systemStats.cpu
        const battery = systemStats.battery

        if (thermals && thermals.cpu !== null &&
            thermals.cpu !== undefined &&
            thermals.cpu >= 75)
            return "hot"

            if (battery && battery.charge !== null &&
                battery.charge !== undefined &&
                battery.charge <= 20)
                return "sleepy"

                if (cpu && cpu.usage !== null &&
                    cpu.usage !== undefined &&
                    cpu.usage >= 75)
                    return "working"

                    return "happy"
    }

    property string catExpression: {
        switch (catMood) {
            case "hot":
                return "ฅ(×﹏×)ฅ"
            case "sleepy":
                return "ฅ-ω-ฅ"
            case "working":
                return "ฅ^•̀ﻌ•́^ฅ"
            default:
                return "ฅ^•ﻌ•^ฅ"
        }
    }

    property string catGreeting: {
        switch (catMood) {
            case "hot":
                return "It's getting hot!"
            case "sleepy":
                return "Nyaa... sleepy..."
            case "working":
                return "Working hard!"
            default:
                return "Nya~!"
        }
    }

    property string catMessage: {
        switch (catMood) {
            case "hot":
                return "Your CPU is running rather toasty. Let it cool down!"
            case "sleepy":
                return "Battery is running low. Time to find a charger!"
            case "working":
                return "Wow! That's a lot of work for this little machine!"
            default:
                return "Everything looks comfy. Let's enjoy the day!"
        }
    }

    Plasma5Support.DataSource {
        id: monitorSource

        engine: "executable"
        connectedSources: []

        onNewData: function(sourceName, data) {
            monitorSource.disconnectSource(sourceName)
            console.log("Monitor response:", sourceName, JSON.stringify(data))

            if (sourceName !== root.monitorCommand) {
                return
            }

            const output = data["stdout"]

            if (!output || output.trim().length === 0) {
                root.monitorStatus = "No monitoring data received"
                return
            }

            try {
                root.systemStats = JSON.parse(output)
                root.monitorStatus = "System data updated"
            } catch (error) {
                root.monitorStatus = "Could not parse monitoring data"
                console.error("Cat Dashboard:", error)
                console.error("Monitor output:", output)
            }
        }
    }

    Timer {
        id: monitorTimer

        interval: plasmoid.configuration.refreshInterval * 1000
        repeat: true
        running: true

        onTriggered: {
            if (monitorSource.connectedSources.length === 0) {
                monitorSource.connectSource(root.monitorCommand)
            }
        }
    }

    Component.onCompleted: {
        monitorSource.connectSource(root.monitorCommand)
        console.log("Starting system monitor:", root.monitorCommand)
        console.log("Monitor command:", root.monitorCommand)
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            root.currentTime = Qt.formatTime(new Date(), "hh:mm")
            root.currentDate = Qt.formatDate(new Date(), "dddd, MMMM d")
        }
    }

    Rectangle {
            anchors.fill: parent
            radius: 20
            clip: true

            color: Kirigami.Theme.backgroundColor

            border.width: 1
            border.color: Kirigami.Theme.highlightColor

        ColumnLayout {
            id: contentLayout

            anchors.fill: parent
            anchors.margins: 20
            spacing: 14

            RowLayout {
                Layout.fillWidth: true

                ColumnLayout {
                    spacing: 2

                    PlasmaComponents.Label {
                        text: "NYARCH COMPANION"
                        color: Kirigami.Theme.highlightColor
                        font.pixelSize: 12
                        font.bold: true
                        font.letterSpacing: 2
                    }

                    PlasmaComponents.Label {
                        text: root.systemStats.system
                        ? root.systemStats.system.hostname
                        : "System Monitor"
                        color: Kirigami.Theme.disabledTextColor
                        font.pixelSize: 11
                    }
                }

                Item { Layout.fillWidth: true }

                PlasmaComponents.Label {
                    text: "✦"
                    color: Kirigami.Theme.highlightColor
                    font.pixelSize: 24
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 110
                radius: 14
                color: Qt.rgba(
                    Kirigami.Theme.textColor.r,
                    Kirigami.Theme.textColor.g,
                    Kirigami.Theme.textColor.b, 0.08
                )

                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 3

                    PlasmaComponents.Label {
                        Layout.alignment: Qt.AlignHCenter
                        text: root.currentTime
                        color: Kirigami.Theme.textColor
                        font.pixelSize: 43
                        font.weight: Font.Light
                    }

                    PlasmaComponents.Label {
                        Layout.alignment: Qt.AlignHCenter
                        text: root.currentDate
                        color: Kirigami.Theme.disabledTextColor
                        font.pixelSize: 12
                    }
                }
            }

            CatCompanion {
                id: catCompanion

                expression: root.catExpression
                greeting: root.catGreeting
                message: root.catMessage

                animationsEnabled: plasmoid.configuration.animationsEnabled

                onAnimationsEnabledChanged: {
                    if (!animationsEnabled) {
                        blinkAnimation.stop()
                        isBlinking = false
                    }
                }
            }

            PlasmaComponents.Label {
                text: "SYSTEM STATUS"
                color: Kirigami.Theme.highlightColor
                font.pixelSize: 11
                font.bold: true
                font.letterSpacing: 1.5
            }

            GridLayout {
                Layout.fillWidth: true

                Layout.bottomMargin: 8

                implicitHeight: root.metricGridHeight
                Layout.minimumHeight: root.metricGridHeight
                Layout.preferredHeight: root.metricGridHeight
                Layout.maximumHeight: root.metricGridHeight

                columns: root.effectiveColumns
                rowSpacing: 8
                columnSpacing: 10

                Repeater {
                    model: root.metricModel

                    delegate: MetricTile {
                        required property var modelData

                        name: modelData.name
                        value: modelData.value
                        icon: modelData.icon

                        tileHeight: root.effectiveTileHeight
                    }
                }
            }


            PlasmaComponents.Label {
                Layout.alignment: Qt.AlignHCenter
                text: "Made with ♡ for Nyarch Linux"
                color: Kirigami.Theme.disabledTextColor
                font.pixelSize: 10
            }
        }
    }
}
