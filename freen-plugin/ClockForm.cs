using System;
using System.Drawing;
using System.Windows.Forms;
using Timer = System.Windows.Forms.Timer;

namespace FreeN
{
    // -------------------------------------------------------
    //  ClockForm
    //  The main popup window shown when the tray icon is clicked
    //  Three tabs: Clock | Audit | About
    // -------------------------------------------------------

    public class ClockForm : Form
    {
        private Timer       _ticker;
        private TabControl  _tabs;
        private Label       _timeLabel;
        private Label       _dateLabel;
        private Label       _unixLabel;
        private Label       _countdownLabel;
        private ProgressBar _overflowBar;
        private Label       _pctLabel;
        private Label       _statusLabel;
        private ListView    _auditList;
        private Button      _auditBtn;
        private Label       _auditSummary;

        // Dark theme colors
        static readonly Color BG        = Color.FromArgb(17, 17, 32);
        static readonly Color BG2       = Color.FromArgb(13, 13, 26);
        static readonly Color ACCENT    = Color.FromArgb(0, 207, 255);
        static readonly Color WARNING   = Color.FromArgb(255, 170, 0);
        static readonly Color DANGER    = Color.FromArgb(255, 68, 68);
        static readonly Color TEXT      = Color.FromArgb(220, 220, 240);
        static readonly Color TEXTDIM   = Color.FromArgb(100, 100, 130);

        public ClockForm()
        {
            InitializeForm();
            BuildTabs();
            StartTicker();
            UpdateClock();
        }

        void InitializeForm()
        {
            Text            = "free(n) Clock Monitor";
            Size            = new Size(440, 520);
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox     = false;
            BackColor       = BG;
            ForeColor       = TEXT;
            StartPosition   = FormStartPosition.Manual;
            ShowInTaskbar   = false;

            // Position near system tray (bottom-right)
            var screen = Screen.PrimaryScreen.WorkingArea;
            Location = new Point(screen.Right - Width - 12, screen.Bottom - Height - 12);

            // Close hides rather than exits
            FormClosing += (s, e) => { e.Cancel = true; Hide(); };
        }

        void BuildTabs()
        {
            _tabs = new TabControl
            {
                Dock      = DockStyle.Fill,
                BackColor = BG,
                ForeColor = TEXT,
                Font      = new Font("Segoe UI", 9f),
            };

            _tabs.TabPages.Add(BuildClockTab());
            _tabs.TabPages.Add(BuildAuditTab());
            _tabs.TabPages.Add(BuildAboutTab());

            Controls.Add(_tabs);
        }

        TabPage BuildClockTab()
        {
            var page = MakePage("CLOCK");

            // Time display
            _timeLabel = MakeLabel("00:00:00", 42, FontStyle.Regular, TEXT);
            _timeLabel.TextAlign = ContentAlignment.MiddleCenter;
            _timeLabel.Dock      = DockStyle.None;
            _timeLabel.Size      = new Size(400, 56);
            _timeLabel.Location  = new Point(12, 16);

            _dateLabel = MakeLabel("", 10, FontStyle.Regular, TEXTDIM);
            _dateLabel.TextAlign = ContentAlignment.MiddleCenter;
            _dateLabel.Size      = new Size(400, 20);
            _dateLabel.Location  = new Point(12, 70);

            // Unix timestamp panel
            var unixPanel = MakePanel(12, 100, 400, 56);
            var unixTitle = MakeLabel("UNIX TIMESTAMP (32-BIT)", 8, FontStyle.Regular, TEXTDIM);
            unixTitle.Location = new Point(10, 8);
            unixTitle.Size     = new Size(380, 16);
            _unixLabel = MakeLabel("0", 18, FontStyle.Regular, WARNING);
            _unixLabel.Location = new Point(10, 26);
            _unixLabel.Size     = new Size(280, 24);
            var maxLabel = MakeLabel("MAX: 2,147,483,647", 8, FontStyle.Regular, TEXTDIM);
            maxLabel.Location  = new Point(230, 10);
            maxLabel.Size      = new Size(160, 16);
            maxLabel.TextAlign = ContentAlignment.TopRight;
            unixPanel.Controls.AddRange(new Control[] { unixTitle, _unixLabel, maxLabel });

            // Overflow progress
            var barPanel = MakePanel(12, 168, 400, 40);
            _pctLabel = MakeLabel("0.0000% TO OVERFLOW", 8, FontStyle.Regular, ACCENT);
            _pctLabel.Location = new Point(0, 0);
            _pctLabel.Size     = new Size(400, 16);
            _pctLabel.TextAlign = ContentAlignment.MiddleCenter;
            _overflowBar = new ProgressBar
            {
                Location = new Point(0, 18),
                Size     = new Size(400, 12),
                Minimum  = 0,
                Maximum  = 10000,
                Style    = ProgressBarStyle.Continuous,
                BackColor = Color.FromArgb(30, 30, 50),
            };
            barPanel.Controls.AddRange(new Control[] { _pctLabel, _overflowBar });

            // Countdown panel
            var cdPanel = MakePanel(12, 220, 400, 80);
            var cdTitle = MakeLabel("⏱  COUNTDOWN TO 2038 OVERFLOW", 8, FontStyle.Regular, DANGER);
            cdTitle.Location  = new Point(10, 8);
            cdTitle.Size      = new Size(380, 16);
            _countdownLabel = MakeLabel("", 16, FontStyle.Regular, TEXT);
            _countdownLabel.Location  = new Point(10, 30);
            _countdownLabel.Size      = new Size(380, 40);
            _countdownLabel.TextAlign = ContentAlignment.MiddleCenter;
            cdPanel.Controls.AddRange(new Control[] { cdTitle, _countdownLabel });

            // free(n) status
            _statusLabel = MakeLabel("free(n) LOOP  ·  1 − 1×0 = 1  →  RESOLVED ✓", 9, FontStyle.Regular, ACCENT);
            _statusLabel.Location  = new Point(12, 316);
            _statusLabel.Size      = new Size(400, 24);
            _statusLabel.TextAlign = ContentAlignment.MiddleCenter;

            page.Controls.AddRange(new Control[]
            {
                _timeLabel, _dateLabel, unixPanel, barPanel, cdPanel, _statusLabel
            });
            return page;
        }

        TabPage BuildAuditTab()
        {
            var page = MakePage("AUDIT");

            var title = MakeLabel("SCAN WINDOWS SYSTEMS FOR 2038 VULNERABILITY", 8, FontStyle.Regular, TEXTDIM);
            title.Location = new Point(12, 12);
            title.Size     = new Size(400, 16);

            _auditBtn = new Button
            {
                Text      = "RUN free(n) AUDIT",
                Location  = new Point(12, 36),
                Size      = new Size(400, 34),
                BackColor = ACCENT,
                ForeColor = BG,
                FlatStyle = FlatStyle.Flat,
                Font      = new Font("Courier New", 10f, FontStyle.Bold),
                Cursor    = Cursors.Hand,
            };
            _auditBtn.FlatAppearance.BorderSize = 0;
            _auditBtn.Click += RunAudit;

            _auditList = new ListView
            {
                Location      = new Point(12, 80),
                Size          = new Size(400, 280),
                View          = View.Details,
                FullRowSelect = true,
                GridLines     = false,
                BackColor     = BG2,
                ForeColor     = TEXT,
                Font          = new Font("Courier New", 8.5f),
                BorderStyle   = BorderStyle.None,
            };
            _auditList.Columns.Add("n",       30);
            _auditList.Columns.Add("System", 160);
            _auditList.Columns.Add("Formula",  90);
            _auditList.Columns.Add("Status",   90);
            _auditList.OwnerDraw = false;

            _auditSummary = MakeLabel("", 8, FontStyle.Regular, TEXTDIM);
            _auditSummary.Location = new Point(12, 368);
            _auditSummary.Size     = new Size(400, 20);
            _auditSummary.TextAlign = ContentAlignment.MiddleCenter;

            page.Controls.AddRange(new Control[]
            {
                title, _auditBtn, _auditList, _auditSummary
            });
            return page;
        }

        TabPage BuildAboutTab()
        {
            var page = MakePage("ABOUT");
            int y = 20;

            void Row(string key, string val)
            {
                var k = MakeLabel(key.ToUpper(), 8, FontStyle.Regular, TEXTDIM);
                k.Location = new Point(12, y);
                k.Size     = new Size(100, 20);
                var v = MakeLabel(val, 9, FontStyle.Regular, TEXT);
                v.Location = new Point(120, y);
                v.Size     = new Size(292, 20);
                page.Controls.AddRange(new Control[] { k, v });
                y += 28;
            }

            Row("Product",  "free(n) Clock Monitor");
            Row("Version",  "1.0.0 — Windows Plugin");
            Row("Problem",  "32-bit Unix overflow · Jan 19 2038 03:14:07 UTC");
            Row("Logic",    "1 − 1×0 = 1 → RESOLVED");
            Row("",         "(1−1)×0 = 0 → COMPUTING");
            Row("Loop",     "Runs until every system resolves to n=1");
            Row("Author",   "Developed via free(n) reciprocity framework");
            Row("Overflow", "Max 32-bit signed int = 2,147,483,647");

            y += 10;
            var note = MakeLabel(
                "This plugin monitors your Windows clock and scans\n" +
                "system timestamps for 2038 overflow risk in real time.\n" +
                "Any system still using 32-bit Unix storage will fail\n" +
                "on January 19th 2038. free(n) tracks them all.",
                8, FontStyle.Regular, TEXTDIM);
            note.Location = new Point(12, y);
            note.Size     = new Size(400, 80);
            page.Controls.Add(note);

            return page;
        }

        void StartTicker()
        {
            _ticker = new Timer { Interval = 1000 };
            _ticker.Tick += (s, e) => UpdateClock();
            _ticker.Start();
        }

        void UpdateClock()
        {
            var now  = DateTime.Now;
            long unix = FreeNEngine.NowUnix;
            long secs = FreeNEngine.SecondsTo2038;
            double pct = FreeNEngine.PercentConsumed;

            _timeLabel.Text = now.ToString("HH:mm:ss");
            _dateLabel.Text = now.ToString("dddd, dd MMMM yyyy");
            _unixLabel.Text = unix.ToString("N0");

            // Countdown breakdown
            long y = secs / (long)(365.25 * 86400);
            long rem = secs % (long)(365.25 * 86400);
            long d = rem / 86400; rem %= 86400;
            long h = rem / 3600;  rem %= 3600;
            long m = rem / 60;
            long s = rem % 60;
            _countdownLabel.Text = $"{y}y  {d:D3}d  {h:D2}h  {m:D2}m  {s:D2}s";

            _pctLabel.Text = $"{pct:F4}%  TO OVERFLOW";
            int barVal = (int)Math.Min(pct * 100, 10000);
            _overflowBar.Value = barVal;

            // Color the bar by urgency
            // (ProgressBar color is set via P/Invoke on Windows; approximate here)
            _pctLabel.ForeColor = pct > 99 ? DANGER : pct > 95 ? WARNING : ACCENT;
        }

        void RunAudit(object sender, EventArgs e)
        {
            _auditBtn.Enabled = false;
            _auditBtn.Text    = "SCANNING...";
            _auditList.Items.Clear();

            var results = SystemAuditor.RunFullAudit();

            foreach (var r in results)
            {
                var item = new ListViewItem($"n={r.N}");
                item.SubItems.Add(r.SystemName);
                item.SubItems.Add(r.Formula);
                item.SubItems.Add(r.Status);

                item.ForeColor = r.Risk switch
                {
                    RiskLevel.Safe     => ACCENT,
                    RiskLevel.Warning  => WARNING,
                    RiskLevel.High     => DANGER,
                    RiskLevel.Critical => Color.Red,
                    _                  => TEXT,
                };

                _auditList.Items.Add(item);
            }

            int resolved = results.FindAll(r => r.Result == FreeNResult.Resolved).Count;
            _auditSummary.Text = $"AUDIT COMPLETE  ·  {resolved}/{results.Count} SYSTEMS RESOLVED";

            _auditBtn.Enabled = true;
            _auditBtn.Text    = "RUN free(n) AUDIT";
        }

        // ---- helpers ----

        static TabPage MakePage(string title)
        {
            return new TabPage(title) { BackColor = BG, ForeColor = TEXT };
        }

        static Panel MakePanel(int x, int y, int w, int h)
        {
            return new Panel
            {
                Location  = new Point(x, y),
                Size      = new Size(w, h),
                BackColor = Color.FromArgb(13, 13, 26),
                BorderStyle = BorderStyle.None,
            };
        }

        static Label MakeLabel(string text, float size, FontStyle style, Color color)
        {
            return new Label
            {
                Text      = text,
                Font      = new Font("Segoe UI", size, style),
                ForeColor = color,
                BackColor = Color.Transparent,
                AutoSize  = false,
            };
        }
    }
}
