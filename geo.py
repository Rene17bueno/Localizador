import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.markdown("<h1 style='text-align: center; color: White;'>Tratamento de Dados para Geolocalizador</h1>", unsafe_allow_html=True)
st.divider()


# Função para identificar linhas específicas
def linha_em_branco(row):
    if row['Coordenadas'] == '000;000000;000;000000':
        return 'Informação Específica'
    else:
        return 'Outra Informação'

# Função para ajustar o formato das coordenadas
def ajustar_coordenadas(coordenadas):
    partes = coordenadas.split(';')
    if len(partes) == 5:
        partes[1] = partes[1].lstrip('0')
        partes[3] = partes[3].lstrip('0')
        novas_coordenadas = f"{partes[0]};-{partes[1]};{partes[2]};-{partes[3]};{partes[4]}"
        return novas_coordenadas
    else:
        return coordenadas  # Retorna a coordenada original se o formato não for o esperado

# Função para remover o 0 inicial após o ponto e vírgula
def remove_leading_zero(s):
    return re.sub(r';-0', ';-', s)

# Função para substituir o ponto e vírgula por ponto e garantir que apenas um sinal de menos seja usado
def substituir_ponto_virgula_por_ponto(s):
    partes = s.split(';')
    if len(partes) == 5:
        partes[1] = f"{partes[1]}.{partes[2]}"
        partes[3] = f"{partes[3]}.{partes[4]}"
        novas_coordenadas = f"{partes[0]};-{partes[1]};-{partes[3]}"
        # Remover sinal de menos duplicado
        novas_coordenadas = re.sub(r';--', ';-', novas_coordenadas)
        return novas_coordenadas
    else:
        return s

# Função principal
def main():
    st.title("Geolocalização de Novos Clientes")
    st.markdown("Para obter as informações .csv para o tratamento dos dados importar da rotina do promax:")

    st.sidebar.title("Importação e Exportação de Arquivos")

    uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type="csv")

    if uploaded_file is not None:
        # Leitura do arquivo CSV
        geo = pd.read_csv(uploaded_file, sep=';', encoding='latin1')

        # Mapeamento das filiais
        filial_mapping = {
            1: 'Maringá',
            2: 'Guarapuava',
            3: 'Ponta_Grossa',
            4: 'Norte_Pioneiro'
        }
        geo['Filial'] = geo['Filial'].map(filial_mapping)

        # Substituir vírgulas por ponto e remover espaços
        geo['Coordenadas'] = geo['Coordenadas'].str.replace(',', ';').str.replace(' ', '')

        # Ajustar o formato das coordenadas
        geo['Coordenadas'] = geo['Coordenadas'].apply(ajustar_coordenadas)

        # Criar a coluna "Concatenar"
        geo['Concatenar'] = geo['Cliente'].astype(str) + ';' + geo['Coordenadas'].astype(str)

        # Filtrar as linhas que não terminam com as informações específicas
        geo_filtrado = geo[~geo['Concatenar'].str.endswith('000;000000;000;000000')]

        # Criar a coluna "Linhas Em Branco"
        geo["Linhas Em Branco"] = geo.apply(linha_em_branco, axis=1)

        # Aplicar a função remove_leading_zero à coluna 'Concatenar'
        geo_filtrado['Concatenar'] = geo_filtrado['Concatenar'].apply(remove_leading_zero)

        # Aplicar a função substituir_ponto_virgula_por_ponto à coluna 'Concatenar'
        geo_filtrado['Concatenar'] = geo_filtrado['Concatenar'].apply(substituir_ponto_virgula_por_ponto)

        st.write("Concatenar:")
        st.dataframe(geo_filtrado)

        # Criar o nome do arquivo dinamicamente
        if not geo_filtrado.empty:
            filial = geo_filtrado['Filial'].iloc[0]
            data_inclusao = geo_filtrado['Data Inclusão'].iloc[0]

            # Remover caracteres inválidos para nomes de arquivos, como '/' e '\'
            data_inclusao = data_inclusao.replace('/', '-').replace('\\', '-')

            # Criar o nome do arquivo
            file_name = f"{filial}_{data_inclusao}.txt"
        else:
            file_name = "concatenar.txt"

        # Criar o conteúdo do arquivo TXT
        txt_data = '\n'.join(geo_filtrado['Concatenar'].tolist())

        # Botão para exportar o conteúdo para TXT
        st.sidebar.download_button(label="Exportar para TXT", data=txt_data, file_name=file_name, mime='text/plain')

    st.markdown("---")
    st.title("Corrigir Geolocalizador de cliente Existente")

    uploaded_file_2 = st.sidebar.file_uploader("Escolha um arquivo CSV para Processamento de Coordenadas", type="csv", key="processamento")

    if uploaded_file_2 is not None:
        # Leitura do arquivo CSV
        df = pd.read_csv(uploaded_file_2, sep=',', encoding='utf-8')

        # Verificar se as colunas necessárias estão presentes
        if 'CÓDIGO DO CLIENTE ' in df.columns and 'Coordenadas' in df.columns:
            # Criar a coluna "Concatenado"
            df['Concatenado'] = df['CÓDIGO DO CLIENTE '].astype(str) + ';' + df['Coordenadas']
            df['Concatenado'] = df['Concatenado'].str.replace(',', ';').str.replace(' ', '')

            st.write("Concatenado:")
            st.dataframe(df)

            # Criar o nome do arquivo dinamicamente com base no nome do arquivo inserido e a data atual
            if not df.empty:
                # Extrair o nome base do arquivo carregado
                base_name = uploaded_file_2.name.split('.')[0]
                # Obter a data atual
                current_date = datetime.now().strftime("%Y-%m-%d")
                # Criar o nome do arquivo
                file_name_2 = f"{base_name}_{current_date}.txt"
            else:
                file_name_2 = "planilha.txt"

            # Criar o conteúdo do arquivo TXT
            txt_data_2 = '\n'.join(df['Concatenado'].tolist())

            # Botão para exportar o conteúdo para TXT
            st.sidebar.download_button(label="Exportar para TXT", data=txt_data_2, file_name=file_name_2, mime='text/plain')
        else:
            st.error("As colunas 'CÓDIGO DO CLIENTE ' e 'Coordenadas' não foram encontradas no arquivo CSV.")

if __name__ == "__main__":
    main()
