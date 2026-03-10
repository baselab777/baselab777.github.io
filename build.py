import os
import shutil
import re

def build_site():
    src_dir = 'src'
    dist_dir = 'dist'
    
    # 1. Clear dist if it exists
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
        
    # 2. Copy src to dist
    shutil.copytree(src_dir, dist_dir)
    
    # 3. Read header and footer components
    header_path = os.path.join(src_dir, 'components', 'header.html')
    footer_path = os.path.join(src_dir, 'components', 'footer.html')
    
    with open(header_path, 'r', encoding='utf-8') as f:
        header_html = f.read()
        
    with open(footer_path, 'r', encoding='utf-8') as f:
        footer_html = f.read()
        
    # 4. Inject header and footer into all HTML files in dist
    for root, dirs, files in os.walk(dist_dir):
        # We don't want to process the component fragments themselves
        if 'components' in root.replace('\\', '/').split('/'):
            continue
            
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Replace placeholders using Regex to handle optional newlines
                # Replaces <div id="header-placeholder">...anything inside...</div>
                content = re.sub(
                    r'<div\s+id="header-placeholder"\s*>[\s\S]*?</div>', 
                    f'<div id="header-placeholder">\n{header_html}\n</div>', 
                    content
                )
                
                content = re.sub(
                    r'<div\s+id="footer-placeholder"\s*>[\s\S]*?</div>', 
                    f'<div id="footer-placeholder">\n{footer_html}\n</div>', 
                    content
                )
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

    print("Static site generated successfully in dist/ directory.")

if __name__ == '__main__':
    build_site()
