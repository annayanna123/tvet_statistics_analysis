CREATE TABLE regions (
    region_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    region_name TEXT NOT NULL
);

CREATE TABLE province_stats (
    province_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    region_id INTEGER NOT NULL REFERENCES regions(region_id),
    province_name TEXT NOT NULL,
    reporting_period DATE NOT NULL,
    assessed_female INTEGER CHECK (assessed_female >= 0),
    assessed_male INTEGER CHECK (assessed_male >= 0),
    assessed_total INTEGER CHECK (assessed_total >= 0),
    certified_female INTEGER CHECK (certified_female >= 0),
    certified_male INTEGER CHECK (certified_male >= 0),
    certified_total INTEGER CHECK (certified_total >= 0),
    certification_rate NUMERIC(6,2)
    UNIQUE (region_id, province_id)
    
);