CREATE DATABASE Gans;
USE Gans; 

CREATE TABLE cities (
	city_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    country VARCHAR(50),
    lat FLOAT(8),
    lon FLOAT(8),
    log VARCHAR(100)
);

CREATE TABLE airports (
    city_id INT,
    iata VARCHAR(3) NOT NULL PRIMARY KEY,
	FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

CREATE TABLE population (
	last_update INT NOT NULL,
    city_id INT NOT NULL,
    population INT,
    log VARCHAR(100),
    PRIMARY KEY (last_update, city_id),
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

CREATE TABLE weather (
	weather_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	timestamp INT,
    city_id INT,
    time DATETIME,
    temp FLOAT(2),
    felt_temp FLOAT(2),
	humidity FLOAT(2),
    wind_speed FLOAT(2),
    weather_class VARCHAR(50),
    weather_description VARCHAR(100),
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

CREATE TABLE flights (
	flight_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	iata VARCHAR(3),
    flight_no VARCHAR(10),
    sceduled_arrival_time DATETIME,
    revised_arrival_time DATETIME,
    terminal INT,
    status VARCHAR(50),
    depatured_from VARCHAR(3),
    depatured_from_name VARCHAR(50),
    airline VARCHAR(50),
    log VARCHAR(100),
    FOREIGN KEY (iata) REFERENCES airports(iata)
);