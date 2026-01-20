--table for consultant work hours v1.0--




CREATE TABLE consultanthours (
    id SERIAL PRIMARY KEY,
    startingTime TIMESTAMP, 
    endingTime TIMESTAMP, 
    totalHours INT,
    lunchbreak BOOLEAN DEFAULT FALSE, 
    consultantName VARCHAR (100),
    customername VARCHAR (100)
);