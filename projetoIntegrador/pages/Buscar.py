import psycopg2
import streamlit as st
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

st.set_page_config(page_title="Atualizar Pedidos", layout="wide")

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

def mostrar_resultados(resultados, tipo_consulta):
    """Mostrar resultados no Streamlit com AgGrid."""
    colunas = []  # Inicializa a variável colunas

    if resultados:
        if tipo_consulta == 'nome':
            colunas = ["Cliente", "Data de Envio", "Nome Dr(a)", "Quantidade", 
                       "Montagem a Fazer", "Data de Saída", "Observação", "Status"]  # 8 colunas
        elif tipo_consulta == 'laboratorio':
            colunas = ["ID", "Cliente", "Data de Envio", "Nome Dr(a)", "Quantidade", 
                       "Montagem a Fazer", "Data de Saída", "Observação", "Status", "Laboratório"]  # 10 colunas
        elif tipo_consulta == 'data_envio':
            colunas = ["ID", "Cliente", "Data de Envio", "Nome Dr(a)", "Quantidade", 
                       "Montagem a Fazer", "Data de Saída", "Observação", "Status", "Laboratório"]  # Ajuste se necessário
        elif tipo_consulta == 'data_saida':
            colunas = ["ID", "Cliente", "Data de Envio", "Nome Dr(a)", "Quantidade", 
                       "Montagem a Fazer", "Data de Saída", "Observação", "Status", "Laboratório"]  # Ajuste se necessário

        # Cria o DataFrame
        df_resultados = pd.DataFrame(resultados, columns=colunas)  
        
        # Configura o AgGrid
        gb = GridOptionsBuilder.from_dataframe(df_resultados)
        gb.configure_pagination(enabled=True)
        gb.configure_side_bar()
        gb.configure_default_column(editable=True, groupable=True)
        grid_options = gb.build()
        
        AgGrid(df_resultados, gridOptions=grid_options, height=400, fit_columns_on_grid_load=True)
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
            return f"Erro ao atualizar o status do pedido: {e}"
        finally:
            connection.close()  # Garante que a conexão será fechada


# Estrutura da aplicação Streamlit
st.title("Sistema de Gestão de Pedidos")
pedido_manager = Pedido()

# Seção de busca
st.subheader("Buscar Pedidos")
opcao_busca = st.selectbox("Escolha o método de busca:", 
                            ["Por Nome", "Por Laboratório", "Por Data de Envio", "Por Data de Saída"])

if opcao_busca == "Por Nome":
    nome_cliente = st.text_input("Digite o nome do cliente:")
    if st.button("Buscar"):
        resultados = pedido_manager.buscar_pedido_por_nome(nome_cliente)
        mostrar_resultados(resultados, tipo_consulta='nome')  # Passa o tipo de consulta

elif opcao_busca == "Por Laboratório":
    laboratorio = st.selectbox("Escolha o laboratório:", pedido_manager.obter_laboratorios_disponiveis())
    if st.button("Buscar"):
        resultados = pedido_manager.buscar_pedido_por_laboratorio(laboratorio)
        mostrar_resultados(resultados, tipo_consulta='laboratorio')  # Passa o tipo de consulta

elif opcao_busca == "Por Data de Envio":
    data_envio = st.date_input("Escolha a data de envio:")
    if st.button("Buscar"):
        resultados = pedido_manager.buscar_pedido_por_data_envio(data_envio)
        mostrar_resultados(resultados, tipo_consulta='data_envio')  # Ajuste para data_envio se necessário

elif opcao_busca == "Por Data de Saída":
    data_saida = st.date_input("Escolha a data de saída:")
    if st.button("Buscar"):
        resultados = pedido_manager.buscar_pedido_por_data_entrega(data_saida)
        mostrar_resultados(resultados, tipo_consulta='data_saida')  # Ajuste para data_saida se necessário
