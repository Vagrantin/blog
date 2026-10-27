#!/usr/bin/env python3
"""One-time, reproducible ODT import from the last pre-Hugo source commit.

Pandoc is needed only for this migration, never for normal publication.
Originals remain available in git history at SOURCE; prose is not modernized.
"""
import datetime as dt
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '6c27445de1c99b48933b6a6f266b3cab5ab07c7a'


def original(path):
    return subprocess.check_output(['git', 'show', f'{SOURCE}:{path}'], cwd=ROOT)


def local_url(value, day):
    value = html.unescape(value)
    if value.startswith('https://vagrantin.github.io/blog/'):
        return '/' + value.split('/blog/', 1)[1]
    if value.startswith('../'):
        return '/' + value.removeprefix('../')
    if value.startswith('./Pictures/') or value.startswith('Pictures/'):
        return f'/{day}/' + value.removeprefix('./')
    return value


def plain_inlines(nodes):
    """Restore literal Markdown held in ODT paragraphs without Pandoc escaping."""
    result = ''
    for node in nodes:
        kind, data = node['t'], node.get('c')
        if kind == 'Str':
            result += data
        elif kind in ('Space', 'SoftBreak'):
            result += ' '
        elif kind == 'LineBreak':
            result += '\n'
        elif kind == 'Image':
            result += f'![{plain_inlines(data[1])}]({data[2][0]})'
        elif kind == 'Link':
            text = plain_inlines(data[1])
            result += text if '](' in text else f'[{text}]({data[2][0]})'
        elif kind == 'Code':
            result += data[1]
        elif kind in ('Emph', 'Strong', 'Strikeout', 'Underline'):
            result += plain_inlines(data)
        elif kind == 'Span':
            result += plain_inlines(data[1])
        elif kind == 'Quoted':
            result += '"' + plain_inlines(data[1]) + '"'
        else:
            raise ValueError(f'Unsupported literal Markdown inline: {kind}')
    return result


def main():
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', SOURCE], cwd=ROOT, text=True).splitlines()
    manifest = []
    for path in paths:
        if not re.fullmatch(r'\d{8}/[^/]+\.odt', path):
            continue
        day, filename = path.split('/')
        stem = Path(filename).stem
        content = original(path)
        with tempfile.TemporaryDirectory() as temp:
            odt = Path(temp) / filename
            odt.write_bytes(content)
            ast = json.loads(subprocess.check_output(['pandoc', str(odt), '-f', 'odt', '-t', 'json']))
            first = ast['blocks'][0]
            literal = first['t'] == 'Para' and plain_inlines(first['c']).startswith('# ')
            if literal:
                assert all(b['t'] in ('Para', 'Plain') for b in ast['blocks']), path
                body = '\n\n'.join(plain_inlines(b['c']) for b in ast['blocks']) + '\n'
                # ODT adds paragraph breaks between every line of code. Preserve
                # indentation/text, removing only these conversion artifacts.
                fenced = False
                lines = []
                for line in body.splitlines():
                    if line.startswith('```'):
                        fenced = not fenced
                    if line or not fenced:
                        lines.append(line)
                body = '\n'.join(lines) + '\n'
            else:
                body = subprocess.check_output(['pandoc', str(odt), '-f', 'odt', '-t', 'gfm', '--wrap=none'], text=True)
        body = re.sub(r'<img\b[^>]*src="([^"]+)"[^>]*>', lambda m: '![](' + local_url(m[1], day) + ')', body)
        body = re.sub(r'(?<=\]\()([^\s)]+)', lambda m: local_url(m[0], day), body)
        # Retain all original headings/anchors beneath the page title. Do not
        # change shell comments or Markdown examples inside fenced code blocks.
        lines, fenced = [], False
        for line in body.splitlines():
            if line.startswith('```'):
                fenced = not fenced
            if not fenced:
                line = re.sub(r'^(#{1,5}) ', r'#\1 ', line)
                line = re.sub(r'<sup>(.*?)</sup>', r'\1', line)
                if re.fullmatch(r'#{1,6}\s*', line):
                    continue
                if re.search(r' {2,}$', line) and line.strip() and not line.startswith('#'):
                    line = line.rstrip() + '\\'
                else:
                    line = line.rstrip()
            lines.append(line)
        body = '\n'.join(lines) + '\n'
        title = original(f'titlesOfTheMonth/{stem}.txt').decode().splitlines()[0].strip().strip('"')
        date = dt.datetime.strptime(day, '%Y%m%d').date().isoformat()
        published = day != '20360404'
        target = ROOT / 'content' / 'posts' / day / 'index.md'
        target.parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            'title': title, 'publishDate': f'{date}T09:00:00+09:00',
            'draft': not published, 'url': f'/{day}/{stem}.html',
            'params': {'legacy': True},
        }
        for paragraph in body.split('\n\n'):
            candidate = paragraph.strip()
            if candidate.startswith(('#', '!', '```', 'Disclamer:', 'Disclaimer:')):
                continue
            candidate = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', candidate)
            candidate = re.sub(r'[*`_]', '', candidate)
            candidate = ' '.join(candidate.split())
            if len(candidate) >= 70:
                metadata['description'] = candidate[:207].rsplit(' ', 1)[0] + '…' if len(candidate) > 210 else candidate
                break
        # JSON front matter is native Hugo and avoids quote/colon ambiguity.
        target.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n\n' + body)
        assets = {}
        with zipfile.ZipFile(__import__('io').BytesIO(content)) as archive:
            for member in archive.namelist():
                if member.startswith('Pictures/') and not member.endswith('/'):
                    assets[member] = archive.read(member)
        # Keep the originally tracked media too, including the SSH screencast
        # and original article header illustrations. Never publish ODT/XCF files.
        for asset in paths:
            if asset.startswith(day + '/') and Path(asset).suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4'):
                assets[asset.split('/', 1)[1]] = original(asset)
        for relative, data in assets.items():
            asset = ROOT / 'static' / day / relative
            asset.parent.mkdir(parents=True, exist_ok=True)
            asset.write_bytes(data)
        manifest.append({
            'source': path, 'sourceSha256': hashlib.sha256(content).hexdigest(),
            'content': str(target.relative_to(ROOT)), 'url': metadata['url'],
            'published': published, 'literalMarkdownRepaired': literal,
            'media': sorted(f'/{day}/{name}' for name in assets),
        })
    out = ROOT / 'data' / 'migration.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({'sourceCommit': SOURCE, 'articles': manifest}, indent=2) + '\n')
    print(f'Migrated {len(manifest)} articles ({sum(a["published"] for a in manifest)} published)')


if __name__ == '__main__':
    main()
