# Quantum-to-JS Export Demo

Runs a minimal 2-qubit Bell-state simulation in Python and writes a JavaScript module with the measurement results instead of a histogram.

## Run

```powershell
C:/Users/EC/unix/.venv/Scripts/python.exe src/main.py
```

This generates `dist/results.js`:

```
export const measurementResults = {
	circuit: "bell_pair",
	shots: 512,
	counts: { "00": 257, "11": 255 }
};
```

Use the exported object directly in JavaScript:

```js
import { measurementResults } from "./dist/results.js";
console.log(measurementResults);
```
