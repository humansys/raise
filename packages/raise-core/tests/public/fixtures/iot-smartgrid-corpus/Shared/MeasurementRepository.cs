using System.Collections.Generic;

namespace SmartGrid.Shared;

public class MeasurementRepository
{
    private readonly List<string> _measurements = new();

    public void Insert(string meterId, double value)
    {
        _measurements.Add($"{meterId}:{value}");
    }
}
