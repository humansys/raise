-- Archival insert; note this comment references CREATE PROCEDURE dbo.FakeObject
-- and EXEC dbo.NotReal to verify masking excludes commented-out SQL.
CREATE PROC dbo.InsertMeterMeasurementHistory
    @Measurements dbo.udtMeterMeasurement READONLY
AS
BEGIN
    SET NOCOUNT ON;

    /* block comment: CREATE TABLE dbo.AlsoFake (id int); EXEC dbo.AlsoNotReal */
    INSERT INTO dbo.MeterMeasurementHistory (MeterId, RecordedAtUtc, ValueKwh)
    SELECT MeterId, RecordedAtUtc, ValueKwh
    FROM @Measurements;
END
GO
