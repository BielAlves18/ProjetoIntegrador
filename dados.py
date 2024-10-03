import psycopg2
import pandas as pd

# Função de conexão ao banco
def conectar():
    return psycopg2.connect(
        host="localhost",
        database="Cliente",
        user="postgres",
        password="12181978"
    )

# Carregar a planilha de entrada
df_entrada = pd.read_excel("SpImplantes(Definitivo).xlsx", sheet_name='Planilha de entrada')

# Corrigir valores nulos na coluna 'Montagem a fazer' sem usar inplace=True
df_entrada['Montagem a fazer'] = df_entrada['Montagem a fazer'].fillna('Não especificado')

# Inserir os dados no banco
def inserir_dados_banco(df):
    connection = conectar()
    cursor = connection.cursor()
    
    for _, row in df.iterrows():
        # Prepara os dados, verificando se estão preenchidos
        paciente = row['Paciente']
        doutor = row['Dr.(a)'] if pd.notna(row['Dr.(a)']) else None
        data_entrada = row['Data de entrada'] if pd.notna(row['Data de entrada']) else None
        quantidade = int(row['Qntd']) if pd.notna(row['Qntd']) else 1
        montagem = row['Montagem a fazer'] if pd.notna(row['Montagem a fazer']) else None
        observacao = row['Observação'] if pd.notna(row['Observação']) else None
        data_saida = row['Data de saída'] if pd.notna(row['Data de saída']) else None
        numero_protocolo = row['NP'] if pd.notna(row['NP']) else None
        status = row['Status'] if pd.notna(row['Status']) else 'Em andamento'
        laboratorio = "SpImplantes"  # Nome fixo para laboratório, como especificado

        # Query de inserção com o ID do laboratório sendo buscado pelo nome
        insert_query = """
        INSERT INTO pedidos (cliente, data_envio, nome_dr, quantidade, montagem_a_fazer, observacao, data_saida, status, laboratorio_id, numero_protocolo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, (SELECT id FROM laboratorios WHERE nome = %s), %s);
        """
        cursor.execute(insert_query, (
            paciente, data_entrada, doutor, quantidade, montagem, observacao, data_saida, status, laboratorio, numero_protocolo
        ))
    
    # Confirmar as alterações no banco de dados
    connection.commit()
    cursor.close()
    connection.close()

# Inserir os dados da planilha no banco
inserir_dados_banco(df_entrada)
