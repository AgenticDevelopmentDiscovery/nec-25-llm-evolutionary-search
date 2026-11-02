/* Exercise rejected-write recovery without a browser, network or model calls. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/packing.js'), 'utf8');
const apiSource = source.slice(source.indexOf('async function api('), source.indexOf('function options('));
const runId = 'a'.repeat(32);
function harness(replies) {
  const requests = [], stored = new Map();
  const context = vm.createContext({
    sessionStorage: {setItem: (key, value) => stored.set(key, value)},
    $: () => ({classList: {remove: () => {}}}),
    fetch: async (url, options) => {
      requests.push({url, options});
      assert.ok(replies.length, 'unexpected request');
      const next = replies.shift();
      if (next instanceof Error) throw next;
      return {ok: next[0] < 400, status: next[0], json: async () => next[1]};
    },
  });
  vm.runInContext(`let access={write_token:'old-bootstrap'},run='${runId}',token='old-run';` + apiSource, context);
  return {context, requests, stored};
}
async function main() {
  const action = `/api/packing/runs/${runId}/continue`;
  const h = harness([[403,{error:'run write token required'}],
    [200,{write_token:'new-bootstrap'}], [200,{write_token:'new-run'}], [200,{continued:true}]]);
  const result = await vm.runInContext(`api('${action}',{},token)`, h.context);
  assert.equal(result.continued,true);
  assert.deepEqual(h.requests.map(r=>r.url),[action,'/api/packing/status',`/api/packing/runs/${runId}/claim`,action]);
  assert.equal(h.requests[2].options.headers['X-Demo-Token'],'new-bootstrap');
  assert.equal(h.requests[3].options.headers['X-Demo-Token'],'new-run');
  assert.equal(JSON.parse(h.stored.get('circle-run')).key,'new-run');

  const creation=harness([[403,{error:'write token required'}],
    [200,{write_token:'new-bootstrap'}],[201,{run_id:runId}]]);
  await vm.runInContext("api('/api/packing/runs',{mode:'numerical'},access.write_token)",creation.context);
  assert.equal(creation.requests.length,3);
  assert.equal(creation.requests[2].options.headers['X-Demo-Token'],'new-bootstrap');

  for(const response of [[403,{error:'cross-origin request rejected'}],
    [500,{error:'model worker failed'}],new Error('network timeout')]){
    const failure=harness([response]);
    await assert.rejects(vm.runInContext(`api('${action}',{},token)`,failure.context));
    assert.equal(failure.requests.length,1,'ambiguous failures must never be retried');
  }
  const twice=harness([[403,{error:'run write token required'}],
    [200,{write_token:'new-bootstrap'}],[200,{write_token:'new-run'}],
    [403,{error:'run write token required'}]]);
  await assert.rejects(vm.runInContext(`api('${action}',{},token)`,twice.context));
  assert.equal(twice.requests.length,4,'recovery must be bounded to one retry');
  const read=harness([[403,{error:'write token required'}]]);
  await assert.rejects(vm.runInContext("api('/api/packing/status')",read.context));
  assert.equal(read.requests.length,1);
  console.log('7 token-recovery scenarios passed; zero network/model calls.');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
