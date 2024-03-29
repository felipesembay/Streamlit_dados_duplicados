import streamlit as st
import pandas as pd
from io import BytesIO
import base64

st.sidebar.image("charisma.jpeg")
st.title('Removedor de dados duplicados')

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV file</a>'

uploaded_file = st.file_uploader("Selecione um arquivo", type=['xlsx', 'csv'])

if uploaded_file is not None:
    # Verificar o tipo do arquivo e lê-lo como um DataFrame
    try:
        if uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        elif uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
            
        if 'Publicado por' in df.columns:
            df['Publicado por'] = df['Publicado por'].astype(str)
        st.write(f"O arquivo tem {df.shape[0]} linhas e {df.shape[1]} colunas.")
        colunas = df.columns.tolist()
        coluna_selecionada = st.selectbox("Selecione uma coluna para remover duplicatas", colunas)
        
        if st.button("Remover duplicatas"):
            df.drop_duplicates(subset=coluna_selecionada, keep="first", inplace=True)
            st.write(f"Agora o arquivo tem {df.shape[0]} linhas e {df.shape[1]} colunas.")
            st.dataframe(df)
            st.markdown(get_table_download_link(df), unsafe_allow_html=True)
    except UnicodeDecodeError:
        st.write("Houve um erro ao ler o arquivo. Por favor, verifique se o arquivo está codificado como UTF-8.")
