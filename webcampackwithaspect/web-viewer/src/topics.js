export const topics = [
  {
    name: 'Numeric Types & Subtraction',
    summary:
      'Subtraction uses numeric promotions; integral overflow depends on checked/unchecked; floats follow IEEE 754.',
    links: [
      { title: 'Arithmetic operators (C#)', url: 'https://learn.microsoft.com/dotnet/csharp/language-reference/operators/arithmetic-operators' },
      { title: 'Numeric conversions (C#)', url: 'https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/numeric-conversions' },
      { title: 'checked and unchecked', url: 'https://learn.microsoft.com/dotnet/csharp/language-reference/statements/checked-and-unchecked' }
    ],
    query: 'C# subtraction operator numeric promotions overflow checked unchecked'
  },
  {
    name: 'Floating-Point Precision & Rounding',
    summary:
      'float/double use IEEE 754 binary floating point; rounding via Math.Round; operations may yield NaN/±Infinity.',
    links: [
      { title: 'Floating-point types (C#)', url: 'https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/floating-point-numeric-types' },
      { title: 'System.Double', url: 'https://learn.microsoft.com/dotnet/api/system.double' },
      { title: 'Math.Round', url: 'https://learn.microsoft.com/dotnet/api/system.math.round' }
    ],
    query: 'C# double IEEE 754 precision rounding Math.Round NaN Infinity'
  },
  {
    name: 'Infinity & NaN',
    summary:
      'NaN and ±Infinity constants propagate per IEEE 754; comparisons with NaN are false; use Double.IsNaN/IsInfinity.',
    links: [
      { title: 'Double.NaN', url: 'https://learn.microsoft.com/dotnet/api/system.double.nan' },
      { title: 'Double.PositiveInfinity', url: 'https://learn.microsoft.com/dotnet/api/system.double.positiveinfinity' },
      { title: 'Double.NegativeInfinity', url: 'https://learn.microsoft.com/dotnet/api/system.double.negativeinfinity' }
    ],
    query: 'C# Double.IsNaN IsInfinity PositiveInfinity NegativeInfinity behavior'
  },
  {
    name: 'Decimal vs Double',
    summary:
      'decimal (base‑10, ~28–29 digits) suits financial exactness; double (base‑2, ~15–17 digits) is faster but inexact; avoid mixing types.',
    links: [
      { title: 'System.Decimal', url: 'https://learn.microsoft.com/dotnet/api/system.decimal' },
      { title: 'Floating-point types (C#)', url: 'https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/floating-point-numeric-types' },
      { title: 'Numeric conversions (C#)', url: 'https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/numeric-conversions' }
    ],
    query: 'C# decimal vs double precision performance when to use'
  },
  {
    name: 'Very Large Numbers & Overflow',
    summary:
      'Use BigInteger for arbitrary‑precision integers; integral overflow throws in checked context, wraps silently unchecked.',
    links: [
      { title: 'System.Numerics.BigInteger', url: 'https://learn.microsoft.com/dotnet/api/system.numerics.biginteger' },
      { title: 'OverflowException', url: 'https://learn.microsoft.com/dotnet/api/system.overflowexception' },
      { title: 'checked and unchecked', url: 'https://learn.microsoft.com/dotnet/csharp/language-reference/statements/checked-and-unchecked' }
    ],
    query: 'C# BigInteger arbitrary precision integer overflow checked unchecked'
  },
  {
    name: 'Mixed‑Sign Arithmetic & Overflow',
    summary:
      'Mixed‑sign operations promote to a common type; overflow depends on context and target type range.',
    links: [
      { title: 'Numeric conversions (C#)', url: 'https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/numeric-conversions' },
      { title: 'Integral numeric types (C#)', url: 'https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/integral-numeric-types' },
      { title: 'checked and unchecked', url: 'https://learn.microsoft.com/dotnet/csharp/language-reference/statements/checked-and-unchecked' }
    ],
    query: 'C# mixed sign arithmetic overflow behavior numeric conversions'
  },
  {
    name: 'JSON NaN/Infinity Handling',
    summary:
      'Strict JSON forbids NaN/±Infinity; use JsonNumberHandling or strings/custom converters to preserve special values.',
    links: [
      { title: 'RFC 8259 (JSON)', url: 'https://www.rfc-editor.org/rfc/rfc8259' },
      { title: 'JsonNumberHandling', url: 'https://learn.microsoft.com/dotnet/api/system.text.json.serialization.jsonnumberhandling' },
      { title: 'JsonSerializerOptions.NumberHandling', url: 'https://learn.microsoft.com/dotnet/api/system.text.json.jsonserializeroptions.numberhandling' }
    ],
    query: 'System.Text.Json NaN Infinity serialization JsonNumberHandling'
  }
]
