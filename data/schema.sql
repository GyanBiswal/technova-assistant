CREATE TABLE employees (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    department  TEXT NOT NULL,
    role        TEXT NOT NULL,
    manager_id  INTEGER REFERENCES employees(id),
    hire_date   TEXT NOT NULL,
    location    TEXT NOT NULL
);

CREATE TABLE projects (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    product     TEXT NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('Planning', 'In Progress', 'On Hold', 'Completed')),
    lead_id     INTEGER NOT NULL REFERENCES employees(id),
    start_date  TEXT NOT NULL,
    end_date    TEXT
);

CREATE TABLE tasks (
    id           INTEGER PRIMARY KEY,
    project_id   INTEGER NOT NULL REFERENCES projects(id),
    title        TEXT NOT NULL,
    assignee_id  INTEGER NOT NULL REFERENCES employees(id),
    status       TEXT NOT NULL CHECK (status IN ('To Do', 'In Progress', 'Done')),
    priority     TEXT NOT NULL CHECK (priority IN ('Low', 'Medium', 'High')),
    due_date     TEXT NOT NULL
);

CREATE TABLE sales (
    id          INTEGER PRIMARY KEY,
    sale_date   TEXT NOT NULL,
    region      TEXT NOT NULL CHECK (region IN ('North', 'South', 'East', 'West')),
    product     TEXT NOT NULL CHECK (product IN ('NovaDesk', 'NovaInsight')),
    customer    TEXT NOT NULL,
    amount_rs   INTEGER NOT NULL
);