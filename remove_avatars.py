
try:
    path = r'c:\SPY_Cursor\SP_Code\templates\admin_panel.html'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # We want to remove lines 774 to 1153 (inclusive, 1-based)
    # Line 774 is "<!-- Avatar Tema İçeriği -->"
    # Line 1153 is "</div>" (closing tab-content)
    # Indices: 773 to 1153 (slice 773:1153 deletes 773...1152)
    
    # Verify content to be sure (optional but good practice)
    start_line = lines[773].strip()
    end_line = lines[1152].strip()
    
    print(f"Deleting from: {start_line} to {end_line}")
    if "Avatar Tema" in start_line and "div" in end_line:
        del lines[773:1153]
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Success")
    else:
        print("Content mismatch, not deleting.")
except Exception as e:
    print(f"Error: {e}")
