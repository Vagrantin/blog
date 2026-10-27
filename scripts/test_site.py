import datetime as dt
from pathlib import Path
import tempfile
import unittest

from blog_site import JST, manifest, metadata, public_path, timestamp, validate


class PublishingContract(unittest.TestCase):
    def article(self, when='2026-11-04T09:00:00+09:00', draft=False):
        return {'title': 'An article', 'publishDate': when, 'draft': draft}

    def test_first_wednesday_across_calendar_boundaries(self):
        for when in ['2026-11-04T09:00:00+09:00', '2027-09-01T09:00:00+09:00', '2027-04-07T09:00:00+09:00']:
            validate(self.article(when))

    def test_bad_schedule_and_ambiguous_timestamps_fail(self):
        for when in ['2026-11-11T09:00:00+09:00', '2026-11-04T08:59:00+09:00', '2026-11-05T09:00:00+09:00', '2026-11-04T09:00:00']:
            with self.subTest(when=when), self.assertRaises(ValueError):
                validate(self.article(when))

    def test_utc_timestamp_has_the_same_release_in_japan(self):
        self.assertEqual(validate(self.article('2026-11-04T00:00:00Z')).astimezone(JST).hour, 9)

    def test_historical_dates_and_unfinished_drafts(self):
        validate(self.article('2024-12-06T09:00:00+09:00'), legacy=True)
        validate(self.article('2026-11-05T12:00:00+09:00', draft=True))
        with self.assertRaises(ValueError):
            validate(self.article(draft='false'))

    def test_archive_inventory_and_future_draft(self):
        result = manifest(timestamp('2026-10-27T12:00:00Z'))
        historical = [a for a in result['articles'] if a['legacy']]
        self.assertEqual(len(historical), 22)
        self.assertEqual(sum(a['visible'] for a in historical), 21)
        far_future = manifest(timestamp('2037-01-01T00:00:00Z'))
        self.assertFalse(next(a for a in far_future['articles'] if '20360404' in a['url'])['visible'])

    def test_yaml_and_json_front_matter(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'index.md'
            path.write_text('---\ntitle: Test\npublishDate: 2026-11-04T09:00:00+09:00\ndraft: false\n---\nBody')
            validate(metadata(path))
            path.write_text('{"title":"Test","publishDate":"2026-11-04T09:00:00+09:00","draft":false}\n\nBody')
            validate(metadata(path))

    def test_output_path_cannot_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            public = Path(tmp)
            with self.assertRaises(ValueError):
                public_path(public, '/blog/../../etc/passwd')


if __name__ == '__main__':
    unittest.main()
