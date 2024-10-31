import psycopg2
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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

class Relatorio:
    """Classe para gerar relatórios de serviços mensais."""    
    def __init__(self):
        pass

    def obter_servicos_por_mes(self):
        """Obter a contagem de serviços por mês da view."""    
        connection = conectar()
        if connection is None:
            return []

        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM quantidade_servicos_por_mes;")
                    return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter serviços por mês: {e}")
            return []
        finally:
            connection.close()

    def obter_servicos_por_clinica(self):
        """Obter a contagem de serviços por clínica da view."""    
        connection = conectar()
        if connection is None:
            return []

        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(""" 
                        SELECT l.nome AS clinica, COUNT(p.id) AS quantidade
                        FROM laboratorios l
                        LEFT JOIN pedidos p ON l.id = p.laboratorio_id
                        GROUP BY l.nome;
                    """)
                    return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter serviços por clínica: {e}")
            return []
        finally:
            connection.close()

    def obter_servicos_por_mes_clinica(self, clinica):
        """Obter a contagem de serviços por mês para uma clínica específica."""
        connection = conectar()
        if connection is None:
            return []

        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT EXTRACT(YEAR FROM p.data_saida) AS ano,
                               EXTRACT(MONTH FROM p.data_saida) AS mes,
                               COUNT(p.id) AS quantidade
                        FROM pedidos p
                        JOIN laboratorios l ON p.laboratorio_id = l.id
                        WHERE l.nome = %s
                        GROUP BY ano, mes
                        ORDER BY ano, mes;
                    """, (clinica,))
                    return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter serviços por mês para a clínica {clinica}: {e}")
            return []
        finally:
            connection.close()

def formatar_mes(mes):
    """Formata o mês no formato 'Mês (Ano)'."""
    mes_str = mes.strftime('%B')  # Nome do mês completo
    ano = mes.strftime('%Y')       # Ano
    return f"{mes_str} ({ano})"

# Estrutura da aplicação Streamlit
st.title("Relatório de Serviços")

col1, col2 = st.columns(2)

# Obter os dados mensais
relatorio = Relatorio()
dados_mensais = relatorio.obter_servicos_por_mes()

with col1:
    # Gráfico de Serviços por Mês
    if dados_mensais:
        meses, quantidades = zip(*dados_mensais)  
        meses = [mes for mes in meses if mes is not None]
        quantidades = [quantidade for i, quantidade in enumerate(quantidades) if i < len(meses)]

        if len(meses) != len(quantidades):
            st.write("Erro: A quantidade de meses e quantidades não coincide.")
        else:
            meses_formatados = [formatar_mes(mes) for mes in meses]  # Formatar os meses

            # Criar o gráfico de pizza com Plotly e estilizar
            df_meses = pd.DataFrame({'Meses': meses_formatados, 'Quantidade': quantidades})
            
            # Criar o gráfico de pizza
            fig_meses = px.pie(
                df_meses,
                values='Quantidade',
                names='Meses',
                title='Quantidade Total de Serviços por Mês',
                hole=0.3,
                color_discrete_sequence=px.colors.sequential.RdBu  # Altera a paleta de cores
            )

            # Customização adicional
            fig_meses.update_traces(textposition='inside', textinfo='percent+label')  # Mostra percentagem e rótulo
            fig_meses.update_layout(margin=dict(t=0, b=0, l=0, r=0))  # Remove margens
            st.plotly_chart(fig_meses)
    else:
        st.write("Nenhum serviço encontrado.")

with col2:
    # Gráfico de Serviços por Clínica
    dados_clinica = relatorio.obter_servicos_por_clinica()
    if dados_clinica:
        clinicas, quantidades_clinica = zip(*dados_clinica)
        clinicas = [clinica for clinica in clinicas if clinica is not None]

        if len(clinicas) != len(quantidades_clinica):
            st.write("Erro: A quantidade de clínicas e quantidades não coincide.")
        else:
            # Criar o gráfico de serviços por clínica e estilizar
            df_clinica = pd.DataFrame({'Clínica': clinicas, 'Quantidade': quantidades_clinica})
            fig_clinica = px.bar(
                df_clinica,
                x='Clínica',
                y='Quantidade',
                title='Quantidade Total de Serviços por Clínica',
                color='Quantidade',  # Define cor pela quantidade
                color_continuous_scale=px.colors.sequential.RdBu  # Altera a paleta de cores
            )
            
            # Customização adicional
            fig_clinica.update_traces(texttemplate='%{y}', textposition='outside')  # Mostra valores fora das barras
            fig_clinica.update_layout(margin=dict(t=0, b=0, l=0, r=0))  # Remove margens
            st.plotly_chart(fig_clinica)
    else:
        st.write("Nenhum serviço encontrado para clínicas.")

# Gráfico de Crescimento/Diminuição de Serviços para Clínica Selecionada
if clinicas:
    clinica_selecionada = st.selectbox("Selecione uma clínica para visualizar o crescimento de serviços:", clinicas)
    
    # Obter os dados de serviços por mês para a clínica selecionada
    dados_clinica_selecionada = relatorio.obter_servicos_por_mes_clinica(clinica_selecionada)
    
    if dados_clinica_selecionada:
        # Filtrando apenas os dados válidos
        dados_validos = [(ano, mes, quantidade) for ano, mes, quantidade in dados_clinica_selecionada if ano is not None and mes is not None and quantidade is not None]
        
        if dados_validos:
            anos, meses, quantidades = zip(*dados_validos)
            meses = [datetime(int(ano), int(mes), 1) for ano, mes in zip(anos, meses)]  # Converte para datetime

            # Criar o gráfico de crescimento/diminuição e estilizar
            df_crescimento = pd.DataFrame({'Meses': meses, 'Quantidade': quantidades})
            fig_crescimento = px.line(
                df_crescimento,
                x='Meses',
                y='Quantidade',
                title=f'Crescimento de Serviços - {clinica_selecionada}',
                markers=True,  # Adiciona marcadores aos pontos da linha
                color_discrete_sequence=px.colors.sequential.RdBu  # Altera a paleta de cores
            )

            # Customização adicional
            fig_crescimento.update_layout(margin=dict(t=0, b=0, l=0, r=0))  # Remove margens
            st.plotly_chart(fig_crescimento)
        else:
            st.write(f"Nenhum serviço encontrado para a clínica {clinica_selecionada} com dados válidos.")
    else:
        st.write(f"Nenhum serviço encontrado para a clínica {clinica_selecionada}.")
