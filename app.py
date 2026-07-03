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
            session["admin"] = u["admin"]

            return redirect(url_for("menu"))

    return render_template("login.html", msg="Usuário ou senha inválidos")


@app.route('/menu')
def menu():
    if 'usuario' not in session:
        return redirect(url_for('index'))

    return render_template(
        'menu.html',
        usuario=session['usuario']
    )


@app.route('/pesquisa')
def pesquisa():
    if 'usuario' not in session:
        return redirect(url_for('index'))

    resposta = supabase.table("jogos").select("*").execute()

    return render_template(
        'pesquisa.html',
        usuario=session['usuario'],
        jogos=resposta.data
    )


@app.route('/entrada')
def entrada():
    if 'usuario' not in session:
        return redirect(url_for('index'))

    return render_template(
        'entrada.html',
        usuario=session['usuario']
    )


@app.route('/perfil')
def perfil():
    if 'usuario' not in session:
        return redirect(url_for('index'))

    resposta = (
        supabase.table("usuarios")
        .select("*")
        .eq("usuario", session['usuario'])
        .execute()
    )

    if not resposta.data:
        return redirect(url_for('logout'))

    user = resposta.data[0]

    return render_template(
        'perfil.html',
        usuario=user["usuario"],
        email=user["email"]
    )


@app.route('/add-jogo', methods=['POST'])
def add_jogo():
    if 'usuario' not in session:
        return redirect(url_for('index'))

    nome = request.form.get('nome')
    desenvolvedora = request.form.get('desenvolvedora')
    genero = request.form.get('genero')
    nota = request.form.get('nota')
    imagem_url = request.form.get('imagem_url')

    supabase.table("jogos").insert({
        "nome": nome,
        "desenvolvedora": desenvolvedora,
        "genero": genero,
        "nota": float(nota),
        "imagem_url": imagem_url
    }).execute()

    return redirect(url_for('pesquisa'))


@app.route('/delete-jogo/<int:id>')
def delete_jogo(id):
    if 'usuario' not in session:
        return redirect(url_for('index'))

    if session.get("admin") != 1:
        return "Sem permissão", 403

    supabase.table("jogos").delete().eq("id", id).execute()

    return redirect(url_for('pesquisa'))


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('admin', None)

    return redirect(url_for('index'))