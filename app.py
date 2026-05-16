from flask import Flask, render_template, request, redirect
from flask_mail import Mail, Message
import boto3
import os
import uuid
from datetime import datetime

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'eu-west-1'))
table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'corecloud-bootcamp-registrations'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        whatsapp = request.form['whatsapp']
        motivation = request.form['motivation']

        table.put_item(Item={
            'id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'whatsapp': whatsapp,
            'motivation': motivation,
            'registered_at': datetime.utcnow().isoformat()
        })

        try:
            admin_msg = Message(
                'New Student Registration',
                recipients=[os.environ.get('ADMIN_EMAIL')]
            )
            admin_msg.body = f'''
New registration received:

Name: {name}
Email: {email}
WhatsApp: {whatsapp}
Motivation: {motivation}
'''
            mail.send(admin_msg)
        except Exception as e:
            print(f"Email failed: {e}")

        return redirect('/success')
    return render_template('register.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
