from flask import Flask, request, redirect, url_for, render_template
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.office365.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'test@test.com'
app.config['MAIL_PASSWORD'] = 'mail_password'
app.config['MAIL_DEFAULT_SENDER'] = 'test@test.com'

mail = Mail(app)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if 'submit_button' in request.form:
            selected_item = request.form.get('selected_option')
            selected_title = request.form.get('selected_title')  # Get the selected title

            recipient_emails = 'test@test.com'

            msg = Message('Demande de stockage', recipients=[recipient_emails])
            msg.body = f'Nouvelle commande pour {selected_item} dans la {selected_title}'
            msg.add_recipient('private@email.com')
            mail.send(msg)

            # Redirect after processing the form
            return redirect(url_for('index'))
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
