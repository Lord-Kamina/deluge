from platformdirs import PlatformDirs
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys

dirs = PlatformDirs("deluge", ensure_exists=True)
config_dir = dirs.user_config_dir
logs_dir = dirs.user_log_dir

bundle_path = Path(__file__).parent.parent
os.environ["GTK_PATH"] = str(bundle_path / "Resources/share")
os.environ["GI_TYPELIB_PATH"] = str(bundle_path / "Resources/gi_typelibs")
os.environ["GDK_PIXBUF_MODULEDIR"] = str(bundle_path / "Resources/lib/gdk-pixbuf/loaders")
os.environ["GDK_PIXBUF_MODULE_FILE"] = str(bundle_path / "Resources/lib/gdk-pixbuf/loaders.cache")

old_config_dirs = [ 
	Path(os.path.expanduser("~/Library/Preferences/org.deluge-2.0")),
	Path(os.path.expanduser("~/.config/deluge")),
]
for old_config in old_config_dirs:
	exclude_paths = shutil.ignore_patterns(
		"deluged.pid",
		"plugins",
		"gtkui*",
		"deluged.log",
		"ipc",
		os.path.join(old_config,"deluge-gtk"),
		os.path.join(old_config,"deluge-gtk.lock"),
		)
	if (Path.is_dir(dirs.user_config_path / "gtk3ui_state")):
		print(f"Deluge 2.x data already found at {config_dir}")
		break
	if (Path.is_dir(old_config)):
		print(f"Old Deluge data found at {old_config}, will try to import it.")
		shutil.copytree(old_config / "", dirs.user_config_path,symlinks=True, ignore=exclude_paths, dirs_exist_ok=True)
		break
style = ""
defaults_proc = subprocess.run(
	[ "defaults", "read", "-g", "AppleInterfaceStyle" ],
	text=True,
	capture_output=True
	)
if defaults_proc.returncode == 0:
	style = defaults_proc.stdout.strip()
gtk_theme = "WhiteSur-Dark" if style == "Dark" else "WhiteSur-Light"
os.environ["GTK_THEME"] = gtk_theme

defaults_proc = subprocess.run(
	[ "defaults", "read", "-g", "AppleLanguages" ],
	text=True,
	capture_output=True
	)
match = re.search(r'([a-zA-Z0-9-]+)', defaults_proc.stdout)
lang = match.group(1).replace("-", "_") if match else "en_US"
lang += ".UTF-8"
os.environ["LANG"] = lang