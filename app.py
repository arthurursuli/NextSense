from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verificarlogin', methods=['POST'])
def verificarlogin():
    nome = request.form.get('nome')
    idade = request.form.get('idade')
    email = request.form.get('email')
    return '''<h1>Olá {{nome}}</h1>
            <hr>
            <h3>Nome: {{nome}}</h3>
            <h3>Idade: {{idade}}</h3>
            <h3>Email: {{email}}</h3>'''