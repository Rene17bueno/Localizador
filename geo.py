import streamlit as st
import pandas as pd
import re

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
    st.title("Filtro de Geolocalização")
    st.markdown("Para obter as informações .csv para o tratamento dos dados importar da rotina do promax:")

    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

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
        st.download_button(label="Exportar para TXT", data=txt_data, file_name=file_name, mime='text/plain')

if __name__ == "__main__":
    main()
