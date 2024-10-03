import psycopg2
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def conectar():
    """Função para conectar ao banco de dados PostgreSQL."""
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="Cliente",  # Nome do banco de dados
            user="postgres",     # Nome do usuário
            password="12181978"  # Senha do banco
        )
        return connection
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

class Paciente:
    def __init__(self, nome, laboratorio, doutor, data_entrada, data_saida, fazer, observacao):
        self.__nome = nome
        self.__laboratorio = laboratorio
        self.__doutor = doutor
        self.__data_entrada = data_entrada
        self.__data_saida = data_saida
        self.__fazer = fazer
        self.__observacao = observacao

    def dados_paciente(self):
        doutor_info = self.__doutor if self.__doutor else "O nome do dr(a) não foi informado"
        observacao_info = self.__observacao if self.__observacao else "N/A"
        
        return (f"Nome: {self.__nome} \n"
                f"Laboratório: {self.__laboratorio} \n"
                f"Nome Dr(a): {doutor_info} \n"
                f"Data de Entrada: {self.__data_entrada} \n"
                f"Data de Saída: {self.__data_saida} \n"
                f"O que é pra fazer: {self.__fazer} \n"
                f"Observação: {observacao_info} \n")

    def inserir_paciente(self):
        """Método para inserir o paciente no banco de dados PostgreSQL."""
        connection = conectar()
        if connection is None:
            return "Erro ao conectar ao banco de dados."

        try:
            with connection:
                with connection.cursor() as cursor:
                    insert_query = """
                        INSERT INTO pedidos (cliente, data_envio, nome_dr, quantidade, montagem_a_fazer, observacao, data_saida, status, laboratorio_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                        (SELECT id FROM laboratorios WHERE nome = %s));
                    """
                    cursor.execute(insert_query, (
                        self.__nome,
                        self.__data_entrada,
                        self.__doutor,
                        1,  # Considerar substituir por um valor dinâmico
                        self.__fazer,
                        self.__observacao,
                        self.__data_saida,
                        'Em andamento',
                        self.__laboratorio
                    ))
            return "Paciente inserido com sucesso!"
        except Exception as e:
            return f"Erro ao inserir paciente: {e}"
        finally:
            connection.close()  # Garante que a conexão será fechada

class Pedido:
    """Classe para gerenciar pedidos do banco de dados."""
    
    def __init__(self):
        pass

    def obter_laboratorios_disponiveis(self):
        """Obter a lista de laboratórios disponíveis.""" 
        connection = conectar()
        if connection is None:
            return []

        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT nome FROM laboratorios;")
                    resultados = cursor.fetchall()
                    return [laboratorio[0] for laboratorio in resultados]  # Retorna apenas os nomes
        except Exception as e:
            print(f"Erro ao obter laboratórios: {e}")
            return []
        finally:
            connection.close()

    def buscar_pedido_por_nome(self, nome):
        """Buscar pedidos pelo nome do cliente.""" 
        connection = conectar()
        if connection is None:
            return []

        try:
            with connection:
                with connection.cursor() as cursor:
                    search_query = """
                        SELECT cliente, data_envio, nome_dr, quantidade, montagem_a_fazer, data_saida, observacao, status 
                        FROM pedidos 
                        WHERE cliente ILIKE %s;
                    """
                    cursor.execute(search_query, (f"%{nome}%",))
                    return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar pedidos: {e}")
            return []
        finally:
            connection.close()

    def buscar_pedido_por_laboratorio(self, laboratorio):
        """Buscar todos os pedidos de um determinado laboratório.""" 
        connection = conectar()
        if connection is None:
            return []

        try:
            with connection:
                with connection.cursor() as cursor:
                    search_query = """
                        SELECT p.id, p.cliente, p.data_envio, p.nome_dr, p.quantidade, 
                               p.montagem_a_fazer, p.data_saida, p.observacao, p.status, l.nome
                        FROM pedidos p
                        JOIN laboratorios l ON p.laboratorio_id = l.id
                        WHERE l.nome ILIKE %s;
                    """
                    cursor.execute(search_query, (laboratorio,))
                    return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar pedidos: {e}")
            return []
        finally:
            connection.close()

    def buscar_pedido_por_data_envio(self, data_envio):
        """Buscar pedidos pela data de envio.""" 
        connection = conectar()
        if connection is None:
            return []

        try:
            with connection:
                with connection.cursor() as cursor:
                    search_query = """
                        SELECT p.id, p.cliente, p.data_envio, p.nome_dr,
                               p.quantidade, p.montagem_a_fazer, p.data_saida,
                               p.observacao, p.status, l.nome
                        FROM pedidos p
                        JOIN laboratorios l ON p.laboratorio_id = l.id
                        WHERE p.data_envio = %s;
                    """
                    cursor.execute(search_query, (data_envio,))
                    return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar pedidos: {e}")
            return []
        finally:
            connection.close()

    def buscar_pedido_por_data_entrega(self, data_entrega):
        """Buscar pedidos pela data de entrega.""" 
        connection = conectar()
        if connection is None:
            return []

        try:
            with connection:
                with connection.cursor() as cursor:
                    search_query = """
                        SELECT p.id, p.cliente, p.data_envio, p.nome_dr,
                               p.quantidade, p.montagem_a_fazer, p.data_saida,
                               p.observacao, p.status, l.nome
                        FROM pedidos p
                        JOIN laboratorios l ON p.laboratorio_id = l.id
                        WHERE p.data_saida = %s;
                    """
                    cursor.execute(search_query, (data_entrega,))
                    return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar pedidos: {e}")
            return []
        finally:
            connection.close()

def mostrar_resultados(resultados):
    """Mostrar resultados no Streamlit.""" 
    if resultados:
        colunas = ["ID", "Cliente", "Data de Envio", "Nome Dr(a)", "Quantidade", 
                   "Montagem a Fazer", "Data de Saída", "Observação", "Status", "Laboratório"]
        
        # Ajusta dinamicamente as colunas do DataFrame
        df_resultados = pd.DataFrame(resultados, columns=colunas[:len(resultados[0])])  
        st.dataframe(df_resultados, use_container_width=True)
    else:
        st.write("Nenhum pedido encontrado.")

class AtualizarPedido:
    """Classe para gerenciar a atualização de pedidos do banco de dados."""
    
    def __init__(self):
        pass

    def obter_pedidos_do_mes(self):
        """Obter todos os pedidos do mês atual."""
        connection = conectar()
        if connection is None:
            return []

        try:
            with connection:
                with connection.cursor() as cursor:
                    primeiro_dia = datetime.now().replace(day=1)
                    query = """
                        SELECT p.id, p.cliente, p.data_envio, p.nome_dr, p.quantidade, 
                               p.montagem_a_fazer, p.data_saida, p.observacao, 
                               p.status, l.nome
                        FROM pedidos p
                        JOIN laboratorios l ON p.laboratorio_id = l.id
                        WHERE p.data_envio >= %s;
                    """
                    cursor.execute(query, (primeiro_dia,))
                    return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter pedidos do mês: {e}")
            return []
        finally:
            connection.close()

    def atualizar_status_pedido(self, pedido_id, novo_status):
        """Atualizar o status de um pedido."""
        connection = conectar()
        if connection is None:
            return "Erro ao conectar ao banco de dados."

        try:
            with connection:
                with connection.cursor() as cursor:
                    update_query = """
                        UPDATE pedidos
                        SET status = %s
                        WHERE id = %s;
                    """
                    cursor.execute(update_query, (novo_status, pedido_id))
            return "Status do pedido atualizado com sucesso!"
        except Exception as e:
            return f"Erro ao atualizar status do pedido: {e}"
        finally:
            connection.close()

    def obter_pedidos_em_andamento(self, mes_num):
        """Obter todos os pedidos que estão em andamento para o mês especificado."""
        connection = conectar() 
        if connection is None:
            return []

        try:
            with connection:
                with connection.cursor() as cursor:
                    primeiro_dia = datetime(datetime.now().year, mes_num, 1)
                    ultimo_dia = datetime(datetime.now().year, mes_num + 1, 1) - timedelta(days=1)
                    
                    search_query = """
                        SELECT p.id, p.cliente, p.data_envio, p.nome_dr, p.quantidade, 
                               p.montagem_a_fazer, p.data_saida, p.observacao, p.status, l.nome
                        FROM pedidos p
                        JOIN laboratorios l ON p.laboratorio_id = l.id
                        WHERE p.status = 'Em andamento' AND p.data_envio BETWEEN %s AND %s;
                    """
                    cursor.execute(search_query, (primeiro_dia, ultimo_dia))
                    return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar pedidos em andamento: {e}")
            return []
        finally:
            connection.close()