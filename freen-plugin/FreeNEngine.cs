using System;

namespace FreeN
{
    // -------------------------------------------------------
    //  free(n) Reciprocity Engine
    //  Evaluates any Unix timestamp for 2038 overflow risk
    //  1 - 1*0 = 1  → RESOLVED
    //  (1-1)*0 = 0  → COMPUTING
    // -------------------------------------------------------

    public enum FreeNResult { Resolved = 1, Computing = 0 }
    public enum RiskLevel { Safe, Warning, High, Critical }

    public class EvalResult
    {
        public int            N          { get; set; }
        public string         SystemName { get; set; }
        public long           Timestamp  { get; set; }
        public FreeNResult    Result     { get; set; }
        public RiskLevel      Risk       { get; set; }
        public string         Formula    { get; set; }
        public string         Status     => Result == FreeNResult.Resolved ? "RESOLVED" : "COMPUTING";
        public DateTime       AsDateTime => DateTimeOffset.FromUnixTimeSeconds(Timestamp).LocalDateTime;
    }

    public static class FreeNEngine
    {
        // Max value of a 32-bit signed integer — the overflow point
        public const long MAX_INT32_UNIX = 2147483647L;

        // Jan 19 2038 03:14:07 UTC
        public static readonly DateTime OverflowDate =
            new DateTime(2038, 1, 19, 3, 14, 7, DateTimeKind.Utc);

        // Current Unix timestamp (64-bit safe)
        public static long NowUnix =>
            (long)(DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;

        // Seconds remaining until 32-bit overflow
        public static long SecondsTo2038 => MAX_INT32_UNIX - NowUnix;

        // Percentage of 32-bit range consumed
        public static double PercentConsumed => (double)NowUnix / MAX_INT32_UNIX * 100.0;

        // Core free(n) evaluation
        // If the timestamp fits safely in a 32-bit int on 2038-01-19 → RESOLVED
        // Otherwise → COMPUTING (keep patching)
        public static FreeNResult Evaluate(long unixTimestamp)
        {
            // Apply order-of-operations rule:
            //   1 - 1*0  =  1  (safe)
            //   (1-1)*0  =  0  (unsafe)
            return unixTimestamp <= MAX_INT32_UNIX
                ? FreeNResult.Resolved
                : FreeNResult.Computing;
        }

        public static RiskLevel GetRisk(long unixTimestamp)
        {
            long delta = MAX_INT32_UNIX - unixTimestamp;
            if (delta < 0)            return RiskLevel.Critical;
            if (delta < 86400 * 365)  return RiskLevel.High;
            if (delta < 86400 * 365 * 5) return RiskLevel.Warning;
            return RiskLevel.Safe;
        }

        public static string FormulaFor(FreeNResult result) =>
            result == FreeNResult.Resolved ? "1 - 1×0 = 1" : "(1-1)×0 = 0";

        // Audit a named system timestamp
        public static EvalResult Audit(int n, string systemName, long timestamp)
        {
            var result = Evaluate(timestamp);
            return new EvalResult
            {
                N          = n,
                SystemName = systemName,
                Timestamp  = timestamp,
                Result     = result,
                Risk       = GetRisk(timestamp),
                Formula    = FormulaFor(result),
            };
        }
    }
}
