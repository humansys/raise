CREATE TRIGGER dbo.trMeterMeasurementArchive
ON dbo.MeterMeasurement
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.MeterMeasurementAudit (MeterId, RecordedAtUtc)
    SELECT MeterId, RecordedAtUtc
    FROM inserted;

    EXEC dbo.InsertMeterMeasurementHistory @Measurements = NULL;
END
