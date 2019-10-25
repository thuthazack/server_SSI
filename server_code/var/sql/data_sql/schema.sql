CREATE TABLE data_table(
    username VARCHAR(40) NOT NULL,
    deviceID VARCHAR(40) NOT NULL,
    sensorID VARCHAR(160) NOT NULL,
    data_path VARCHAR(160) NOT NULL,
    PRIMARY KEY (deviceID)
);
