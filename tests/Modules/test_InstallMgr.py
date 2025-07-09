"""
tests/Modules/test_InstallMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""
import os, sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from db4e.Modules.InstallMgr import InstallMgr
from db4e.Constants.Fields import (
    BIN_DIR_FIELD, BLOCKCHAIN_DIR_FIELD, DB4E_FIELD, CONF_DIR_FIELD, GOOD_FIELD, 
    ENABLE_FIELD, GROUP_FIELD, INSTALL_DIR_FIELD, LOG_DIR_FIELD,
    MONEROD_FIELD, P2POOL_FIELD, 
    RUN_DIR_FIELD, SERVICE_FILE_FIELD, SOCKET_FILE_FIELD, SYSTEMD_DIR_FIELD, 
    TEMPLATE_DIR_FIELD, TMP_DIR_ENVIRON_FIELD, USER_FIELD,
    USER_WALLET_FIELD, VENDOR_DIR_FIELD, 
    VERSION_FIELD, XMRIG_FIELD
)
from db4e.Constants.SystemdTemplates import (
    DB4E_USER_PLACEHOLDER, DB4E_GROUP_PLACEHOLDER, DB4E_DIR_PLACEHOLDER,
    MONEROD_DIR_PLACEHOLDER, P2POOL_DIR_PLACEHOLDER, XMRIG_DIR_PLACEHOLDER
)
from db4e.Constants.Labels import DB4E_LABEL, INSTALL_DIR_LABEL
from tests.conftest import get_effective_user_group, has_message, has_status

def test_configmgr_init(config):
    install_mgr = InstallMgr(config)
    assert install_mgr is not None

def test_check_form_data_valid(install_mgr, sample_rec):
    # Patch the deployment manager
    install_mgr.depl_mgr.update_deployment = MagicMock()

    user_wallet = "44abcdefxyz1234567890"
    vendor_dir = "/opt/db4e/vendor"

    results, updated_rec, abort = install_mgr._check_form_data(
        user_wallet, vendor_dir, sample_rec.copy()
    )

    assert not abort
    assert updated_rec[USER_WALLET_FIELD] == user_wallet
    assert updated_rec[VENDOR_DIR_FIELD] == vendor_dir
    install_mgr.depl_mgr.update_deployment.assert_called_once_with(updated_rec)

def test_check_form_data_missing_wallet(install_mgr, sample_rec):
    install_mgr.depl_mgr.update_deployment = MagicMock()

    user_wallet = ""
    vendor_dir = "/opt/db4e/vendor"

    results, updated_rec, abort = install_mgr._check_form_data(
        user_wallet, vendor_dir, sample_rec.copy()
    )

    assert abort
    # Check that at least one result dict's message contains the error string
    assert has_message(results, "Missing Monero Wallet")
    install_mgr.depl_mgr.update_deployment.assert_not_called()

def test_check_form_data_missing_vendor_dir(install_mgr, sample_rec):
    install_mgr.depl_mgr.update_deployment = MagicMock()

    user_wallet = "44abcdefxyz1234567890"
    vendor_dir = ""

    results, updated_rec, abort = install_mgr._check_form_data(
        user_wallet, vendor_dir, sample_rec.copy()
    )

    assert abort
    # Check that at least one result dict's message contains the error string
    assert has_message(results, "Missing Deployment Directory")
    install_mgr.depl_mgr.update_deployment.assert_not_called()

def test_check_form_data_missing_wallet_and_vendor_dir(install_mgr, sample_rec):
    install_mgr.depl_mgr.update_deployment = MagicMock()

    user_wallet = ""
    vendor_dir = ""

    results, updated_rec, abort = install_mgr._check_form_data(
        user_wallet, vendor_dir, sample_rec.copy()
    )

    assert abort
    # Check that at the result dict's message contains both error strings
    assert has_message(results, "Missing Monero Wallet")
    assert has_message(results, "Missing Deployment Directory")

    install_mgr.depl_mgr.update_deployment.assert_not_called()

def test_create_vendor_dir_creates_new_dir(install_mgr, tmp_path):
    vendor_dir = tmp_path / "new_vendor_dir"
    results, abort = install_mgr._create_vendor_dir(str(vendor_dir), [])
    assert not abort
    assert has_message(results, "Created")
    assert vendor_dir.exists()

def test_create_vendor_dir_backs_up_existing_dir(install_mgr, tmp_path):
    vendor_dir = tmp_path / "existing_vendor_dir"
    vendor_dir.mkdir()

    original_rename = os.rename  # Save original function

    def rename_side_effect(src, dst):
        return original_rename(src, dst)  # Call original, not patched one

    with patch("os.rename", side_effect=rename_side_effect) as mock_rename:
        results, abort = install_mgr._create_vendor_dir(str(vendor_dir), [])
        mock_rename.assert_called_once()
        assert not abort
    assert has_message(results, "Backed up old deployment")

def test_create_vendor_dir_backup_fails(install_mgr, tmp_path):
    vendor_dir = tmp_path / "existing_vendor_dir"
    vendor_dir.mkdir()
    with patch("os.rename", side_effect=PermissionError("Denied")):
        results, abort = install_mgr._create_vendor_dir(str(vendor_dir), [])
    assert abort
    assert has_message(results, "Failed to backup")

def test_create_vendor_dir_makedirs_fails(install_mgr, tmp_path):
    vendor_dir = tmp_path / "new_vendor_dir"
    with patch("os.makedirs", side_effect=PermissionError("Denied")):
        results, abort = install_mgr._create_vendor_dir(str(vendor_dir), [])
    assert abort
    assert has_message(results, "Failed to create directory")

def test_check_or_create_db4e_rec_existing(install_mgr):
    mock_rec = {"_id": "existing"}
    install_mgr.depl_mgr.get_deployment = MagicMock(return_value=mock_rec)
    install_mgr.depl_mgr.get_new_rec = MagicMock()

    results, rec = install_mgr._check_or_create_db4e_rec()

    assert rec == mock_rec
    assert has_message(results, f"Found existing {DB4E_LABEL} deployment record")
    install_mgr.depl_mgr.get_deployment.assert_called_once_with(DB4E_FIELD)
    install_mgr.depl_mgr.get_new_rec.assert_not_called()

def test_check_or_create_db4e_rec_new(install_mgr):
    mock_rec = {"_id": "new"}
    install_mgr.depl_mgr.get_deployment = MagicMock(return_value=None)
    install_mgr.depl_mgr.get_new_rec = MagicMock(return_value=mock_rec)

    results, rec = install_mgr._check_or_create_db4e_rec()

    assert rec == mock_rec
    assert results == []  # no message in this branch
    install_mgr.depl_mgr.get_deployment.assert_called_once_with(DB4E_FIELD)
    install_mgr.depl_mgr.get_new_rec.assert_called_once_with(DB4E_FIELD)

def test_copy_monerod_files_success(install_mgr, tmp_path):
    results = []

    vendor_dir = tmp_path / "vendor"
    vendor_dir.mkdir()

    with patch.object(install_mgr, "_get_templates_dir", return_value="/fake/templates"), \
         patch("db4e.Modules.InstallMgr.shutil.copy") as mock_copy:

        updated_results = install_mgr._copy_monerod_files(str(vendor_dir), results)

        assert mock_copy.call_count == 2
        assert has_status(updated_results, GOOD_FIELD)
        assert len(updated_results) == 2

def test_copy_p2pool_files_success(install_mgr, tmp_path):
    results = []

    vendor_dir = tmp_path / "vendor"
    vendor_dir.mkdir()

    with patch.object(install_mgr, "_get_templates_dir", return_value="/fake/templates"), \
         patch("db4e.Modules.InstallMgr.shutil.copy") as mock_copy:

        updated_results = install_mgr._copy_p2pool_files(str(vendor_dir), results)

        assert mock_copy.call_count == 2
        assert has_status(updated_results, GOOD_FIELD)
        assert len(updated_results) == 2

def test_copy_xmrig_file_success(install_mgr, tmp_path):
    results = []

    vendor_dir = tmp_path / "vendor"
    vendor_dir.mkdir()

    with patch.object(install_mgr, "_get_templates_dir", return_value="/fake/templates"), \
         patch("db4e.Modules.InstallMgr.shutil.copy") as mock_copy:

        updated_results = install_mgr._copy_xmrig_file(str(vendor_dir), results)

        assert mock_copy.call_count == 1
        assert has_status(updated_results, GOOD_FIELD)
        assert len(updated_results) == 1

def test_create_monerod_dirs_calls_mkdir_correctly(install_mgr, tmp_path):
    vendor_dir = str(tmp_path / "vendor")

    monerod_dir_name = f"monerod-{install_mgr.ini.config[MONEROD_FIELD][VERSION_FIELD]}"

    with patch("os.mkdir") as mock_mkdir:
        install_mgr._create_monerod_dirs(vendor_dir)

    expected_calls = [
        call(os.path.join(vendor_dir, monerod_dir_name)),
        call(os.path.join(vendor_dir, install_mgr.ini.config[MONEROD_FIELD][BLOCKCHAIN_DIR_FIELD])),
    ]

    # Also the subdirs under monerod_dir
    for sub_dir in [
        install_mgr.ini.config[DB4E_FIELD][BIN_DIR_FIELD],
        install_mgr.ini.config[DB4E_FIELD][CONF_DIR_FIELD],
        install_mgr.ini.config[DB4E_FIELD][RUN_DIR_FIELD],
        install_mgr.ini.config[DB4E_FIELD][LOG_DIR_FIELD],
    ]:
        expected_calls.append(call(os.path.join(vendor_dir, monerod_dir_name, sub_dir)))

    mock_mkdir.assert_has_calls(expected_calls, any_order=True)
    assert mock_mkdir.call_count == len(expected_calls)

def test_create_p2pool_dirs_calls_mkdir_correctly(install_mgr, tmp_path):
    vendor_dir = str(tmp_path / "vendor")

    p2pool_version = install_mgr.ini.config[P2POOL_FIELD][VERSION_FIELD]
    p2pool_dir_name = f"{P2POOL_FIELD}-{p2pool_version}"

    with patch("os.mkdir") as mock_mkdir:
        install_mgr._create_p2pool_dirs(vendor_dir)

    expected_calls = [
        call(os.path.join(vendor_dir, p2pool_dir_name)),
    ]

    for sub_dir in [
        install_mgr.ini.config[DB4E_FIELD][BIN_DIR_FIELD],
        install_mgr.ini.config[DB4E_FIELD][CONF_DIR_FIELD],
        install_mgr.ini.config[DB4E_FIELD][RUN_DIR_FIELD],
    ]:
        expected_calls.append(call(os.path.join(vendor_dir, p2pool_dir_name, sub_dir)))

    mock_mkdir.assert_has_calls(expected_calls, any_order=True)
    assert mock_mkdir.call_count == len(expected_calls)

def test_create_xmrig_dirs_calls_mkdir_correctly(install_mgr, tmp_path):
    vendor_dir = str(tmp_path / "vendor")

    xmrig_version = install_mgr.ini.config[XMRIG_FIELD][VERSION_FIELD]
    xmrig_dir_name = f"{XMRIG_FIELD}-{xmrig_version}"

    with patch("os.mkdir") as mock_mkdir:
        install_mgr._create_xmrig_dirs(vendor_dir)

    expected_calls = [
        call(os.path.join(vendor_dir, xmrig_dir_name)),
    ]

    for sub_dir in [
        install_mgr.ini.config[DB4E_FIELD][BIN_DIR_FIELD],
        install_mgr.ini.config[DB4E_FIELD][CONF_DIR_FIELD],
    ]:
        expected_calls.append(call(os.path.join(vendor_dir, xmrig_dir_name, sub_dir)))

    mock_mkdir.assert_has_calls(expected_calls, any_order=True)
    assert mock_mkdir.call_count == len(expected_calls)

def test_generate_db4e_service_file_writes_correct_contents(install_mgr, tmp_path):
    user, group = get_effective_user_group()
    vendor_dir = str(tmp_path / "vendor")
    vendor_dir_path = Path(vendor_dir)
    vendor_dir_path.mkdir()

    # Setup fake template and tmp dir
    tmpl_dir = tmp_path / "templates"
    tmp_dir = tmp_path / "tmp"
    tmpl_dir.mkdir()
    tmp_dir.mkdir()

    systemd_dir = install_mgr.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
    service_file_name = install_mgr.ini.config[DB4E_FIELD][SERVICE_FILE_FIELD]
    template_path = tmpl_dir / DB4E_FIELD / systemd_dir
    template_path.mkdir(parents=True)

    # Create dummy template content
    service_template_file = template_path / service_file_name
    service_template_file.write_text(
        f"[[{DB4E_USER_PLACEHOLDER}]]\n[[{DB4E_GROUP_PLACEHOLDER}]]\n[[{DB4E_DIR_PLACEHOLDER}]]"
    )

    # Patch paths and placeholder replacement
    with patch.object(install_mgr, "_get_templates_dir", return_value=str(tmpl_dir)), \
         patch.object(install_mgr, "_get_tmp_dir", return_value=str(tmp_dir)), \
        patch("db4e.Modules.InstallMgr.get_effective_identity", return_value={USER_FIELD: user, GROUP_FIELD: group}):

        install_mgr._generate_db4e_service_file(str(vendor_dir))

    # Assert that file was written with expected content
    written_file = tmp_dir / service_file_name
    assert written_file.exists()

    expected_content = f"{user}\n{group}\n{os.path.join(vendor_dir, DB4E_FIELD)}"
    actual_content = written_file.read_text()
    assert actual_content == expected_content

def test_generate_monerod_service_files_writes_correct_contents(install_mgr, tmp_path):
    from pathlib import Path
    user, group = get_effective_user_group()
    vendor_dir = str(tmp_path / "vendor")
    Path(vendor_dir).mkdir()

    tmpl_dir = tmp_path / "templates"
    tmp_dir = tmp_path / "tmp"
    tmpl_dir.mkdir()
    tmp_dir.mkdir()

    monerod_version = install_mgr.ini.config[MONEROD_FIELD][VERSION_FIELD]
    monerod_dir = f"{MONEROD_FIELD}-{monerod_version}"
    systemd_dir = install_mgr.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
    monerod_service_file = install_mgr.ini.config[MONEROD_FIELD][SERVICE_FILE_FIELD]
    monerod_socket_file = install_mgr.ini.config[MONEROD_FIELD][SOCKET_FILE_FIELD]

    service_template_path = tmpl_dir / monerod_dir / systemd_dir
    service_template_path.mkdir(parents=True)

    # Write mock template files with placeholders
    (service_template_path / monerod_service_file).write_text(
        f"[[{MONEROD_DIR_PLACEHOLDER}]]\n[[{DB4E_USER_PLACEHOLDER}]]\n[[{DB4E_GROUP_PLACEHOLDER}]]"
    )
    (service_template_path / monerod_socket_file).write_text(
        f"[[{MONEROD_DIR_PLACEHOLDER}]]\n[[{DB4E_USER_PLACEHOLDER}]]\n[[{DB4E_GROUP_PLACEHOLDER}]]"
    )

    with patch.object(install_mgr, "_get_templates_dir", return_value=str(tmpl_dir)), \
         patch.object(install_mgr, "_get_tmp_dir", return_value=str(tmp_dir)), \
         patch("db4e.Modules.InstallMgr.get_effective_identity", return_value={USER_FIELD: user, GROUP_FIELD: group}):

        install_mgr._generate_monerod_service_files(vendor_dir)

    # Assert service and socket files exist and have the correct contents
    fq_expected_dir = os.path.join(vendor_dir, monerod_dir)
    expected_contents = f"{fq_expected_dir}\n{user}\n{group}"

    written_service_file = tmp_dir / monerod_service_file
    written_socket_file = tmp_dir / monerod_socket_file

    assert written_service_file.exists()
    assert written_socket_file.exists()
    assert written_service_file.read_text() == expected_contents
    assert written_socket_file.read_text() == expected_contents

def test_generate_p2pool_service_files_writes_correct_contents(install_mgr, tmp_path):
    from pathlib import Path
    user, group = get_effective_user_group()
    vendor_dir = str(tmp_path / "vendor")
    Path(vendor_dir).mkdir()

    tmpl_dir = tmp_path / "templates"
    tmp_dir = tmp_path / "tmp"
    tmpl_dir.mkdir()
    tmp_dir.mkdir()

    p2pool_version = install_mgr.ini.config[P2POOL_FIELD][VERSION_FIELD]
    p2pool_dir = f"{P2POOL_FIELD}-{p2pool_version}"
    systemd_dir = install_mgr.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
    p2pool_service_file = install_mgr.ini.config[P2POOL_FIELD][SERVICE_FILE_FIELD]
    p2pool_socket_file = install_mgr.ini.config[P2POOL_FIELD][SOCKET_FILE_FIELD]

    service_template_path = tmpl_dir / p2pool_dir / systemd_dir
    service_template_path.mkdir(parents=True)

    # Write mock template files with placeholders
    (service_template_path / p2pool_service_file).write_text(
        f"[[{P2POOL_DIR_PLACEHOLDER}]]\n[[{DB4E_USER_PLACEHOLDER}]]\n[[{DB4E_GROUP_PLACEHOLDER}]]"
    )
    (service_template_path / p2pool_socket_file).write_text(
        f"[[{P2POOL_DIR_PLACEHOLDER}]]\n[[{DB4E_USER_PLACEHOLDER}]]\n[[{DB4E_GROUP_PLACEHOLDER}]]"
    )

    with patch.object(install_mgr, "_get_templates_dir", return_value=str(tmpl_dir)), \
         patch.object(install_mgr, "_get_tmp_dir", return_value=str(tmp_dir)), \
         patch("db4e.Modules.InstallMgr.get_effective_identity", return_value={USER_FIELD: user, GROUP_FIELD: group}):

        install_mgr._generate_p2pool_service_files(vendor_dir)

    # Assert service and socket files exist and have the correct contents
    fq_expected_dir = os.path.join(vendor_dir, p2pool_dir)
    expected_contents = f"{fq_expected_dir}\n{user}\n{group}"

    written_service_file = tmp_dir / p2pool_service_file
    written_socket_file = tmp_dir / p2pool_socket_file

    assert written_service_file.exists()
    assert written_socket_file.exists()
    assert written_service_file.read_text() == expected_contents
    assert written_socket_file.read_text() == expected_contents

def test_generate_xmrig_service_file_writes_correct_contents(install_mgr, tmp_path):
    from pathlib import Path
    user, group = get_effective_user_group()
    vendor_dir = str(tmp_path / "vendor")
    Path(vendor_dir).mkdir()

    tmpl_dir = tmp_path / "templates"
    tmp_dir = tmp_path / "tmp"
    tmpl_dir.mkdir()
    tmp_dir.mkdir()

    xmrig_version = install_mgr.ini.config[XMRIG_FIELD][VERSION_FIELD]
    xmrig_dir = f"{XMRIG_FIELD}-{xmrig_version}"
    systemd_dir = install_mgr.ini.config[DB4E_FIELD][SYSTEMD_DIR_FIELD]
    xmrig_service_file = install_mgr.ini.config[XMRIG_FIELD][SERVICE_FILE_FIELD]
    
    service_template_path = tmpl_dir / xmrig_dir / systemd_dir
    service_template_path.mkdir(parents=True)

    # Write mock template files with placeholders
    (service_template_path / xmrig_service_file).write_text(
        f"[[{XMRIG_DIR_PLACEHOLDER}]]\n[[{DB4E_USER_PLACEHOLDER}]]\n[[{DB4E_GROUP_PLACEHOLDER}]]"
    )
    
    with patch.object(install_mgr, "_get_templates_dir", return_value=str(tmpl_dir)), \
         patch.object(install_mgr, "_get_tmp_dir", return_value=str(tmp_dir)), \
         patch("db4e.Modules.InstallMgr.get_effective_identity", return_value={USER_FIELD: user, GROUP_FIELD: group}):

        install_mgr._generate_xmrig_service_file(vendor_dir)

    # Assert service and socket files exist and have the correct contents
    fq_expected_dir = os.path.join(vendor_dir, xmrig_dir)
    expected_contents = f"{fq_expected_dir}\n{user}\n{group}"

    written_service_file = tmp_dir / xmrig_service_file
    
    assert written_service_file.exists()
    assert written_service_file.read_text() == expected_contents
    
def test_get_templates_dir_returns_expected_path(install_mgr):
    expected_relative = install_mgr.ini.config[DB4E_FIELD][TEMPLATE_DIR_FIELD]
    base_path = os.path.dirname(sys.modules[install_mgr.__module__].__file__)
    expected_path = os.path.abspath(os.path.join(base_path, '..', expected_relative))

    result = install_mgr._get_templates_dir()

    assert result == expected_path

def test_get_tmp_dir_sets_env_var_and_returns_path(install_mgr):
    tmp_dir = install_mgr._get_tmp_dir()

    assert TMP_DIR_ENVIRON_FIELD in os.environ
    assert os.environ[TMP_DIR_ENVIRON_FIELD] == tmp_dir
    assert os.path.exists(tmp_dir)

def test_init_db4e_rec_sets_fields_and_appends_results(install_mgr):
    # Setup
    fake_rec = {}
    results = []
    user, group = get_effective_user_group()

    # Patch
    with patch("db4e.Modules.InstallMgr.get_effective_identity", return_value={USER_FIELD: user, GROUP_FIELD: group}), \
         patch.object(install_mgr.depl_mgr, "add_deployment") as mock_add:

        updated_results, updated_rec = install_mgr._init_db4e_rec(fake_rec, results)

    # Validate the record
    assert updated_rec[USER_FIELD] == user
    assert updated_rec[GROUP_FIELD] == group
    assert INSTALL_DIR_FIELD in updated_rec
    assert os.path.isdir(updated_rec[INSTALL_DIR_FIELD])

    # Validate results
    assert has_message(updated_results, f"Created new {DB4E_LABEL} deployment record")
    assert has_message(updated_results, f"Added user ({user}) to the {DB4E_LABEL} deployment record")
    assert has_message(updated_results, f"Added group ({group}) to the {DB4E_LABEL} deployment record")
    assert has_message(updated_results, f"Added the {DB4E_LABEL} {INSTALL_DIR_LABEL} to the deployment record")

    # Validate that the DB write was called
    mock_add.assert_called_once_with(updated_rec)

def test_replace_placeholders_replaces_all_correctly(tmp_path, install_mgr):
    # Create dummy template file
    template_file = tmp_path / "template.txt"
    template_file.write_text("Hello [[NAME]], welcome to [[PLACE]]!")

    # Define placeholders
    placeholders = {
        "NAME": "Nadim",
        "PLACE": "Db4E Land",
    }

    # Call the method
    result = install_mgr._replace_placeholders(str(template_file), placeholders)

    # Check that placeholders were replaced
    assert result == "Hello Nadim, welcome to Db4E Land!"

def test_run_sudo_installer_success(monkeypatch, install_mgr, tmp_path):
    results = []
    vendor_dir = str(tmp_path / "vendor")
    db4e_rec = {}

    # Mocks
    monkeypatch.setattr(install_mgr, "_get_tmp_dir", lambda: tmp_path)
    monkeypatch.setattr("db4e.Modules.InstallMgr.get_effective_identity", lambda: {USER_FIELD: "dan", GROUP_FIELD: "dan"})
    monkeypatch.setattr("subprocess.run", lambda *a, **k: type('Proc', (), {
        "returncode": 0,
        "stdout": b"Success output",
        "stderr": b"",
    })())
    monkeypatch.setattr("shutil.rmtree", lambda path: None)
    monkeypatch.setattr(install_mgr.depl_mgr, "update_deployment", lambda rec: None)

    updated_results = install_mgr._run_sudo_installer(vendor_dir, db4e_rec, results)

    assert has_status(updated_results, GOOD_FIELD)
    assert db4e_rec.get(ENABLE_FIELD) is True
