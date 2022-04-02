function build_tool {
  pyinstaller \
    --specpath /tmp \
    --workpath /tmp/build \
    --distpath /dist \
    --paths /src \
    -F $1 \
    -n $2.exe

  chown $FIXUID:$FIXUID /dist/$2.exe
}

build_tool tools/manage/__main__.py dl24_manage
build_tool tools/monitor/__main__.py dl24_monitor
build_tool tools/plotter/__main__.py dl24_plotter
