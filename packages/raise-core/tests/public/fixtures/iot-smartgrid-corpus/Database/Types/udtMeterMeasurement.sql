CREATE TYPE [dbo].[udtMeterMeasurement] AS TABLE
(
    MeterId       INT           NOT NULL,
    RecordedAtUtc DATETIME2     NOT NULL,
    ValueKwh      DECIMAL(10,3) NOT NULL
);
