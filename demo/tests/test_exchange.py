"""The exchange is read-only and cannot reveal a replay's future response."""
import json
from pathlib import Path
import sys,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from controller import Manager
import backend as b

class ExchangeTests(unittest.TestCase):
 def test_request_response_and_replay_disclosure_gate(self):
  with tempfile.TemporaryDirectory() as directory:
   m=Manager(directory);source='a'*32;folder=Path(directory)/source/'model-1';folder.mkdir(parents=True)
   (folder/'payload.json').write_text(json.dumps({'model':'test','messages':[{'role':'user','content':'public context'}]}))
   (folder/'context.json').write_text('{}');(folder/'response.txt').write_text('complete answer')
   (folder/'result.json').write_text('{"status":"completed"}')
   with patch.object(m,'recordings',return_value={source:{'seed':3,'instance':b.INSTANCE.name}}):
    r=m.create({'mode':'replay','replay':source})
    early=m.exchange(r.id,1);self.assertIsNone(early['request_body']);self.assertEqual(early['public_text'],'')
    r.emit('replay_event',original_type='model_started',original_elapsed=1,data={'round_id':1,'call':1})
    r.emit('replay_event',original_type='model_public_delta',original_elapsed=2,data={'round_id':1,'text':'partial'})
    partial=m.exchange(r.id,1);self.assertIsNotNone(partial['request_body']);self.assertEqual(partial['public_text'],'partial');self.assertIsNone(partial['validated_response'])
    r.emit('replay_event',original_type='proposal_received',original_elapsed=3,data={'round_id':1})
    final=m.exchange(r.id,1);self.assertEqual(final['public_text'],'complete answer');self.assertFalse(final['authorization_included'])
    self.assertEqual(r.calls,0)
   with self.assertRaises(KeyError):m.exchange('b'*32,1)
   with self.assertRaises(ValueError):m.exchange(r.id,4)
   m.close()
 def test_failed_source_keeps_provenance_and_replay_uses_zero_calls(self):
  with tempfile.TemporaryDirectory() as directory:
   m=Manager(directory);source='c'*32
   record={'seed':3,'instance':b.COMPARISON_INSTANCE,'seconds':0,'sha256':'verified-fixture','status':'failed','reason':'invalid parent reference','events':[{'type':'run_failed','mode':'live','run_id':source,'seq':1,'elapsed':0,'reason':'invalid parent reference','status':'failed'}]}
   with patch.object(m,'recordings',return_value={source:record}):
    r=m.create({'mode':'replay','replay':source,'speed':4});m.start(r);r.thread.join(3)
   self.assertEqual(r.status,'finished');self.assertEqual(r.calls,0)
   provenance=next(e for e in r.events if e['type']=='replay_provenance')
   self.assertEqual(provenance['source_status'],'failed');self.assertEqual(provenance['source_reason'],'invalid parent reference')
   self.assertTrue(any(e['type']=='replay_event' and e['original_type']=='run_failed' for e in r.events));m.close()
if __name__=='__main__':unittest.main()
