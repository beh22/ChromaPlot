#!/bin/tcsh

mkdir -p dist/dmg
rm -r dist/dmg/*

cp -r "dist/ChromaPlot.app" dist/dmg
test -f "dist/ChromaPlot.app" && rm "dist/ChromaPlot.app"

create-dmg \
  --volname "ChromaPlot Installer" \
  # --volicon "cp_thumbnail.icns" \      # This would give same icon to installer as main app - confusing?
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "ChromaPlot.app" 175 120 \
  --hide-extension "ChromaPlot.app" \
  --app-drop-link 425 120 \
  "dist/ChromaPlot.dmg" \
  "dist/dmg/"
