from flask import Flask, request, render_template, url_for, flash, redirect
from datetime import datetime
import sqlite3
from flask_wtf import FlaskForm
from wtforms import DateField, RadioField, StringField, SubmitField, IntegerField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Optional, Email

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

        # Add observer field first
#        setattr(DynamicFormClass, 'observer_id', SelectField('Observer', choices=[(str(o['id']), o['fullname']) for o in observers], validators=[DataRequired()]))
        setattr(DynamicFormClass, 'observer_id', SelectField('Observer', choices=observers))

        for field in fields:
            field_name = f"field_{field['field_id']}"
            validators = [DataRequired()] if field.get('required') else [Optional()]

            if field['type'] == 'text':
                setattr(DynamicFormClass, field_name, StringField(field['label'], validators=validators))
            elif field['type'] == 'number':
                setattr(DynamicFormClass, field_name, IntegerField(field['label'], validators=validators))
            elif field['type'] == 'email':
                setattr(DynamicFormClass, field_name, StringField(field['label'], validators=validators))
            elif field['type'] == 'date':
                setattr(DynamicFormClass, field_name, DateField(field['label'], validators=validators))
            elif field['type'] == 'textarea':
                setattr(DynamicFormClass, field_name, TextAreaField(field['label'], validators=validators))
            elif field['type'] == 'radio':
                choices = [(option.strip(), option.strip()) for option in field['options'].split(',')]
                setattr(DynamicFormClass, field_name, RadioField(field['label'], choices=choices, validators=validators))
            elif field['type'] == 'select':
                choices = [(option.strip(), option.strip()) for option in field['options'].split(',')]
                setattr(DynamicFormClass, field_name, SelectField(field['label'], choices=choices, validators=validators))

        return DynamicFormClass()




def get_observers():
    conn = get_db_connection()
    observers = conn.execute('SELECT id, fullname FROM Users WHERE role = ?', ('observer',)).fetchall()
    conn.close()
    return [(str(observer['id']), observer['fullname']) for observer in observers]



def get_form_config(form_id):
    conn = get_db_connection()
    form = conn.execute('SELECT * FROM Forms WHERE form_id = ?', (form_id,)).fetchone()
    fields = conn.execute('SELECT * FROM Fields WHERE form_id = ? ORDER BY order_num', (form_id,)).fetchall()
    conn.close()
    return dict(form) if form else None, [dict(field) for field in fields]



def store_form_submission(form_id, trainee_id, observer_id, field_values):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO FormSubmissions (form_id, trainee_id, observer_id, status, created_at, updated_at)
            VALUES (?, ?, ?, 0, ?, ?)
        ''', (form_id, trainee_id, observer_id, datetime.now(), datetime.now()))
        submission_id = cursor.lastrowid

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
        trainee_id = request.headers.get('Remote-User')  # Get trainee_id from headers
        observer_id = form.observer_id.data
        field_values = {field['field_id']: form[f"field_{field['field_id']}"].data for field in fields}
        
        submission_id = store_form_submission(form_id, trainee_id, observer_id, field_values)

        if submission_id:
            flash('Form submitted successfully', 'success')
            return redirect(url_for('index'))
        else:
            flash('An error occurred while submitting the form', 'error')

    return render_template('form_template.html', form=form, form_config=form_config)



@app.route('/view/<int:form_id>')
def display_form(form_id):
    groups = [g for g in request.headers.get('Remote-Groups').split(',')]
    if 'eportfolio-user' not in groups:
#    if 'user_id' not in session:
#        return redirect(url_for('login'))
        return "You're not logged in"

    user = request.headers.get('Remote-User')
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get form details
    cursor.execute("""
        SELECT * FROM FormSubmissions
        WHERE id = ? AND trainee_id = ?
    """, (form_id, user))
    form = cursor.fetchone()

    if not form:
        conn.close()
        return "Form not found", 404

    # Get form fields and their most recent values
    cursor.execute("""
        with formfields as (
            select row_number() over (partition by field_id order by id desc) as rowno
            , id, field_id, value 
            from fieldvalues where submission_id = ?
        ) 
        select f.label, ff.value 
        from formfields ff 
            inner join fields f on f.field_id = ff.field_id and rowno = 1 
        order by ff.field_id

    """, (form_id,))
    
    fields = cursor.fetchall()

    conn.close()

    return render_template('display_form.html', fields=fields)



@app.route('/')
def index():
    user = request.headers.get('Remote-User')
    email = request.headers.get('Remote-Email')
    groups = request.headers.get('Remote-Groups', '').split(',')

    if 'eportfolio-user' in groups:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT fs.id as submission_id, strftime('%d-%m-%Y', fs.created_at) as submitted, f.description
            FROM FormSubmissions fs
            INNER JOIN Forms f ON fs.form_id = f.form_id
            WHERE fs.trainee_id = ?
        ''', (user,))
        submissions = cursor.fetchall()
        conn.close()
        return render_template('usermenu.html', submissions=submissions)
    else:
        return "Access denied. You must be an eportfolio user to view this page."

if __name__ == '__main__':
    app.run(debug=True)

