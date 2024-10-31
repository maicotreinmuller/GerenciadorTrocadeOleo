from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
import locale
from datetime import datetime

# Configurações de moeda
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    print("Locale 'pt_BR.UTF-8' não disponível. Usando formatação alternativa.")

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Verifica se a pasta de banco de dados existe
if not os.path.exists("database"):
    os.makedirs("database")

DATABASE = 'database/data.db'

def connect_db():
    return sqlite3.connect(DATABASE)

# Função auxiliar para formatar moeda BRL
def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Registrando o filtro 'format_currency' no Jinja2
app.jinja_env.filters['format_currency'] = format_currency

# Criação de tabelas se não existirem
def create_tables():
    with connect_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                telefone TEXT,
                placa TEXT,
                marca TEXT,
                modelo TEXT,
                ano INTEGER
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS trocas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                cliente_id INTEGER,
                quilometragem INTEGER,
                valor REAL,
                vencimento TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        ''')

create_tables()

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    with connect_db() as conn:
        cursor = conn.execute("SELECT COUNT(*), SUM(valor) FROM trocas")
        result = cursor.fetchone()
        total_trocas = result[0] if result[0] is not None else 0
        total_ganho = format_currency(result[1]) if result[1] else "R$ 0,00"
        
        # Variáveis de contagem para os status
        no_prazo = 0
        vence_hoje = 0
        vencidos = 0
        hoje = datetime.today().date()

        # Consulta para buscar todas as trocas e contar os status
        cursor = conn.execute("SELECT vencimento FROM trocas")
        for row in cursor.fetchall():
            vencimento = datetime.strptime(row[0], '%Y-%m-%d').date()
            if vencimento > hoje:
                no_prazo += 1
            elif vencimento == hoje:
                vence_hoje += 1
            else:
                vencidos += 1

    return render_template('dashboard.html', 
                           total_trocas=total_trocas, 
                           total_ganho=total_ganho, 
                           no_prazo=no_prazo, 
                           vence_hoje=vence_hoje, 
                           vencidos=vencidos)

# Página unificada para clientes
@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        nome = request.form['nome']
        telefone = request.form['telefone']
        placa = request.form['placa']
        marca = request.form['marca']
        modelo = request.form['modelo']
        ano = request.form['ano']

        with connect_db() as conn:
            if cliente_id:
                conn.execute('''
                    UPDATE clientes SET nome=?, telefone=?, placa=?, marca=?, modelo=?, ano=?
                    WHERE id=?
                ''', (nome, telefone, placa, marca, modelo, ano, cliente_id))
                flash('Cliente atualizado com sucesso!')
            else:
                conn.execute('''
                    INSERT INTO clientes (nome, telefone, placa, marca, modelo, ano)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (nome, telefone, placa, marca, modelo, ano))
                flash('Cliente cadastrado com sucesso!')
            conn.commit()

        return redirect(url_for('clientes'))

    with connect_db() as conn:
        cursor = conn.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()

    return render_template('clientes.html', clientes=clientes)

# Rota para buscar dados do cliente pelo ID para edição
@app.route('/cliente/<int:id>')
def get_cliente(id):
    with connect_db() as conn:
        cursor = conn.execute("SELECT * FROM clientes WHERE id = ?", (id,))
        cliente = cursor.fetchone()
    if cliente:
        return jsonify({
            'id': cliente[0],
            'nome': cliente[1],
            'telefone': cliente[2],
            'placa': cliente[3],
            'marca': cliente[4],
            'modelo': cliente[5],
            'ano': cliente[6]
        })
    return jsonify({'error': 'Cliente não encontrado'}), 404

# Rota para excluir cliente
@app.route('/deletar_cliente/<int:id>')
def deletar_cliente(id):
    with connect_db() as conn:
        conn.execute("DELETE FROM clientes WHERE id = ?", (id,))
        conn.commit()
    flash('Cliente excluído com sucesso!')
    return redirect(url_for('clientes'))

# Rota para troca de óleo
@app.route('/troca_oleo', methods=['GET', 'POST'])
def troca_oleo():
    if request.method == 'POST':
        troca_id = request.form.get('troca_id')
        data = request.form['data']
        cliente_id = request.form['cliente_id']
        quilometragem = request.form['quilometragem']
        valor = float(request.form['valor'].replace('R$', '').replace('.', '').replace(',', '.'))
        vencimento = request.form['vencimento']

        with connect_db() as conn:
            if troca_id:
                conn.execute('''
                    UPDATE trocas SET data=?, cliente_id=?, quilometragem=?, valor=?, vencimento=?
                    WHERE id=?
                ''', (data, cliente_id, quilometragem, valor, vencimento, troca_id))
                flash('Troca de óleo atualizada com sucesso!')
            else:
                conn.execute('''
                    INSERT INTO trocas (data, cliente_id, quilometragem, valor, vencimento)
                    VALUES (?, ?, ?, ?, ?)
                ''', (data, cliente_id, quilometragem, valor, vencimento))
                flash('Troca de óleo lançada com sucesso!')
            conn.commit()

        return redirect(url_for('troca_oleo'))

    with connect_db() as conn:
        cursor = conn.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()

    with connect_db() as conn:
        cursor = conn.execute('''
            SELECT trocas.id, trocas.data, clientes.nome, clientes.placa, trocas.quilometragem, 
                   trocas.valor, trocas.vencimento
            FROM trocas
            JOIN clientes ON trocas.cliente_id = clientes.id
            ORDER BY trocas.vencimento ASC
        ''')
        trocas = cursor.fetchall()

    today = datetime.today()
    return render_template('troca_oleo.html', clientes=clientes, trocas=trocas, today=today, datetime=datetime)

# Rota para buscar dados da troca de óleo pelo ID para edição
@app.route('/troca/<int:id>')
def get_troca(id):
    with connect_db() as conn:
        cursor = conn.execute('''
            SELECT id, data, cliente_id, quilometragem, valor, vencimento 
            FROM trocas 
            WHERE id = ?
        ''', (id,))
        troca = cursor.fetchone()
    
    if troca:
        return jsonify({
            'id': troca[0],
            'data': troca[1],
            'cliente_id': troca[2],
            'quilometragem': troca[3],
            'valor': troca[4],
            'vencimento': troca[5]
        })
    else:
        return jsonify({'error': 'Troca não encontrada'}), 404

# Rota para excluir troca de óleo
@app.route('/deletar_troca/<int:id>')
def deletar_troca(id):
    with connect_db() as conn:
        conn.execute("DELETE FROM trocas WHERE id = ?", (id,))
        conn.commit()
    flash('Lançamento de troca de óleo excluído com sucesso!')
    return redirect(url_for('troca_oleo'))

if __name__ == '__main__':
    app.run(debug=True)
