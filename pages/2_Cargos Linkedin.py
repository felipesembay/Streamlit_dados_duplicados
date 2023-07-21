import streamlit as st
import pandas as pd
import base64
import psycopg2
from datetime import datetime
import numpy as np
import os
#import toml

#config = toml.load('config.toml')
#db_host = config['database']['DB_HOST']
#db_user = config['database']['DB_USER']
#db_password = config['database']['DB_PASSWORD']
#db_database = config['database']['DB_DATABASE']

# Título do aplicativo
st.title('Adicionador de Profissão')

# Carregar arquivo CSV
uploaded_file = st.file_uploader('Selecione um arquivo CSV', type=['csv'])

if uploaded_file is not None:
    # Ler o arquivo CSV como um DataFrame
    df = pd.read_csv(uploaded_file)

    colunas = df.columns.tolist()
    colunas_selecionadas = st.multiselect("Selecione as colunas para preencher valores", colunas)

    if st.button("Preencher valores"):
        # Preencher os valores nulos com base nas colunas selecionadas
        df[colunas_selecionadas] = df.groupby('name')[colunas_selecionadas].fillna(method='ffill')

        # Remover linhas duplicadas mantendo apenas a primeira ocorrência
        #df.drop_duplicates(subset=['name'], keep='first', inplace=True)

        # Exibir o dataframe resultante
        st.subheader('Dataframe Atualizado')
        st.dataframe(df)

        # Gerar o link de download
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Clique aqui para baixar o arquivo CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

        # Salvar as informações no banco de dados PostgreSQL
        try:
            #conn = psycopg2.connect(host=db_host, user=db_user, password=db_password, database=db_database)
            conn = psycopg2.connect(**st.secrets["database"])
            cursor = conn.cursor()

            rows_updated_or_inserted = 0

            # Verificar e adicionar os registros no banco
            for _, row in df.iterrows():
                nome = row['name']
                empresa = row['companyName']
                link_url = row['profileLink']
                horario_salvamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Verificar se o registro já existe para o funcionário no banco
                query = f"SELECT * FROM linkedin WHERE nome = '{nome}'"
                cursor.execute(query)
                result = cursor.fetchone()

                # Verifique se nome e empresa não são None ou Nan antes de inserir ou atualizar
                if pd.notna(nome) and pd.notna(empresa):
                    if result is not None:
                        # Atualizar a empresa no banco
                        query = f"UPDATE linkedin SET empresa = '{empresa}' WHERE nome = '{nome}'"
                        cursor.execute(query)
                        conn.commit()
                        rows_updated_or_inserted += 1
                    else:
                        # Adicionar o registro no banco
                        query = f"INSERT INTO linkedin (nome, empresa, link_url, horario_salvamento) VALUES ('{nome}', '{empresa}', '{link_url}', '{horario_salvamento}')"
                        cursor.execute(query)
                        conn.commit()
                        rows_updated_or_inserted += 1

            cursor.close()
            conn.close()

            st.success(f"As informações foram salvas no banco de dados. {rows_updated_or_inserted} linhas foram inseridas ou atualizadas.")
        except psycopg2.Error as error:
            st.error(f"Ocorreu um erro ao conectar-se ao banco de dados: {error}")

