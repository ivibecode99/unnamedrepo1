#!/bin/bash
# Capt & Co. launcher for R36S / R36H class handhelds (ArkOS, dArkOS, ROCKNIX, AmberELEC style).
# Copy the whole "captco" folder (this script + CaptCo.arm64 + capt.gptk + gamecontrollerdb.txt) to
#   ports/  (ArkOS / dArkOS: /roms/ports or /roms2/ports)   -> start it from the "Ports" system.
# 640x480, GLES3 (Compatibility renderer), 30 FPS cap, Low graphics preset.
XDG_DATA_HOME=${XDG_DATA_HOME:-$HOME/.local/share}

if [ -d "/opt/system/Tools/PortMaster/" ]; then
  controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "/opt/tools/PortMaster/" ]; then
  controlfolder="/opt/tools/PortMaster"
elif [ -d "$XDG_DATA_HOME/PortMaster/" ]; then
  controlfolder="$XDG_DATA_HOME/PortMaster"
else
  controlfolder="/roms/ports/PortMaster"
fi
[ -f "$controlfolder/control.txt" ] && source "$controlfolder/control.txt"
[ -f "${controlfolder}/mod_${CFW_NAME}.txt" ] && source "${controlfolder}/mod_${CFW_NAME}.txt"

GAMEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ -d "$GAMEDIR/captco" ] && GAMEDIR="$GAMEDIR/captco"
cd "$GAMEDIR" || exit 1
mkdir -p "$GAMEDIR/save"
export XDG_DATA_HOME="$GAMEDIR/save"           # save games + settings live next to the game
export CAPT_HANDHELD=1                          # force the handheld (Low) preset
export SDL_GAMECONTROLLERCONFIG="$(cat "$GAMEDIR/gamecontrollerdb.txt" 2>/dev/null)"
[ -f "$GAMEDIR/CaptCo.arm64" ] && chmod +x "$GAMEDIR/CaptCo.arm64"

# Mali (Panfrost) tuning: Mesa GLES 3.0 is enough for the Compatibility renderer.
export MESA_GLES_VERSION_OVERRIDE=3.1
export PAN_MESA_DEBUG=${PAN_MESA_DEBUG:-}

# Optional: gptokeyb turns ANY gamepad into the keyboard bindings the game already supports.
# Enabled automatically when gptokeyb exists and CAPT_USE_GPTOKEYB is not 0.
if [ "${CAPT_USE_GPTOKEYB:-1}" = "1" ] && command -v "${GPTOKEYB:-gptokeyb}" >/dev/null 2>&1; then
  [ -n "$GPTOKEYB" ] && $ESUDO chmod 666 /dev/uinput 2>/dev/null
  ${GPTOKEYB:-gptokeyb} "CaptCo.arm64" -c "$GAMEDIR/capt.gptk" &
  GPTK_PID=$!
fi

./CaptCo.arm64 --handheld --rendering-driver opengl3 --fullscreen "$@" 2>&1 | tee "$GAMEDIR/log.txt"

[ -n "$GPTK_PID" ] && kill "$GPTK_PID" 2>/dev/null
command -v pm_finish >/dev/null 2>&1 && pm_finish
exit 0
