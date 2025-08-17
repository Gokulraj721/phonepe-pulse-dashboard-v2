CREATE DATABASE phonepe_dashboard;
USE phonepe_dashboard;
CREATE TABLE aggregated_user (
    year INT,
    quarter INT,
    registered_users BIGINT,
    app_opens BIGINT
);

CREATE TABLE aggregated_transaction (
    year INT,
    quarter INT,
    transaction_type VARCHAR(100),
    count BIGINT,
    amount DOUBLE
);

CREATE TABLE aggregated_insurance (
    year INT,
    quarter INT,
    insurance_type VARCHAR(100),
    count BIGINT,
    amount DOUBLE
);
CREATE TABLE map_user (
    year INT,
    quarter INT,
    state VARCHAR(100),
    registered_users BIGINT,
    app_opens BIGINT
);

CREATE TABLE map_transaction (
    year INT,
    quarter INT,
    state VARCHAR(100),
    district VARCHAR(100),
    count BIGINT,
    amount DOUBLE
);

CREATE TABLE map_insurance (
    year INT,
    quarter INT,
    state VARCHAR(100),
    district VARCHAR(100),
    insurance_type VARCHAR(100),
    count BIGINT,
    amount DOUBLE
);

CREATE TABLE top_user (
    year INT,
    quarter INT,
    state VARCHAR(100),
    district VARCHAR(100),
    pin_code VARCHAR(20),
    registered_users BIGINT
);

CREATE TABLE top_transaction (
    year INT,
    quarter INT,
    state VARCHAR(100),
    district VARCHAR(100),
    pin_code VARCHAR(20),
    count BIGINT,
    amount DOUBLE
);

CREATE TABLE top_insurance (
    year INT,
    quarter INT,
    insurance_type VARCHAR(100),
    count BIGINT,
    amount DOUBLE
);

CREATE TABLE user_device_data (
    year INT,
    quarter INT,
    brand VARCHAR(100),
    count BIGINT,
    percentage DOUBLE
);

SELECT COUNT(*) FROM insurance_data;
SELECT * FROM insurance_data LIMIT 10;

SELECT COUNT(*) FROM map_hover_transactions;
SELECT * FROM map_hover_transactions LIMIT 10;

SELECT COUNT(*) FROM transaction_categories;
SELECT * FROM transaction_categories LIMIT 10;

SELECT COUNT(*) FROM user_device_data;
SELECT * FROM user_device_data;


