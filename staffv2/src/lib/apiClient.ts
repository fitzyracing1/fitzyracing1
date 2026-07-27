export interface AIConfig {
  gptVersion: string;
  enableGpt5: boolean;
}

const API_BASE = import.meta.env.VITE_API_BASE || '';

export async function fetchAIConfig(): Promise<AIConfig> {
  try {
    const res = await fetch(`${API_BASE}/api/config`);
    if (!res.ok) throw new Error(`Failed config: ${res.status}`);
    return res.json();
  } catch (err) {
    console.error('Fetch config error:', err);
    throw new Error(`Cannot connect to server. Is it running on port 3007?`);
  }
}

export interface AskResponse {
  model: string;
  reply: string;
}

export async function askModel(prompt: string): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/api/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
  if (!res.ok) throw new Error(`Ask failed: ${res.status}`);
  return res.json();
}
