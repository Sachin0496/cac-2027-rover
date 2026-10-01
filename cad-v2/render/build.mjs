// Bundle scene.js with three.js and inline the (optimised) GLBs into one self-contained HTML viewer.
import * as esbuild from 'esbuild';
import fs from 'node:fs';
import path from 'node:path';
import { optimizeGlb } from './optimize.mjs';

const out = path.resolve(process.argv[2] ?? '../out');
const dir = path.join(out, 'viewer');
const manifest = JSON.parse(fs.readFileSync(path.join(dir, 'manifest.json'), 'utf8'));
const b64 = async (f) => (await optimizeGlb(fs.readFileSync(path.join(dir, f)))).toString('base64');
const data = { poses: manifest.poses, parts: manifest.parts, static: await b64(manifest.files.static), arm: {} };
for (const p of manifest.poses) data.arm[p] = await b64(manifest.files.arm[p]);

const js = (await esbuild.build({ entryPoints: ['scene.js'], bundle: true, minify: true, format: 'iife', write: false }))
  .outputFiles[0].text.replaceAll('</script', '<\\/script');
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rover v2 viewer</title>
<style>
html,body{margin:0;height:100%;overflow:hidden;font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#1a1a1a}
body{background:radial-gradient(ellipse at 50% 35%,#f7f8fa 0%,#e4e7ec 55%,#cfd4dc 100%)}
#app{position:fixed;inset:0}
.panel{position:fixed;z-index:2;display:none;gap:8px;flex-wrap:wrap;align-items:center;font-size:13px}
#views{left:16px;bottom:16px;max-width:52vw}
#controls{right:16px;bottom:16px;max-width:44vw;justify-content:flex-end}
#title{left:16px;top:14px;display:block;font-weight:600;font-size:15px;letter-spacing:.2px}
#title small{display:block;font-weight:400;opacity:.65;margin-top:2px}
button{border:0;border-radius:8px;padding:8px 12px;background:#2b2e33;color:#fff;font-size:13px;cursor:pointer;opacity:.92}
button:hover,button.on{background:#ffcd11;color:#1a1a1a}
label.chip{display:flex;gap:6px;align-items:center;background:#fff;border-radius:8px;padding:7px 10px;box-shadow:0 1px 3px rgba(0,0,0,.18)}
input[type=range]{width:120px;accent-color:#ffcd11}
#tip{position:fixed;z-index:3;pointer-events:none;background:#1a1a1a;color:#fff;font-size:12px;padding:5px 8px;border-radius:6px;display:none;white-space:nowrap}
#busy{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;font-size:15px;opacity:.6}
</style></head>
<body><div id="app"></div><div id="busy">Loading the rover...</div>
<div id="title" class="panel">CAC 2027 rover v2<small>drag to orbit, scroll to zoom, right-drag to pan; hover a part for its name</small></div>
<div id="views" class="panel"></div><div id="controls" class="panel"></div><div id="tip"></div>
<script>window.ROVER=${JSON.stringify(data)};</script><script>${js}</script></body></html>`;
fs.writeFileSync(path.join(out, 'rover_v2_viewer.html'), html);
console.log(`viewer written: ${(html.length / 1e6).toFixed(1)} MB`);
