# EdgeBook Windows Backend

Backend service for handling iOS to Windows app launching and control.

## Setup

```bash
cd windows-backend
npm install
```

## Development

```bash
npm run dev
```

The server will start on `http://localhost:3000`

## Building

```bash
npm run build
npm start
```

## Environment Variables

Create a `.env` file:

```
PORT=3000
NODE_ENV=development
```

## API Endpoints

### Launch Application
```
POST /api/windows/launch
Content-Type: application/json

{
  "appId": "vscode",
  "userId": "user123",
  "deviceId": "device456"
}
```

### Check App Installation
```
GET /api/windows/apps/:appId/installed
```

### Get Installed Apps
```
GET /api/windows/apps/installed
```

### Start Remote Session
```
POST /api/windows/remote-session
Content-Type: application/json

{
  "userId": "user123",
  "deviceId": "device456",
  "sessionType": "rdp"
}
```

### Close Application
```
POST /api/windows/apps/:appId/close
```

### Health Check
```
GET /api/health
```
