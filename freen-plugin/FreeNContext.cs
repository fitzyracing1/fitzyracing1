using System;
using System.Drawing;
using System.Windows.Forms;
using Timer = System.Windows.Forms.Timer;

namespace FreeN
{
    // -------------------------------------------------------
    //  FreeNContext
    //  Runs silently in the Windows system tray
    //  Left click  → open/close the clock window
    //  Right click → context menu (open, audit, exit)
    // -------------------------------------------------------

    public class FreeNContext : ApplicationContext
    {
        private NotifyIcon  _trayIcon;
        private ClockForm   _clockForm;
        private Timer       _alertTimer;

        public FreeNContext()
        {
            _clockForm = new ClockForm();
            BuildTrayIcon();
            StartAlertMonitor();
        }

        void BuildTrayIcon()
        {
            var menu = new ContextMenuStrip();
            menu.Items.Add("Open free(n) Monitor",  null, (s, e) => ShowClock());
            menu.Items.Add("Run 2038 Audit",         null, (s, e) => { ShowClock(); });
            menu.Items.Add(new ToolStripSeparator());
            menu.Items.Add("Exit",                   null, (s, e) => ExitApp());

            _trayIcon = new NotifyIcon
            {
                Text             = "free(n) Clock Monitor — 2038 Watch",
                Icon             = CreateTrayIcon(),
                ContextMenuStrip = menu,
                Visible          = true,
            };

            _trayIcon.MouseClick += (s, e) =>
            {
                if (e.Button == MouseButtons.Left) ToggleClock();
            };
        }

        // Generates a simple tray icon programmatically (no .ico file needed)
        Icon CreateTrayIcon()
        {
            using var bmp = new Bitmap(16, 16);
            using var g   = Graphics.FromImage(bmp);
            g.Clear(Color.Transparent);

            // Clock face
            g.FillEllipse(new SolidBrush(Color.FromArgb(0, 207, 255)), 1, 1, 13, 13);
            g.DrawEllipse(new Pen(Color.FromArgb(17, 17, 32), 1.5f), 1, 1, 13, 13);

            // Clock hands
            g.DrawLine(new Pen(Color.FromArgb(17, 17, 32), 1.5f), 8, 8, 8, 4);   // 12 o'clock
            g.DrawLine(new Pen(Color.FromArgb(17, 17, 32), 1.5f), 8, 8, 11, 8);  // 3 o'clock

            return Icon.FromHandle(bmp.GetHicon());
        }

        void StartAlertMonitor()
        {
            // Check once per hour if we're dangerously close to 2038
            _alertTimer = new Timer { Interval = 3600000 };
            _alertTimer.Tick += (s, e) => CheckOverflowAlert();
            _alertTimer.Start();
        }

        void CheckOverflowAlert()
        {
            long secs = FreeNEngine.SecondsTo2038;
            long daysLeft = secs / 86400;

            // Alert thresholds
            if (daysLeft <= 30)
            {
                _trayIcon.ShowBalloonTip(10000,
                    "⚠ free(n) CRITICAL",
                    $"2038 overflow in {daysLeft} days! Run audit immediately.",
                    ToolTipIcon.Error);
            }
            else if (daysLeft <= 365)
            {
                _trayIcon.ShowBalloonTip(5000,
                    "free(n) WARNING",
                    $"2038 overflow in {daysLeft} days. Check your systems.",
                    ToolTipIcon.Warning);
            }

            // Update tray tooltip with live countdown
            long y = daysLeft / 365;
            long d = daysLeft % 365;
            _trayIcon.Text = $"free(n) · 2038 in {y}y {d}d · n={FreeNEngine.NowUnix}";
        }

        void ShowClock()
        {
            _clockForm.Show();
            _clockForm.BringToFront();
        }

        void ToggleClock()
        {
            if (_clockForm.Visible) _clockForm.Hide();
            else ShowClock();
        }

        void ExitApp()
        {
            _trayIcon.Visible = false;
            _clockForm.Dispose();
            Application.Exit();
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _trayIcon?.Dispose();
                _alertTimer?.Dispose();
                _clockForm?.Dispose();
            }
            base.Dispose(disposing);
        }
    }
}
