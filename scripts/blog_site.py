#!/usr/bin/env python3
"""Content contract and generated-output checks shared by CI and Jenkins."""
import argparse
import datetime as dt
import gzip
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
JST = ZoneInfo('Asia/Tokyo')
BASE = 'https://vagrantin.github.io/blog/'


def timestamp(value):
    if isinstance(value, dt.datetime):
        result = value
    else:
        result = dt.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('publication timestamps must include a timezone')
    return result


def metadata(path):
    text = path.read_text()
    if text.startswith('{'):
        data, _ = json.JSONDecoder().raw_decode(text)
    elif text.startswith('---\n'):
        data = yaml.safe_load(text.split('---', 2)[1])
    else:
        raise ValueError(f'{path}: use YAML or JSON front matter')
    return data


def validate(data, legacy=False):
    if not isinstance(data.get('title'), str) or not data['title'].strip():
        raise ValueError('title is required')
    if type(data.get('draft')) is not bool:
        raise ValueError('draft must be true or false')
    when = timestamp(data.get('publishDate'))
    local = when.astimezone(JST)
    if not legacy and not data['draft']:
        if local.weekday() != 2 or local.day > 7 or local.time() != dt.time(9):
            raise ValueError('ready articles must publish on the first Wednesday at 09:00 Asia/Tokyo')
    return when


def articles(root=ROOT):
    migration = json.loads((root / 'data/migration.json').read_text())
    recorded = {a['content']: a for a in migration['articles']}
    result = []
    for path in sorted((root / 'content/posts').rglob('*.md')):
        if path.name == '_index.md':
            continue
        relative = path.relative_to(root).as_posix()
        data = metadata(path)
        legacy = relative in recorded
        when = validate(data, legacy=legacy)
        # Exempt only the reviewed migration inventory, never an arbitrary
        # params.legacy flag on a new article.
        if legacy:
            old = recorded[relative]
            expected_date = dt.datetime.strptime(old['source'].split('/')[0], '%Y%m%d').date()
            if data.get('url') != old['url'] or when.astimezone(JST).date() != expected_date:
                raise ValueError(f'{relative}: preserve the migrated URL and date')
        url = data.get('url') or '/posts/' + path.parent.name + '/'
        if not re.fullmatch(r'/[A-Za-z0-9_./-]+', url) or '..' in url or url.startswith('/blog/'):
            raise ValueError(f'{relative}: invalid site-relative URL: {url}')
        result.append({'path': relative, 'url': url, 'publishDate': when.isoformat(), 'draft': data['draft'], 'legacy': legacy})
    if not set(recorded).issubset(a['path'] for a in result):
        raise ValueError('a migrated article is missing')
    urls = [a['url'] for a in result]
    if len(set(urls)) != len(urls):
        raise ValueError('duplicate article URLs')
    return result


def manifest(now, root=ROOT):
    return {'clock': now.isoformat(), 'articles': [dict(a, visible=not a['draft'] and timestamp(a['publishDate']) <= now) for a in articles(root)]}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ['href', 'src', 'poster']:
            if attrs.get(key):
                self.urls.append(attrs[key])
        if attrs.get('srcset'):
            self.urls.extend(part.strip().split()[0] for part in attrs['srcset'].split(','))


def public_path(public, url):
    parsed = urlsplit(url)
    if parsed.netloc and parsed.netloc != 'vagrantin.github.io':
        return None
    if not parsed.path.startswith('/blog/'):
        return None
    relative = unquote(parsed.path.removeprefix('/blog/'))
    target = public / relative
    if not target.resolve().is_relative_to(public.resolve()):
        raise ValueError(f'URL escaped output: {url}')
    if target.is_dir() or not Path(relative).suffix:
        target /= 'index.html'
    return target


def verify(public, now, root=ROOT):
    inventory = manifest(now, root)
    for item in inventory['articles']:
        target = public_path(public, '/blog' + item['url'])
        if target.exists() != item['visible']:
            raise ValueError(f'incorrect publication state: {item["path"]}')
        if not item['visible']:
            # A withheld article must not be advertised through any HTML, feed,
            # sitemap or generated JSON. Its URL is unique across the inventory.
            for output in public.rglob('*'):
                if output.is_file() and output.suffix in ('.html', '.xml', '.json'):
                    if item['url'] in output.read_text():
                        raise ValueError(f'unpublished URL leaked into {output}')
    parsers = {}
    for path in public.rglob('*.html'):
        parser = Links()
        parser.feed(path.read_text())
        parsers[path] = parser
    errors = []
    for path, parser in parsers.items():
        page_url = urljoin(BASE, path.relative_to(public).as_posix())
        for link in parser.urls:
            parsed = urlsplit(link)
            if parsed.scheme not in ('', 'http', 'https') or link.startswith('//'):
                continue
            if not parsed.netloc and parsed.path.startswith('/') and not parsed.path.startswith('/blog/'):
                errors.append(f'{path.relative_to(public)}: URL escaped /blog/: {link}')
                continue
            absolute = urljoin(page_url, link)
            target = public_path(public, absolute)
            if target is None:
                continue
            if not target.is_file():
                errors.append(f'{path.relative_to(public)}: missing {link}')
            elif urlsplit(absolute).fragment and target in parsers and unquote(urlsplit(absolute).fragment) not in parsers[target].ids:
                errors.append(f'{path.relative_to(public)}: missing anchor {link}')
    if errors:
        raise ValueError('\n'.join(sorted(set(errors))))
    if not (public / '.nojekyll').is_file():
        raise ValueError('missing .nojekyll')
    homepage = (public / 'index.html').read_bytes()
    css = list(public.glob('journal*.css'))
    js = list(public.glob('appearance*.js'))
    # JPEG fallback is larger than the WebP header: use that for the budget.
    transferred = sum(len(gzip.compress(p.read_bytes())) for p in css + js)
    transferred += len(gzip.compress(homepage)) + (public / 'images/nekkuma-1440.jpg').stat().st_size
    if transferred > 250 * 1024:
        raise ValueError(f'homepage transfer budget exceeded: {transferred}')
    if sum(p.stat().st_size for p in js) > 8 * 1024:
        raise ValueError('appearance JavaScript budget exceeded')
    print(f'PASS: {sum(a["visible"] for a in inventory["articles"])} visible articles; all local links/media resolve; homepage budget {transferred} bytes')
    return inventory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['manifest', 'verify'])
    parser.add_argument('--clock', required=True)
    parser.add_argument('--public', type=Path)
    args = parser.parse_args()
    now = timestamp(args.clock)
    if args.command == 'manifest':
        print(json.dumps(manifest(now), indent=2))
    else:
        if args.public is None:
            parser.error('--public is required')
        verify(args.public, now)


if __name__ == '__main__':
    main()
