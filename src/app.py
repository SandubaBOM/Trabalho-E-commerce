from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, session
from db import create_connection, create_tables, Error
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Chave secreta para a sessão

# Dados de login fictícios
USER_CREDENTIALS = {
    'admin': 'guga'
}

@app.before_request
def setup():
    try:
        create_tables()  # Chama a função para criar as tabelas antes da primeira requisição
        print("Tabelas configuradas.")
    except Exception as e:
        print(f"Erro ao configurar tabelas: {e}")

@app.route("/")
def index():
    return redirect(url_for("home"))

@app.route("/home")
def home():
    return render_template("home.html")

@app.route('/loginAD', methods=['GET', 'POST'])
def loginAD():
    if 'admin_logged_in' in session and session['admin_logged_in']:
        return redirect(url_for('admin'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if USER_CREDENTIALS.get(username) == password:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin'))
        else:
            return render_template('loginAD.html', error='Credenciais inválidas')

    return render_template('loginAD.html')


@app.route('/logoutAD')
def logoutAD():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('loginAD'))

@app.route('/loginCL')
def loginCL():
   return render_template('loginCL.html')




@app.route('/fazer_pedido')
def fazer_pedido():
    # Verifique se o usuário está logado
    if 'logged_in' in session and session['logged_in']:
        flash("Isso é uma mensagem de teste!", "info")
        return render_template('fazer_pedido.html')
    else:
        flash("Você precisa estar logado para fazer um pedido.", "danger")
        return redirect(url_for('login'))


@app.route("/processar")
def processar():
    return render_template("processar.html")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_logged_in' in session and session['admin_logged_in']:
        if request.method == 'POST':
            action = request.form.get('action')  # Verifica se a ação é 'inserir' ou 'apagar'
            table = request.form.get('table')
            data = {key: request.form[key] for key in request.form if key not in ['table', 'action', 'confirm_password']}
            confirm_password = request.form.get('confirm_password')

            # Verifica se uma tabela foi selecionada
            if not table:
                flash("Por favor, selecione uma tabela.", "warning")
                return redirect(url_for('admin'))

            connection = None
            cursor = None

            try:
                connection = create_connection()
                if connection is None:
                    flash("Não foi possível conectar ao banco de dados.", "danger")
                    return redirect(url_for('admin'))
                
                flash("Connection feita ao banco", "info")
                
                cursor = connection.cursor()

                if action == 'inserir':
                    
                    flash("Tentando inserir dados...", "info")

                    if table == 'clientes':
                        query = """
                            INSERT INTO Clientes (id_cliente, nome, telefone)
                            VALUES (?, ?, ?, ?)
                        """
                        values = (
                            data.get('id_cliente'),
                            data.get('nome'),
                            data.get('telefone'),
                        )
                    elif table == 'produto':
                        query = """
                            INSERT INTO Produto (id_produto, nome_produto, valor_prod, categoria, tamanho, ponto_carne)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """
                        values = (
                            data.get('id_produto'),
                            data.get('nome_produto'),
                            data.get('valor_prod'),
                            data.get('categoria'),
                            data.get('tamanho'),
                            data.get('ponto_carne')
                        )
                    elif table == 'pedido':
                        query = """
                            INSERT INTO Pedido (id_compra, produto_id, cliente_id, forma_pagamento, status)
                            VALUES (?, ?, ?, ?, ?)
                        """
                        values = (
                            data.get('id_compra'),
                            data.get('produto_id'),
                            data.get('cliente_id'),
                            data.get('forma_pagamento'),
                            data.get('status')
                        )
                    elif table == 'endereco':
                        query = """
                            INSERT INTO Endereco (cep, rua, bairro, numero_casa, cliente_id)
                            VALUES (?, ?, ?, ?, ?)
                        """
                        values = (
                            data.get('cep'),
                            data.get('rua'),
                            data.get('bairro'),
                            data.get('numero_casa'),
                            data.get('cliente_id')
                        )
                    elif table == 'feedback':
                        query = """
                            INSERT INTO Feedback (client_id, produtoId, descricao_avalia)
                            VALUES (?, ?, ?)
                        """
                        values = (
                            data.get('client_id'),
                            data.get('produtoId'),
                            data.get('descricao_avalia')
                        )
                    else:
                        flash("Tabela inválida.", "warning")
                        return redirect(url_for('admin'))

                    # Verificar se todos os valores necessários estão presentes
                    if None in values:
                        flash("Todos os campos são obrigatórios para inserção.", "warning")
                        return redirect(url_for('admin'))

                    cursor.execute(query, values)
                    connection.commit()
                    flash("Registro inserido com sucesso.", "success")

                elif action == 'apagar':
                    # Apagar dados da tabela
                    confirm_password = request.form.get('confirm_password')

                    if confirm_password != 'admin':  
                        flash("Senha incorreta. Ação não permitida.", "danger")
                        return redirect(url_for('admin'))
                    
                    flash("Tentando apagar dados...", "info")


                    if table == 'clientes':
                        cursor.execute("DELETE FROM Clientes")
                    elif table == 'produto':
                        cursor.execute("DELETE FROM Produto")
                    elif table == 'pedido':
                        cursor.execute("DELETE FROM Pedido")
                    elif table == 'endereco':
                        cursor.execute("DELETE FROM Endereco")
                    elif table == 'feedback':
                        cursor.execute("DELETE FROM Feedback")  # Corrigido
                    else:
                        flash("Tabela inválida.", "warning")
                        return redirect(url_for('admin'))

                    connection.commit()
                    flash("Todos os dados da tabela foram apagados com sucesso.", "success")
                    
                else:
                    flash("Pulou a porra toda e nao leu os buttons", "info")
                    

            except sqlite3.Error as e:
                flash(f"Erro ao processar os dados: {e}", "danger")
                if connection:
                    connection.rollback()

            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()

            return redirect(url_for('admin'))

        return render_template('admin.html')  # Template de administração

    else:
        flash("Você precisa estar logado para acessar esta página.", "warning")
        return redirect(url_for('loginAD'))
    
    

def get_db_connection():
    conn = sqlite3.connect('hamburgueria.db')  # Substitua pelo nome do seu banco
    conn.row_factory = sqlite3.Row
    return conn

# Rota para deletar um item de uma tabela genérica
@app.route('/delete/<tabela>/<coluna>/<valor>', methods=['POST'])
def delete_item(tabela, coluna, valor):
    conn = get_db_connection()
    cursor = conn.cursor()

    tabelas_permitidas = {
        "Clientes": "cliente_id",
        "Produto": "id_produto",
        "Pedido": "id_compra",
        "Endereco": "client_id",
        "Feedback": "cliente_id"
    }

    if tabela not in tabelas_permitidas:
        return jsonify({'success': False, 'error': 'Tabela não permitida.'})

    coluna = tabelas_permitidas[tabela]

    try:
        if tabela == "Feedback":
            # Aqui você pode passar um valor adicional, como um id de produto, se necessário
            id_cliente, id_produto = valor.split(',')
            query = f"DELETE FROM {tabela} WHERE {coluna} = ? AND id_produto = ?"
            cursor.execute(query, (id_cliente, id_produto))
        else:
            query = f"DELETE FROM {tabela} WHERE {coluna} = ?"
            cursor.execute(query, (valor,))

        conn.commit()
        conn.close()
        return jsonify({'success': True})

    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)})



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('loginAD'))

@app.route('/dados')
def dados():
    """Consulta os dados de todas as tabelas e os envia para o template."""
    connection = create_connection()
    if connection is None:
        flash("Não foi possível conectar ao banco de dados.", "warning")
        

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Clientes")
        clientes = cursor.fetchall()

        cursor.execute("SELECT * FROM Produto")
        produtos = cursor.fetchall()

        cursor.execute("SELECT * FROM Pedido")
        pedidos = cursor.fetchall()

        cursor.execute("SELECT * FROM Endereco")
        enderecos = cursor.fetchall()

        cursor.execute("SELECT * FROM Feedback")
        feedbacks = cursor.fetchall()

        return render_template(
            'dados.html', 
            clientes=clientes, 
            produtos=produtos, 
            pedidos=pedidos, 
            enderecos=enderecos, 
            feedbacks=feedbacks
        )
    except sqlite3.Error as e:
        flash(f"Erro ao executar a consulta: {e}", "warning")
        return "Ocorreu um erro ao recuperar os dados."
    finally:
        cursor.close()
        connection.close()

@app.before_request
def initialize_sacola():
    if 'sacola' not in session:
        session['sacola'] = []

# Endpoint para adicionar itens à sacola
@app.route('/fazer_pedido', methods=['POST'])
def adicionar_sacola():
    if 'logged_in' in session and session['logged_in']:
        # Captura os dados do corpo da requisição como formulário
        produto_nome = request.form.get('produto')  # Obtém o nome do produto do formulário
        quantidade = request.form.get('quantidade', type=int)  # Define 1 como padrão se não especificado
        preco = request.form.get('preco', type=float)  # Assume que o preço é enviado junto no formulário
        cliente_id = session['user_id']  # Assumindo que o cliente está logado
        ponto = request.form.get('ponto')  # Captura o ponto, se fornecido

        # Debug: Verificando os valores recebidos
        print(f"Produto: {produto_nome}, Ponto: {ponto}")

        # Verifica se os campos necessários estão preenchidos
        if not cliente_id or not produto_nome:
            flash("Erro: Cliente ou produto não especificado.", "danger")
            return jsonify(success=False, message="Cliente ou produto não especificado."), 400

        # Verifica se o produto é um burger e se o ponto foi selecionado
        if produto_nome in ["uni_burger", "max_burger"] and not ponto:
            flash("Erro: Ponto da carne é obrigatório para burgers.", "danger")
            return jsonify(success=False, message="Ponto da carne é obrigatório para burgers."), 400

        # Exibe as informações no console (para depuração)
        print(f"Cliente ID: {cliente_id}, Produto: {produto_nome}, Quantidade: {quantidade}, Preço: {preco}, Ponto: {ponto}")

        # Cria a conexão com o banco de dados
        connection = create_connection()
        if connection is None:
            flash("Não foi possível conectar ao banco de dados.", "danger")
            return jsonify(success=False, message="Não foi possível conectar ao banco de dados."), 500

        try:
            cursor = connection.cursor()

            # Insere o item na sacola
            query = """
                INSERT INTO Sacola (cliente_id, produto_nome, quantidade, preco)
                VALUES (?, ?, ?, ?)
            """
            values = (cliente_id, produto_nome, quantidade, preco)

            cursor.execute(query, values)
            connection.commit()
            flash("Item adicionado à sacola com sucesso.", "success")

        except Exception as e:
            connection.rollback()
            flash(f"Erro ao adicionar item à sacola: {e}", "danger")
            return jsonify(success=False, message=str(e)), 500

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('fazer_pedido'))  # Retorna sucesso se o item foi adicionado
    else:
        flash("Você precisa estar logado para adicionar itens à sacola.", "danger")
        return redirect(url_for('loginCL'))  # Retorna erro de não autorizado







@app.route('/sacola', methods=['GET'])
def sacola():
    if 'logged_in' in session and session['logged_in']:
        connection = create_connection()
        if connection is None:
            flash("Não foi possível conectar ao banco de dados.", "danger")
            return redirect(url_for('shop'))

        try:
            cursor = connection.cursor()
            query = """
                SELECT produto_nome, quantidade, preco
                FROM Sacola
                WHERE cliente_id = ?
            """
            cursor.execute(query, (session['user_id'],))
            sacola = cursor.fetchall()
            total = sum(item[1] * item[2] for item in sacola)  # Corrigido para usar os índices corretos
            flash("Itens da sacola recuperados com sucesso.")

        except Exception as e:
            flash(f"Erro ao recuperar itens da sacola: {e}", "danger")
            sacola = []
            total = 0.0

        finally:
            cursor.close()
            connection.close()

        return render_template('sacola.html', sacola=sacola, total=total)
    else:
        flash("Por favor, faça login para ver sua sacola.", "danger")
        return redirect(url_for('login'))

    
    
@app.route('/remover_item/<int:item_index>', methods=['POST'])
def remover_item(item_index):
    connection = create_connection()
    if connection is None:
        return jsonify({'success': False, 'error': 'Erro de conexão.'})

    try:
        cursor = connection.cursor()
        # Primeiro, obtenha o produto que será removido
        cursor.execute("""
            SELECT produto_nome FROM Sacola 
            WHERE cliente_id = ? LIMIT 1 OFFSET ?""", 
            (session['user_id'], item_index))
        produto = cursor.fetchone()
        
        if produto:
            # Remove o item da tabela
            cursor.execute("DELETE FROM Sacola WHERE cliente_id = ? AND produto_nome = ?", 
                           (session['user_id'], produto[0]))
            connection.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Item não encontrado.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

    finally:
        cursor.close()
        connection.close()





    


@app.route('/cancelar_pedido', methods=['POST'])
def cancelar_pedido():
    # Limpar os itens da sacola
    session.pop('sacola', None)  # Remove a sacola da sessão, se estiver armazenada assim
    flash('Seu pedido foi cancelado com sucesso.', 'success')
    return redirect(url_for('sacola'))  # Redireciona para a página da sacola



@app.route('/register', methods=['POST'])
def register():
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')

    if not nome or not telefone:
        flash("Nome e telefone são obrigatórios.", "warning")
        return redirect(url_for('loginCL'))

    connection = None
    cursor = None

    try:
        connection = create_connection()
        if connection is None:
            flash("Não foi possível conectar ao banco de dados.", "danger")
            return redirect(url_for('loginCL'))

        cursor = connection.cursor()

        # Verificando se o telefone já está cadastrado
        cursor.execute("SELECT * FROM Clientes WHERE telefone = ?", (telefone,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Este número de telefone já está cadastrado.", "warning")
            return redirect(url_for('loginCL'))

        # Obtendo o próximo ID disponível
        cursor.execute("SELECT MAX(id_cliente) AS max_id FROM Clientes")
        result = cursor.fetchone()
        max_id = result[0] if result and result[0] is not None else 0
        next_id = max_id + 1

        # Inserindo o novo usuário com o próximo ID
        cursor.execute("""
                       INSERT INTO Clientes (id_cliente, nome, telefone) 
                       VALUES (?, ?, ?)
                       """, (next_id, nome, telefone))
        connection.commit()

        # Realiza login automático após o cadastro
        session['logged_in'] = True
        session['user_id'] = next_id
        session['user_name'] = nome
        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for('loginCL'))

    except sqlite3.Error as e:
        flash(f"Erro ao cadastrar: {str(e)}", "danger")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('loginCL'))







@app.route('/login', methods=['POST'])
def login():
    telefone = request.form.get('telefone')
    
    connection = create_connection()
    if connection is None:
        flash("Não foi possível conectar ao banco de dados.", "danger")
        return redirect(url_for('loginCL'))

    try:
        cursor = connection.cursor()

        # Usando ? ao invés de %s para SQLite
        cursor.execute("SELECT * FROM Clientes WHERE telefone = ?", (telefone,))
        user = cursor.fetchone()

        if user:
            # Supondo que os índices corretos de user[0] e user[1] correspondam ao id_cliente e nome
            session['client_logged_in'] = True
            session['user_id'] = user[0]  # id_cliente
            session['user_name'] = user[1]  # nome
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('home'))
        else:
            flash("Número de telefone não encontrado. Por favor, cadastre-se.", "warning")
            return redirect(url_for('loginCL'))
        
    except sqlite3.Error as e:
        flash(f"Erro ao fazer login: {e}", "danger")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('loginCL'))



@app.route('/logoutCL')
def logoutCL():
    session.pop('client_logged_in', None)
    session.pop('admin_logged_in', None)
    session.pop('user_name', None)
    session.pop('admin_username', None)
    flash('Você saiu com sucesso!', 'success')
    return redirect(url_for('loginCL'))


@app.route('/delete/<tabela>/<coluna>/<valor>', methods=['POST'])
def delete(tabela, coluna, valor):
    """Deleta um item da tabela especificada."""
    connection = create_connection()
    if connection is None:
        flash("Não foi possível conectar ao banco de dados.", "warning")
        
    
    try:
        cursor = connection.cursor()
        # Crie a query de exclusão dinamicamente
        query = f"DELETE FROM {tabela} WHERE {coluna} = ?"
        cursor.execute(query, (valor,))
        connection.commit()

        # Redireciona de volta para a página de dados
        flash(f"Valor: {valor} foi apagado da Tabela:{tabela}", "warning")
        return redirect(url_for('dados'))
        
    
    except sqlite3.Error as e:
        flash(f"Erro ao executar a exclusão: {e}", "warning")
        
    
    finally:
        cursor.close()
        connection.close()
        
        
        
        


@app.route('/pagamento')
def pagamento():
    return render_template('pagamento.html')
@app.route('/endereco')
def endereco():
    return render_template('endereco.html')




@app.route('/confirmacao', methods=['GET', 'POST'])
def confirmacao():
    """Confirmação da compra e exclusão de todos os itens da sacola."""
    connection = create_connection()
    if connection is None:
        flash("Não foi possível conectar ao banco de dados.", "warning")
        return redirect(url_for('sacola'))
    
    try:
        cursor = connection.cursor()
        # Cria a query para deletar todos os itens da tabela sacola
        query = "DELETE FROM sacola"
        cursor.execute(query)
        connection.commit()
        
        flash("Todos os itens da sacola foram apagados com sucesso.", "success")
    
    except sqlite3.Error as e:
        connection.rollback()
        flash(f"Erro ao excluir itens da sacola: {e}", "danger")
    
    finally:
        cursor.close()
        connection.close()

    # Renderiza a página de confirmação
    return render_template('home.html')

        





if __name__ == '__main__':
    app.run(debug=True)
