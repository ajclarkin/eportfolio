from flask import Flask, request, render_template, url_for, flash, redirect
from datetime import datetime
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, DateField, TextAreaField, RadioField, HiddenField
from wtforms.validators import DataRequired, Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'


def get_db_connection():
    conn = sqlite3.connect('data/data.db')
    conn.row_factory = sqlite3.Row
    return conn


class DynamicForm(FlaskForm):
    trainee_id = HiddenField('Trainee ID')
    observer_id = SelectField('Observer', validators=[DataRequired()])

    @classmethod
    def create(cls, fields, observers):
        class DynamicFormClass(cls):
            pass

        for field in fields:
            field_name = f"field_{field['field_id']}"
            validators = [DataRequired()] if field.get('required') else [Optional()]
            
            if field['type'] == 'text':
                setattr(DynamicFormClass, field_name, StringField(field['label'], validators=validators))
            elif field['type'] == 'number':
                setattr(DynamicFormClass, field_name, IntegerField(field['label'], validators=validators))
            elif field['type'] == 'email':
                validators.append(Email())
                setattr(DynamicFormClass, field_name, StringField(field['label'], validators=validators))
            elif field['type'] == 'textarea':
                setattr(DynamicFormClass, field_name, TextAreaField(field['label'], validators=validators))
            elif field['type'] == 'select':
                choices = [(option.strip(), option.strip()) for option in field['options'].split(',')]
                setattr(DynamicFormClass, field_name, SelectField(field['label'], choices=choices, validators=validators))

        setattr(DynamicFormClass, 'observer_id', SelectField('Observer', choices))





def get_observers():
    conn = get_db_connection()
    observers = conn.execute('SELECT id, fullname FROM Users WHERE role = ?', ('observer',)).fetchall()
    conn.close()
    
    # Convert SQLite Row objects to dictionaries
    observers = [dict(observer) for observer in observers]
    
    return observers




def get_form_config(form_id):
    conn = get_db_connection()
    form = conn.execute('SELECT * FROM Forms WHERE form_id = ?', (form_id,)).fetchone()
    fields = conn.execute('SELECT * FROM Fields WHERE form_id = ? ORDER BY order_num', (form_id,)).fetchall()
    conn.close()
    
    # Convert SQLite Row objects to dictionaries
    form = dict(form) if form else None
    fields = [dict(field) for field in fields]
    
    return form, fields






def generate_form(form_id):
    form, fields = get_form_config(form_id)
    return render_template('form_template.html', form=form, fields=fields, observers = ['Clarkin', 'Sim', 'Gamble'])



def store_form_submission(form_id, trainee_id, observer_id, field_values):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert into FormSubmissions
        cursor.execute('''
            INSERT INTO FormSubmissions (form_id, trainee_id, observer_id, status, created_at, updated_at)
            VALUES (?, ?, ?, 0, ?, ?)
        ''', (form_id, trainee_id, observer_id, datetime.now(), datetime.now()))
        
        submission_id = cursor.lastrowid

        # Insert into FieldValues
        for field_id, value in field_values.items():
            cursor.execute('''
                INSERT INTO FieldValues (submission_id, field_id, value)
                VALUES (?, ?, ?)
            ''', (submission_id, field_id, value))

        conn.commit()
        return submission_id
    except sqlite3.Error as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.close()



@app.route('/form/<int:form_id>', methods=['GET', 'POST'])
def handle_form(form_id):
    form_config, fields = get_form_config(form_id)
    observers = get_observers()
    
    if not form_config:
        return "Form not found", 404
    
    form = DynamicForm.create(fields, observers)
    
    if form.validate_on_submit():
        # Process the form data
        trainee_id = form.trainee_id.data
        observer_id = form.observer_id.data
        
        field_values = {field['field_id']: form[str(field['field_id'])].data for field in fields}
        
        submission_id = store_form_submission(form_id, trainee_id, observer_id, field_values)
        
        if submission_id:
            return redirect(url_for('submission_success', submission_id=submission_id))
        else:
            return "An error occurred while submitting the form.", 500

    return render_template('form_template.html', form=form, form_config=form_config)




@app.route('/submission_success/<int:submission_id>')
def submission_success(submission_id):
    return f"Form submitted successfully. Submission ID: {submission_id}"


@app.route('/')
def index():
    user = request.headers.get('Remote-User')
    email = request.headers.get('Remote-Email')
    groups = [g for g in request.headers.get('Remote-Groups').split(',')]

    if 'eportfolio-user' in groups:
#        conn = sqlite3.connect('data/data.db')
#        # The following row required in order to address output data by column name
#        conn.row_factory = sqlite3.Row
#        cursor = conn.cursor()
#        # To add the observer here would require some complicated sql
#
#        cursor.execute('''
#            select fs.submission_id, strftime('%d-%m-%Y', fs.submitted_at) as submitted, f.description 
#            from formsubmissions fs 
#                inner join forms f on fs.form_id = f.form_id
#            where user_id = ?''',
#            (user,)
#        )
#        return render_template('usermenu.html', data = cursor.fetchall())
        return render_template('usermenu.html')
    else:
        return f"<p>Hello world</p>{groups}"



@app.route('/placeholder')
def view_previous_assessments():
    pass
