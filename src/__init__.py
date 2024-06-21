import sys
import os 

cur_dir = os.path.dirname(os.path.abspath("__file__"))  # Gets the current notebook directory
src_dir = os.path.join(cur_dir, '../')  # Constructs the path to the 'src' directory
if src_dir not in sys.path:
    sys.path.append(src_dir)