from flask import Flask, render_template, request, redirect, url_for, session
import re
from werkzeug.security import generate_password_hash, check_password_hash
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = "segredo_super_importante"


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

    email_existe = supabase.table("usuarios") \
        .select("id") \
        .eq("email", email) \
        .execute()

    if email_existe.data and len(email_existe.data) > 0:
        return render_template("cadastro.html", msg="Email já cadastrado")

    usuario_existe = supabase.table("usuarios") \
        .select("id") \
        .eq("usuario", usuario) \
        .execute()

    if usuario_existe.data and len(usuario_existe.data) > 0:
        return render_template("cadastro.html", msg="Usuário já existe")

    try:
        supabase.table("usuarios").insert({
            "email": email,
            "usuario": usuario,
            "senha": generate_password_hash(senha)
        }).execute()

    except Exception:
        return render_template("cadastro.html", msg="Erro ao cadastrar usuário")

    return redirect(url_for('index'))


@app.route('/verificarlogin', methods=['POST'])
def verificarlogin():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')

    if not usuario or not senha:
        return render_template('login.html', msg="Preencha todos os campos")

    resposta = (
        supabase.table("usuarios")
        .select("*")
        .eq("usuario", usuario)
        .execute()
    )

    if resposta.data:
        u = resposta.data[0]

        if check_password_hash(u["senha"], senha):
            session["usuario"] = usuario
            return redirect(url_for("menu"))

    return render_template("login.html", msg="Usuário ou senha inválidos")


@app.route('/menu')
def menu():
    if 'usuario' not in session:
        return redirect(url_for('index'))

    return render_template('menu.html', usuario=session['usuario'])


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))