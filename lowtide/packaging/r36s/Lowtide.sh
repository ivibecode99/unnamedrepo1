#!/bin/bash
# LOWTIDE launcher for PortMaster-style CFWs (ArkOS / dArkOS / ROCKNIX / AmberELEC) on the R36S / R36H (640x480, gamepad only).
XDG_DATA_HOME=${XDG_DATA_HOME:-$HOME/.local/share}
if [ -d "/opt/system/Tools/PortMaster/" ]; then controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "/opt/tools/PortMaster/" ]; then controlfolder="/opt/tools/PortMaster"
elif [ -d "$XDG_DATA_HOME/PortMaster/" ]; then controlfolder="$XDG_DATA_HOME/PortMaster"
else controlfolder="/roms/ports/PortMaster"; fi
source $controlfolder/control.txt
[ -f "${controlfolder}/mod_${CFW_NAME}.txt" ] && source "${controlfolder}/mod_${CFW_NAME}.txt"
get_controls
GAMEDIR=/$directory/ports/lowtide
cd "$GAMEDIR"
> "$GAMEDIR/log.txt" && exec > >(tee "$GAMEDIR/log.txt") 2>&1
export LT_SAVE_DIR="$GAMEDIR/saves"; mkdir -p "$LT_SAVE_DIR"
export SDL_GAMECONTROLLERCONFIG="$sdl_controllerconfig"
export LD_LIBRARY_PATH="$GAMEDIR/libs:$LD_LIBRARY_PATH"
# A=confirm  B=cancel/run  START=menu  SELECT=item shortcut.  Hold START+SELECT for 1.5s to quit.
$GPTOKEYB "lowtide" -c "" &
./lowtide
pm_finish
