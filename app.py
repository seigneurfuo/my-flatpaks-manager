import os
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('XApp', '1.0')

from gi.repository import Gtk, XApp, GLib

import utils

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.liststore_tab0 = Gtk.ListStore(str, str, str, str, utils.flatpak_ref)
        self.liststore_tab1 = Gtk.ListStore(str, str, str, str, str, utils.flatpak_ref)

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

        for col_index, col_name in enumerate(["Name", "Package", "Version", "Type"]):
            column_text = Gtk.TreeViewColumn(col_name, Gtk.CellRendererText(), text=col_index)
            treeview.append_column(column_text)

    def _init_ui_tab1(self):
        box = Gtk.Box()
        vbox = Gtk.VBox()
        box.add(vbox)
        self.notebook.append_page(box, Gtk.Label(label="Available"))

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

        for col_index, col_name in enumerate(["Name", "Package", "Branch", "Arch", "Remote"]):
            column_text = Gtk.TreeViewColumn(col_name, Gtk.CellRendererText(), text=col_index)
            treeview.append_column(column_text)

    def _init_ui_tab2(self):
        box = Gtk.Box()
        vbox = Gtk.VBox()
        box.add(vbox)
        self.notebook.append_page(box, Gtk.Label(label="Updates"))

        # scrolled_window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        vbox.pack_start(scrolled_window, True, True, 0)

        # Launch button
        launch_button = Gtk.Button(label="Update")
        launch_button.connect("clicked", self._on_update_button_clicked)
        vbox.pack_start(launch_button, False, False, 0)

        treeview = Gtk.TreeView(model=self.liststore_tab2)
        self.treeview_tab2 = treeview
        scrolled_window.add(treeview)

        for col_index, col_name in enumerate(["Name"]): # TODO: ["Name", "Version", "New Version", "Type"]
            column_text = Gtk.TreeViewColumn(col_name, Gtk.CellRendererText(), text=col_index)
            treeview.append_column(column_text)

    def _fill_all(self):
        self._fill_treeview_tab0()
        self._fill_treeview_tab1()
        self._fill_treeview_tab2()

    def _fill_treeview_tab0(self) -> None:
        self.liststore_tab0.clear()

        refs = utils.flatpak_get_installed_refs()
        for ref in refs:
            data = [
                ref.get_appdata_name(),
                ref.get_name(),
                utils.get_flatpak_ref_version_str(ref),
                utils.get_flatpak_ref_kind_str(ref),
                ref
            ]
            self.liststore_tab0.append(data)

    def _fill_treeview_tab1(self):
        refs = utils.flatpak_get_remotes_applications()
        for ref in refs:
            data = [
                ref.get_name(),
                ref.get_name(),
                ref.get_arch(),
                ref.get_branch(),
                ref.get_remote_name(),
                ref
            ]
            self.liststore_tab1.append(data)

    def _fill_treeview_tab2(self):
        self.liststore_tab2.clear()

        refs = utils.flatpak_get_updates()
        for ref in refs:
            data = [
                ref
            ]
            self.liststore_tab2.append(data)

    def _on_notebook_page_switched(self, notebook, tab, index):
        if index == 0:
            self._fill_treeview_tab0()
        elif index == 1:
            self._fill_treeview_tab1()
        elif index == 2:
            self._fill_treeview_tab2()

    def _on_launch_button_clicked(self, widget) -> None:
        selection = self.treeview_tab0.get_selection()
        model, treeiter = selection.get_selected()

        if not treeiter:
            return

        # Fixme
        app_id = model[treeiter][1]
        utils.flatpak_launch_app(app_id)

    def on_install_button_clicked(self, widget) -> None:
        selection = self.treeview_tab1.get_selection()
        model, treeiter = selection.get_selected()

        if not treeiter:
            return

        ref = model[treeiter][-1]
        utils.flatpak_install_package(ref)

    def on_uninstall_button_clicked(self):
        selection = self.treeview_tab0.get_selection()
        model, treeiter = selection.get_selected()

        if not treeiter:
            return

        ref = model[treeiter][-1]
        utils.flatpak_uninstall_package(ref)

def main():
    app = MainWindow()
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()