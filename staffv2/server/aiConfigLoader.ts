export interface AIConfig {
  gptVersion: string;
  enableGpt5: boolean;
}

export function loadAIConfig(): AIConfig {
  const raw = process.env.ENABLE_GPT5;
  const enableGpt5 = raw ? !['0', 'false'].includes(raw.toLowerCase()) : true;
  return {
    gptVersion: 'gpt-5',
    enableGpt5,
  };
}
