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
        
    # 4. Pre-render CSV Data into Full HTML Structures
    # ---------------------------------------------------------
    # 4.1 Publications
    pub_csv = os.path.join(src_dir, 'Publications', 'publications.csv')
    pub_data = parse_csv(pub_csv)
    # Sort publications by year descending First
    pub_data = sorted([item for item in pub_data if item.get('year', '').strip()], key=lambda x: int(x.get('year', 0)), reverse=True)
    
    pub_html = '<div style="display: flex; flex-direction: column; gap: 1rem;">\n'
    for item in pub_data:
        authors_formatted = item.get('authors', '').replace('**', '<strong>')
        authors_formatted = authors_formatted.replace('**', '</strong>') # Handle closing bold (naive replace since it splits by **)
        
        # Proper strong tag replacement
        import re as regexp
        authors_formatted = regexp.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item.get('authors', ''))

        link = item.get('link', '').strip()
        bibtex = item.get('bibtex', '').strip().replace('"', '&quot;')
        thumb = item.get('thumbnail', '').strip()
        thumb_src = f"/Publications/thumbnail/{thumb}" if thumb else "/Publications/thumbnail/default-thumb.png"
        
        links_html = ''
        if link and link != '#':
            links_html += f'<a href="{link}" class="icon-link" aria-label="PDF" target="_blank"><i class="ri-links-line"></i></a>\n'
        if bibtex:
            links_html += f'<button class="icon-btn bibtex-copy-btn" data-bibtex="{bibtex}" onclick="copyBibtex(this)" aria-label="Copy BibTeX"><i class="ri-double-quotes-l"></i></button>\n'
            
        status_text = f"[{item.get('status')}]" if item.get('status') else ""
        
        pub_html += f"""
        <div class="publication-card">
            <div class="pub-card-layout">
                <div class="pub-img-wrapper">
                    <img src="{thumb_src}" onerror="this.onerror=null; this.src='/Publications/thumbnail/default-thumb.png';" alt="Thumbnail">
                </div>
                <div class="pub-content">
                    <h3 style="font-size: 1.1rem; margin-bottom: 0.5rem;">{item.get('title', '')}</h3>
                    <p style="color: var(--color-text-muted); margin-bottom: 0.5rem; font-size: 0.95rem;">
                        {authors_formatted}
                    </p>
                    <p style="color: var(--color-accent); font-weight: 500; font-size: 0.9rem;">
                        {item.get('venue', '')}, {item.get('year', '')} {status_text}
                    </p>
                    <div class="pub-links" style="margin-top: 0.5rem;">
                        {links_html}
                    </div>
                </div>
            </div>
        </div>
        """
    pub_html += '</div>'

    # 4.2 Projects (Research)
    proj_csv = os.path.join(src_dir, 'Research', 'project.csv')
    proj_data = parse_csv(proj_csv)
    
    proj_html = '<div style="display: flex; flex-direction: column; gap: 1rem;">\n'
    for item in proj_data:
        # Defaulting to EN title for SEO structural baseline (JS will handle KR/EN translation later if needed)
        title = item.get('title_en', '')
        summary = item.get('sum_en', '').replace('\\n', '<br>').replace('\n', '<br>')
        
        link = item.get('link', '').strip()
        btn_action = ""
        btn_class = "cv-btn"
        if not link or link == '#':
            btn_class += " disabled"
        elif link.startswith('http'):
            btn_action = f'onclick="window.open(\'{link}\', \'_blank\'); return false;"'
        else:
            btn_action = f'onclick="openNewsModal(\'/Research/data/contents/{link}\')"'
            
        thumb = item.get('thumbnail', '').strip()
        thumb_src = f"/Research/data/thumbnail/{thumb}" if thumb else "asset/default-thumb.png"
        
        start_str = item.get('start', '').split('.')[0].split('-')[0] if item.get('start') else ''
        end_str = item.get('end', '').split('.')[0].split('-')[0] if item.get('end') else ''
        date_display = f"{start_str} ~ Present" if end_str == '' else f"{start_str} ~ {end_str}"
        
        proj_html += f"""
        <div class="publication-card">
            <div class="pub-card-layout">
                <div class="pub-img-wrapper">
                    <img src="{thumb_src}" onerror="this.onerror=null; this.src='asset/default-thumb.png';" alt="Thumbnail">
                </div>
                <div class="pub-content">
                    <h3 style="font-size: 1.1rem; margin-bottom: 0.5rem;">{title}</h3>
                    <p style=" margin-bottom: 0.5rem; font-size: 0.95rem;">
                        {summary}
                    </p>
                    <p style="color: var(--color-text-muted); font-weight: 500; font-size: 0.9rem;">
                        {date_display}
                    </p>
                    <a href="#" {btn_action} class="{btn_class}" style="margin-top: 1rem; font-size: 0.85rem; padding: 0.3rem 1rem;">Read More</a>
                </div>
            </div>
        </div>
        """
    proj_html += '</div>'

    # 4.3 News
    news_csv = os.path.join(src_dir, 'News', 'news.csv')
    news_data = parse_csv(news_csv)
    news_data = sorted(news_data, key=lambda x: x.get('date', ''), reverse=True)
    
    news_html = '<div style="display: flex; flex-direction: column; gap: 1rem;">\n'
    for item in news_data:
        title = item.get('title_en', '')
        summary = item.get('sum_en', '').replace('\\n', '<br>').replace('\n', '<br>')
        
        link = item.get('link', '').strip()
        btn_action = ""
        btn_class = "cv-btn"
        if not link or link == '#':
            btn_class += " disabled"
        elif link.startswith('http'):
            btn_action = f'onclick="window.open(\'{link}\', \'_blank\'); return false;"'
        else:
            btn_action = f'onclick="openNewsModal(\'/News/data/contents/{link}\')"'
            
        thumb = item.get('thumbnail', '').strip()
        thumb_src = f"/News/data/thumbnail/{thumb}" if thumb else "asset/default-thumb.png"
        
        news_html += f"""
        <div class="publication-card">
            <div class="pub-card-layout">
                <div class="pub-img-wrapper">
                    <img src="{thumb_src}" onerror="this.onerror=null; this.src='asset/default-thumb.png';" alt="Thumbnail">
                </div>
                <div class="pub-content">
                    <h3 style="font-size: 1.1rem; margin-bottom: 0.5rem;">{title}</h3>
                    <p style=" margin-bottom: 0.5rem; font-size: 0.95rem;">
                        {summary}
                    </p>
                    <p style="color: var(--color-text-muted); font-weight: 500; font-size: 0.9rem;">
                        {item.get('date', '')}
                    </p>
                    <a href="#" {btn_action} class="{btn_class}" style="margin-top: 1rem; font-size: 0.85rem; padding: 0.3rem 1rem;">Read More</a>
                </div>
            </div>
        </div>
        """
    news_html += '</div>'

    # 4.4 Members
    member_csv = os.path.join(src_dir, 'Members', 'members.csv')
    member_data = parse_csv(member_csv)
    
    # We will just generate a generic dump of member cards for SEO purposes,
    # as students/alumni are complexly categorized. The JS will override this visually anyway,
    # but the DOM will contain all the rich info.
    member_html = '<div class="grid">\n'
    for item in member_data:
        name = item.get('name_en', '')
        mtype = item.get('Type', '')
        bio = item.get('bio_en', '').replace('\\n', '<br>').replace('\n', '<br>')
        thumb = item.get('image', '').strip()
        thumb_src = f"/Members/data/images/{thumb}" if thumb else "/Members/data/images/unknown.webp"
        
        member_html += f"""
        <div class="member-card">
            <img src="{thumb_src}" alt="{name}" style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem;">
            <h4 style="font-size: 1.1rem; margin-bottom: 0.25rem;">{name}</h4>
            <p style="color: var(--color-accent); font-weight: 500; font-size: 0.9rem; margin-bottom: 0.5rem;">{mtype}</p>
            <p style="color: var(--color-text-muted); font-size: 0.85rem; line-height: 1.4;">{bio}</p>
        </div>
        """
    member_html += '</div>'
    
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

                # Inject FULL HTML Data directly into the target containers
                norm_filepath = filepath.replace('\\', '/')
                
                if 'Publications/' in norm_filepath:
                    import re as regexp
                    content = regexp.sub(r'<div[^>]*id="publication-list"[^>]*>[\s\S]*?</div>', f'<div id="publication-list">\n{pub_html}\n</div>', content)
                elif 'Research/Project/' in norm_filepath:
                    import re as regexp
                    content = regexp.sub(r'<div[^>]*id="project-list"[^>]*>[\s\S]*?</div>', f'<div id="project-list">\n{proj_html}\n</div>', content)
                elif 'News/' in norm_filepath:
                    import re as regexp
                    content = regexp.sub(r'<div[^>]*id="news-list"[^>]*>[\s\S]*?</div>', f'<div id="news-list">\n{news_html}\n</div>', content)
                elif 'Members/' in norm_filepath and 'Professor' not in norm_filepath:
                    import re as regexp
                    content = regexp.sub(r'<div[^>]*id="member-list"[^>]*>[\s\S]*?</div>', f'<div id="member-list">\n{member_html}\n</div>', content)
                elif norm_filepath.endswith('index.html') and root.replace('\\', '/') == dist_dir.replace('\\', '/'):
                    # Home page (Recent News preview)
                    import re as regexp
                    content = regexp.sub(r'<div[^>]*id="recent-news-list"[^>]*>[\s\S]*?</div>', f'<div id="recent-news-list">\n{news_html}\n</div>', content)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

    print("Static site generated successfully in dist/ directory.")

if __name__ == '__main__':
    build_site()
