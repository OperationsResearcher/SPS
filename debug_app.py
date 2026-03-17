import sys
import traceback

log_file = open('debug_error.log', 'w', encoding='utf-8')
sys.stderr = log_file
sys.stdout = log_file

print("Starting debug run...")

try:
    from app import create_app
    print("Importing create_app done.")
    app = create_app()
    print("create_app() called successfully.")
except Exception:
    traceback.print_exc()

print("Debug run finished.")
log_file.close()
