using System;
using SmartGrid.Shared;

namespace SmartGrid.ConsoleClient;

public class Program
{
    public static void Main(string[] args)
    {
        var repository = new MeasurementRepository();
        var publisher = new MeasurementPublisher(repository);
        publisher.Run();
    }
}

public class MeasurementPublisher
{
    private readonly MeasurementRepository _repository;

    public MeasurementPublisher(MeasurementRepository repository)
    {
        _repository = repository;
    }

    public void Run()
    {
        Console.WriteLine("Publishing meter measurements...");
    }
}
