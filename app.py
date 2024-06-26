from flask import Flask, request, render_template, url_for, flash, redirect
from datetime import datetime
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, DateField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'


# This reads the configuration of the specified form and associated fields into variable form_config.
# This is used to set up the form.

def get_form_config(form_id):
    conn = sqlite3.connect('data/data.db')
    cursor = conn.cursor()

    # Get form details
    cursor.execute("SELECT * FROM Forms WHERE form_id = ?", (form_id,))
    form = cursor.fetchone()

    if not form:
        conn.close()
        return None

    # Get fields for the form
    cursor.execute("SELECT * FROM Fields WHERE form_id = ? ORDER BY order_num", (form_id,))
    fields = cursor.fetchall()

    conn.close()

    # Construct the form configuration
    form_config = {
        'form_id': form[0],
        'name': form[1],
        'description': form[2],
        'fields': []
    }

    for field in fields:
        field_config = {
            'field_id': field[0],
            'name': field[2],
            'label': field[3],
            'type': field[4],
            'order': field[5],
            'required': bool(field[6]),
            'options': field[7],
            'validation_rules': field[8]
        }
        form_config['fields'].append(field_config)

    return form_config



# This creates the form object which will be inserted into the template document.
def generate_form(form_config):
    class DynamicForm(FlaskForm):
        pass


    for field in form_config['fields']:
        field_type = field['type'].lower()

        validators = [DataRequired()] if field['required'] else [Optional()]

        if field_type == 'text':
            setattr(DynamicForm, field['name'], StringField(field['label'], validators=validators))
        elif field_type == 'textarea':
            setattr(DynamicForm, field['name'], TextAreaField(field['label'], validators=validators))
        elif field_type == 'number':
            setattr(DynamicForm, field['name'], IntegerField(field['label'], validators=validators))
        elif field_type == 'select':
            choices = [(option.strip(), option.strip()) for option in field['options'].split(',')]
            setattr(DynamicForm, field['name'], SelectField(field['label'], choices=choices, validators=validators))
        elif field_type == 'date':
            setattr(DynamicForm, field['name'], DateField(field['label'], validators=validators))
        elif field_type == 'radio':
            choices = [(option.strip(), option.strip()) for option in field['options'].split(',')]
            setattr(DynamicForm, field['name'], RadioField(field['label'], choices=choices, validators=validators))
        elif field_type == 'checkbox':
            setattr(DynamicForm, field['name'], BooleanField(field['label'], validators=validators))
        elif field_type == 'file':
            setattr(DynamicForm, field['name'], FileField(field['label'], validators=validators))
        else:
            setattr(DynamicForm, field['name'], StringField(field['label'], validators=validators))


    return DynamicForm




def store_form_submission(form_id, form_data):
    conn = sqlite3.connect('data/data.db')
    cursor = conn.cursor()

    try:
        # Insert into FormSubmissions table
        cursor.execute('''
            INSERT INTO FormSubmissions (form_id, submitted_at)
            VALUES (?, ?)
        ''', (form_id, datetime.now()))
        
        submission_id = cursor.lastrowid

        # Insert into FieldValues table
        for field_name, value in form_data.items():
            if field_name != 'csrf_token':  # Skip CSRF token
                # Get field_id from Fields table
                cursor.execute('SELECT field_id FROM Fields WHERE form_id = ? AND name = ?', (form_id, field_name))
                field_id = cursor.fetchone()[0]

                cursor.execute('''
                    INSERT INTO FieldValues (submission_id, field_id, value)
                    VALUES (?, ?, ?)
                ''', (submission_id, field_id, str(value)))

        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()




@app.route('/form/<int:form_id>', methods=['GET', 'POST'])
def handle_form(form_id):
    form_config = get_form_config(form_id)
    if not form_config:
        return "Form not found", 404

    DynamicForm = generate_form(form_config)
    form = DynamicForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Process form submission
        store_form_submission(form_id, form.data)
        flash('Form submitted successfully!', 'success')
        return redirect(url_for('handle_form', form_id=form_id))

    # If it's a GET request or form validation failed, display the form
    return render_template('form.html', form=form, form_config=form_config)






@app.route('/')
def hello():
    user = request.headers.get('Remote-User')
    email = request.headers.get('Remote-Email')
    groups = [g for g in request.headers.get('Remote-Groups').split(',')]

    if 'eportfolio-user' in groups:
        return render_template('usermenu.html')
    else:
        return f"<p>Hello world</p>{groups}"





