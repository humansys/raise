CREATE TABLE dbo.MeterMeasurementHistory
(
    MeterId INT NOT NULL,
    RecordedAtUtc DATETIME2 NOT NULL,
    ValueKwh DECIMAL(10,3) NOT NULL,
    ArchivedAtUtc DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
