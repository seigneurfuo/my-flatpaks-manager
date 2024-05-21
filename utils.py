import subprocess

import gi
gi.require_version('Flatpak', '1.0')
from gi.repository import Flatpak

flatpak_ref = Flatpak.Ref

def flatpak_get_installed_refs():
    installation = Flatpak.Installation.new_system()
    return Flatpak.Installation.list_installed_refs(installation)

def flatpak_get_remotes_applications():
    installation = Flatpak.Installation.new_system()
    remotes = installation.list_remotes()

    for remote in remotes:
        if remote.get_disabled():
            continue

        refs = installation.list_remote_refs_sync(remote.get_name(), None)
        for ref in refs:
            kind_str = ref.get_kind()
            if kind_str != Flatpak.RefKind.APP:
                continue

            yield ref
def flatpak_install_package(ref: Flatpak.Ref):
    installation = Flatpak.Installation.new_system()
    transaction = Flatpak.Transaction.new_for_installation(installation)
    transaction.connect("new-operation", _on_progress, None)
    result = transaction.add_install(ref.get_remote_name(), ref.format_ref())

    _flatpak_check_transaction_result(transaction, ref, result)

def flatpak_uninstall_package(ref: Flatpak.Ref):
    installation = Flatpak.Installation.new_system()
    transaction = Flatpak.Transaction.new_for_installation(installation)
    transaction.connect("new-operation", _on_progress, None)

    _flatpak_check_transaction_result(transaction, ref, result)

def flatpak_launch_app(app_id):
    cmd = ['flatpak', 'run', app_id]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

def _flatpak_check_transaction_result(transaction, ref, result):
    ref_name = ref.get_name()
    try:
        result = transaction.run()
        if result:
            print(f"Install done for: {ref_name}")
        else:
            print(f"Error while installing: {ref_name}.")
    except GLib.Error as e:
        print(f"Error: {ref_name} : {e.message}")

def _on_progress(operation, transaction, progress, _):
    print(f"Progress : {progress.get_progress() * 100:.2f}%")

def get_flatpak_ref_version_str(ref):
    appdata_version = ref.get_appdata_version()
    if appdata_version:
        return appdata_version
    else:
        return ref.get_branch()

def get_flatpak_ref_kind_str(ref):
    kind = ref.get_kind()
    if kind == Flatpak.RefKind.APP:
        kind_str = "Application"
    elif kind == Flatpak.RefKind.RUNTIME:
        kind_str = "Runtime"
    else:
        kind_str = "?"

    return kind_str