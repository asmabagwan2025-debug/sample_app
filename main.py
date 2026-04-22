import sys

def main():
    print("Hello! This is a simple test script.")
    print("Checking system compatibility...")
    # A simple logic to ensure the script actually executes
    if sys.version_info.major == 3:
        print("Python 3 detected. Success!")
    else:
        print("Python version issue.")
        sys.exit(1)

if __name__ == "__main__":
    main()