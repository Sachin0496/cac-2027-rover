// Rover v2 viewer: static rover + one arm-driven group per design pose, PBR materials by colour group (spec 8.1),
// explode slider, hood and fastener toggles, hover names, named camera views for the render script.
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';

const DATA = window.ROVER;
const params = new URLSearchParams(location.hash.slice(1));
const SHOT = params.has('shot');
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.95;
scene.add(new THREE.HemisphereLight(0xffffff, 0xaab2bb, 0.45));
const key = new THREE.DirectionalLight(0xffffff, 2.4);
key.castShadow = true;
key.shadow.mapSize.set(4096, 4096);
key.shadow.bias = -0.0004;
key.shadow.normalBias = 0.6;
scene.add(key, key.target);

const camera = new THREE.PerspectiveCamera(28, innerWidth / innerHeight, 10, 30000);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = false;

const world = new THREE.Group();          // millimetres, three frame: (x, y, z) = robot (x, z, -y)
scene.add(world);

const GROUPS = [   // colour group -> material settings (spec 8.1)
  { hex: 0xffcd11, m: { metalness: 0.0, roughness: 0.48, clearcoat: 0.35, clearcoatRoughness: 0.35 } },   // yellow
  { hex: 0x2b2e33, m: { metalness: 0.05, roughness: 0.6, clearcoat: 0.15, clearcoatRoughness: 0.5 } },    // graphite
  { hex: 0xc9cdd2, m: { metalness: 0.9, roughness: 0.42 } },                                             // aluminium
  { hex: 0x8a8f98, m: { metalness: 0.95, roughness: 0.33 } },                                            // steel
  { hex: 0xb5a642, m: { metalness: 0.95, roughness: 0.3 } },                                             // brass
  { hex: 0x1a1a1a, m: { metalness: 0.2, roughness: 0.55 } },                                             // black
  { hex: 0xd7191c, m: { metalness: 0.0, roughness: 0.22, clearcoat: 1.0, clearcoatRoughness: 0.1 } },    // red
  { hex: 0xf2f2f2, m: { metalness: 0.0, roughness: 0.6 } },                                              // arrow plates
];
const styleFor = (color) => {
  let best = GROUPS[0], bd = 1e9;
  for (const g of GROUPS) {
    const c = new THREE.Color(g.hex);
    const d = (c.r - color.r) ** 2 + (c.g - color.g) ** 2 + (c.b - color.b) ** 2;
    if (d < bd) { bd = d; best = g; }
  }
  return best;
};

const loader = new GLTFLoader();
loader.setMeshoptDecoder(MeshoptDecoder);
const decode = (b64) => { const s = atob(b64), u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u.buffer; };
const parse = (b64) => new Promise((res, rej) => loader.parse(decode(b64), '', res, rej));

const items = [];                          // { id, m, p, k, mv, obj (wrapper), centre (robot mm), off (robot mm), group }
const armGroups = {};                      // pose -> THREE.Group
const staticGroup = new THREE.Group();
world.add(staticGroup);
const FASTENER = /^(bolt_|nut_|tnut_|washer_)/;

function adopt(gltf, group, tag) {
  const model = gltf.scene;
  const box0 = new THREE.Box3().setFromObject(model);
  model.scale.setScalar(Math.max(...box0.getSize(new THREE.Vector3()).toArray()) < 20 ? 1000 : 1);   // glTF is metres
  group.add(model);
  model.updateMatrixWorld(true);
  const found = [];
  model.traverse((o) => { if (DATA.parts[o.name] && !found.some((f) => f.contains?.(o))) found.push(o); });
  for (const o of found) {
    const info = DATA.parts[o.name];
    o.traverse((c) => {
      if (!c.isMesh) return;
      const g = styleFor(c.material.color ? c.material.color : new THREE.Color(0x888888));
      c.material = new THREE.MeshPhysicalMaterial({ color: new THREE.Color(g.hex), ...g.m, side: THREE.DoubleSide });
      c.castShadow = true; c.receiveShadow = true;
      c.userData.id = o.name;
    });
    const w = new THREE.Group();
    o.parent.add(w); w.add(o);
    const b = new THREE.Box3().setFromObject(o);
    const c = b.getCenter(new THREE.Vector3());
    const inv3 = new THREE.Matrix3().setFromMatrix4(new THREE.Matrix4().copy(w.parent.matrixWorld).invert());   // world displacement -> local (the glTF root is rotated and scaled)
    items.push({ id: o.name, m: info.m, p: info.p, k: info.k, mv: info.mv, obj: w, model, inv3, centre: [c.x, -c.z, c.y], off: [0, 0, 0] });
  }
}

const uiViews = document.getElementById('views'), uiCtl = document.getElementById('controls');
if (SHOT) document.getElementById('title').style.display = 'none';
const state = { pose: params.get('pose') ?? '35', explode: +(params.get('explode') ?? 0), hood: params.get('hood') !== '0', hw: params.get('hw') !== '0' };

// --- explode: robot-frame offset (mm) of every item at full explosion
function explodeOffset(it) {
  const [cx, cy, cz] = it.centre, s = cy >= 0 ? 1 : -1, id = it.id, m = it.m;
  if (it.mv === 'arm' || it.mv === 'carriage') return [220, id.startsWith('drum_motor') || id.startsWith('drum_coupler') ? s * 80 : 0, 30];
  switch (m) {
    case 'drive':
      if (/^(wheel|wheel_cap|spacer_|bearing_|axle_|cap_bolt|cap_nut)/.test(id)) return [0, s * 150, 0];
      if (/^(mount)/.test(id)) return [0, s * 70, 0];
      if (/^(motor|coupler)/.test(id)) return [0, -s * 70, 0];
      if (/^(cap_|clamp_bolt)/.test(id)) return [0, 0, -75];
      if (/^(roof|clamp_nut)/.test(id)) return [0, 0, -35];
      return [0, 0, 0];
    case 'excavator':
      if (/^(lift_|tie_)/.test(id)) return [50, 0, 105];
      return [0, s * 20, 95];                                   // pivot brackets, ToF, their hardware
    case 'electronics':
      if (/^(batt|battery)/.test(id)) return [-95, 0, 50];
      return [0, 0, 105];
    case 'tower':
      if (/^(estop|ped_)/.test(id)) return [-140, s * 45, 60];
      return [-140, 0, 0.55 * (cz - 141)];
    case 'body':
      if (/^hood_(bolt)/.test(id)) return [0, 0, 300];
      if (/^hood_nut/.test(id)) return [0, 0, 105];
      if (/^(hood_left|hood_right)/.test(id)) return [0, s * 30, 250];
      if (/^(cover)/.test(id)) return [0, s * 75, 0];
      if (/^handle/.test(id)) return [0, 0, 330];
      if (/^arrow/.test(id)) return [0, 0, 270];
      return [0, 0, 0];
    default: return [0, 0, 0];
  }
}
function applyExplode() {
  const d = new THREE.Vector3();
  for (const it of items) {
    const [dx, dy, dz] = it.off;
    it.obj.position.copy(d.set(dx, dz, -dy).multiplyScalar(state.explode).applyMatrix3(it.inv3));
  }
}
function applyVisibility() {
  for (const it of items) {
    let v = true;
    if (!state.hood && it.m === 'body' && /^(hood_|handle|arrow)/.test(it.id)) v = false;
    if (!state.hw && FASTENER.test(it.p)) v = false;
    it.obj.visible = v;
  }
  for (const [p, g] of Object.entries(armGroups)) g.visible = p === state.pose;
}
let target = new THREE.Vector3(), radius = 800, view = params.get('view') || 'front_left';
const VIEWS = {   // azimuth deg from +x toward +y, elevation deg, distance in radii, fov
  front_left: [38, 20, 3.1, 28], rear_right: [-142, 22, 3.1, 28], side: [90, 3, 3.5, 22],
  front: [0, 4, 3.4, 22], top: [90, 89, 3.2, 22], iso_low: [55, 9, 3.0, 30], rear: [180, 8, 3.4, 24],
};
function setView(name) {
  view = name;
  const [az, el, dist, fov] = VIEWS[name] || VIEWS.front_left;
  const a = THREE.MathUtils.degToRad(az), e = THREE.MathUtils.degToRad(el);
  const dir = new THREE.Vector3(Math.cos(e) * Math.cos(a), Math.sin(e), -Math.cos(e) * Math.sin(a));   // robot (x fwd, y left, z up) -> three (x, z, -y)
  camera.fov = fov; camera.updateProjectionMatrix();
  camera.position.copy(target).addScaledVector(dir, radius * dist * (1 + 0.55 * state.explode));
  controls.target.copy(target); controls.update();
}
function setPose(p) { state.pose = String(p); applyVisibility(); refreshUi(); }

function refreshUi() {
  if (SHOT) return;
  uiCtl.querySelectorAll('button[data-pose]').forEach((b) => b.classList.toggle('on', b.dataset.pose === state.pose));
}
function buildUi() {
  if (SHOT) return;
  document.querySelectorAll('.panel').forEach((e) => { e.style.display = e.id === 'title' ? 'block' : 'flex'; });
  const NAMES = { '-28': 'press', '-25': 'dig', '0': 'level', '20': 'mid', '35': 'carry' };
  for (const n of Object.keys(VIEWS)) {
    const b = document.createElement('button'); b.textContent = n.replace('_', ' '); b.onclick = () => setView(n); uiViews.appendChild(b);
  }
  for (const p of DATA.poses) {
    const b = document.createElement('button'); b.dataset.pose = p; b.textContent = `${NAMES[p] ?? 'pose'} ${p > 0 ? '+' : ''}${p}°`; b.onclick = () => setPose(p); uiCtl.appendChild(b);
  }
  const chip = (html, init, on) => { const l = document.createElement('label'); l.className = 'chip'; l.innerHTML = html; uiCtl.appendChild(l); return l; };
  const ex = chip(`Explode <input type="range" min="0" max="100" value="${Math.round(state.explode * 100)}">`);
  ex.querySelector('input').oninput = (e) => { state.explode = e.target.value / 100; applyExplode(); setView(view); };
  const hood = chip(`<input type="checkbox" ${state.hood ? 'checked' : ''}> Hood`);
  hood.querySelector('input').onchange = (e) => { state.hood = e.target.checked; applyVisibility(); };
  const hw = chip(`<input type="checkbox" ${state.hw ? 'checked' : ''}> Fasteners`);
  hw.querySelector('input').onchange = (e) => { state.hw = e.target.checked; applyVisibility(); };
  refreshUi();
}

// hover names
const tip = document.getElementById('tip'), ray = new THREE.Raycaster(), mouse = new THREE.Vector2();
if (!SHOT) renderer.domElement.addEventListener('pointermove', (e) => {
  mouse.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  ray.setFromCamera(mouse, camera);
  const hit = ray.intersectObjects(world.children, true).find((h) => h.object.userData.id && h.object.visible);
  if (hit) {
    const info = DATA.parts[hit.object.userData.id];
    tip.textContent = `${hit.object.userData.id}  •  ${info.p}  •  ${info.m}${info.k === 'printed' ? '  •  printed' : ''}`;
    tip.style.left = e.clientX + 14 + 'px'; tip.style.top = e.clientY + 14 + 'px'; tip.style.display = 'block';
  } else tip.style.display = 'none';
});

(async () => {
  adopt(await parse(DATA.static), staticGroup, 'static');
  for (const p of DATA.poses) {
    const g = new THREE.Group(); world.add(g); armGroups[p] = g;
    adopt(await parse(DATA.arm[p]), g, 'arm' + p);
  }
  for (const it of items) it.off = explodeOffset(it);
  // frame on everything (all poses visible once)
  for (const g of Object.values(armGroups)) g.visible = true;
  const box = new THREE.Box3().setFromObject(world);
  box.getCenter(target); radius = box.getSize(new THREE.Vector3()).length() / 2 * 0.95;
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(radius * 30, radius * 30), new THREE.ShadowMaterial({ opacity: 0.3 }));
  floor.rotation.x = -Math.PI / 2; floor.position.y = box.min.y - 0.5; floor.receiveShadow = true;
  scene.add(floor);
  key.position.copy(target).add(new THREE.Vector3(-radius * 1.2, radius * 2.2, radius * 1.4));
  key.target.position.copy(target);
  const s = radius * 1.8;
  Object.assign(key.shadow.camera, { left: -s, right: s, top: s, bottom: -s, near: 1, far: radius * 9 });
  key.shadow.camera.updateProjectionMatrix();
  applyExplode(); applyVisibility(); buildUi(); setView(view);
  document.getElementById('busy').remove();
  window.dispatchEvent(new Event('rover-ready'));
  document.title = 'ready';
})();

window.setView = setView; window.setPose = setPose;
addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });
renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });
