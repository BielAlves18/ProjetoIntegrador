import streamlit as st
from classes import AtualizarPedido
import pandas as pd
from datetime import datetime


# Configuração da página
st.set_page_config(page_title="Atualizar Pedidos", layout="centered")
st.title("Atualizar Pedidos")

atualizar_pedido = AtualizarPedido()

# Criação das abas
tab1, tab2 = st.tabs(["Atualizar Pedido Individual", "Atualizar Pedidos Múltiplos"])

# Aba 1: Atualizar Pedido Individual
with tab1:
    st.header("Atualizar Pedido Individual")
    
    # Obtém pedidos do mês
    pedidos = atualizar_pedido.obter_pedidos_do_mes()

    if pedidos:
        # Cria um DataFrame para visualização
        df_pedidos = pd.DataFrame(pedidos, columns=["ID", "Cliente", "Data de Envio", "Nome Dr(a)", 
                                                    "Quantidade", "Montagem a Fazer", "Data de Saída", 
                                                    "Observação", "Status", "Laboratório"])
        
        st.dataframe(df_pedidos, use_container_width=True)

        # Exibe os pedidos em formato de lista
        pedido_id = st.selectbox("Selecione o ID do pedido para atualizar:", df_pedidos['ID'], key="selectbox_individual")

        # Mostra informações detalhadas do pedido selecionado
        if pedido_id:
            pedido_selecionado = df_pedidos[df_pedidos['ID'] == pedido_id]
            st.write("Detalhes do Pedido Selecionado:")
            st.write(pedido_selecionado)

        # Selecione o novo status
        novo_status = st.selectbox("Novo Status:", ["Em andamento", "Entregue"], key="status_individual")
        
        if st.button("Atualizar Status"):
            resultado = atualizar_pedido.atualizar_status_pedido(pedido_id, novo_status)
            st.success(resultado)

        # Atualização dos dados do cliente
        novo_cliente = st.text_input("Novo nome do cliente:")
        nova_observacao = st.text_input("Nova observação:")
        
        if st.button("Atualizar Dados do Cliente"):
            resultado = atualizar_pedido.atualizar_dados_cliente(pedido_id, novo_cliente, nova_observacao)
            st.success(resultado)
    else:
        st.write("Nenhum pedido encontrado para este mês.")

# Aba 2: Atualizar Pedidos Múltiplos
with tab2:
    st.header("Atualizar Pedidos Múltiplos")

    # Seletor de mês
    mes_selecionado = st.selectbox("Selecione o Mês:", 
                                    [f"{m:02d} - {datetime(2023, m, 1).strftime('%B')}" for m in range(1, 13)])
    
    mes_num = int(mes_selecionado.split()[0])  # Extrai o número do mês
    pedidos_em_andamento = atualizar_pedido.obter_pedidos_em_andamento(mes_num)

    if pedidos_em_andamento:
        # Exibir checkboxes para cada pedido em andamento
        pedido_ids_selecionados = st.multiselect(
            "Selecione os pedidos para atualizar:",
            options=[f"ID: {pedido[0]} - Cliente: {pedido[1]} - Status: {pedido[8]}" for pedido in pedidos_em_andamento],
            format_func=lambda x: x  # Formato de exibição
        )
        
        # Novo status
        novo_status = st.radio("Novo Status:", ["Em andamento", "Entregue"])

        # Botão para atualizar status com chave única
        if st.button("Atualizar Status", key="atualizar_status"):
            for pedido in pedido_ids_selecionados:
                pedido_id = int(pedido.split()[1])  # Extrai o ID do pedido
                resultado = atualizar_pedido.atualizar_status_pedido(pedido_id, novo_status)
                st.success(resultado)
    else:
        st.warning("Nenhum pedido encontrado para o mês selecionado.")