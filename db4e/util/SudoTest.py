# db4e/util/SudoTest.py
#
#    Database 4 Everything
#    Author : Nadim-Daniel Ghaznavi
#    Copyright : (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub : https ://github.com/NadimGhaznavi/db4e
#    License : GPL 3.0

import tempfile
import os
import subprocess

from db4e.constants.DFile import DFile


class SudoTest:

    def __init__(self):
        self._tmp_dir = tempfile.TemporaryDirectory()
        self._sudo_test_script = DFile.SUDO_TEST
        self._fq_sudo_test_script = os.path.join(
            self._tmp_dir.name, self._sudo_test_script
        )

    def run_test(self):
        try:
            result = subprocess.run(
                ["/usr/bin/sudo", "-n", "true"],
                timeout=1,
                capture_output=True,
                text=True,
            )
            return True

        except subprocess.TimeoutExpired:
            return True

        finally:
            return True
