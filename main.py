#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Folder watch: application to monitor a folder.

Application that displays an icon in the notification area. The icon is
updated when a new file appears in a specific folder. A click on the icon
opens the new file.
"""

import gobject
import gtk
import os
import stat
import subprocess
import time


class FolderWatch(object):
    """An icon that show a folder status (usefule for CupsPDF for example)."""

    def __init__(self):
        """Create the icon and init status."""
        self._next_update = None
        self._last_file_seen = None
        self._folder = "/home/gl/PDF/"
        self._command = "/home/gl/bin/show_last_pdf"
        self.statusicon = gtk.StatusIcon()
        self.statusicon.set_from_stock(gtk.STOCK_PRINT)
        self.statusicon.connect("popup-menu", self.right_click_event)
        self.statusicon.connect("activate", self.activated)
        self.statusicon.set_tooltip("FolderWatch")

    def activated(self, icon):
        """Handle the activate event."""
        self.statusicon.set_from_stock(gtk.STOCK_PRINT)
        self.statusicon.set_tooltip("FolderWatch")
        subprocess.call([self._command], shell=True)

    def refresh(self):
        """Refresh the icon status."""
        if self._next_update is None or time.time() > self._next_update:
            self._refresh()
            self._next_update = time.time() + 0.8
        return True

    def right_click_event(self, icon, button, time):
        """Handle right click event on icon."""
        menu = gtk.Menu()

        about = gtk.MenuItem("About")
        quit = gtk.MenuItem("Quit")

        about.connect("activate", self.show_about_dialog)
        quit.connect("activate", gtk.main_quit)

        menu.append(about)
        menu.append(quit)

        menu.show_all()

        menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusicon)

    def show_about_dialog(self, widget):
        """Show about dialog."""
        about_dialog = gtk.AboutDialog()

        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name("Folder Watch")
        about_dialog.set_version("1.0")
        about_dialog.set_authors([u"Ghislain Lévêque"])

        about_dialog.run()
        about_dialog.destroy()

    def _refresh(self):
        entries = ((os.path.join(self._folder, fn)
                   for fn in os.listdir(self._folder)))
        entries = ((os.stat(path), path) for path in entries)
        entries = ((stat_data[stat.ST_CTIME], path)
                   for stat_data, path in entries
                   if stat.S_ISREG(stat_data[stat.ST_MODE]))
        last_date, last_name = sorted(entries)[-1]
        if self._last_file_seen is None or self._last_file_seen < last_date:
            self.statusicon.set_from_stock(gtk.STOCK_PRINT_REPORT)
            self.statusicon.set_tooltip("Last file: {} ({})".format(
                last_name, time.ctime(last_date)
            ))
            self._last_file_seen = last_date


def main():
    """Launch the app."""
    app = FolderWatch()
    gobject.timeout_add(1, app.refresh)
    gtk.main()

if __name__ == "__main__":
    main()
