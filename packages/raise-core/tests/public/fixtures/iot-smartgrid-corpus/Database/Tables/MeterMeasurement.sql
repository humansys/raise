CREATE TABLE [dbo].[MeterMeasurement]
(
    [MeterId]         INT           NOT NULL,
    [RecordedAtUtc]   DATETIME2     NOT NULL,
    [ValueKwh]        DECIMAL(10,3) NOT NULL,
    CONSTRAINT [PK_MeterMeasurement] PRIMARY KEY NONCLUSTERED ([MeterId], [RecordedAtUtc])
)
WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA);
