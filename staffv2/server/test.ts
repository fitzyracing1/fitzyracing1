import express from 'express';

const app = express();
const PORT = process.env.PORT || 3006;

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

const server = app.listen(PORT, () => {
  console.log(`[test-server] listening on ${PORT}`);
});

// Keep alive
setInterval(() => {
  console.log('[test-server] alive');
}, 5000);

server.on('error', (err) => {
  console.error('[test-server] error:', err);
});
