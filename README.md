# Nyarch Cat Dashboard

A kawaii system companion for Linux, built as a KDE Plasma 6 desktop widget.
It displays system and hardware readings in a configurable dashboard.

## Features

- CPU use and frequency when the system exposes frequency data.
- Memory and swap usage.
- Battery charge, health, energy, and cycle information when available.
- Temperature, fan, and storage readings when exposed by Linux system interfaces.
- GPU readings for AMD and NVIDIA. NVIDIA monitoring uses the optional
  `nvidia-smi` command; AMD monitoring reads the kernel's `amdgpu` sysfs data.
- Configurable layout, tile density, refresh interval, animations, and visible
  metrics.

Some readings depend on hardware and kernel support. Missing values are simply
unavailable on systems that do not expose the corresponding data. The automatic
GPU mode tries NVIDIA first and then AMD; the backend can also be selected in the
widget settings.

## Requirements

- Linux with KDE Plasma 6 (the package metadata declares Plasma 6.0 as its
  minimum version).
- Python 3, available to the Plasma session. The widget's monitor script uses
  only Python's standard library.
- `nvidia-smi` is optional and needed only for NVIDIA GPU monitoring. AMD GPU
  monitoring uses Linux `amdgpu` sysfs data and does not need an extra utility.

The widget reads standard Linux interfaces such as `/proc`, `/sys`, and
`/sys/class/hwmon`. Which metrics are available depends on the kernel, drivers,
and hardware.

## Install from a local checkout

For a tagged download, get the `.plasmoid` package from the project's
[GitHub Releases](https://github.com/gqpdx/nyarch-cat-dashboard/releases), then
install it for your user:

```sh
kpackagetool6 --type Plasma/Applet --install ./nyarch-cat-dashboard-v0.1.0.plasmoid
```

After installation, add **Nyarch Cat Dashboard** from Plasma's **Add Widgets**
interface.

To install directly from a source checkout instead, continue with the steps
below.

1. Install KDE Plasma 6 and Python 3 if they are not already installed.
2. Open a terminal in the directory containing this README and `metadata.json`.
3. Install the widget for your user:

   ```sh
   kpackagetool6 --type Plasma/Applet --install .
   ```

4. Add **Nyarch Cat Dashboard** from Plasma's **Add Widgets** interface. If it doesn't appear in the widget list, reload the Plasma shell or sign out and back in,
   then check **Add Widgets** again.

To update an existing user installation from this checkout, run:

```sh
kpackagetool6 --type Plasma/Applet --upgrade .
```

To remove the installed package, run:

```sh
kpackagetool6 --type Plasma/Applet --remove com.nyarch.catdashboard
```

## Configure

Open the widget's settings to choose the layout, number of columns, tile
density, refresh interval, animation setting, and which metrics to show. The
GPU backend can be set to automatic, AMD, NVIDIA, or disabled.

## Run the tests

From the project root, run:

```sh
python3 -m unittest discover -s tests -v
```

The GPU tests mock command output and hardware interfaces where appropriate;
they do not replace testing against physical hardware. NVIDIA hardware behavior
in particular should be confirmed on an NVIDIA system before making hardware
compatibility claims.

## Project layout

```text
contents/   Plasma widget configuration, QML interface, and monitoring script
tests/      Python unit tests
metadata.json  Plasma package metadata
```

## License

This project is licensed under the GNU General Public License, version 3 or (at
your option) any later version. See [LICENSE](LICENSE).
