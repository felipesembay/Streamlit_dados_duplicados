import streamlit as st
import pandas as pd
import re
import base64

st.sidebar.image("charisma.jpeg")

def extract_company(row):
    col_name = 'job' if 'job' in row.index else 'occupation'
    job_description = row[col_name]
    keywords = [" na ", " no ", " in ", " at ", " @"]
    for keyword in keywords:
        pattern = re.compile(keyword + '([\w\s&]+)')
        match = pattern.search(job_description)
        if match:
            return match.group(1).strip()
    return None

def main():
    st.title('Processador de CSV Anbima Likers')

    uploaded_file = st.file_uploader("Carregar arquivo CSV ou XLSX", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)

        st.dataframe(df)

        df['job'] = df['job'].fillna("")
        df['job'] = df['job'].astype(str)

        df['companyName'] = df.apply(extract_company, axis=1)
        
        st.write("Processamento completo!")
        st.dataframe(df)

        # Se você quiser fornecer uma opção para o usuário baixar o DataFrame modificado:
        csv_download = df.to_csv(index=False)
        b64 = base64.b64encode(csv_download.encode()).decode()
        st.markdown(f'<a href="data:file/csv;base64,{b64}" download="processed_data.csv">Baixar CSV Processado</a>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
