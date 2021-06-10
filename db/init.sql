CREATE TABLE users(
    user_id INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_id)
);

INSERT INTO users (first_name, last_name)
VALUES
    ('Mikhail', 'Tsirlin'),
    ('Henry', 'Chen'),
    ('Daniel', 'Pechersky'),
    ('Dylan', 'Shortt'),
    ('Sky', 'Qiao');
