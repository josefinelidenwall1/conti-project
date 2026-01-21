--table for consultant work hours v1.0--
--JN: check some names etc, but should otherwise be ok? 


CREATE TABLE consultants (
    consultant_id SERIAL PRIMARY KEY,
    consultant_name VARCHAR(100)
);

CREATE TABLE consultanthours (
    workday_id SERIAL PRIMARY KEY,
    consultant_id INT,
    startingTime TIMESTAMP, 
    endingTime TIMESTAMP, 
    totalHours INT,
    lunchbreak BOOLEAN DEFAULT FALSE,
    customername VARCHAR (100),
    FOREIGN KEY (consultant_id) REFERENCES consultants (consultant_id)
);



--DROP TABLE consultants;
--DELETE FROM consultants;