import subprocess

import gi
gi.require_version('Flatpak', '1.0')
from gi.repository import Flatpak, GLib

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
def flatpak_install_package(window, ref: Flatpak.Ref):
    installation = Flatpak.Installation.new_system()
    transaction = Flatpak.Transaction.new_for_installation(installation)
    transaction.set_parent_window(str(window.get_window().get_xid()))
    transaction.connect("new-operation", _on_progress, None)
    result = transaction.add_install(ref.get_remote_name(), ref.format_ref())

    return _flatpak_check_transaction_result(transaction, ref)

def flatpak_uninstall_package(window, ref: Flatpak.Ref):
    installation = Flatpak.Installation.new_system()
    transaction = Flatpak.Transaction.new_for_installation(installation)
    transaction.set_parent_window(str(window.get_window().get_xid()))
    transaction.connect("new-operation", _on_progress, None)
    result = transaction.add_uninstall(ref.format_ref())

    return _flatpak_check_transaction_result(transaction, ref)

def flatpak_get_updates():
    installation = Flatpak.Installation.new_system()
    installed_refs = flatpak_get_installed_refs()

    updates = []
    for ref in installed_refs:
        installed_version = ref.get_commit()
        installed_ref = ref.format_ref()

        remote_refs = installation.list_remote_refs_sync(ref.get_origin(), None)
        for remote_ref in remote_refs:
            if remote_ref.format_ref() == installed_ref:
                remote_version = remote_ref.get_commit()
                if installed_version != remote_version:
                    updates.append(installed_ref)
                    break

    return updates

def flatpak_update_packages(packages):
    installation = Flatpak.Installation.new_system(None)  # ou Flatpak.Installation.new_user(None) pour l'installation utilisateur
    transaction = Flatpak.Transaction.new_for_installation(installation)
    for package in packages:
        transaction.add_update(package, None)

    return _flatpak_check_transaction_result(transaction, None)

def flatpak_launch_app(app_id):
    cmd = ['flatpak', 'run', app_id]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

def _flatpak_check_transaction_result(transaction, ref):
    ref_name = ref.get_name() if ref else "" # FIXME
    try:
        #transaction.connect("operation-changed", _on_progress, None)
        result = transaction.run()
        if result:
            print(f"Install done for: {ref_name}")
        else:
            print(f"Error while installing: {ref_name}.")

        return result

    except GLib.Error as e:
        print(f"Error: {ref_name} : {e.message}")
        return None

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