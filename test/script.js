const canvas = document.getElementById("world");
const ctx = canvas.getContext("2d");

const playPauseBtn = document.getElementById("playPauseBtn");
const stepBtn = document.getElementById("stepBtn");
const seedBtn = document.getElementById("seedBtn");
const clearBtn = document.getElementById("clearBtn");
const speedRange = document.getElementById("speedRange");
const foodRange = document.getElementById("foodRange");
const mutationRange = document.getElementById("mutationRange");
const speedValue = document.getElementById("speedValue");
const foodValue = document.getElementById("foodValue");
const mutationValue = document.getElementById("mutationValue");
const generationEl = document.getElementById("generation");
const lifeCountEl = document.getElementById("lifeCount");
const foodCountEl = document.getElementById("foodCount");

const cellSize = 8;
const cols = Math.floor(canvas.width / cellSize);
const rows = Math.floor(canvas.height / cellSize);
const maxOrganisms = 420;
const initialOrganisms = 80;
const initialFood = 900;

let organisms = [];
let food = createGrid();
let trails = createGrid();
let running = false;
let generation = 0;
let timerId = null;
let pointerDown = false;

function createGrid(fill = 0) {
  return Array.from({ length: rows }, () => Array(cols).fill(fill));
}

function randomInt(max) {
  return Math.floor(Math.random() * max);
}

function wrap(value, max) {
  return (value + max) % max;
}

function makeOrganism(x = randomInt(cols), y = randomInt(rows), parent = null) {
  const hue = parent ? parent.hue + randomRange(-16, 16) : randomRange(135, 205);

  return {
    x,
    y,
    energy: parent ? Math.max(18, parent.energy * 0.46) : randomRange(30, 70),
    hue: wrap(hue, 360),
    turnBias: parent ? clamp(parent.turnBias + randomRange(-0.22, 0.22), -1, 1) : randomRange(-0.7, 0.7),
    direction: randomInt(8),
    age: 0,
  };
}

function randomRange(min, max) {
  return min + Math.random() * (max - min);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function seedWorld() {
  organisms = Array.from({ length: initialOrganisms }, () => makeOrganism());
  food = createGrid();
  trails = createGrid();
  generation = 0;
  scatterFood(initialFood);
  draw();
}

function scatterFood(amount) {
  for (let i = 0; i < amount; i += 1) {
    food[randomInt(rows)][randomInt(cols)] = 1;
  }
}

function directionToDelta(direction) {
  return [
    [0, -1],
    [1, -1],
    [1, 0],
    [1, 1],
    [0, 1],
    [-1, 1],
    [-1, 0],
    [-1, -1],
  ][wrap(direction, 8)];
}

function senseFood(organism) {
  let bestDirection = organism.direction;
  let bestScore = -1;

  for (let turn = -2; turn <= 2; turn += 1) {
    const direction = wrap(organism.direction + turn, 8);
    const [dx, dy] = directionToDelta(direction);
    let score = 0;

    for (let distance = 1; distance <= 5; distance += 1) {
      const x = wrap(organism.x + dx * distance, cols);
      const y = wrap(organism.y + dy * distance, rows);
      score += food[y][x] ? 6 - distance : 0;
    }

    if (score > bestScore) {
      bestScore = score;
      bestDirection = direction;
    }
  }

  return bestScore > 0 ? bestDirection : organism.direction + Math.round(organism.turnBias + randomRange(-1.1, 1.1));
}

function stepLife() {
  const mutation = Number(mutationRange.value) / 100;
  const babies = [];

  fadeTrails();
  growFood();

  organisms.forEach((organism) => {
    organism.age += 1;
    organism.energy -= 0.58;
    organism.direction = wrap(senseFood(organism), 8);

    const [dx, dy] = directionToDelta(organism.direction);
    organism.x = wrap(organism.x + dx, cols);
    organism.y = wrap(organism.y + dy, rows);
    trails[organism.y][organism.x] = Math.min(1, trails[organism.y][organism.x] + 0.55);

    if (food[organism.y][organism.x]) {
      food[organism.y][organism.x] = 0;
      organism.energy += 18;
    }

    if (organism.energy > 70 && organisms.length + babies.length < maxOrganisms) {
      organism.energy *= 0.54;
      const child = makeOrganism(wrap(organism.x + randomInt(3) - 1, cols), wrap(organism.y + randomInt(3) - 1, rows), organism);

      if (Math.random() < mutation) {
        child.hue = wrap(child.hue + randomRange(-70, 70), 360);
        child.turnBias = clamp(child.turnBias + randomRange(-0.5, 0.5), -1, 1);
      }

      babies.push(child);
    }
  });

  organisms = organisms.concat(babies).filter((organism) => organism.energy > 0 && organism.age < 1400);
  generation += 1;
  draw();
}

function fadeTrails() {
  for (let y = 0; y < rows; y += 1) {
    for (let x = 0; x < cols; x += 1) {
      trails[y][x] *= 0.94;
    }
  }
}

function growFood() {
  const growth = Number(foodRange.value);
  scatterFood(Math.floor(growth / 2));

  if (Math.random() < (growth % 2) / 2) {
    scatterFood(1);
  }
}

function draw() {
  ctx.fillStyle = "#07090c";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  let foodTotal = 0;

  for (let y = 0; y < rows; y += 1) {
    for (let x = 0; x < cols; x += 1) {
      const trail = trails[y][x];

      if (trail > 0.025) {
        ctx.fillStyle = `rgba(154, 119, 255, ${trail * 0.34})`;
        ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
      }

      if (food[y][x]) {
        foodTotal += 1;
        ctx.fillStyle = "#f3d45b";
        ctx.fillRect(x * cellSize + 3, y * cellSize + 3, 2, 2);
      }
    }
  }

  organisms.forEach((organism) => {
    const energyScale = clamp(organism.energy / 80, 0.35, 1);

    ctx.fillStyle = `hsl(${organism.hue} 72% ${54 + energyScale * 14}%)`;
    ctx.fillRect(
      organism.x * cellSize + 1,
      organism.y * cellSize + 1,
      cellSize - 2,
      cellSize - 2
    );
  });

  generationEl.textContent = String(generation);
  lifeCountEl.textContent = String(organisms.length);
  foodCountEl.textContent = String(foodTotal);
}

function clearWorld() {
  organisms = [];
  food = createGrid();
  trails = createGrid();
  generation = 0;
  draw();
}

function getCellFromEvent(event) {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  const clientX = event.touches ? event.touches[0].clientX : event.clientX;
  const clientY = event.touches ? event.touches[0].clientY : event.clientY;

  return {
    x: Math.floor(((clientX - rect.left) * scaleX) / cellSize),
    y: Math.floor(((clientY - rect.top) * scaleY) / cellSize),
  };
}

function addLifeAtEvent(event) {
  const { x, y } = getCellFromEvent(event);

  if (x >= 0 && x < cols && y >= 0 && y < rows) {
    organisms.push(makeOrganism(x, y));
    scatterFood(8);
    draw();
  }
}

function stop() {
  running = false;
  playPauseBtn.textContent = "Start";

  if (timerId !== null) {
    clearInterval(timerId);
    timerId = null;
  }
}

function start() {
  if (running) {
    return;
  }

  running = true;
  playPauseBtn.textContent = "Pause";

  const fps = Number(speedRange.value);
  const intervalMs = Math.max(33, Math.round(1000 / fps));
  timerId = setInterval(stepLife, intervalMs);
}

function restartIfRunning() {
  if (!running) {
    return;
  }

  stop();
  start();
}

playPauseBtn.addEventListener("click", () => {
  if (running) {
    stop();
  } else {
    start();
  }
});

stepBtn.addEventListener("click", () => {
  if (!running) {
    stepLife();
  }
});

seedBtn.addEventListener("click", seedWorld);

clearBtn.addEventListener("click", () => {
  stop();
  clearWorld();
});

speedRange.addEventListener("input", restartIfRunning);
speedRange.addEventListener("input", () => {
  speedValue.textContent = speedRange.value;
});
foodRange.addEventListener("input", () => {
  foodValue.textContent = foodRange.value;
});
mutationRange.addEventListener("input", () => {
  mutationValue.textContent = mutationRange.value;
});

canvas.addEventListener("pointerdown", (event) => {
  pointerDown = true;
  addLifeAtEvent(event);
});

canvas.addEventListener("pointermove", (event) => {
  if (pointerDown) {
    addLifeAtEvent(event);
  }
});

window.addEventListener("pointerup", () => {
  pointerDown = false;
});

speedValue.textContent = speedRange.value;
foodValue.textContent = foodRange.value;
mutationValue.textContent = mutationRange.value;
seedWorld();
