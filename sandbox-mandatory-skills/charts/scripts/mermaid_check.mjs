// Parses ```mermaid blocks with the Mermaid GenAI UI draws them with, so a block it cannot
// read is fixed before it reaches the chat (it would show as code there).
//
// stdin: a JSON array of diagram sources. stdout: a JSON array, null for a diagram Mermaid
// reads, else its parse error. Exit 3 when the validator is not installed.
//
// The sandbox vendors it in $MERMAID_DIR (default /opt/mermaid):
// mermaid.min.js, the same version as genai-ui, run in a jsdom window.
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { join } from 'node:path';
import { Script } from 'node:vm';

const dir = process.env.MERMAID_DIR || '/opt/mermaid';
let window;
try {
  const { JSDOM } = createRequire(join(dir, 'package.json'))('jsdom');
  const dom = new JSDOM('<!doctype html><body></body>', { runScripts: 'outside-only', pretendToBeVisual: true });
  // Browser globals jsdom leaves out and Mermaid's parsers use (structuredClone: pie, packet…)
  for (const name of ['structuredClone', 'TextEncoder', 'TextDecoder']) dom.window[name] ??= globalThis[name];
  // Run as a classic <script>: its top-level `var` must land on the window
  new Script(readFileSync(join(dir, 'mermaid.min.js'), 'utf8')).runInContext(dom.getInternalVMContext());
  ({ window } = dom);
} catch (e) {
  console.error(`mermaid validator not available in ${dir}: ${e.message}`);
  process.exit(3);
}

const { mermaid } = window;
// As genai-ui's renderMermaid initializes it
mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', htmlLabels: false, flowchart: { htmlLabels: false } });

const sources = JSON.parse(readFileSync(0, 'utf8'));
const errors = [];
for (const source of sources) {
  try {
    await mermaid.parse(source);
    errors.push(null);
  } catch (e) {
    errors.push(String(e?.message ?? e).split('\n').slice(0, 4).join('\n'));
  }
}
console.log(JSON.stringify(errors));
