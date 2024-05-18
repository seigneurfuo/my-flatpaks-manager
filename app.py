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
        self.liststore = Gtk.ListStore(str, str, str)

        # Create a StatusIcon
        #self.status_icon = XApp.StatusIcon()
        #self.status_icon.set_from_icon_name("dialog-information")
        #self.status_icon.set_title("My XApp Example")
        #self.status_icon.set_tooltip_text("This is an example using XApp.StatusIcon")
        #self.status_icon.set_visible(True)

        self._init_ui()
        self._init_events()
        self._fill_treeview()

    def _init_ui(self) -> None:
        self.set_default_size(800, 600)

        self.set_title("MyFlatpaksManager - 0.1")
        self.set_position(Gtk.WindowPosition.CENTER)

        label = Gtk.Label(label="Hello, XApp!")
        #self.add(label)

        vbox = Gtk.VBox()

        # scrolled_window
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_hexpand(True)

        self.treeview = Gtk.TreeView(model=self.liststore)

        # Tableau
        # Création d'une colonne texte pour le nom
        column_text = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=0)
        self.treeview.append_column(column_text)

        column_text = Gtk.TreeViewColumn("Version", Gtk.CellRendererText(), text=1)
        self.treeview.append_column(column_text)

        column_text = Gtk.TreeViewColumn("Type", Gtk.CellRendererText(), text=2)
        self.treeview.append_column(column_text)

        self.scrolled_window.add(self.treeview)

        self.button = Gtk.Button(label="Launch")
        self.button.connect("clicked", self.on_launch_button_clicked)

        vbox.pack_start(self.scrolled_window, True, True, 0)
        vbox.pack_start(self.button, False, False, 0)

        self.add(vbox)

    def _init_events(self) -> None:
        self.connect("destroy", Gtk.main_quit)

    def _fill_treeview(self) -> None:
        installation = Flatpak.Installation.new_system()
        installed = Flatpak.Installation.list_installed_refs(installation)
        for package in installed:
            # Kind
            kind = package.get_kind()
            if kind == Flatpak.RefKind.APP:
                kind_str = "Application"
            elif kind == Flatpak.RefKind.RUNTIME:
                kind_str = "Runtime"
            else:
                kind_str = "?"

            data = [package.get_name(), package.get_appdata_version(), kind_str]
            self.liststore.append(data)

    def on_launch_button_clicked(self, widget) -> None:
        selection = self.treeview.get_selection()
        model, treeiter = selection.get_selected()

        if not treeiter:
            return

        app_id = model[treeiter][0]
        cmd = ['flatpak', 'run', app_id]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

def main():
    app = MainWindow()
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()