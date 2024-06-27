-- Create the Forms table
CREATE TABLE Forms (
    form_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_DATE
);

-- Create the Fields table
CREATE TABLE Fields (
    field_id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER,
    name TEXT NOT NULL,
    label TEXT NOT NULL,
    type TEXT NOT NULL,
    order_num INTEGER,
    required BOOLEAN,
    options TEXT,
    validation_rules TEXT,
    FOREIGN KEY (form_id) REFERENCES Forms(form_id)
);

-- Create the FormSubmissions table
CREATE TABLE FormSubmissions (
    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    form_id INTEGER,
    submitted_at TIMESTAMP DEFAULT CURRENT_DATE,
    user_id INTEGER,
    complete BOOLEAN,
    FOREIGN KEY (form_id) REFERENCES Forms(form_id)
);

-- Create the FieldValues table
CREATE TABLE FieldValues (
    value_id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER,
    field_id INTEGER,
    value TEXT,
    FOREIGN KEY (submission_id) REFERENCES FormSubmissions(submission_id),
    FOREIGN KEY (field_id) REFERENCES Fields(field_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_fields_form_id ON Fields(form_id);
CREATE INDEX idx_formsubmissions_form_id ON FormSubmissions(form_id);
CREATE INDEX idx_fieldvalues_submission_id ON FieldValues(submission_id);
CREATE INDEX idx_fieldvalues_field_id ON FieldValues(field_id);

