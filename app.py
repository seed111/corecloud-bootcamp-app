from flask import Flask, render_template, request, redirect
import boto3
from botocore.exceptions import ClientError
import os
import uuid
from datetime import datetime

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'eu-west-1'))
table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'corecloud-bootcamp-registrations'))

ses = boto3.client('ses', region_name=os.environ.get('AWS_REGION', 'eu-west-1'))

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
            ses.send_email(
                Source=os.environ.get('ADMIN_EMAIL'),
                Destination={'ToAddresses': [os.environ.get('ADMIN_EMAIL')]},
                Message={
                    'Subject': {'Data': 'New Student Registration'},
                    'Body': {
                        'Text': {
                            'Data': f'''New registration received:

Name: {name}
Email: {email}
WhatsApp: {whatsapp}
Motivation: {motivation}
'''
                        }
                    }
                }
            )
        except ClientError as e:
            print(f"SES email failed: {e}")

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
