
path = r'c:\SPY_Cursor\SP_Code\templates\stratejik_planlama_akisi.html'
try:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for unbalanced braces
    open_braces = content.count('{{')
    close_braces = content.count('}}')
    print(f"Open braces: {open_braces}")
    print(f"Close braces: {close_braces}")

    if open_braces != close_braces:
        print("MISMATCH DETECTED!")

    open_tags = content.count('{%')
    close_tags = content.count('%}')
    print(f"Open tags: {open_tags}")
    print(f"Close tags: {close_tags}")

    if open_tags != close_tags:
        print("MISMATCH DETECTED!")

except Exception as e:
    print(f"Error: {e}")
