import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import tekton
original_rom_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "fixtures", "original_rom.sfc")