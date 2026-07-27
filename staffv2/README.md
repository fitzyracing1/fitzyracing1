# Staff Bot Nanobot Build Simulation

This project extends the base React + TypeScript + Vite template into a "staff bot" simulation environment. It provides:

* A shared configuration layer for AI model selection
* An Express backend exposing configuration and a stub `/api/ask` endpoint
* Frontend helper client for retrieving GPT configuration
* A feature flag to globally enable GPT-5 for all clients with environment overrides

> Default model: **GPT-5** (feature flag `ENABLE_GPT5` defaults to enabled unless explicitly set to `0` / `false`).

## Quick Start

```powershell
npm install
npm run dev
```

This starts both the Vite dev server and the Express API (default port `3007`).

## Enable Real GPT Responses

To use real OpenAI GPT responses instead of stub data:

1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add it to your `.env` file:
```bash
OPENAI_API_KEY=sk-your-key-here
```
3. Restart the dev server

Without an API key, the bot will use simulated responses.

## Feature Flag: Enable GPT-5

Backend reads `process.env.ENABLE_GPT5`.

| Value | Result            |
|-------|-------------------|
| unset | Enabled (default) |
| `1`   | Enabled           |
| `true`| Enabled           |
| `0`   | Disabled          |
| `false` | Disabled        |

Computed config returned by `GET /api/config`:

```json
{
  "gptVersion": "gpt-5",
  "enableGpt5": true
}
```

## API Endpoints (Stub)

| Method | Path         | Description                         |
|--------|--------------|-------------------------------------|
| GET    | /api/config  | Returns current AI configuration    |
| POST   | /api/ask     | Accepts `{ prompt }`, returns stub  |

Example request:

```powershell
curl -X POST http://localhost:3001/api/ask -H "Content-Type: application/json" -d '{"prompt":"Hello"}'
```

## Frontend Usage

Use `apiClient.fetchAIConfig()` to get the active GPT configuration.

```ts
import { fetchAIConfig } from './lib/apiClient'

const cfg = await fetchAIConfig()
console.log(cfg.gptVersion, cfg.enableGpt5)
```

---

# React + TypeScript + Vite

The original template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
