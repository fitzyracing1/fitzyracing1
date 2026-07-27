# free(n) Clock Monitor
### Windows System Tray Plugin · 2038 Overflow Protection

---

## What It Does

Sits in your Windows system tray and monitors your clock and system timestamps for the **2038 Unix overflow problem** using the `free(n)` reciprocity logic loop.

- Live clock with Unix timestamp display
- Real-time countdown to January 19 2038 03:14:07 UTC
- System audit — scans Windows timestamps for 32-bit overflow risk
- Tray alerts when you're within 1 year or 30 days of overflow

---

## The 2038 Problem

Unix time stores dates as a 32-bit signed integer counting seconds since 1970.

```
Maximum value:  2,147,483,647
Overflow date:  January 19 2038 at 03:14:07 UTC
After that:     clock rolls back to December 13 1901
```

Any system still using 32-bit timestamp storage will fail or behave unpredictably after that point.

---

## free(n) Logic

```
1 - 1*0  = 1  →  RESOLVED   (timestamp safe beyond 2038)
(1-1)*0  = 0  →  COMPUTING  (timestamp at risk — fix needed)
```

The loop runs until every system resolves to n=1.

---

## How to Build

### Requirements
- Windows 10 or 11
- [.NET 6 SDK](https://dotnet.microsoft.com/download/dotnet/6.0)

### Build

```bash
cd freen-plugin
dotnet build
```

### Run

```bash
dotnet run
```

### Publish as single .exe (no install needed)

```bash
dotnet publish -c Release -r win-x64 --self-contained true
```

Output: `bin/Release/net6.0-windows/win-x64/publish/FreeNPlugin.exe`

---

## How to Install (run on startup)

1. Build and publish the `.exe`
2. Press `Win + R` → type `shell:startup` → Enter
3. Copy `FreeNPlugin.exe` into that folder
4. It will now start automatically with Windows

---

## Usage

- **Left click** the tray icon → open/close the monitor window
- **Right click** → open, run audit, or exit
- **CLOCK tab** → live time, Unix timestamp, countdown, progress bar
- **AUDIT tab** → scan Windows systems for 2038 risk
- **ABOUT tab** → documentation

---

## Files

```
Program.cs          Entry point
FreeNContext.cs     System tray, alerts, lifecycle
ClockForm.cs        Main window — clock, audit, about tabs
FreeNEngine.cs      Core free(n) evaluation logic
SystemAuditor.cs    Windows system timestamp scanner
FreeNPlugin.csproj  Build configuration
app.manifest        Windows DPI + permission settings
```

---

*Built with the free(n) reciprocity framework.*
*The loop does not close until every system resolves to n=1.*
