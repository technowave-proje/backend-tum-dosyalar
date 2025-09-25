-- 1. Users tablosu
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 2. Locations tablosu
CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    grid_name VARCHAR(100) NULL,
    UNIQUE(latitude, longitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 3. TempoData (NASA TEMPO verileri)
CREATE TABLE tempodata (
    tempo_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    o3 FLOAT,
    no2 FLOAT,
    so2 FLOAT,
    co FLOAT,
    aerosol_index FLOAT,
    FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 4. AirQualityData (yer istasyonu verileri)
CREATE TABLE airqualitydata (
    aq_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    aqi INT,
    pm25 FLOAT,
    pm10 FLOAT,
    o3 FLOAT,
    co FLOAT,
    so2 FLOAT,
    FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 5. WeatherData (hava durumu verileri)
CREATE TABLE weatherdata (
    weather_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    pressure FLOAT,
    FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 6. Predictions (tahmin edilen hava kalitesi)
CREATE TABLE predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    predicted_aqi INT,
    model_version VARCHAR(50),
    FOREIGN KEY (location_id) REFERENCES Locations(location_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE users 
ADD CONSTRAINT username_unique UNIQUE (username); 

ALTER TABLE tempodata
ADD CONSTRAINT uniq_tempodata UNIQUE (location_id, timestamp); 

ALTER TABLE weatherdata
ADD CONSTRAINT uniq_weatherdata UNIQUE (location_id, timestamp); 

ALTER TABLE predictions
ADD CONSTRAINT uniq_predictions UNIQUE (location_id, timestamp, model_version); 

ALTER TABLE airqualitydata
ADD CONSTRAINT uniq_airqualitydata UNIQUE (location_id, timestamp);

ALTER TABLE tempodata
ADD CONSTRAINT hcho FLOAT
