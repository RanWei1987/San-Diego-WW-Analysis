import sys
sys.path.append(r"C:\Users\E107484\Documents\projects\Freyja")
from freyja._cli import aggregate

if len(sys.argv) != 3:
    print("Usage: python aggregate_wrapper.py <input_folder> <output_file>")
    sys.exit(1)

input_folder = sys.argv[1]
output_file = sys.argv[2]

aggregate([input_folder, "--output", output_file])