import os
import tomllib
import tomli_w  # install via `pip install tomli-w`


class BootstrapMgr:
    """
    Handles reading and writing the ~/.db4e bootstrap configuration.
    This file contains minimal system-level information needed before
    the SQLite DB is accessible (e.g. vendor_dir, user_wallet, etc).
    """

    CONFIG_PATH = os.path.expanduser("~/.db4e")

    def __init__(self):
        self._config = {}
        if os.path.exists(self.CONFIG_PATH):
            self._config = self._load()
        else:
            self._config = {}

    def _load(self):
        with open(self.CONFIG_PATH, "rb") as f:
            return tomllib.load(f)

    def _save(self):
        with open(self.CONFIG_PATH, "wb") as f:
            tomli_w.dump(self._config, f)

    def initialize(self, vendor_dir: str, user_wallet: str = None):
        """
        Create a new bootstrap config file.
        """
        if not os.path.isdir(vendor_dir):
            os.makedirs(vendor_dir, exist_ok=True)

        self._config["vendor_dir"] = os.path.abspath(vendor_dir)
        if user_wallet:
            self._config["user_wallet"] = user_wallet
        self._save()

    def get_vendor_dir(self) -> str:
        """Return the configured vendor directory path."""
        return self._config.get("vendor_dir")

    def get_user_wallet(self) -> str:
        """Return the configured Monero wallet (if available)."""
        return self._config.get("user_wallet")

    def is_initialized(self) -> bool:
        """Check whether bootstrap configuration exists."""
        return os.path.exists(self.CONFIG_PATH)

    def __repr__(self):
        return f"BootstrapMgr(vendor_dir={self.get_vendor_dir()}, user_wallet={self.get_user_wallet()})"
