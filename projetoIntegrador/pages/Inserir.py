import streamlit as st
from datetime import date
from classes import Paciente, Pedido

st.set_page_config(page_title="Página de inserção de dados", layout="wide")
st.title("Página de inserção de dados")

pedido = Pedido()

nome = st.text_input("Digite o nome do paciente:")
tab1, tab2 = st.columns(2)
with tab1:
    # Aqui você faz a consulta para obter os laboratórios disponíveis
    laboratorios = pedido.obter_laboratorios_disponiveis()
    laboratorio = st.selectbox("Laboratório:", laboratorios)
    doutor = st.text_input("Coloque o nome do doutor/doutora, caso tiver:")
    fazer = st.text_area("O que fazer:")
with tab2:
    data_entrada = st.date_input("Data de entrada:", value=date.today())
    data_saida = st.date_input("Data de saída:", value=date.today())
    observacao = st.text_area("Observação:")

processar = st.button("Processar")

if processar:
    # Verificando se a data de saída é anterior à data atual
    if data_saida < date.today() or data_entrada < date.today():
        st.error("Erro: A data de saída não pode ser anterior à data atual.")
    elif nome and laboratorio and data_entrada and data_saida and fazer:
        paciente = Paciente(nome, laboratorio, doutor, data_entrada, data_saida, fazer, observacao)
        resultado = paciente.inserir_paciente()
        st.success(resultado)
    else:
        st.error("Existem campos obrigatórios que não foram inseridos.")
