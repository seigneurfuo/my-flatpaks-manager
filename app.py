import os
import subprocess

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('XApp', '1.0')
gi.require_version('Flatpak', '1.0')

from gi.repository import Gtk, XApp, Flatpak, GLib


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.liststore_tab0 = Gtk.ListStore(str, str, str)
        self.liststore_tab1 = Gtk.ListStore(str, str, str, str)

        # Create a StatusIcon
        #self.status_icon = XApp.StatusIcon()
        #self.status_icon.set_from_icon_name("dialog-information")
        #self.status_icon.set_title("My XApp Example")
        #self.status_icon.set_tooltip_text("This is an example using XApp.StatusIcon")
        #self.status_icon.set_visible(True)

        self._init_ui()
        self._init_events()

    def _init_events(self) -> None:
        self.connect("destroy", Gtk.main_quit)
        self.notebook.connect('switch-page', self._on_notebook_page_switched)

    def _init_ui(self) -> None:
        self.set_default_size(800, 600)

        self.set_title("MyFlatpaksManager - 0.1")
        self.set_position(Gtk.WindowPosition.CENTER)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        self._init_ui_tab0()
        self._init_ui_tab1()

    def _init_ui_tab0(self):
        box = Gtk.Box()
        vbox = Gtk.VBox()
        box.add(vbox)
        self.notebook.append_page(box, Gtk.Label(label="Installed"))

        # scrolled_window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        vbox.pack_start(scrolled_window, True, True, 0)

        button = Gtk.Button(label="Launch")
        button.connect("clicked", self.on_launch_button_clicked)
        vbox.pack_start(button, False, False, 0)

        treeview = Gtk.TreeView(model=self.liststore_tab0)
        self.treeview_tab0 = treeview
        scrolled_window.add(treeview)

        # Tableau
        # Création d'une colonne texte pour le nom
        column_text = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=0)
        treeview.append_column(column_text)

        column_text = Gtk.TreeViewColumn("Version", Gtk.CellRendererText(), text=1)
        treeview.append_column(column_text)

        column_text = Gtk.TreeViewColumn("Type", Gtk.CellRendererText(), text=2)
        treeview.append_column(column_text)

    def _init_ui_tab1(self):
        box = Gtk.Box()
        vbox = Gtk.VBox()
        box.add(vbox)
        self.notebook.append_page(box, Gtk.Label(label="Avaiable"))

        # scrolled_window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        vbox.pack_start(scrolled_window, True, True, 0)

        button = Gtk.Button(label="Install")
        button.connect("clicked", self.on_install_button_clicked)
        vbox.pack_start(button, False, False, 0)

        treeview = Gtk.TreeView(model=self.liststore_tab1)
        self.treeview_tab1 = treeview

        scrolled_window.add(treeview)

        # Tableau
        # Création d'une colonne texte pour le nom
        column_text = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=0)
        treeview.append_column(column_text)

        column_text = Gtk.TreeViewColumn("Branch", Gtk.CellRendererText(), text=1)
        treeview.append_column(column_text)

        column_text = Gtk.TreeViewColumn("Arch", Gtk.CellRendererText(), text=2)
        treeview.append_column(column_text)

        column_text = Gtk.TreeViewColumn("Remote", Gtk.CellRendererText(), text=3)
        treeview.append_column(column_text)


    def _fill_treeview_tab0(self) -> None:
        installation = Flatpak.Installation.new_system()
        refs = Flatpak.Installation.list_installed_refs(installation)
        for ref in refs:
            # Kind
            kind = ref.get_kind()
            if kind == Flatpak.RefKind.APP:
                kind_str = "Application"
            elif kind == Flatpak.RefKind.RUNTIME:
                kind_str = "Runtime"
            else:
                kind_str = "?"

            data = [ref.get_name(), ref.get_appdata_version(), kind_str]
            self.liststore_tab0.append(data)

    def _fill_treeview_tab1(self):
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

                data = [ref.get_name(), ref.get_arch(), ref.get_branch(), remote.get_name()]
                self.liststore_tab1.append(data)

    def _on_notebook_page_switched(self, notebook, tab, index):
        if index == 0:
            self._fill_treeview_tab0()
        elif index == 1:
            self._fill_treeview_tab1()

    def on_launch_button_clicked(self, widget) -> None:
        selection = self.treeview_tab0.get_selection()
        model, treeiter = selection.get_selected()

        if not treeiter:
            return

        app_id = model[treeiter][0]

        cmd = ['flatpak', 'run', app_id]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

    def on_install_button_clicked(self, widget) -> None:
        selection = self.treeview_tab1.get_selection()
        model, treeiter = selection.get_selected()

        if not treeiter:
            return

        app_id = model[treeiter][0]
        branch = model[treeiter][1]
        arch = model[treeiter][2]
        remote_name = model[treeiter][3]

        ref_name = f"app/{app_id}/{arch}/{branch}"

        installation = Flatpak.Installation.new_system()
        transaction = Flatpak.Transaction.new_for_installation(installation)
        result = transaction.add_install(remote_name, ref_name)

        def on_progress(transaction, progress, user_data):
            print(f"Progress : {progress * 100:.2f}%")

        transaction.connect("new-operation", on_progress, None)

        try:
            result = transaction.run()
            if result == Flatpak.TransactionResult.DONE:
                print(f"Installdone for{ref_name}")
            else:
                print(f"Error while installing: {ref_name}.")
        except GLib.Error as e:
            print(f"Error: {ref_name} : {e.message}")


def main():
    app = MainWindow()
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()