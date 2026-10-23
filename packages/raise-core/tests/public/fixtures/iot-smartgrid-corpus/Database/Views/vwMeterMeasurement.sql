CREATE VIEW dbo.vwMeterMeasurement
AS
SELECT MeterId, RecordedAtUtc, ValueKwh
FROM dbo.MeterMeasurement;
