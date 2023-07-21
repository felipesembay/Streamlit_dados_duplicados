import streamlit as st
import pandas as pd
import base64
import psycopg2
from datetime import datetime
import numpy as np


@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

st.title('Adicionador de Profissão')

uploaded_file = st.file_uploader('Selecione um arquivo CSV', type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    colunas = df.columns.tolist()
    colunas_selecionadas = st.multiselect("Selecione as colunas para preencher valores", colunas)

    if st.button("Preencher valores"):
        df[colunas_selecionadas] = df.groupby('name')[colunas_selecionadas].fillna(method='ffill')

        st.subheader('Dataframe Atualizado')
        st.dataframe(df)

        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Clique aqui para baixar o arquivo CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

        try:
            cursor = conn.cursor()
            rows_updated_or_inserted = 0

            for _, row in df.iterrows():
                nome = row['name']
                empresa = row['companyName']
                link_url = row['profileLink']
                horario_salvamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                query = "SELECT * FROM linkedin WHERE nome = %s"
                cursor.execute(query, (nome,))
                result = cursor.fetchone()

                if pd.notna(nome) and pd.notna(empresa):
                    if result is not None:
                        query = "UPDATE linkedin SET empresa = %s WHERE nome = %s"
                        cursor.execute(query, (empresa, nome))
                        conn.commit()
                        rows_updated_or_inserted += 1
                    else:
                        query = "INSERT INTO linkedin (nome, empresa, link_url, horario_salvamento) VALUES (%s, %s, %s, %s)"
                        cursor.execute(query, (nome, empresa, link_url, horario_salvamento))
                        conn.commit()
                        rows_updated_or_inserted += 1

            st.success(f"As informações foram salvas no banco de dados. {rows_updated_or_inserted} linhas foram inseridas ou atualizadas.")
        except psycopg2.Error as error:
            st.error(f"Ocorreu um erro ao conectar-se ao banco de dados: {error}")
