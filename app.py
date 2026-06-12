from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "segredo_super_importante"

ARQUIVO = "usuarios.json"


def carregar_usuarios():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []


def salvar_usuarios(usuarios):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)


def email_valido(email):
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrao, email)


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')


@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    email = request.form.get('email')
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    confirmar = request.form.get('confirmarsenha')

    if not email or not usuario or not senha or not confirmar:
        return render_template('cadastro.html', msg="Preencha todos os campos")

    if not email_valido(email):
        return render_template('cadastro.html', msg="Email inválido")

    if senha != confirmar:
        return render_template('cadastro.html', msg="Senhas não conferem")

    usuarios = carregar_usuarios()

    for u in usuarios:
        if u['email'] == email:
            return "Usuário já existe"

    novo_usuario = {
        "email": email,
        "usuario": usuario,
        "senha": generate_password_hash(senha)
    }

    usuarios.append(novo_usuario)
    salvar_usuarios(usuarios)

    return redirect(url_for('index'))


@app.route('/verificarlogin', methods=['POST'])
def verificarlogin():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')

    if not usuario or not senha:
        return render_template('login.html', msg="Preencha todos os campos")

    usuarios = carregar_usuarios()

    for u in usuarios:
        if u['usuario'] == usuario and check_password_hash(u['senha'], senha):
            session['usuario'] = usuario
            return redirect(url_for('menu'))

    return render_template('login.html', msg="Usuário ou senha inválidos")


@app.route('/menu')
def menu():
    if 'usuario' not in session:
        return redirect(url_for('index'))

    return render_template('menu.html', usuario=session['usuario'])


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))