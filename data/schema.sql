-- Users table
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    fullname TEXT NOT NULL,
    role TEXT NOT NULL,
    expiry_date DATE,
    created_at DATETIME DEFAULT CURRENT_DATE,
    updated_at DATETIME DEFAULT CURRENT_DATE
);

-- Forms table
CREATE TABLE Forms (
    form_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_DATE,
    updated_at DATETIME DEFAULT CURRENT_DATE
);

-- Fields table
CREATE TABLE Fields (
    field_id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    label TEXT NOT NULL,
    type TEXT NOT NULL,
    order_num INTEGER NOT NULL,
    required BOOLEAN NOT NULL DEFAULT 0,
    options TEXT,
    validation_rules TEXT,
    FOREIGN KEY (form_id) REFERENCES Forms(form_id)
);

-- FormSubmissions table
CREATE TABLE FormSubmissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER NOT NULL,
    trainee_id INTEGER NOT NULL,
    observer_id INTEGER NOT NULL,
    status BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_DATE,
    updated_at DATETIME DEFAULT CURRENT_DATE,
    FOREIGN KEY (form_id) REFERENCES Forms(form_id),
    FOREIGN KEY (trainee_id) REFERENCES Users(id),
    FOREIGN KEY (observer_id) REFERENCES Users(id)
);

-- FieldValues table
CREATE TABLE FieldValues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    field_id INTEGER NOT NULL,
    value TEXT,
    FOREIGN KEY (submission_id) REFERENCES FormSubmissions(id),
    FOREIGN KEY (field_id) REFERENCES Fields(field_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_form_submissions_form_id ON FormSubmissions(form_id);
CREATE INDEX idx_form_submissions_trainee_id ON FormSubmissions(trainee_id);
CREATE INDEX idx_form_submissions_observer_id ON FormSubmissions(observer_id);
CREATE INDEX idx_field_values_submission_id ON FieldValues(submission_id);
CREATE INDEX idx_field_values_field_id ON FieldValues(field_id);

