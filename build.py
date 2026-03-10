import os
import shutil
import re
import csv

def parse_csv(filepath):
    if not os.path.exists(filepath):
        return []
        
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        # csv python module handles newlines & quotes within fields nicely matching Javascript parser
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

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
        
    # 4. Pre-render CSV Data for SEO (<noscript>)
    # 4.1 Publications
    pub_csv = os.path.join(src_dir, 'Publications', 'publications.csv')
    pub_data = parse_csv(pub_csv)
    pub_seo_html = '<noscript id="seo-data"><ul>\n'
    for item in pub_data:
        # Strip bold tokens from authors
        authors = item.get('authors', '').replace('**', '')
        title = item.get('title', '')
        venue = item.get('venue', '')
        year = item.get('year', '')
        pub_seo_html += f"<li>{authors}. <strong>{title}</strong>. {venue} ({year}).</li>\n"
    pub_seo_html += '</ul></noscript>'

    # 4.2 Projects (Research)
    proj_csv = os.path.join(src_dir, 'Research', 'project.csv')
    proj_data = parse_csv(proj_csv)
    proj_seo_html = '<noscript id="seo-data"><ul>\n'
    for item in proj_data:
        title = item.get('title_kr', '') + " / " + item.get('title_en', '')
        summary = item.get('sum_kr', '') + " / " + item.get('sum_en', '')
        start = item.get('start', '')
        end = item.get('end', '')
        proj_seo_html += f"<li><strong>{title}</strong> ({start} ~ {end}): {summary}</li>\n"
    proj_seo_html += '</ul></noscript>'

    # 4.3 News (Recent News + All News pages)
    news_csv = os.path.join(src_dir, 'News', 'news.csv')
    news_data = parse_csv(news_csv)
    news_seo_html = '<noscript id="seo-data"><ul>\n'
    for item in news_data:
        title = item.get('title_kr', '') + " / " + item.get('title_en', '')
        summary = item.get('sum_kr', '') + " / " + item.get('sum_en', '')
        date = item.get('date', '')
        news_seo_html += f"<li><strong>{title}</strong> ({date}): {summary}</li>\n"
    news_seo_html += '</ul></noscript>'

    # 4.4 Members
    member_csv = os.path.join(src_dir, 'Members', 'members.csv')
    member_data = parse_csv(member_csv)
    member_seo_html = '<noscript id="seo-data"><ul>\n'
    for item in member_data:
        name = item.get('name_kr', '') + " / " + item.get('name_en', '')
        mtype = item.get('Type', '')
        bio = item.get('bio_kr', '') + " / " + item.get('bio_en', '')
        member_seo_html += f"<li><strong>{name}</strong> ({mtype}): {bio}</li>\n"
    member_seo_html += '</ul></noscript>'
    
    # 5. Inject header, footer and SEO blocks into HTML files
    for root, dirs, files in os.walk(dist_dir):
        # We don't want to process the component fragments themselves
        if 'components' in root.replace('\\', '/').split('/'):
            continue
            
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Replace placeholders using Regex
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

                # Inject SEO <noscript> just before </body>
                norm_filepath = filepath.replace('\\', '/')
                if 'Publications/' in norm_filepath:
                    content = content.replace('</body>', f'{pub_seo_html}\n</body>')
                elif 'Research/Project/' in norm_filepath:
                    content = content.replace('</body>', f'{proj_seo_html}\n</body>')
                elif 'News/' in norm_filepath:
                    content = content.replace('</body>', f'{news_seo_html}\n</body>')
                elif 'Members/' in norm_filepath and 'Professor' not in norm_filepath:
                    # Ignore professor page as it is static HTML already
                    content = content.replace('</body>', f'{member_seo_html}\n</body>')
                elif norm_filepath.endswith('index.html') and root.replace('\\', '/') == dist_dir.replace('\\', '/'):
                    # Home page (Recent News preview)
                    content = content.replace('</body>', f'{news_seo_html}\n</body>')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

    print("Static site generated successfully in dist/ directory.")

if __name__ == '__main__':
    build_site()
