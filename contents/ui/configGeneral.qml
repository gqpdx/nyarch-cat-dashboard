import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Kirigami.FormLayout {
    id: page

    property alias cfg_layoutMode: layoutMode.currentIndex
    property alias cfg_columns: columns.value
    property alias cfg_tileDensity: tileDensity.currentIndex
    property alias cfg_refreshInterval: refreshInterval.value
    property alias cfg_animationsEnabled: animationsEnabled.checked
    property alias cfg_showCpu: showCpu.checked
    property alias cfg_showMemory: showMemory.checked
    property alias cfg_showBattery: showBattery.checked
    property alias cfg_showTemperature: showTemperature.checked
    property alias cfg_showFan: showFan.checked
    property alias cfg_showStorage: showStorage.checked
    property alias cfg_gpuBackend: gpuBackend.currentIndex
    property alias cfg_showGpu: showGpu.checked

    QQC2.ComboBox {
        id: layoutMode

        Kirigami.FormData.label: i18n("Layout behavior:")
        model: [
            i18n("Automatic"),
            i18n("Compact"),
            i18n("Expand")
        ]
    }

    QQC2.SpinBox {
        id: columns

        Kirigami.FormData.label: i18n("Grid columns:")
        from: 1
        to: 3
    }

    QQC2.ComboBox {
        id: tileDensity

        Kirigami.FormData.label: i18n("Tile density:")
        model: [
            i18n("Comfortable"),
            i18n("Compact")
        ]
    }

    QQC2.SpinBox {
        id: refreshInterval

        Kirigami.FormData.label: i18n("Refresh interval (seconds):")
        from: 1
        to: 15
    }

    QQC2.ComboBox {
        id: gpuBackend

        Kirigami.FormData.label: i18n("GPU backend:")
        model: [
            i18n("Automatic"),
            i18n("AMD"),
            i18n("NVIDIA"),
            i18n("Disabled")
        ]
    }

    QQC2.CheckBox {
        id: animationsEnabled

        Kirigami.FormData.label: i18n("Cat animations:")
        text: i18n("Enable animations")
    }

    Kirigami.Separator {
        Kirigami.FormData.label: i18n("Visible metrics")
        Kirigami.FormData.isSection: true
    }

    QQC2.CheckBox {
        id: showCpu
        Kirigami.FormData.label: i18n("System metrics:")
        text: i18n("CPU")
    }

    QQC2.CheckBox {
        id: showMemory
        text: i18n("Memory")
    }

    QQC2.CheckBox {
        id: showBattery
        text: i18n("Battery")
    }

    QQC2.CheckBox {
        id: showTemperature
        text: i18n("Temperature")
    }

    QQC2.CheckBox {
        id: showFan
        text: i18n("Fan speed")
    }

    QQC2.CheckBox {
        id: showStorage
        text: i18n("Storage")
    }

    QQC2.CheckBox {
        id: showGpu
        Kirigami.FormData.label: i18n("GPU metrics:")
        text: i18n("GPU")
    }
}
