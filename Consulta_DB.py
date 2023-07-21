import streamlit as st
import pandas as pd
import psycopg2
import base64

@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

st.title('Adicionador de Profissão do banco de dados no arquivo csv/xlsx')

def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV file</a>'

uploaded_file = st.file_uploader("Selecione um arquivo", type=['csv', 'xlsx'])

if uploaded_file is not None:
    if uploaded_file.type == 'text/csv':
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    
    st.subheader('Dataframe Original')
    st.dataframe(df)

    if st.button("Consultar no Banco de Dados"):
        try:
            conn = init_connection()
            cursor = conn.cursor()

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

            st.subheader('Dataframe Atualizado')
            st.dataframe(df)
            st.markdown(get_table_download_link(df), unsafe_allow_html=True)

        except psycopg2.Error as error:
            st.error(f"Ocorreu um erro ao conectar-se ao banco de dados: {error}")
