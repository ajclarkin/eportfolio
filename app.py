from flask import Flask, request, render_template

app = Flask(__name__)




@app.route('/')
def hello():
    user = request.headers.get('Remote-User')
    email = request.headers.get('Remote-Email')
    groups = [g for g in request.headers.get('Remote-Groups').split(',')]

    if 'eportfolio-user' in groups:
        return render_template('usermenu.html')
    else:
        return f"<p>Hello world</p>{groups}"

@app.route('/assessment_form')
def assessment_form():
    pass

@app.route('/view_previous_assessments')
def view_previous_assessments():
    pass
