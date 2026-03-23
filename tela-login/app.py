from flask import Flask, render_template, request, redirect
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session


app = Flask(__name__)
app.secret_key = "segredo123"

# 🔹 Função para conectar no banco
def conectar():
    return sqlite3.connect("database.db")


# 🔹 Criar tabela (se não existir)
def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            senha TEXT
        )
    """)
    conn.commit()
    conn.close()


criar_tabela()


# 🏠 Página inicial
@app.route("/")
def home():
    return render_template("cadastro.html")


# 🔐 Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE nome=?",
            (nome,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], senha):
            
            # 👇 AQUI entra o session
            session["usuario"] = nome
            
            # 👇 redireciona
            return redirect("/dashboard")

        else:
            return "Usuário ou senha incorretos"

    return render_template("login.html")


# 📝 Cadastro
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]
        senha_hash = generate_password_hash(senha)

        conn = conectar()
        cursor = conn.cursor()

        # 🔍 verifica se já existe
        cursor.execute("SELECT * FROM usuarios WHERE nome = ?", (nome,))
        usuario = cursor.fetchone()

        if usuario:
            conn.close()
            return "Usuário já existe!"

        # ✅ só insere se não existir
        cursor.execute(
            "INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
            (nome, senha_hash)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("cadastro.html")



@app.route("/usuarios")
def usuarios():
    if "usuario" in session:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios")
        dados = cursor.fetchall()

        conn.close()

        return render_template("usuarios.html", usuarios=dados)
    else:
        return redirect("/login")

@app.route("/dashboard")
def dashboard():
    if "usuario" in session:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total = cursor.fetchone()[0]

        conn.close()

        return render_template("dashboard.html",
                               usuario=session["usuario"],
                               total=total)
    else:
        return redirect("/login")
    
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect("/login")

app.run(debug=True)