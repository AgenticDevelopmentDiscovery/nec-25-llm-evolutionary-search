"""Author preview lifecycle: edited drafts never destroy the last good deck."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_presentation import atomic_write, source_hash
from preview import PresentationPreview


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.root=Path(self.folder.name)
        (self.root/'sections').mkdir();(self.root/'demo/static').mkdir(parents=True)
        self.prose=self.root/'sections/01.prose.md';self.prose.write_text('saved draft')
        (self.root/'references.bib').write_text('')
        self.bundle=self.root/'demo/static/presentation.json'
        self.notes=self.root/'demo/static/teaching-notes.html'
        self.calls=0
        self.publish()
    def tearDown(self): self.folder.cleanup()
    def publish(self):
        self.calls+=1
        text=self.prose.read_text()
        if text=='invalid': raise ValueError('frame: expected question, two blocks, answer')
        atomic_write(self.bundle,json.dumps({'source_sha256':source_hash(self.root),'text':text}))
        atomic_write(self.notes,text)
    def test_saved_prose_rebuilds_once_without_an_explicit_command(self):
        preview=PresentationPreview(self.root,self.publish,True)
        self.assertIsNone(preview.ensure()['error']);self.assertEqual(self.calls,1)
        self.prose.write_text('edited draft')
        self.assertIsNone(preview.ensure()['error'])
        self.assertEqual(json.loads(self.bundle.read_text())['text'],'edited draft')
        self.assertEqual(self.notes.read_text(),'edited draft')
        preview.ensure();self.assertEqual(self.calls,2)
    def test_invalid_draft_preserves_both_artifacts_and_recovers(self):
        preview=PresentationPreview(self.root,self.publish,True)
        before=self.bundle.read_bytes(),self.notes.read_bytes()
        self.prose.write_text('invalid')
        self.assertIn('expected question',preview.ensure()['error'])
        preview.ensure();self.assertEqual(self.calls,2) # No repeated build of an unchanged invalid draft.
        self.assertEqual(before,(self.bundle.read_bytes(),self.notes.read_bytes()))
        self.prose.write_text('repaired')
        self.assertIsNone(preview.ensure()['error']);self.assertEqual(self.notes.read_text(),'repaired')
    def test_external_manual_rebuild_is_recognized(self):
        preview=PresentationPreview(self.root,self.publish,True)
        self.prose.write_text('manual build');self.publish()
        preview.ensure();self.assertEqual(self.calls,2)
    def test_bundled_frames_work_without_pandoc_and_edits_explain_requirement(self):
        preview=PresentationPreview(self.root,self.publish,False)
        self.assertIsNone(preview.ensure()['error'])
        self.prose.write_text('edited on student machine')
        self.assertIn('Pandoc is required',preview.ensure()['error'])
        self.assertEqual(self.calls,1)


if __name__=='__main__':unittest.main()
