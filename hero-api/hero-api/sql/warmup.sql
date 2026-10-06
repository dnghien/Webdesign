CREATE TABLE team (id SERIAL PRIMARY KEY, name VARCHAR NOT NULL UNIQUE, headquarters VARCHAR NOT NULL);
CREATE TABLE hero (id SERIAL PRIMARY KEY, name VARCHAR NOT NULL, age INTEGER, team_id INTEGER REFERENCES team(id));
INSERT INTO team (name, headquarters) VALUES ('Avengers', 'New York'), ('X-Men', 'Westchester');
INSERT INTO hero (name, age, team_id) VALUES ('Tony', 45, 1), ('Natasha', 35, 1), ('Logan', 150, 2), ('Peter', 16, NULL);
-- Task 1
SELECT * FROM hero WHERE age >= 18 ORDER BY age DESC;
SELECT h.name AS hero, t.name AS team FROM hero h LEFT JOIN team t ON h.team_id = t.id ORDER BY h.id;
SELECT t.name, COUNT(h.id) AS n_heroes FROM team t LEFT JOIN hero h ON h.team_id = t.id GROUP BY t.id, t.name ORDER BY t.id;
SELECT * FROM hero ORDER BY id LIMIT 2 OFFSET 2;
-- 1.3
INSERT INTO team (name, headquarters) VALUES ('Avengers', 'Los Angeles');
INSERT INTO hero (name, team_id) VALUES ('Ghost', 99);
INSERT INTO hero (age) VALUES (30);
DELETE FROM team WHERE id = 1;
DROP TABLE hero; DROP TABLE team;
\dt
