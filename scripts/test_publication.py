#!/usr/bin/env python3
"""Exercise real Hugo output immediately before/at release and after downtime."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from blog_site import ROOT, timestamp, verify


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / 'site'
        root.mkdir()
        for name in ['assets', 'layouts', 'static', 'content', 'data']:
            shutil.copytree(ROOT / name, root / name)
        shutil.copy(ROOT / 'hugo.toml', root / 'hugo.toml')
        for slug, when, draft in [
            ('release-boundary-sentinel', '2026-11-04T09:00:00+09:00', False),
            ('future-sentinel', '2026-12-02T09:00:00+09:00', False),
            ('draft-sentinel', '2026-11-04T09:00:00+09:00', True),
        ]:
            bundle = root / 'content/posts' / slug
            bundle.mkdir()
            (bundle / 'index.md').write_text(json.dumps({'title': slug, 'publishDate': when, 'draft': draft}) + '\n\n# ' + slug)
        for clock, released in [
            ('2026-11-04T08:59:59+09:00', False),
            ('2026-11-04T09:00:00+09:00', True),
            ('2026-11-05T09:00:00+09:00', True),
        ]:
            output = Path(tmp) / 'output'
            shutil.rmtree(output, ignore_errors=True)
            subprocess.run([os.environ.get('HUGO', 'hugo'), '--source', str(root), '--destination', str(output), '--clock', clock, '--minify', '--panicOnWarning'], check=True, stdout=subprocess.DEVNULL)
            verify(output, timestamp(clock), root)
            assert (output / 'posts/release-boundary-sentinel/index.html').exists() == released
            for item in output.rglob('*'):
                if item.is_file() and item.suffix in ('.html', '.xml', '.json'):
                    text = item.read_text()
                    assert 'future-sentinel' not in text and 'draft-sentinel' not in text, item
        print('PASS: real Hugo release boundary, future/draft feed exclusion, and missed-run catch-up')


if __name__ == '__main__':
    main()
