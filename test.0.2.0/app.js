const canvas = document.querySelector("#world");
const ctx = canvas.getContext("2d");

const els = {
  toggle: document.querySelector("#toggle"),
  seed: document.querySelector("#seed"),
  clear: document.querySelector("#clear"),
  foodRate: document.querySelector("#foodRate"),
  speed: document.querySelector("#speed"),
  population: document.querySelector("#population"),
  generation: document.querySelector("#generation"),
  food: document.querySelector("#food"),
  oldest: document.querySelector("#oldest"),
  dominant: document.querySelector("#dominant"),
  events: document.querySelector("#events"),
};

const world = {
  cols: 96,
  rows: 64,
  food: new Set(),
  life: new Map(),
  paused: false,
  tick: 0,
  highGeneration: 0,
  selected: null,
};

const dirs = [
  [0, -1],
  [1, 0],
  [0, 1],
  [-1, 0],
];

const key = (x, y) => `${x},${y}`;
const wrap = (value, max) => (value + max) % max;
const rand = (max) => Math.floor(Math.random() * max);
const chance = (n) => Math.random() < n;

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function geneColor(genes) {
  return `hsl(${genes.hue} 82% ${genes.light}%)`;
}

function makeGenes(base) {
  if (!base) {
    return {
      hue: rand(360),
      speed: 1 + rand(4),
      sense: 1 + rand(6),
      caution: rand(7),
      light: 49 + rand(18),
    };
  }

  return {
    hue: wrap(base.hue + rand(33) - 16, 360),
    speed: clamp(base.speed + rand(3) - 1, 1, 6),
    sense: clamp(base.sense + rand(3) - 1, 1, 8),
    caution: clamp(base.caution + rand(3) - 1, 0, 8),
    light: clamp(base.light + rand(9) - 4, 42, 72),
  };
}

function addEvent(text) {
  const item = document.createElement("li");
  item.textContent = `t${world.tick}: ${text}`;
  els.events.appendChild(item);
  while (els.events.children.length > 24) {
    els.events.firstElementChild.remove();
  }
}

function spawnLife(x = rand(world.cols), y = rand(world.rows), genes = makeGenes(), energy = 28, gen = 1) {
  const cellKey = key(x, y);
  if (world.life.has(cellKey)) return false;

  world.life.set(cellKey, {
    x,
    y,
    genes,
    energy,
    age: 0,
    gen,
    dir: rand(4),
    memory: 0,
  });
  world.highGeneration = Math.max(world.highGeneration, gen);
  return true;
}

function seedWorld(count = 90) {
  for (let i = 0; i < count; i += 1) {
    spawnLife();
  }
  for (let i = 0; i < 520; i += 1) {
    world.food.add(key(rand(world.cols), rand(world.rows)));
  }
  addEvent(`${count} ancestor programs entered the grid`);
}

function resetWorld() {
  world.food.clear();
  world.life.clear();
  world.tick = 0;
  world.highGeneration = 0;
  world.selected = null;
  els.events.replaceChildren();
  seedWorld();
}

function placeFood(amount) {
  for (let i = 0; i < amount; i += 1) {
    world.food.add(key(rand(world.cols), rand(world.rows)));
  }
}

function scoreFood(cell, dir) {
  const [dx, dy] = dirs[dir];
  let score = 0;

  for (let step = 1; step <= cell.genes.sense; step += 1) {
    const x = wrap(cell.x + dx * step, world.cols);
    const y = wrap(cell.y + dy * step, world.rows);
    if (world.food.has(key(x, y))) {
      score += cell.genes.sense + 1 - step;
    }
  }

  return score;
}

function chooseDirection(cell) {
  const options = dirs.map((_, index) => ({
    dir: index,
    score: scoreFood(cell, index) + (index === cell.dir ? cell.genes.caution : 0) + Math.random(),
  }));
  options.sort((a, b) => b.score - a.score);
  return chance(0.08) ? rand(4) : options[0].dir;
}

function tryReproduce(cell, nextLife) {
  if (cell.energy < 46 || cell.age < 7) return;

  const start = rand(4);
  for (let i = 0; i < 4; i += 1) {
    const dir = (start + i) % 4;
    const [dx, dy] = dirs[dir];
    const x = wrap(cell.x + dx, world.cols);
    const y = wrap(cell.y + dy, world.rows);
    const childKey = key(x, y);

    if (!world.life.has(childKey) && !nextLife.has(childKey)) {
      cell.energy = Math.floor(cell.energy * 0.48);
      nextLife.set(childKey, {
        x,
        y,
        genes: makeGenes(cell.genes),
        energy: cell.energy,
        age: 0,
        gen: cell.gen + 1,
        dir,
        memory: cell.genes.hue,
      });

      if (cell.gen + 1 > world.highGeneration) {
        world.highGeneration = cell.gen + 1;
        addEvent(`generation ${world.highGeneration} emerged`);
      }
      return;
    }
  }
}

function step() {
  const nextLife = new Map();
  const cells = [...world.life.values()].sort(() => Math.random() - 0.5);

  for (const cell of cells) {
    cell.age += 1;
    cell.energy -= 1 + cell.genes.speed * 0.18;
    cell.dir = chooseDirection(cell);

    let moved = false;
    for (let attempt = 0; attempt < cell.genes.speed; attempt += 1) {
      const turn = attempt === 0 ? 0 : rand(3) - 1;
      const dir = wrap(cell.dir + turn, 4);
      const [dx, dy] = dirs[dir];
      const x = wrap(cell.x + dx, world.cols);
      const y = wrap(cell.y + dy, world.rows);
      const nextKey = key(x, y);

      if (!world.life.has(nextKey) && !nextLife.has(nextKey)) {
        cell.x = x;
        cell.y = y;
        cell.dir = dir;
        moved = true;
        break;
      }
    }

    if (!moved) {
      cell.energy -= 1.5;
    }

    const cellKey = key(cell.x, cell.y);
    if (world.food.delete(cellKey)) {
      cell.energy += 18;
      cell.memory = 100;
    } else {
      cell.memory = Math.max(0, cell.memory - 2);
    }

    if (cell.energy > 0 && cell.age < 240) {
      tryReproduce(cell, nextLife);
      nextLife.set(cellKey, cell);
    }
  }

  world.life = nextLife;
  world.tick += 1;
  placeFood(Number(els.foodRate.value));

  if (world.life.size === 0) {
    addEvent("extinction; reseeding from archived ancestors");
    seedWorld(24);
  }
}

function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  const scale = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.floor(rect.width * scale));
  canvas.height = Math.max(1, Math.floor(rect.height * scale));
  ctx.setTransform(scale, 0, 0, scale, 0, 0);
}

function draw() {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const cellW = width / world.cols;
  const cellH = height / world.rows;

  ctx.fillStyle = "#050809";
  ctx.fillRect(0, 0, width, height);

  ctx.globalAlpha = 0.22;
  ctx.strokeStyle = "#233139";
  ctx.lineWidth = 1;
  for (let x = 0; x <= world.cols; x += 8) {
    ctx.beginPath();
    ctx.moveTo(x * cellW, 0);
    ctx.lineTo(x * cellW, height);
    ctx.stroke();
  }
  for (let y = 0; y <= world.rows; y += 8) {
    ctx.beginPath();
    ctx.moveTo(0, y * cellH);
    ctx.lineTo(width, y * cellH);
    ctx.stroke();
  }
  ctx.globalAlpha = 1;

  ctx.fillStyle = "#f2ca63";
  for (const foodKey of world.food) {
    const [x, y] = foodKey.split(",").map(Number);
    ctx.globalAlpha = 0.65;
    ctx.fillRect(x * cellW + cellW * 0.3, y * cellH + cellH * 0.3, cellW * 0.4, cellH * 0.4);
  }
  ctx.globalAlpha = 1;

  for (const cell of world.life.values()) {
    const x = cell.x * cellW;
    const y = cell.y * cellH;
    const glow = cell.memory > 0 ? 0.9 : 0.18;
    ctx.fillStyle = geneColor(cell.genes);
    ctx.globalAlpha = 0.42 + glow * 0.3;
    ctx.fillRect(x, y, cellW, cellH);
    ctx.globalAlpha = 1;
    ctx.fillRect(x + 1, y + 1, Math.max(1, cellW - 2), Math.max(1, cellH - 2));

    ctx.fillStyle = "#07100c";
    const [dx, dy] = dirs[cell.dir];
    ctx.fillRect(
      x + cellW * (0.42 + dx * 0.22),
      y + cellH * (0.42 + dy * 0.22),
      Math.max(1, cellW * 0.16),
      Math.max(1, cellH * 0.16),
    );
  }
}

function geneStats() {
  if (world.life.size === 0) return [];

  const totals = [...world.life.values()].reduce(
    (acc, cell) => {
      acc.speed += cell.genes.speed;
      acc.sense += cell.genes.sense;
      acc.caution += cell.genes.caution;
      acc.energy += cell.energy;
      return acc;
    },
    { speed: 0, sense: 0, caution: 0, energy: 0 },
  );

  const count = world.life.size;
  return [
    ["Speed", totals.speed / count, 6],
    ["Sense", totals.sense / count, 8],
    ["Caution", totals.caution / count, 8],
    ["Energy", totals.energy / count, 80],
  ];
}

function renderStats() {
  const cells = [...world.life.values()];
  els.population.textContent = cells.length.toString();
  els.generation.textContent = world.highGeneration.toString();
  els.food.textContent = world.food.size.toString();
  els.oldest.textContent = cells.length ? Math.max(...cells.map((cell) => cell.age)).toString() : "0";

  els.dominant.replaceChildren(
    ...geneStats().map(([name, value, max]) => {
      const row = document.createElement("div");
      const label = document.createElement("span");
      const bar = document.createElement("span");
      const fill = document.createElement("span");
      const amount = document.createElement("span");

      row.className = "gene-row";
      bar.className = "bar";
      fill.style.width = `${clamp((value / max) * 100, 0, 100)}%`;
      label.textContent = name;
      amount.textContent = value.toFixed(1);
      bar.appendChild(fill);
      row.append(label, bar, amount);
      return row;
    }),
  );
}

let last = 0;
let statTime = 0;

function loop(time) {
  const interval = 140 / Number(els.speed.value);
  if (!world.paused && time - last > interval) {
    step();
    last = time;
  }

  draw();
  if (time - statTime > 250) {
    renderStats();
    statTime = time;
  }
  requestAnimationFrame(loop);
}

els.toggle.addEventListener("click", () => {
  world.paused = !world.paused;
  els.toggle.textContent = world.paused ? "Resume" : "Pause";
});

els.seed.addEventListener("click", () => {
  seedWorld(36);
});

els.clear.addEventListener("click", resetWorld);

canvas.addEventListener("click", (event) => {
  const rect = canvas.getBoundingClientRect();
  const x = Math.floor(((event.clientX - rect.left) / rect.width) * world.cols);
  const y = Math.floor(((event.clientY - rect.top) / rect.height) * world.rows);
  const clicked = world.life.get(key(x, y));
  if (clicked) {
    addEvent(`cell g${clicked.gen} age ${clicked.age} energy ${Math.round(clicked.energy)} inspected`);
  } else {
    spawnLife(x, y, makeGenes(), 32, 1);
    addEvent("new ancestor injected by hand");
  }
});

window.addEventListener("resize", resizeCanvas);

resizeCanvas();
resetWorld();
requestAnimationFrame(loop);
