#!/usr/bin/env bash -xe

cd ~/deluge
clear
for pycache in $(find ./ -type d -name __pycache__); do rm -Rv "$pycache" || true; done
CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1 pyinstaller-3.13 --clean --noconfirm --log-level TRACE packaging/osx/Deluge.spec
cp -Rv /opt/local/share/gir-1.0 ~/deluge/dist/Deluge.app/Contents/Resources/
find -H ~/deluge/dist/Deluge.app/Contents/Resources/gir-1.0/ -name "*.gir" -exec sed -i '' 's|/opt/local/lib|@executable_path/../Frameworks|g' {} \;

pushd ~/deluge/dist/Deluge.app/Contents/Resources

GDK_PIXBUF_MODULEDIR=../Resources/lib/gdk-pixbuf/loaders GDK_PIXBUF_MODULE_FILE=../Resources/lib/gdk-pixbuf/loaders.cache gdk-pixbuf-query-loaders --update-cache

sed -i '' 's|../Resources/lib|@executable_path/../Resources/lib|g' ~/deluge/dist/Deluge.app/Contents/Resources/lib/gdk-pixbuf/loaders.cache
popd
