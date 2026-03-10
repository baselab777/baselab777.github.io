import os
import re
import urllib.request
import urllib.parse

def minify_js(file_path, out_path):
    print(f"Minifying {os.path.basename(file_path)}...")
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        url = 'https://www.toptal.com/developers/javascript-minifier/api/raw'
        data = urllib.parse.urlencode({'input': code}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=5) as response:
            minified = response.read().decode('utf-8')
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(minified)
        print(f"  [SUCCESS] API -> {os.path.basename(out_path)}")
        return True
    except Exception as e:
        print(f"  [WARNING] API failed ({e}). Using regex fallback.")
        # Super basic JS minifier (remove comments and extra whitespace)
        minified = "\n".join([line.strip() for line in code.split("\n") if line.strip() and not line.strip().startswith("//")])
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(minified)
        print(f"  [SUCCESS] Fallback -> {os.path.basename(out_path)}")
        return True

def minify_css(file_path, out_path):
    print(f"Minifying {os.path.basename(file_path)}...")
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
        
    try:
        url = 'https://www.toptal.com/developers/cssminifier/api/raw'
        data = urllib.parse.urlencode({'input': code}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=5) as response:
            minified = response.read().decode('utf-8')
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(minified)
        print(f"  [SUCCESS] API -> {os.path.basename(out_path)}")
        return True
    except Exception as e:
        print(f"  [WARNING] API failed ({e}). Using regex fallback.")
        # Basic CSS minifier
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL) # remove comments
        code = re.sub(r'\s+', ' ', code) # remove newlines and multiple spaces
        code = code.replace('{ ', '{').replace(' }', '}').replace('; ', ';').replace(': ', ':').replace(' ,', ',').replace(', ', ',')
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"  [SUCCESS] Fallback -> {os.path.basename(out_path)}")
        return True

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    css_files = ["style.css", "modal.css"]
    js_files = ["script.js"]
    
    print("--- Starting Minification ---")
    for f in css_files:
        in_path = os.path.join(current_dir, f)
        out_path = os.path.join(current_dir, f.replace(".css", ".min.css"))
        if os.path.exists(in_path):
            minify_css(in_path, out_path)
            
    for f in js_files:
        in_path = os.path.join(current_dir, f)
        out_path = os.path.join(current_dir, f.replace(".js", ".min.js"))
        if os.path.exists(in_path):
            minify_js(in_path, out_path)
            
    print("All files minified successfully!")
