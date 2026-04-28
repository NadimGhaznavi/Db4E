# db4e/mgr/LogMgr.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

import os


class LogMgr:

    def get_log_lines(self, log_file, num_lines):
        num_lines = int(num_lines)
        if not os.path.exists(log_file):
            return []

        with open(log_file, "rb") as f:
            f.seek(0, os.SEEK_END)
            buffer = bytearray()
            pointer = f.tell()
            lines_found = 0
            while pointer > 0 and lines_found <= num_lines:
                block_size = min(1024, pointer)
                pointer -= block_size
                f.seek(pointer)
                buffer[:0] = f.read(block_size)
                lines_found = buffer.count(b"\n")
            return buffer.decode(errors="ignore").splitlines()[-num_lines:]
