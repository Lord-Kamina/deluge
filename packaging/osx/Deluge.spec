# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata, collect_data_files
from pathlib import Path

def exclude_plugin_dirs(item):
	return (
		'deluge/plugins' not in item[0] or
		('deluge/plugins' in item[0] and
		item[0].endswith('.whl'))
	)

preliminary_datas = collect_data_files('deluge')

deluge_metadata = copy_metadata('deluge')
deluge_resources = list(filter(exclude_plugin_dirs, preliminary_datas))

block_cipher = None
from PyInstaller.utils.hooks import exec_statement
deluge_version=exec_statement('from version import get_version; print(get_version())')

# print(f"Spec located in dir: {Path(__file__).parent}")
print(f"deluge metadata: {deluge_metadata}")

deluge_datas = [
	(os.path.join(SPECPATH, "torrent.icns"),'.'),
	(os.path.join(SPECPATH, "launchd"),'launchd'),
	(os.path.join(SPECPATH, "../../deluge/ui"), 'deluge/ui'),
	(os.path.join(SPECPATH, "../../deluge/ui/console"), 'deluge/ui/console')
] + deluge_resources + deluge_metadata

main_entry_points = [
	os.path.join(SPECPATH, "macos_app_shims/start_ui.py"),
	os.path.join(SPECPATH, "macos_app_shims/start_console.py"),
	os.path.join(SPECPATH, "macos_app_shims/start_daemon.py"),
	os.path.join(SPECPATH, "macos_app_shims/start_web.py")
]

print(f"main_entry_points: {main_entry_points}")

a = Analysis(
    main_entry_points,
    pathex=[os.path.join(SPECPATH, "../../")],
    binaries=[],
    datas=deluge_datas,
    hiddenimports=['deluge', 'deluge.*', 'deluge.plugins.init', 'deluge.plugins.pluginbase'],
    hookspath=[],
    hooksconfig={
    	"gi": {
    		"icons": ["Adwaita", "hicolor"],
    		"themes": ["Mac", "WhiteSur-Light", "WhiteSur-Dark", "Tahoe-Light", "Tahoe-Dark"]
    	}
    },
    runtime_hooks=[os.path.join(SPECPATH, "macos_app_shims/macos_environment.py")],
    excludes=[],
    noarchive=False,
    optimize=0,
)

all_hooks = [s for s in a.scripts if os.path.join(SPECPATH,s[1]) not in main_entry_points]

print("Debugging hooks:")
for hook in all_hooks:
    print(hook)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

def get_script(name):
    for s in a.scripts:
        if name in s[0]:
            return [s]
    raise Exception(f"Could not find script {name}")

exe_gui = EXE(
    pyz,
    all_hooks + get_script('start_ui'),
    [],
    exclude_binaries=True,
    name='Deluge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['deluge.icns'],
)

exe_console = EXE(
    pyz,
    all_hooks + get_script('start_console'),
    [],
    exclude_binaries=True,
    name='deluge-console',
    debug=False,
    strip=False,
    upx=True,
    console=True, # Shows terminal
    target_arch=None,
)

exe_daemon = EXE(
    pyz,
    all_hooks + get_script('start_daemon'),
    [],
    exclude_binaries=True,
    name='deluged',
    debug=False,
    strip=False,
    upx=True,
    console=True,
    target_arch=None,
)

exe_web = EXE(
    pyz,
    all_hooks + get_script('start_web'),
    [],
    exclude_binaries=True,
    name='deluge-web',
    debug=False,
    strip=False,
    upx=True,
    console=True,
    target_arch=None,
)

coll = COLLECT(
    exe_gui,
    exe_console,
    exe_daemon,
    exe_web,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Deluge',
)

app = BUNDLE(
    coll,
    name='Deluge.app',
    icon='deluge.icns',
    bundle_identifier='org.deluge',
    version=deluge_version,
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': '0',
        'CFBundleName': 'Deluge',
        'CFBundleDisplayName': 'Deluge',
        'CFBundlePackageType': 'APPL',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeExtensions': ['torrent'],
                'CFBundleTypeIconFile': 'torrent',
                'CFBundleTypeName': 'BitTorrent Document',
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Owner',
                'LSItemContentTypes': ['org.bittorrent.torrent']
            }
        ],
        'CFBundleURLTypes': [
            {
                'CFBundleURLName': 'BitTorrent Magnet URL',
                'CFBundleURLSchemes': ['magnet']
            }
        ]
    }
)
