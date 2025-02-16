import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import os
os.environ['GDK_BACKEND'] = 'x11'
import sys

def show_about_dialog():
    about_dialog = Gtk.AboutDialog()
    about_dialog.set_program_name("Yel-Updater")
    about_dialog.set_version("1.0 v060225a Elena")
    about_dialog.set_comments("Gestor de actualizaciones CLI/Python para CuerdOS GNU/Linux.")
    about_dialog.set_website("https://github.com/CuerdOS")
    about_dialog.set_website_label("GitHub")
    about_dialog.set_license_type(Gtk.License.GPL_3_0)
    about_dialog.set_authors([
        "Ale D.M ",
        "Leo H. Pérez (GatoVerde95)",
        "Pablo G.",
        "Welkis",
        "GatoVerde95 Studios",
        "CuerdOS Community"
    ])
    logo_path = find_icon_path("yelena.svg")
    if logo_path:
        logo_pixbuf = GdkPixbuf.Pixbuf.new_from_file(logo_path)
        about_dialog.set_logo(logo_pixbuf)
    
    about_dialog.connect("response", lambda dialog, response: dialog.destroy())
    about_dialog.run()

def find_icon_path(icon_name):
    possible_paths = [
        f"/usr/share/icons/{icon_name}",
        f"/usr/local/share/icons/{icon_name}",
        f"./{icon_name}"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--about":
        show_about_dialog()
    else:
        print("Usage: python3 about.py")