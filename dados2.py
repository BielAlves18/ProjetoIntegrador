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

# Carregar a planilha de entrada (CSV) com tratamento para erros
try:
    df_entrada = pd.read_csv("Sandro-8-Entrada.csv", encoding='ISO-8859-1', delimiter=';')
except Exception as e:
    print(f"Erro ao ler o arquivo: {e}")
    exit()

# Remover espaços em branco dos nomes das colunas
df_entrada.columns = df_entrada.columns.str.strip()

# Imprimir os nomes das colunas para verificação
print("Nomes das colunas:", df_entrada.columns)

# Corrigir valores nulos em uma coluna específica, se necessário
df_entrada['Montagem a fazer'] = df_entrada['Montagem a fazer'].fillna('Não especificado')

# Inserir os dados no banco
def inserir_dados_banco(df):
    connection = conectar()
    cursor = connection.cursor()
    
    for _, row in df.iterrows():
        # Prepara os dados, verificando se estão preenchidos
        paciente = row['Paciente']
        
        # Verifica se o laboratório é Oz3 ou Motorama e trata o Dr.(a) adequadamente
        if row['Laboratório'] in ['Oz3', 'Motorama']:
            doutor = None  # Não há Dr.(a) para esses laboratórios
        else:
            doutor = row['Dr.(a)'] if 'Dr.(a)' in df.columns and pd.notna(row['Dr.(a)']) else None
        
        data_entrada = row['Data de entrada'] if pd.notna(row['Data de entrada']) else None
        quantidade = int(row['Qntd']) if pd.notna(row['Qntd']) else 1
        montagem = row['Montagem a fazer'] if pd.notna(row['Montagem a fazer']) else None
        observacao = row['Observação'] if pd.notna(row['Observação']) else None
        data_saida = row['Data de saída'] if pd.notna(row['Data de saída']) else '0001-01-01'  # ou outra data padrão
        
        # Verifica se a coluna NP existe e define o valor do número de protocolo
        numero_protocolo = row['NP'] if 'NP' in df.columns and pd.notna(row['NP']) else None
        
        status = row['Status'] if pd.notna(row['Status']) else 'Em andamento'
        
        # Nome do laboratório baseado na planilha
        laboratorio = row['Laboratório'] if 'Laboratório' in df.columns and pd.notna(row['Laboratório']) else None

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