import streamlit as st
import pandas as pd
import psycopg2
import base64

# main.py
#from dotenv import load_dotenv
import os

#load_dotenv()  # take environment variables from .env.
#db_host = os.getenv('DB_HOST')
#db_user = os.getenv('DB_USER')
#db_password = os.getenv('DB_PASSWORD')
#db_database = os.getenv('DB_DATABASE')

#import toml

#config = toml.load('config.toml')
#db_host = config['database']['DB_HOST']
#db_user = config['database']['DB_USER']
#db_password = config['database']['DB_PASSWORD']
#db_database = config['database']['DB_DATABASE']


st.title('Adicionador de Profissão do banco de dados no arquivo csv/xlsx')

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV file</a>'

uploaded_file = st.file_uploader("Selecione um arquivo", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Ler o arquivo carregado como um DataFrame
    if uploaded_file.type == 'text/csv':
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    
    st.subheader('Dataframe Original')
    st.dataframe(df)

    if st.button("Consultar no Banco de Dados"):
        try:
            # Conectar ao banco de dados
            #conn = psycopg2.connect(host=db_host, user=db_user, password=db_password, database=db_database)
            conn = psycopg2.connect(**st.secrets["database"])
            cursor = conn.cursor()

            # Para cada funcionário no DataFrame, consulte o banco de dados e insira o nome da empresa ou "Dados Incompletos"
            for index, row in df.iterrows():
                nome = row['name']
                link_url = row['profileLink']

                query = f"SELECT empresa FROM linkedin WHERE nome = '{nome}' OR link_url = '{link_url}'"
                cursor.execute(query)
                result = cursor.fetchone()

                if result is not None:
                    if pd.notna(result[0]):
                        df.loc[index, 'companyName'] = result[0]
                    else:
                        df.loc[index, 'companyName'] = 'Dados Incompletos'

            cursor.close()
            conn.close()

            st.subheader('Dataframe Atualizado')
            st.dataframe(df)
            st.markdown(get_table_download_link(df), unsafe_allow_html=True)

        except psycopg2.Error as error:
            st.error(f"Ocorreu um erro ao conectar-se ao banco de dados: {error}")