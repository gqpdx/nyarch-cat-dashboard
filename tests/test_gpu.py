
#!/usr/bin/env python3

import sys
import unittest
import subprocess

from pathlib import Path
from unittest.mock import patch, MagicMock

# Make the monitoring script importable from the tests directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(
    0,
    str(PROJECT_ROOT / "contents" / "scripts")
)

import linux_monitor


class TestNvidiaGPU(unittest.TestCase):

    @patch("linux_monitor.shutil.which", return_value="/usr/bin/nvidia-smi")
    @patch("linux_monitor.subprocess.run")
    def test_successful_detection(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(
            stdout="NVIDIA GeForce RTX 4070, 52, 45, 4096, 12288, 35\n"
        )

        result = linux_monitor.read_nvidia_gpu()

        self.assertEqual(result["vendor"], "NVIDIA")
        self.assertEqual(result["name"], "NVIDIA GeForce RTX 4070")
        self.assertEqual(result["temperature"], 52)
        self.assertEqual(result["utilization"], 45)
        self.assertEqual(result["memory_used"], 4096)
        self.assertEqual(result["memory_total"], 12288)
        self.assertEqual(result["fan_speed"], 35)

    @patch("linux_monitor.shutil.which", return_value="/usr/bin/nvidia-smi")
    @patch("linux_monitor.subprocess.run")
    def test_unavailable_metrics(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(
            stdout="NVIDIA GPU, N/A, N/A, N/A, 8192, N/A\n"
        )

        result = linux_monitor.read_nvidia_gpu()

        self.assertEqual(result["vendor"], "NVIDIA")
        self.assertIsNone(result["temperature"])
        self.assertIsNone(result["utilization"])
        self.assertIsNone(result["memory_used"])
        self.assertEqual(result["memory_total"], 8192)
        self.assertIsNone(result["fan_speed"])

    @patch("linux_monitor.shutil.which", return_value=None)
    def test_missing_nvidia_smi(self, mock_which):
        result = linux_monitor.read_nvidia_gpu()

        self.assertIsNone(result)

    @patch("linux_monitor.shutil.which", return_value="/usr/bin/nvidia-smi")
    @patch("linux_monitor.subprocess.run")
    def test_driver_or_gpu_unavailable(self, mock_run, mock_which):
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "nvidia-smi"
        )

        result = linux_monitor.read_nvidia_gpu()

        self.assertIsNone(result)

    @patch("linux_monitor.shutil.which", return_value="/usr/bin/nvidia-smi")
    @patch("linux_monitor.subprocess.run")
    def test_command_timeout(self, mock_run, mock_which):
        mock_run.side_effect = subprocess.TimeoutExpired(
            "nvidia-smi", 2
        )

        result = linux_monitor.read_nvidia_gpu()

        self.assertIsNone(result)

    @patch("linux_monitor.shutil.which", return_value="/usr/bin/nvidia-smi")
    @patch("linux_monitor.subprocess.run")
    def test_malformed_output(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(
            stdout="NVIDIA GPU, 52, 45\n"
        )

        result = linux_monitor.read_nvidia_gpu()

        self.assertIsNone(result)

    @patch("linux_monitor.shutil.which", return_value="/usr/bin/nvidia-smi")
    @patch("linux_monitor.subprocess.run")
    def test_empty_output(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(stdout="")

        result = linux_monitor.read_nvidia_gpu()

        self.assertIsNone(result)


    @patch("linux_monitor.shutil.which", return_value="/usr/bin/nvidia-smi")
    @patch("linux_monitor.subprocess.run")
    def test_extra_whitespace(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(
            stdout="  NVIDIA GPU  ,  55  ,  70  ,  4096  ,  8192  ,  40  \n"
        )

        result = linux_monitor.read_nvidia_gpu()

        self.assertEqual(result["name"], "NVIDIA GPU")
        self.assertEqual(result["temperature"], 55)
        self.assertEqual(result["utilization"], 70)
        self.assertEqual(result["memory_used"], 4096)
        self.assertEqual(result["memory_total"], 8192)
        self.assertEqual(result["fan_speed"], 40)

    @patch("linux_monitor.shutil.which", return_value="/usr/bin/nvidia-smi")
    @patch("linux_monitor.subprocess.run")
    def test_non_numeric_metrics(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(
            stdout="NVIDIA GPU, invalid, unknown, N/A, 8192, N/A\n"
        )

        result = linux_monitor.read_nvidia_gpu()

        self.assertIsNone(result["temperature"])
        self.assertIsNone(result["utilization"])
        self.assertIsNone(result["memory_used"])
        self.assertEqual(result["memory_total"], 8192)
        self.assertIsNone(result["fan_speed"])

    @patch("linux_monitor.shutil.which", return_value="/usr/bin/nvidia-smi")
    @patch("linux_monitor.subprocess.run")
    def test_negative_metrics(self, mock_run, mock_which):
        mock_run.return_value.stdout = "RTX 4090, -1, -1, -1, -1, -1\n"

        result = linux_monitor.read_nvidia_gpu()

        self.assertIsNotNone(result)

        self.assertIsNone(result["temperature"])
        self.assertIsNone(result["utilization"])
        self.assertIsNone(result["memory_used"])
        self.assertIsNone(result["memory_total"])
        self.assertIsNone(result["fan_speed"])

    @patch("linux_monitor.shutil.which", return_value="/usr/bin/nvidia-smi")
    @patch("linux_monitor.subprocess.run")
    def test_multiple_gpu_rows_uses_first(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(
            stdout=(
                "NVIDIA GPU 1, 50, 30, 2048, 8192, 25\n"
                "NVIDIA GPU 2, 60, 70, 4096, 8192, 45\n"
            )
        )

        result = linux_monitor.read_nvidia_gpu()

        self.assertEqual(result["name"], "NVIDIA GPU 1")
        self.assertEqual(result["temperature"], 50)

    @patch("linux_monitor.shutil.which", return_value="/usr/bin/nvidia-smi")
    @patch("linux_monitor.subprocess.run")
    def test_empty_gpu_name(self, mock_run, mock_which):
        mock_run.return_value.stdout = " , 45, 30, 4096, 16384, 50\n"

        result = linux_monitor.read_nvidia_gpu()

        self.assertIsNone(result)

    @patch("linux_monitor.shutil.which", return_value="/usr/bin/nvidia-smi")
    @patch("linux_monitor.subprocess.run")
    def test_missing_metric_fields(self, mock_run, mock_which):
        mock_run.return_value.stdout = "RTX 4090, 45, , 4096, , 50\n"

        result = linux_monitor.read_nvidia_gpu()

        self.assertIsNotNone(result)
        self.assertIsNone(result["utilization"])
        self.assertIsNone(result["memory_total"])

class TestGPUSelection(unittest.TestCase):

    @patch("linux_monitor.read_amd_gpu")
    @patch("linux_monitor.read_nvidia_gpu")
    def test_automatic_prefers_nvidia(
        self, mock_nvidia, mock_amd
    ):
        mock_nvidia.return_value = {"vendor": "NVIDIA"}
        mock_amd.return_value = {"vendor": "AMD"}

        result = linux_monitor.read_gpu("auto")

        self.assertEqual(result["vendor"], "NVIDIA")
        mock_amd.assert_not_called()

    @patch("linux_monitor.read_amd_gpu")
    @patch("linux_monitor.read_nvidia_gpu")
    def test_automatic_falls_back_to_amd(
        self, mock_nvidia, mock_amd
    ):
        mock_nvidia.return_value = None
        mock_amd.return_value = {"vendor": "AMD"}

        result = linux_monitor.read_gpu("auto")

        self.assertEqual(result["vendor"], "AMD")

    @patch("linux_monitor.read_amd_gpu")
    @patch("linux_monitor.read_nvidia_gpu")
    def test_manual_nvidia_selection(
        self, mock_nvidia, mock_amd
    ):
        mock_nvidia.return_value = {"vendor": "NVIDIA"}

        result = linux_monitor.read_gpu("nvidia")

        self.assertEqual(result["vendor"], "NVIDIA")
        mock_amd.assert_not_called()

    @patch("linux_monitor.read_amd_gpu")
    @patch("linux_monitor.read_nvidia_gpu")
    def test_manual_amd_selection(
        self, mock_nvidia, mock_amd
    ):
        mock_amd.return_value = {"vendor": "AMD"}

        result = linux_monitor.read_gpu("amd")

        self.assertEqual(result["vendor"], "AMD")
        mock_nvidia.assert_not_called()

    @patch("linux_monitor.read_amd_gpu")
    @patch("linux_monitor.read_nvidia_gpu")
    def test_disabled_backend(
        self, mock_nvidia, mock_amd
    ):
        result = linux_monitor.read_gpu("disabled")

        self.assertIsNone(result)
        mock_nvidia.assert_not_called()
        mock_amd.assert_not_called()


    @patch("linux_monitor.read_amd_gpu", return_value=None)
    @patch("linux_monitor.read_nvidia_gpu", return_value=None)
    def test_automatic_when_no_gpu_available(
        self, mock_nvidia, mock_amd
    ):
        result = linux_monitor.read_gpu("auto")

        self.assertIsNone(result)
        mock_nvidia.assert_called_once()
        mock_amd.assert_called_once()


class TestAmdGPU(unittest.TestCase):

    def setUp(self):
        self.patches = []

        self.mock_listdir = patch(
            "linux_monitor.os.listdir"
        )
        self.mock_read = patch(
            "linux_monitor.read_file"
        )

        self.listdir = self.mock_listdir.start()
        self.read = self.mock_read.start()

        self.patches.extend([
            self.mock_listdir,
            self.mock_read
        ])

        self.listdir.return_value = ["card0", "renderD128"]

    def tearDown(self):
        for mocked in reversed(self.patches):
            mocked.stop()

    def configure_gpu(self, files):
        def read_file(path):
            return files.get(path)

        self.read.side_effect = read_file

        def listdir(path):
            if path == "/sys/class/drm":
                return ["card0", "renderD128"]

            if path == "/sys/class/drm/card0/device/hwmon":
                return ["hwmon0"]

            if path.endswith("/hwmon0"):
                return [
                    "name",
                    "temp1_input", "temp1_label",
                    "temp2_input", "temp2_label",
                    "temp3_input", "temp3_label",
                    "fan1_input"
                ]

            return []

        self.listdir.side_effect = listdir

    def test_successful_detection(self):
        files = {
            "/sys/class/drm/card0/device/vendor": "0x1002",
            "/sys/class/drm/card0/device/hwmon/hwmon0/name": "amdgpu",
            "/sys/class/drm/card0/device/hwmon/hwmon0/device/product_name":
                "AMD Radeon RX 9070 XT",

            "/sys/class/drm/card0/device/hwmon/hwmon0/temp1_input": "52000",
            "/sys/class/drm/card0/device/hwmon/hwmon0/temp1_label": "edge",

            "/sys/class/drm/card0/device/hwmon/hwmon0/temp2_input": "60000",
            "/sys/class/drm/card0/device/hwmon/hwmon0/temp2_label": "junction",

            "/sys/class/drm/card0/device/hwmon/hwmon0/temp3_input": "65000",
            "/sys/class/drm/card0/device/hwmon/hwmon0/temp3_label": "mem",

            "/sys/class/drm/card0/device/hwmon/hwmon0/fan1_input": "1200",

            "/sys/class/drm/card0/device/gpu_busy_percent": "45",
            "/sys/class/drm/card0/device/mem_info_vram_used": "4294967296",
            "/sys/class/drm/card0/device/mem_info_vram_total": "17179869184"
        }

        self.configure_gpu(files)

        result = linux_monitor.read_amd_gpu()

        self.assertEqual(result["vendor"], "AMD")
        self.assertEqual(result["name"], "AMD Radeon RX 9070 XT")
        self.assertEqual(result["temperature"], 52.0)
        self.assertEqual(result["hotspot"], 60.0)
        self.assertEqual(result["utilization"], 45)
        self.assertEqual(result["memory_used"], 4096)
        self.assertEqual(result["memory_total"], 16384)
        self.assertEqual(result["fan_speed"], 1200)

    def test_zero_rpm_fan(self):
        files = {
            "/sys/class/drm/card0/device/vendor": "0x1002",
            "/sys/class/drm/card0/device/hwmon/hwmon0/name": "amdgpu",
            "/sys/class/drm/card0/device/hwmon/hwmon0/temp1_input": "52000",
            "/sys/class/drm/card0/device/hwmon/hwmon0/temp1_label": "edge",
            "/sys/class/drm/card0/device/hwmon/hwmon0/fan1_input": "0"
        }

        self.configure_gpu(files)

        result = linux_monitor.read_amd_gpu()

        self.assertEqual(result["fan_speed"], 0)

    def test_missing_gpu(self):
        self.listdir.return_value = []

        result = linux_monitor.read_amd_gpu()

        self.assertIsNone(result)

    def test_missing_gpu_metrics(self):
        files = {
            "/sys/class/drm/card0/device/vendor": "0x1002",
            "/sys/class/drm/card0/device/hwmon/hwmon0/name": "amdgpu"
        }

        self.configure_gpu(files)

        result = linux_monitor.read_amd_gpu()

        self.assertIsNone(result)

    def test_non_amd_device_is_ignored(self):
        files = {
            "/sys/class/drm/card0/device/vendor": "0x10de"
        }

        self.configure_gpu(files)

        result = linux_monitor.read_amd_gpu()

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
