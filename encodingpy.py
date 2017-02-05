from gi.repository import GObject, Gtk, Gedit, PeasGtk, Gio, GtkSource, GLib
#import os, sys
#import inspect

enc_array = []

def ReloadFileAsyncCallback(obj, result, usr_data):
  obj.load_finish(result)

class EncodingWindowActivatable(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "EncodingWindowActivatable"

    window = GObject.property(type=Gedit.Window)
    view_dict = {}
    _proxy_dict = {}

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        for i in range(len(enc_array)):
          action = Gio.SimpleAction(name="encoding" + str(i))
          action.connect('activate', self.encoding)
          self.window.add_action(action)


    def do_deactivate(self):
        for i in range(len(enc_array)):
          self.window.remove_action("encoding" + str(i))

    def do_update_state(self):
        pass

    def encoding(self, action, parameter, user_data=None):
        enc_num = action.get_property("name")[8:]
        enc = enc_array[int(enc_num)]
        doc = self.window.get_active_document()
        source_file = doc.get_file()
        se = source_file.get_encoding().copy()
        loader = GtkSource.FileLoader.new(doc, doc.get_file())
        loader.set_candidate_encodings ([se.get_from_charset(enc)])
        loader.load_async(GLib.PRIORITY_DEFAULT, None, None, None, ReloadFileAsyncCallback , enc)




class EncodingAppActivatable(GObject.Object, Gedit.AppActivatable):

    app = GObject.property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        global enc_array
        settings = Gio.Settings.new("org.gnome.gedit.preferences.encodings")
        enc_array = settings.get_strv("candidate-encodings")
        settings = None
        self.menu = Gio.Menu()
        for i in range(len(enc_array)):
          sub_menu_item = Gio.MenuItem.new(enc_array[i], "win.encoding" + str(i))
          self.menu.append_item(sub_menu_item)
        self.menu_item = Gio.MenuItem.new_submenu("Encoding", self.menu)
        self.menu_ext = self.extend_menu("file-section")
        self.menu_ext.append_menu_item(self.menu_item)

    def do_deactivate(self):
        self.menu = None
        self.menu_item = None
        self.menu_ext = None
