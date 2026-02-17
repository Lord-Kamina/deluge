# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata, collect_data_files
deluge_metadata = copy_metadata('deluge')
deluge_resources = collect_data_files('deluge')
block_cipher = None
from PyInstaller.utils.hooks import exec_statement
deluge_version=exec_statement('from version import get_version; print(get_version())')

print(f"deluge metadata: {deluge_metadata}")

deluge_datas = [
	('packaging/osx/torrent.icns','.'),
	('packaging/osx/launchd','launchd'),
	('deluge/plugins/*.whl', 'plugins'),
	('deluge/ui', 'ui'),
# 	('/opt/local/share/themes/WhiteSur-*', 'themes'),
# 	('/opt/local/share/themes/Mac', 'themes/Mac')
] + deluge_resources + deluge_metadata

print(f"deluge resources: {deluge_resources}")

a = Analysis(
    ['packaging/osx/macos_app_shims/start_ui.py', 'packaging/osx/macos_app_shims/start_console.py', 'packaging/osx/macos_app_shims/start_daemon.py', 'packaging/osx/macos_app_shims/start_web.py'],
    pathex=['.'],
    binaries=[],
    datas=deluge_datas,
    hiddenimports=['deluge'],
    hookspath=[],
    hooksconfig={
    	"gi": {
    		"icons": ["Adwaita", "hicolor"],
    		"themes": ["Mac", "WhiteSur-Light", "WhiteSur-Dark"]
    	}
    },
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

def get_script(name):
    for s in a.scripts:
        if name in s[0]:
            return [s]
    raise Exception(f"Could not find script {name}")

exe_gui = EXE(
    pyz,
    get_script('start_ui'),
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
    icon=['packaging/osx/deluge.icns'],
)

exe_console = EXE(
    pyz,
    get_script('start_console'),
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
    get_script('start_daemon'),
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
    get_script('start_web'),
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
    icon='packaging/osx/deluge.icns',
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
