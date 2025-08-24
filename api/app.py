from flask import Flask, request, jsonify
import os
import mysql.connector
import time
from flask_cors import CORS # Adicione esta linha

app = Flask(__name__)
CORS(app) # Adicione esta linha aqui

# Configurações do banco de dados lidas das variáveis de ambiente
DB_HOST = os.getenv('DB_HOST', 'db')
DB_DATABASE = os.getenv('MYSQL_DATABASE', 'api_db')
DB_USER = os.getenv('MYSQL_USER', 'api_user')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', 'api')

# Tenta conectar ao banco de dados
def get_db_connection():
    max_retries = 10
    retry_delay = 5  # segundos

    for i in range(max_retries):
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                database=DB_DATABASE,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Conexão com o banco de dados bem-sucedida!")
            return connection
        except mysql.connector.Error as err:
            print(f"Tentativa {i+1} de {max_retries}: Erro ao conectar com o banco de dados: {err}")
            time.sleep(retry_delay)
    return None

# Nova rota para criar a tabela de usuários
@app.route('/create_table')
def create_table():
    conn = get_db_connection()
    if conn and conn.is_connected():
        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL
        );
        """
        try:
            cursor.execute(create_table_query)
            conn.commit()
            return "Tabela 'users' criada ou já existente com sucesso!"
        except mysql.connector.Error as err:
            return f"Erro ao criar tabela: {err}", 500
        finally:
            cursor.close()
            conn.close()
    return "Erro ao conectar com o banco de dados.", 500

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    if conn and conn.is_connected():
        cursor = conn.cursor(dictionary=True) # Usamos dictionary=True para obter resultados como dicionários
        select_query = "SELECT first_name, last_name FROM users;"
        try:
            cursor.execute(select_query)
            users = cursor.fetchall()
            return jsonify(users), 200
        except mysql.connector.Error as err:
            return jsonify({"message": f"Erro ao buscar usuários: {err}"}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({"message": "Erro ao conectar com o banco de dados."}), 500

# Rota para receber os dados do formulário e salvar no banco
@app.route('/save', methods=['POST'])
def save_user():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if not first_name or not last_name:
        return jsonify({"message": "Nome e sobrenome são obrigatórios."}), 400

    conn = get_db_connection()
    if conn and conn.is_connected():
        cursor = conn.cursor()
        insert_query = "INSERT INTO users (first_name, last_name) VALUES (%s, %s);"
        user_data = (first_name, last_name)
        try:
            cursor.execute(insert_query, user_data)
            conn.commit()
            return jsonify({"message": "Dados salvos com sucesso!"}), 201
        except mysql.connector.Error as err:
            return jsonify({"message": f"Erro ao salvar dados: {err}"}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({"message": "Erro ao conectar com o banco de dados."}), 500

# Rota principal
@app.route('/')
def home():
    return "Olá do container da API!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)