#!/usr/bin/env python3
"""
Simple site snapshotter (homepage + linked CSS/JS/IMG assets).
Usage: python tools/pull_site.py <url> <output_dir>

Notes:
- Uses only Python stdlib so it should run without extra deps.
- Saves index.html and assets under <output_dir>/assets/<netloc>/...
- Rewrites href/src in the saved index.html to local asset paths.
- Best-effort: won't follow links beyond the given page.
"""
import os
import sys
import urllib.request
import urllib.parse
from html.parser import HTMLParser

class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img' and 'src' in attrs:
            self.assets.append(attrs['src'])
        elif tag == 'script' and 'src' in attrs:
            self.assets.append(attrs['src'])
        elif tag == 'link' and 'href' in attrs:
            rel = attrs.get('rel','')
            # collect stylesheet and icons
            if 'stylesheet' in rel or 'icon' in rel or rel=='' or rel is None:
                self.assets.append(attrs['href'])
        elif tag == 'source' and 'src' in attrs:
            self.assets.append(attrs['src'])


def safe_path_for_url(url):
    # create a filesystem-safe path from url (netloc + path)
    p = urllib.parse.urlparse(url)
    path = p.path
    if path.endswith('/') or path == '':
        path = path + 'index'
    # join netloc and path, remove leading '/'
    parts = [p.netloc] + [seg for seg in path.split('/') if seg]
    # include query hash as part of filename if present
    if p.query:
        parts[-1] = parts[-1] + '_' + str(abs(hash(p.query)))
    return os.path.join(*parts)


def download_url(url, dest_path, headers=None):
    try:
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "python-urllib/3"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, 'wb') as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"WARN: failed to download {url}: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/pull_site.py <url> <output_dir>")
        sys.exit(2)
    url = sys.argv[1]
    outdir = sys.argv[2]
    if not url.startswith('http'):
        url = 'https://' + url
    os.makedirs(outdir, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0 (Snapshotter/1.0)"}

    print(f"Fetching {url} ...")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode(resp.headers.get_content_charset('utf-8'), errors='replace')
    except Exception as e:
        print(f"ERROR: failed to fetch {url}: {e}")
        sys.exit(1)

    parser = AssetParser()
    parser.feed(html)
    assets = list(dict.fromkeys(parser.assets))  # preserve order, remove dupes
    print(f"Found {len(assets)} candidate asset URLs in the page.")

    local_map = {}
    for a in assets:
        if a.startswith('data:'):
            # skip inline data URIs
            continue
        abs_url = urllib.parse.urljoin(url, a)
        parsed = urllib.parse.urlparse(abs_url)
        if not parsed.scheme.startswith('http'):
            print(f"Skipping non-http asset: {abs_url}")
            continue
        relpath = safe_path_for_url(abs_url)
        dest = os.path.join(outdir, 'assets', relpath)
        ok = download_url(abs_url, dest, headers=headers)
        if ok:
            # store local relative path (from index.html) e.g. assets/<netloc>/path
            local_map[a] = os.path.join('assets', relpath).replace('\\','/')

    # rewrite HTML occurrences of the original URLs to local_map values
    new_html = html
    # sort keys by length desc to avoid partial replacements
    for orig in sorted(local_map.keys(), key=len, reverse=True):
        new_html = new_html.replace(orig, local_map[orig])
        # also replace absolute version
        abs_url = urllib.parse.urljoin(url, orig)
        new_html = new_html.replace(abs_url, local_map[orig])

    index_path = os.path.join(outdir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"Saved snapshot to {index_path}")
    print("Assets saved under:", os.path.join(outdir, 'assets'))

if __name__ == '__main__':
    main()
