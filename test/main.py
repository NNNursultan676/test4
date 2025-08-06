
#!/usr/bin/env python3
import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Change to the script directory
os.chdir(current_dir)

if __name__ == '__main__':
    from bot import main
    main()
