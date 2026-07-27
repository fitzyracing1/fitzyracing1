using AspectControlUnit.Models;

namespace AspectControlUnit.Core;

/// <summary>
/// Prime number game engine
/// </summary>
public class PrimeGameEngine
{
    private readonly PrimeGameState _state = new();

    public bool IsPrime(int number)
    {
        if (number <= 1) return false;
        if (number == 2) return true;
        if (number % 2 == 0) return false;

        int boundary = (int)Math.Floor(Math.Sqrt(number));
        for (int i = 3; i <= boundary; i += 2)
        {
            if (number % i == 0) return false;
        }

        return true;
    }

    public PrimeGameState ProcessNumber(int number)
    {
        _state.CurrentNumber = number;
        _state.IsPrime = IsPrime(number);
        
        if (_state.IsPrime)
        {
            _state.PrimesFound.Add(number);
            _state.Score += number;
        }

        _state.LastUpdated = DateTime.UtcNow;
        return _state;
    }

    public PrimeGameState ProcessDataSet(DataSet dataSet)
    {
        foreach (var value in dataSet.Values)
        {
            int intValue = (int)Math.Round(value);
            ProcessNumber(intValue);
        }

        return _state;
    }

    public PrimeGameState GetState() => _state;

    public void ResetGame()
    {
        _state.CurrentNumber = 0;
        _state.IsPrime = false;
        _state.Score = 0;
        _state.PrimesFound.Clear();
        _state.LastUpdated = DateTime.UtcNow;
    }
}
