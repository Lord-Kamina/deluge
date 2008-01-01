#
# addtorrentdialog.py
#
# Copyright (C) 2007 Andrew Resch ('andar') <andrewresch@gmail.com>
# 
# Deluge is free software.
# 
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 2 of the License, or (at your option)
# any later version.
# 
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA    02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.

import pygtk
pygtk.require('2.0')
import gtk, gtk.glade
import gettext

import pkg_resources

import deluge.component as component
import deluge.ui.gtkui.listview as listview
from deluge.configmanager import ConfigManager
from deluge.log import LOG as log
import deluge.common

class AddTorrentDialog:
    def __init__(self, parent=None):
        self.glade = gtk.glade.XML(
            pkg_resources.resource_filename(
                "deluge.ui.gtkui", "glade/add_torrent_dialog.glade"))
        
        self.dialog = self.glade.get_widget("dialog_add_torrent")
        
        self.dialog.set_transient_for(component.get("MainWindow").window)
        
        self.glade.signal_autoconnect({
            "on_button_file_clicked": self._on_button_file_clicked,
            "on_button_url_clicked": self._on_button_url_clicked,
            "on_button_hash_clicked": self._on_button_hash_clicked,
            "on_button_remove_clicked": self._on_button_remove_clicked,
            "on_button_trackers_clicked": self._on_button_trackers_clicked,
            "on_button_cancel_clicked": self._on_button_cancel_clicked,
            "on_button_add_clicked": self._on_button_add_clicked
        })

        
        self.torrent_liststore = gtk.ListStore(str, str)
        self.files_liststore = gtk.ListStore(bool, str, int)
        # Holds the files info
        self.files = {}
        
        self.listview_torrents = self.glade.get_widget("listview_torrents")
        self.listview_files = self.glade.get_widget("listview_files")

        render = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Torrent"), render, text=1)
        self.listview_torrents.append_column(column)

        render = gtk.CellRendererToggle()
        render.connect("toggled", self._on_file_toggled)
        column = gtk.TreeViewColumn(None, render, active=0)
        self.listview_files.append_column(column)
        
        render = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Filename"), render, text=1)
        column.set_expand(True)
        self.listview_files.append_column(column)

        render = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Size"))
        column.pack_start(render)
        column.set_cell_data_func(render, listview.cell_data_size, 2)
        self.listview_files.append_column(column)
        
        self.listview_torrents.set_model(self.torrent_liststore)
        self.listview_files.set_model(self.files_liststore)

        self.listview_torrents.get_selection().connect("changed", 
                                    self._on_torrent_changed)

    def show(self):
        self.dialog.show_all()
        return None
    
    def hide(self):
        self.dialog.destroy()
        return None
    
    def add_to_torrent_list(self, filenames):
        import deluge.libtorrent as lt
        import os.path

        for filename in filenames:
            # Get the torrent data from the torrent file
            try:
                log.debug("Attempting to open %s for add.", filename)
                _file = open(filename, "rb")
                filedump = lt.bdecode(_file.read())
                _file.close()
            except IOError, e:
                log.warning("Unable to open %s: e", filename, e)
                continue
            
            info = lt.torrent_info(filedump)

            # Get list of files from torrent info
            files = []
            for f in info.files():
                files.append({
                    'path': f.path,
                    'size': f.size,
                    'download': True
                })

            name = os.path.split(filename)[-1] + ": " + info.name()
            self.torrent_liststore.append([str(info.info_hash()), name])
            self.files[str(info.info_hash())] = files


    def _on_torrent_changed(self, treeselection):
        (model, row) = treeselection.get_selected()
        self.files_liststore.clear()
        
        if row is None:
            return
            
        files_list = self.files[model.get_value(row, 0)]

        for file_dict in files_list:
            self.files_liststore.append([
                file_dict["download"], 
                file_dict["path"], 
                file_dict["size"]
                ])
    
    def _on_file_toggled(self, render, path):
        row = self.files_liststore.get_iter(path)
        self.files_liststore.set_value(
            row, 0, not self.files_liststore.get_value(row, 0))
        
    def _on_button_file_clicked(self, widget):
        log.debug("_on_button_file_clicked")
        # Setup the filechooserdialog
        chooser = gtk.FileChooserDialog(_("Choose a .torrent file"),
            None,
            gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, 
                        gtk.RESPONSE_OK))

        chooser.set_transient_for(self.dialog)
        chooser.set_select_multiple(True)
        chooser.set_property("skip-taskbar-hint", True)
        
        # Add .torrent and * file filters
        file_filter = gtk.FileFilter()
        file_filter.set_name(_("Torrent files"))
        file_filter.add_pattern("*." + "torrent")
        chooser.add_filter(file_filter)
        file_filter = gtk.FileFilter()
        file_filter.set_name(_("All files"))
        file_filter.add_pattern("*")
        chooser.add_filter(file_filter)

        # Load the 'default_load_path' from the config
        self.config = ConfigManager("gtkui.conf")
        if self.config.get("default_load_path") is not None:
            chooser.set_current_folder(self.config.get("default_load_path"))

        # Run the dialog
        response = chooser.run()

        if response == gtk.RESPONSE_OK:
            result = chooser.get_filenames()
            self.config.set("default_load_path", chooser.get_current_folder())
        else:
            chooser.destroy()
            return

        chooser.destroy()
        self.add_to_torrent_list(result)
                                        
    def _on_button_url_clicked(self, widget):
        log.debug("_on_button_url_clicked")
        dialog = self.glade.get_widget("url_dialog")
        entry = self.glade.get_widget("entry_url")

        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_transient_for(self.dialog)

        if deluge.common.windows_check():
            import win32clipboard as clip 
            import win32con
            clip.OpenClipboard() 
            text = clip.GetClipboardData(win32con.CF_UNICODETEXT) 
            clip.CloseClipboard() 
        else:
            clip = gtk.clipboard_get(selection='PRIMARY')
            text = clip.wait_for_text()
        if text:
            text = text.strip()
            if deluge.common.is_url(text):
                entry.set_text(text)

        dialog.show_all()
        response = dialog.run()

        if response == gtk.RESPONSE_OK:
            url = entry.get_text().decode("utf_8")
        else:
            url = None

        log.debug("url: %s", url)
        dialog.hide()


    def _on_button_hash_clicked(self, widget):
        log.debug("_on_button_hash_clicked")

    def _on_button_remove_clicked(self, widget):
        log.debug("_on_button_remove_clicked")
        (model, row) = self.listview_torrents.get_selection().get_selected()
        if row is None:
            return
            
        torrent_id = model.get_value(row, 0)
        
        model.remove(row)
        del self.files[torrent_id]

    def _on_button_trackers_clicked(self, widget):
        log.debug("_on_button_trackers_clicked")

    def _on_button_cancel_clicked(self, widget):
        log.debug("_on_button_cancel_clicked")
        self.hide()

    def _on_button_add_clicked(self, widget):
        log.debug("_on_button_add_clicked")

