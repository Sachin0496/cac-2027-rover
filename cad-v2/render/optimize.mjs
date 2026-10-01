// Shrink a GLB for the viewer: weld, quantize (KHR_mesh_quantization) and meshopt-compress. Node names are kept.
import { NodeIO, Logger } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { weld, quantize, meshopt, prune } from '@gltf-transform/functions';
import { MeshoptEncoder } from 'meshoptimizer';

export async function optimizeGlb(bytes) {
  await MeshoptEncoder.ready;
  const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.encoder': MeshoptEncoder });
  const doc = await io.readBinary(new Uint8Array(bytes));
  doc.setLogger(new Logger(Logger.Verbosity.ERROR));
  await doc.transform(prune(), weld({ tolerance: 1e-6 }), quantize({ quantizePosition: 14, quantizeNormal: 10 }), meshopt({ encoder: MeshoptEncoder, level: 'medium' }));
  return Buffer.from(await io.writeBinary(doc));
}

import { pathToFileURL } from 'node:url';
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const fs = await import('node:fs');
  const src = fs.readFileSync(process.argv[2]);
  const t = Date.now();
  const out = await optimizeGlb(src);
  fs.writeFileSync(process.argv[3], out);
  console.log(`${process.argv[2]}: ${(src.length / 1e6).toFixed(2)} MB -> ${(out.length / 1e6).toFixed(2)} MB in ${Date.now() - t} ms`);
}
