"""Author edits may shorten frames or add more sequential blocks."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_presentation import reveal_count
from preview import PresentationPreview


def div(name, children=None):
    return {'t': 'Div', 'c': [['', [name], []], children or []]}


class PresentationTests(unittest.TestCase):
    def test_question_and_answer_can_be_removed(self):
        self.assertEqual(reveal_count([div('block')]), 1)
        self.assertEqual(reveal_count([div('block'), div('block')]), 2)
        self.assertEqual(reveal_count([div('question'), div('block'), div('block')]), 3)

    def test_additional_blocks_reveal_individually(self):
        blocks = [div('question'), *[div('block') for _ in range(4)], div('answer')]
        self.assertEqual(reveal_count(blocks), 6)

    def test_plain_markdown_and_heading_only_frames_have_one_state(self):
        self.assertEqual(reveal_count([{'t': 'Para', 'c': [{'t': 'Str', 'c': 'Demo'}]}]), 1)
        self.assertEqual(reveal_count([]), 1)

    def test_nested_reveal_divs_match_browser_count(self):
        self.assertEqual(reveal_count([div('wrapper', [div('block'), div('answer')])]), 2)

    @unittest.skipUnless(shutil.which('pandoc'), 'Pandoc needed for the real authoring rebuild')
    def test_saved_edits_rebuild_short_frames_and_remove_deleted_frame(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'sections').mkdir(); (root/'demo/static').mkdir(parents=True)
            (root/'references.bib').write_text('')
            script = root/'demo/build_presentation.py'
            shutil.copyfile(Path(__file__).resolve().parents[1]/'build_presentation.py', script)
            source = root/'sections/01.prose.md'
            source.write_text('## Demo {#demo data-seconds="10"}\n\n::: {.block}\nOriginal\n:::\n\n'
                              '## Removed {#removed data-seconds="10"}\n\n::: {.block}\nOld\n:::\n')
            def rebuild():
                subprocess.run([sys.executable, str(script)], check=True, capture_output=True, text=True)
            preview = PresentationPreview(root, rebuild, True)
            self.assertIsNone(preview.ensure()['error'])
            source.write_text('## Edited demo {#demo data-seconds="10"}\n\n::: {.block}\nFresh first\n:::\n\n'
                              '::: {.block}\nFresh second\n:::\n\n::: {.notes}\nPrivate explanation\n:::\n')
            self.assertIsNone(preview.ensure()['error'])
            data = json.loads((root/'demo/static/presentation.json').read_text())
            self.assertEqual(data['main_frame_count'], 1)
            self.assertEqual(data['main_reveals'], 2)
            self.assertEqual(data['frames'][0]['title'], 'Edited demo')
            self.assertIn('Fresh second', data['frames'][0]['html'])
            self.assertNotIn('Private explanation', data['frames'][0]['html'])
            self.assertIn('Private explanation', (root/'demo/static/teaching-notes.html').read_text())

    @unittest.skipUnless(shutil.which('pandoc'), 'Pandoc needed for PDF overlay conversion')
    def test_pdf_overlays_do_not_add_empty_states_when_question_is_removed(self):
        source = ('## One\n\n::: {.block}\nOne\n:::\n\n'
                  '## Two\n\n::: {.block}\nFirst\n:::\n\n::: {.block}\nSecond\n:::\n\n'
                  '## Full\n\n::: {.question}\nQuestion\n:::\n\n::: {.block}\nFirst\n:::\n\n'
                  '::: {.block}\nSecond\n:::\n\n::: {.answer}\nAnswer\n:::\n')
        lua = Path(__file__).resolve().parents[2]/'filters/slides.lua'
        result = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'beamer', '--slide-level=2',
                                 '--lua-filter='+str(lua)], input=source, text=True, capture_output=True, check=True)
        self.assertEqual(result.stdout.count('\\pause'), 4)  # (1-1) + (2-1) + (4-1)

    @unittest.skipUnless(shutil.which('pandoc'), 'Pandoc needed for article conversion')
    def test_article_groups_close_when_questions_or_answers_are_deleted(self):
        source = ('## Block only\n\n::: {.block}\nFirst\n:::\n\n'
                  '## No answer\n\n::: {.question}\nQuestion\n:::\n\n::: {.block}\nSecond\n:::\n\n'
                  '::: {.notes}\nExplanation\n:::\n\n'
                  '## Ends without answer\n\n::: {.question}\nFinal\n:::\n')
        lua = Path(__file__).resolve().parents[2]/'filters/pdf-images.lua'
        result = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'latex', '--lua-filter='+str(lua)],
                                input=source, text=True, capture_output=True, check=True)
        self.assertEqual(result.stdout.count('\\begin{minipage}'), 3)
        self.assertEqual(result.stdout.count('\\end{minipage}'), 3)
        self.assertLess(result.stdout.index('\\end{minipage}'), result.stdout.index('No answer'))


if __name__ == '__main__': unittest.main()
