from flask import Flask, render_template, request, session, redirect
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import logging
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
csrf = CSRFProtect(app)


# Configurar o arquivo de log
log_file = "connections.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# Middleware para registrar as conexões
@app.before_request
def log_request_info():
    client_ip = request.remote_addr
    log_message = f"{request.method} {request.url} - {client_ip}"
    logger.info(log_message)

@app.after_request
def log_response_info(response):
    client_ip = request.remote_addr
    log_message = f"{request.method} {request.url} - {client_ip} - status:{response.status_code}"
    logger.info(log_message)
    return response

def verificar_flags(flag1, flag2, flag3):
    # Verifique se as flags estão corretas
    return flag1 == 'a' and flag2 == 'b' and flag3 == 'c'

def salvar_nome_usuario(nome):
    # Salvar o nome do usuário em um arquivo de texto
    with open('nomes.txt', 'a') as arquivo:
        arquivo.write(nome + '\n')

def nome_repetido(nome):
    # Verificar se o nome do usuário já existe no arquivo de texto
    with open('nomes.txt', 'r') as arquivo:
        nomes_salvos = arquivo.read().splitlines()
        return nome in nomes_salvos

class FlagsForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    flag1 = StringField('Flag 1', validators=[DataRequired()])
    flag2 = StringField('Flag 2', validators=[DataRequired()])
    flag3 = StringField('Flag 3', validators=[DataRequired()])
    submit = SubmitField('Enviar')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = FlagsForm()
    if form.validate_on_submit():
        nome = form.nome.data
        flag1 = form.flag1.data
        flag2 = form.flag2.data
        flag3 = form.flag3.data

        if verificar_flags(flag1, flag2, flag3):
            if not nome_repetido(nome):
                salvar_nome_usuario(nome)
                return redirect('/success')
            else:
                session['error'] = 'Nome já foi registrado.'
        else:
            session['error'] = 'Flags incorretas.'
    return render_template('flags.html', form=form)

@app.route('/success')
def success():
    return 'Sucesso! Nome registrado.'

if __name__ == '__main__':
    app.run(port=80, debug=True)
