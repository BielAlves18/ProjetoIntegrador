import streamlit as st
import pandas as pd
from classes import Pedido
from datetime import date

st.set_page_config(page_title="Buscar Pedidos", layout="wide")
st.title("Buscar Pedidos")

def aplicar_estilos():
    st.markdown(
        """
        <style>
        .dataframe th, .dataframe td {
            font-size: 30px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Aplicar estilos
aplicar_estilos()

# Instância da classe Pedido
pedido = Pedido()

# Seleção de critério de busca
opcao_busca = st.selectbox("Escolha o critério de busca:", ["Nome", "Laboratório", "Data de Envio", "Data de Entrega"])

# Função para mostrar resultados em formato DataFrame
def mostrar_resultados(resultados):
    if resultados:
        df_resultados = pd.DataFrame(resultados,
                                      columns=["ID", "Cliente", "Data de Envio", "Nome Dr(a)", "Quantidade", 
                                               "Montagem a Fazer", "Data de Saída", "Observação", 
                                               "Status", "Laboratório"])
        st.dataframe(df_resultados, use_container_width=True)
    else:
        st.write("Nenhum pedido encontrado.")

# Busca por nome do cliente
if opcao_busca == "Nome":
    nome_busca = st.text_input("Digite o nome do cliente:")
    if st.button("Buscar por Nome"):
        if nome_busca.strip():
            resultados = pedido.buscar_pedido_por_nome(nome_busca)
            mostrar_resultados(resultados)
        else:
            st.warning("Por favor, insira um nome válido.")

# Busca por laboratório
elif opcao_busca == "Laboratório":
    laboratorios = pedido.obter_laboratorios_disponiveis()
    if laboratorios:
        laboratorio_busca = st.selectbox("Escolha o laboratório:", laboratorios)
        if st.button("Buscar por Laboratório"):
            resultados = pedido.buscar_pedido_por_laboratorio(laboratorio_busca)
            mostrar_resultados(resultados)
    else:
        st.write("Nenhum laboratório disponível no banco de dados.")

# Busca por data de envio
elif opcao_busca == "Data de Envio":
    data_envio = st.date_input("Selecione a data de envio:", value=date.today())
    if st.button("Buscar por Data de Envio"):
        resultados = pedido.buscar_pedido_por_data_envio(data_envio)
        mostrar_resultados(resultados)

# Busca por data de entrega
elif opcao_busca == "Data de Entrega":
    data_entrega = st.date_input("Selecione a data de entrega:", value=date.today())
    if st.button("Buscar por Data de Entrega"):
        resultados = pedido.buscar_pedido_por_data_entrega(data_entrega)
        mostrar_resultados(resultados)
