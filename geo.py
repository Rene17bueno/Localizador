import streamlit as st
import pandas as pd
import io

# Função para identificar linhas específicas
def linha_em_branco(row):
    if row['Coordenadas'] == '000;000000;000;000000':
        return 'Informação Específica'
    else:
        return 'Outra Informação'

# Função principal
def main():
    st.title("Filtro de Geolocalização")

    # Upload do arquivo CSV
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

    if uploaded_file is not None:
        # Leitura do arquivo CSV
        geo = pd.read_csv(uploaded_file, sep=';', encoding='latin1')

        # Substituir vírgulas por ponto e remover espaços
        geo['Coordenadas'] = geo['Coordenadas'].str.replace(',', ';').str.replace(' ', '')

        # Criar a coluna "Concatenar"
        geo['Concatenar'] = geo['Cliente'].astype(str) + ';' + geo['Coordenadas'].astype(str)

        # Filtrar as linhas que não terminam com as informações específicas
        geo_filtrado = geo[~geo['Concatenar'].str.endswith('000;000000;000;000000')]

        # Criar a coluna "Linhas Em Branco"
        geo["Linhas Em Branco"] = geo.apply(linha_em_branco, axis=1)

        # Exibir a planilha filtrada
        st.write("Concatenar:")
        st.dataframe(geo_filtrado)

        # Preparar o arquivo para download
        txt = geo_filtrado['Concatenar'].to_csv(index=False, header=False)
        st.download_button(label="Exportar para TXT", data=txt, file_name='concatenar.txt', mime='text/plain')

if __name__ == "__main__":
    main()
