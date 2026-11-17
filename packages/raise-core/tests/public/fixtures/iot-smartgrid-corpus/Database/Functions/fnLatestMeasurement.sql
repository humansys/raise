CREATE FUNCTION dbo.fnLatestMeasurement(@MeterId INT)
RETURNS TABLE
AS
RETURN
    SELECT TOP (1) MeterId, RecordedAtUtc, ValueKwh
    FROM dbo.MeterMeasurement
    WHERE MeterId = @MeterId
    ORDER BY RecordedAtUtc DESC;
