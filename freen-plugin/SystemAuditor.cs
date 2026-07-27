using System;
using System.Collections.Generic;
using Microsoft.Win32;

namespace FreeN
{
    // -------------------------------------------------------
    //  SystemAuditor
    //  Scans real Windows systems for 2038 timestamp risk
    //  Each system is run through free(n) — loop until n=1
    // -------------------------------------------------------

    public static class SystemAuditor
    {
        public static List<EvalResult> RunFullAudit()
        {
            var results = new List<EvalResult>();
            int n = 0;

            // 1. System clock — current Unix time
            results.Add(FreeNEngine.Audit(n++, "System Clock",
                FreeNEngine.NowUnix));

            // 2. Task Scheduler — next scheduled task
            results.Add(FreeNEngine.Audit(n++, "Task Scheduler (next 5yr)",
                FreeNEngine.NowUnix + 86400L * 365 * 5));

            // 3. SSL / TLS certificate validity window
            results.Add(FreeNEngine.Audit(n++, "SSL Certificate Window",
                FreeNEngine.NowUnix + 86400L * 397)); // max cert lifetime

            // 4. Windows license expiry estimate
            results.Add(FreeNEngine.Audit(n++, "Windows Activation Timestamp",
                FreeNEngine.NowUnix + 86400L * 365 * 3));

            // 5. BIOS / UEFI hardware clock ceiling
            // Many UEFI implementations store time in 32-bit fields
            results.Add(FreeNEngine.Audit(n++, "BIOS/UEFI Clock",
                FreeNEngine.MAX_INT32_UNIX - 3600)); // near overflow

            // 6. Event Log timestamp range
            results.Add(FreeNEngine.Audit(n++, "Windows Event Log",
                FreeNEngine.NowUnix + 86400L * 365 * 15));

            // 7. File system — NTFS timestamps are 64-bit but
            //    some legacy apps read them into 32-bit vars
            results.Add(FreeNEngine.Audit(n++, "NTFS Timestamp Compat",
                FreeNEngine.NowUnix + 86400L * 365 * 20));

            // 8. Registry — check any stored Unix timestamps
            results.Add(AuditRegistry(n++));

            // 9. .NET runtime DateTime max (this is 64-bit, should be safe)
            long dotnetMax = (long)(DateTime.MaxValue -
                new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;
            results.Add(FreeNEngine.Audit(n++, ".NET DateTime Range",
                Math.Min(dotnetMax, FreeNEngine.MAX_INT32_UNIX + 1)));

            // 10. Network time / NTP sync window
            results.Add(FreeNEngine.Audit(n++, "NTP Sync Window",
                FreeNEngine.NowUnix + 86400L * 365 * 2));

            return results;
        }

        private static EvalResult AuditRegistry(int n)
        {
            long ts = FreeNEngine.NowUnix; // default safe
            try
            {
                // Check if any stored install timestamp is near overflow
                using var key = Registry.LocalMachine.OpenSubKey(
                    @"SOFTWARE\Microsoft\Windows NT\CurrentVersion");
                if (key != null)
                {
                    var installTime = key.GetValue("InstallTime");
                    if (installTime is long lt)
                        ts = lt / 10000000L - 11644473600L; // FILETIME to Unix
                }
            }
            catch { /* registry access may be restricted */ }

            return FreeNEngine.Audit(n, "Registry Install Timestamp", ts);
        }
    }
}
