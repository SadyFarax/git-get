import os
import re
import zipfile
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; SiteMirror/1.0)'})

start_url = os.environ['SITE_URL']
domain = urlparse(start_url).netloc
visited = set()
queue = [start_url]
output_dir = 'site_mirror'
os.makedirs(output_dir, exist_ok=True)
css_url_pattern = re.compile(r'url\([\'"]?([^\'")\s]+)[\'"]?\)')

def local_path(url):
    parsed = urlparse(url)
    path = parsed.path.lstrip('/')
    if not path or path.endswith('/'):
        path += 'index.html'
    return os.path.join(output_dir, domain, path)

def download_file(url):
    if url in visited:
        return None
    visited.add(url)
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        path = local_path(url)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(resp.content)
        return path, resp
    except:
        return None

def rewrite_asset_url(url, base_url, folder):
    if not url or url.startswith('data:'):
        return url
    if urlparse(url).netloc and urlparse(url).netloc != domain:
        return url
    abs_url = urljoin(base_url, url)
    download_file(abs_url)
    return '/' + urlparse(abs_url).path.lstrip('/')

def process_html(path, resp):
    soup = BeautifulSoup(resp.content, 'lxml')
    base_url = resp.url
    for tag in soup.find_all(['a','link','script','img','source']):
        if tag.name == 'a' and tag.has_attr('href'):
            href = tag['href']
            if not urlparse(href).netloc or urlparse(href).netloc == domain:
                abs_href = urljoin(base_url, href)
                if urlparse(abs_href).netloc == domain:
                    dl = download_file(abs_href)
                    if dl:
                        tag['href'] = '/' + urlparse(abs_href).path.lstrip('/')
                        queue.append(abs_href) if abs_href not in visited else None
        elif tag.name == 'link' and tag.has_attr('href'):
            tag['href'] = rewrite_asset_url(tag['href'], base_url, '')
        elif tag.name == 'script' and tag.has_attr('src'):
            tag['src'] = rewrite_asset_url(tag['src'], base_url, '')
        elif tag.name == 'img' and tag.has_attr('src'):
            tag['src'] = rewrite_asset_url(tag['src'], base_url, '')
        elif tag.name == 'source' and tag.has_attr('srcset'):
            srcset = tag['srcset']
            parts = []
            for part in srcset.split(','):
                part = part.strip()
                if part:
                    url_part = part.split(' ')[0]
                    new_url = rewrite_asset_url(url_part, base_url, '')
                    parts.append(part.replace(url_part, new_url, 1))
            tag['srcset'] = ', '.join(parts)
    with open(path, 'wb') as f:
        f.write(soup.prettify('utf-8'))
    for css_tag in soup.find_all('link', rel='stylesheet'):
        css_href = css_tag.get('href')
        if css_href:
            css_abs = urljoin(base_url, css_href) if not urlparse(css_href).netloc or urlparse(css_href).netloc == domain else None
            if css_abs and urlparse(css_abs).netloc == domain:
                css_path = local_path(css_abs)
                if os.path.exists(css_path):
                    with open(css_path, 'r', encoding='utf-8') as f:
                        css_content = f.read()
                    def replace_url(m):
                        u = m.group(1)
                        return f"url({rewrite_asset_url(u, css_abs, os.path.dirname(css_path))})"
                    new_css = css_url_pattern.sub(replace_url, css_content)
                    with open(css_path, 'w', encoding='utf-8') as f:
                        f.write(new_css)

while queue:
    url = queue.pop(0)
    if url in visited:
        continue
    dl = download_file(url)
    if dl:
        path, resp = dl
        if 'text/html' in resp.headers.get('content-type', ''):
            process_html(path, resp)

zip_name = 'site_mirror.zip'
with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            full = os.path.join(root, file)
            arcname = os.path.relpath(full, output_dir)
            zf.write(full, arcname)
print('ZIP_CREATED', zip_name)
