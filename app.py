# import pandas as pd
# import streamlit as st


# # =====================================
# # 1. DEFINIÇÃO DOS PESOS DOS INDICADORES
# # =====================================

# PESOS_FIXOS = {
#     'GRAFICOS_ATUALIZADOS': 0.35,
#     'EXISTEM_PROCEDIMENTOS': 0.33,
#     'NOTA_QTDE_SUGESTOES': 0.33,
#     'QUADRO_LIMPO': 0.33,
#     'POSSUI_VISAO': 0.33,
#     'REUNIOES_REALIZADAS': 0.33,
#     'ACIDENTES': 2.5,
#     'QUALIFICACAO_TECNICA_UGB': 2.5,
#     'CHECKLIST_PROCEDIMENTO': 3.0
# }

# CAMPOS_DESCONSIDERADOS = []


# # ===========================================
# # 2. FUNÇÃO AUXILIAR: CONVERTER VALOR PARA NÚMERO
# # ===========================================

# def converter_para_numero(valor):
#     """
#     Converte valor para número, tratando vírgulas como separador decimal.
    
#     Retorna:
#         float se conseguir converter
#         None se for NULL/vazio
#     """
#     # Se já é NaN ou None
#     if pd.isna(valor) or valor is None:
#         return None
    
#     # Se já é número
#     if isinstance(valor, (int, float)):
#         return float(valor)
    
#     # Se é string
#     if isinstance(valor, str):
#         # Remove espaços
#         valor = valor.strip()
        
#         # Se está vazio
#         if valor == '' or valor.upper() in ['NULL', 'NONE', 'N/A', 'NA']:
#             return None
        
#         # Substitui vírgula por ponto (para decimais brasileiros)
#         valor = valor.replace(',', '.')
        
#         try:
#             return float(valor)
#         except ValueError:
#             return None
    
#     return None


# # ===========================================
# # 3. FUNÇÃO PARA CALCULAR A NOTA POR LINHA
# # ===========================================

# def calcular_nota_com_redistribuicao(row):
#     """
#     Calcula a nota ponderada da UGB com redistribuição proporcional.
    
#     REGRAS:
#     1. Campos NULL → Peso redistribuído
#     2. Campos com valor = 0 → SUBTRAI o peso (penalização)
#     3. Campos com valor > 0 → MULTIPLICA (valor × peso)
#     4. QUALIFICACAO_TECNICA_UGB: Só penaliza se valor = 0
#     """
    
#     pesos_ativos = {
#         nome_campo: peso
#         for nome_campo, peso in PESOS_FIXOS.items()
#         if nome_campo not in CAMPOS_DESCONSIDERADOS
#     }
    
#     campos_avaliados = {}
#     campos_nao_avaliados = {}
    
#     # Separa avaliados e não avaliados
#     for nome_campo, peso in pesos_ativos.items():
#         valor_original = row.get(nome_campo)
#         valor_convertido = converter_para_numero(valor_original)
        
#         if valor_convertido is None:
#             # Campo NULL
#             campos_nao_avaliados[nome_campo] = peso
#         else:
#             # Campo avaliado (mesmo que seja 0)
#             campos_avaliados[nome_campo] = peso
    
#     # Se nenhum campo foi avaliado
#     if not campos_avaliados:
#         return None
    
#     # Calcula pesos totais
#     peso_total_avaliados = sum(campos_avaliados.values())
#     peso_total_nao_avaliados = sum(campos_nao_avaliados.values())
#     peso_desconsiderados = sum(PESOS_FIXOS[campo] for campo in CAMPOS_DESCONSIDERADOS)
#     peso_total_redistribuir = peso_total_nao_avaliados + peso_desconsiderados
    
#     # Calcula nota ponderada
#     nota_ponderada = 0
    
#     for nome_campo, peso_original in campos_avaliados.items():
#         valor_original = row.get(nome_campo)
#         valor_indicador = converter_para_numero(valor_original)
        
#         # Se não conseguiu converter, pula
#         if valor_indicador is None:
#             continue
        
#         # Calcula redistribuição
#         proporcao = peso_original / peso_total_avaliados
#         rateio = proporcao * peso_total_redistribuir
#         peso_final = peso_original + rateio
        
#         # REGRA ESPECIAL: QUALIFICACAO_TECNICA_UGB só penaliza se = 0
#         if nome_campo == 'QUALIFICACAO_TECNICA_UGB':
#             if valor_indicador == 0:
#                 contribuicao = -peso_final
#             else:
#                 contribuicao = valor_indicador * peso_final
#         else:
#             # REGRA GERAL
#             if valor_indicador == 0:
#                 contribuicao = -peso_final
#             else:
#                 contribuicao = valor_indicador * peso_final
        
#         nota_ponderada += contribuicao
    
#     nota_final = round(nota_ponderada / 10, 2)
#     return nota_final


# # ============================================
# # 4. FUNÇÃO PARA LER CSV
# # ============================================

# def ler_csv_com_encoding_e_delimitador(uploaded_file):
#     """
#     Lê CSV testando diferentes encodings e delimitadores.
#     NÃO converte automaticamente para evitar perder informação.
#     """
#     encodings = ['utf-8', 'latin1', 'ISO-8859-1', 'windows-1252', 'cp1252']
#     delimitadores = [',', ';', '\t']
    
#     for encoding in encodings:
#         for delimitador in delimitadores:
#             try:
#                 uploaded_file.seek(0)
                
#                 # Lê como string para não perder formatação
#                 df = pd.read_csv(
#                     uploaded_file, 
#                     encoding=encoding,
#                     sep=delimitador,
#                     engine='python',
#                     dtype=str,  # LÊ TUDO COMO STRING
#                     keep_default_na=False  # NÃO CONVERTE AUTOMATICAMENTE
#                 )
                
#                 if df.shape[1] >= 2:
#                     delimitador_nome = {
#                         ',': 'vírgula (,)',
#                         ';': 'ponto-e-vírgula (;)',
#                         '\t': 'tabulação (tab)'
#                     }.get(delimitador, delimitador)
                    
#                     st.success(f"✅ Arquivo lido com sucesso!")
#                     st.info(f"📄 **Encoding:** {encoding} | **Delimitador:** {delimitador_nome}")
                    
#                     # Converte colunas manualmente usando nossa função
#                     for coluna in PESOS_FIXOS.keys():
#                         if coluna in df.columns:
#                             # Aplica conversão personalizada
#                             df[coluna] = df[coluna].apply(converter_para_numero)
                    
#                     st.success(f"✅ Valores convertidos corretamente (vírgulas tratadas)!")
                    
#                     return df
                    
#             except UnicodeDecodeError:
#                 continue
#             except Exception as e:
#                 continue
    
#     st.error("❌ Não foi possível ler o arquivo.")
#     return None


# # ===========================================
# # 5. INTERFACE STREAMLIT
# # ===========================================

# st.set_page_config(
#     page_title="Calculadora Nota UGB",
#     page_icon="📊",
#     layout="wide"
# )

# st.title("📊 Calculadora de Nota Gerencial UGB")
# st.markdown("---")

# with st.expander("ℹ️ Como funciona o Cálculo da Nota"):
#     st.markdown("""
#     ### 📋 Pesos dos Indicadores:
    
#     | Indicador | Peso |
#     |-----------|------|
#     | GRAFICOS_ATUALIZADOS | 0,35 |
#     | EXISTEM_PROCEDIMENTOS | 0,33 |
#     | NOTA_QTDE_SUGESTOES | 0,33 |
#     | QUADRO_LIMPO | 0,33 |
#     | POSSUI_VISAO | 0,33 |
#     | REUNIOES_REALIZADAS | 0,33 |
#     | ACIDENTES | 2,5 |
#     | QUALIFICACAO_TECNICA_UGB | 2,5 |
#     | CHECKLIST_PROCEDIMENTO | 3,0 |
#     | **TOTAL** | **10,0** |
    
#     ### ⚖️ Regras de Cálculo:
    
#     1. **Campos NULL/vazios**: Peso redistribuído proporcionalmente
#     2. **Valor = 0**: PENALIZA (subtrai o peso final)
#     3. **Valor > 0**: MULTIPLICA (valor × peso final)
#     4. **QUALIFICACAO_TECNICA_UGB**: Só penaliza se = 0
    
#     ### 💡 Formato aceito:
    
#     - Decimais com vírgula: **2,5** ✅
#     - Decimais com ponto: **2.5** ✅
#     - Valores vazios: tratados como NULL
#     """)

# uploaded_file = st.file_uploader(
#     "📂 Carregar arquivo CSV com as avaliações",
#     type=['csv'],
#     help="Aceita decimais com vírgula (2,5) ou ponto (2.5)"
# )

# if uploaded_file is not None:
#     df = ler_csv_com_encoding_e_delimitador(uploaded_file)
    
#     if df is None:
#         st.stop()
    
#     st.subheader("📋 Informações do Arquivo")
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.metric("Total de Linhas", df.shape[0])
#     with col2:
#         st.metric("Total de Colunas", df.shape[1])
#     with col3:
#         colunas_presentes = [col for col in PESOS_FIXOS.keys() if col in df.columns]
#         st.metric("Colunas de Avaliação", len(colunas_presentes))
    
#     with st.expander("👁️ Ver dados originais do CSV", expanded=False):
#         st.dataframe(df, use_container_width=True)
#         st.write("**Valores após conversão:**")
#         df_display = df.copy()
#         for col in PESOS_FIXOS.keys():
#             if col in df_display.columns:
#                 # Mostra se está NULL ou número
#                 df_display[f"{col}_tipo"] = df_display[col].apply(
#                     lambda x: "NULL" if pd.isna(x) else f"número: {x}"
#                 )
#         st.dataframe(df_display)
    
#     with st.spinner('⏳ Calculando notas...'):
#         df['NOTA_GERENCIAL_CALCULADA'] = df.apply(
#             calcular_nota_com_redistribuicao,
#             axis=1
#         )
    
#     st.subheader("✅ Dados com Nota Gerencial Calculada")
#     st.dataframe(df, use_container_width=True)
    
#     st.subheader("📈 Estatísticas das Notas")
#     col1, col2, col3, col4 = st.columns(4)
    
#     notas_validas = df['NOTA_GERENCIAL_CALCULADA'].dropna()
    
#     if len(notas_validas) > 0:
#         with col1:
#             st.metric("Média", f"{notas_validas.mean():.2f}")
#         with col2:
#             st.metric("Maior Nota", f"{notas_validas.max():.2f}")
#         with col3:
#             st.metric("Menor Nota", f"{notas_validas.min():.2f}")
#         with col4:
#             st.metric("Total de Avaliações", len(notas_validas))
    
#     csv_resultado = df.to_csv(index=False, encoding='utf-8-sig', sep=';', decimal=',')
    
#     st.download_button(
#         label="📥 Download CSV com Notas Calculadas",
#         data=csv_resultado,
#         file_name='notas_gerenciais_calculadas.csv',
#         mime='text/csv',
#         help="CSV compatível com Excel, decimais com vírgula"
#     )
    
# else:
#     st.info("📂 Faça o upload de um arquivo CSV para começar o cálculo das notas.")
    
#     with st.expander("📖 Como preparar seu arquivo CSV"):
#         st.markdown("""
#         ### Formato do arquivo:
        
#         **Colunas necessárias:**
#         - GRAFICOS_ATUALIZADOS
#         - EXISTEM_PROCEDIMENTOS
#         - NOTA_QTDE_SUGESTOES
#         - QUADRO_LIMPO
#         - POSSUI_VISAO
#         - REUNIOES_REALIZADAS
#         - ACIDENTES
#         - QUALIFICACAO_TECNICA_UGB
#         - CHECKLIST_PROCEDIMENTO
        
#         **Valores aceitos:**
#         - Números inteiros: 0, 10
#         - Decimais com vírgula: 2,5 ✅
#         - Decimais com ponto: 2.5 ✅
#         - Células vazias: tratadas como NULL
#         - Texto "NULL": tratado como NULL
        
#         **Atenção:**
#         - Valor 0 = penalização (reduz nota)
#         - Células vazias = peso redistribuído (não penaliza)
#         """)









# =====================================
#    VERSÃO COM EXPORTAÇÃO EM EXCEL
# =====================================



import pandas as pd
import streamlit as st
from io import BytesIO




# =====================================
# 1. DEFINIÇÃO DOS PESOS DOS INDICADORES
# =====================================



PESOS_FIXOS = {
    'GRAFICOS_ATUALIZADOS': 0.35,
    'EXISTEM_PROCEDIMENTOS': 0.33,
    'NOTA_QTDE_SUGESTOES': 0.33,
    'QUADRO_LIMPO': 0.33,
    'POSSUI_VISAO': 0.33,
    'REUNIOES_REALIZADAS': 0.33,
    'ACIDENTES': 2.5,
    'QUALIFICACAO_TECNICA_UGB': 2.5,
    'CHECKLIST_PROCEDIMENTO': 3.0
}



CAMPOS_DESCONSIDERADOS = []




# ===========================================
# 2. FUNÇÃO AUXILIAR: CONVERTER VALOR PARA NÚMERO
# ===========================================



def converter_para_numero(valor):
    """
    Converte valor para número, tratando vírgulas como separador decimal.
    
    Retorna:
        float se conseguir converter
        None se for NULL/vazio
    """
    # Se já é NaN ou None
    if pd.isna(valor) or valor is None:
        return None
    
    # Se já é número
    if isinstance(valor, (int, float)):
        return float(valor)
    
    # Se é string
    if isinstance(valor, str):
        # Remove espaços
        valor = valor.strip()
        
        # Se está vazio
        if valor == '' or valor.upper() in ['NULL', 'NONE', 'N/A', 'NA']:
            return None
        
        # Substitui vírgula por ponto (para decimais brasileiros)
        valor = valor.replace(',', '.')
        
        try:
            return float(valor)
        except ValueError:
            return None
    
    return None




# ===========================================
# 3. FUNÇÃO PARA CALCULAR A NOTA POR LINHA
# ===========================================



def calcular_nota_com_redistribuicao(row):
    """
    Calcula a nota ponderada da UGB com redistribuição proporcional.
    
    REGRAS:
    1. Campos NULL → Peso redistribuído
    2. Campos com valor = 0 → Contribuição ZERO (não soma, não subtrai)
    3. Campos com valor > 0 → MULTIPLICA (valor × peso)
    """
    
    pesos_ativos = {
        nome_campo: peso
        for nome_campo, peso in PESOS_FIXOS.items()
        if nome_campo not in CAMPOS_DESCONSIDERADOS
    }
    
    campos_avaliados = {}
    campos_nao_avaliados = {}
    
    # Separa avaliados e não avaliados
    for nome_campo, peso in pesos_ativos.items():
        valor_original = row.get(nome_campo)
        valor_convertido = converter_para_numero(valor_original)
        
        if valor_convertido is None:
            # Campo NULL
            campos_nao_avaliados[nome_campo] = peso
        else:
            # Campo avaliado (mesmo que seja 0)
            campos_avaliados[nome_campo] = peso
    
    # Se nenhum campo foi avaliado
    if not campos_avaliados:
        return None
    
    # Calcula pesos totais
    peso_total_avaliados = sum(campos_avaliados.values())
    peso_total_nao_avaliados = sum(campos_nao_avaliados.values())
    peso_desconsiderados = sum(PESOS_FIXOS[campo] for campo in CAMPOS_DESCONSIDERADOS)
    peso_total_redistribuir = peso_total_nao_avaliados + peso_desconsiderados
    
    # Calcula nota ponderada
    nota_ponderada = 0
    
    for nome_campo, peso_original in campos_avaliados.items():
        valor_original = row.get(nome_campo)
        valor_indicador = converter_para_numero(valor_original)
        
        # Se não conseguiu converter, pula
        if valor_indicador is None:
            continue
        
        # Calcula redistribuição
        proporcao = peso_original / peso_total_avaliados
        rateio = proporcao * peso_total_redistribuir
        peso_final = peso_original + rateio
        
        # REGRA: Valor 0 não penaliza, apenas não contribui
        if valor_indicador == 0:
            contribuicao = 0
        else:
            contribuicao = valor_indicador * peso_final
        
        nota_ponderada += contribuicao
    
    nota_final = round(nota_ponderada / 10, 2)
    return nota_final




# ============================================
# 4. FUNÇÃO PARA LER CSV
# ============================================



def ler_csv_com_encoding_e_delimitador(uploaded_file):
    """
    Lê CSV testando diferentes encodings e delimitadores.
    NÃO converte automaticamente para evitar perder informação.
    """
    encodings = ['utf-8', 'latin1', 'ISO-8859-1', 'windows-1252', 'cp1252']
    delimitadores = [',', ';', '\t']
    
    for encoding in encodings:
        for delimitador in delimitadores:
            try:
                uploaded_file.seek(0)
                
                # Lê como string para não perder formatação
                df = pd.read_csv(
                    uploaded_file, 
                    encoding=encoding,
                    sep=delimitador,
                    engine='python',
                    dtype=str,  # LÊ TUDO COMO STRING
                    keep_default_na=False  # NÃO CONVERTE AUTOMATICAMENTE
                )
                
                if df.shape[1] >= 2:
                    delimitador_nome = {
                        ',': 'vírgula (,)',
                        ';': 'ponto-e-vírgula (;)',
                        '\t': 'tabulação (tab)'
                    }.get(delimitador, delimitador)
                    
                    st.success(f"✅ Arquivo lido com sucesso!")
                    st.info(f"📄 **Encoding:** {encoding} | **Delimitador:** {delimitador_nome}")
                    
                    # Converte colunas manualmente usando nossa função
                    for coluna in PESOS_FIXOS.keys():
                        if coluna in df.columns:
                            # Aplica conversão personalizada
                            df[coluna] = df[coluna].apply(converter_para_numero)
                    
                    st.success(f"✅ Valores convertidos corretamente (vírgulas tratadas)!")
                    
                    return df
                    
            except UnicodeDecodeError:
                continue
            except Exception as e:
                continue
    
    st.error("❌ Não foi possível ler o arquivo.")
    return None




# ===========================================
# 5. INTERFACE STREAMLIT
# ===========================================



st.set_page_config(
    page_title="Calculadora Nota UGB",
    page_icon="📊",
    layout="wide"
)



st.title("📊 Calculadora de Nota Gerencial UGB")
st.markdown("---")



with st.expander("ℹ️ Como funciona o Cálculo da Nota"):
    st.markdown("""
    ### 📋 Pesos dos Indicadores:
    
    | Indicador | Peso |
    |-----------|------|
    | GRAFICOS_ATUALIZADOS | 0,35 |
    | EXISTEM_PROCEDIMENTOS | 0,33 |
    | NOTA_QTDE_SUGESTOES | 0,33 |
    | QUADRO_LIMPO | 0,33 |
    | POSSUI_VISAO | 0,33 |
    | REUNIOES_REALIZADAS | 0,33 |
    | ACIDENTES | 2,5 |
    | QUALIFICACAO_TECNICA_UGB | 2,5 |
    | CHECKLIST_PROCEDIMENTO | 3,0 |
    | **TOTAL** | **10,0** |
    
    ### ⚖️ Regras de Cálculo:
    
    1. **Campos NULL/vazios**: Peso redistribuído proporcionalmente
    2. **Valor = 0**: Contribuição ZERO (não soma, não subtrai)
    3. **Valor > 0**: MULTIPLICA (valor × peso final)
    
    ### 💡 Formato aceito:
    
    - Decimais com vírgula: **2,5** ✅
    - Decimais com ponto: **2.5** ✅
    - Valores vazios: tratados como NULL
    """)



uploaded_file = st.file_uploader(
    "📂 Carregar arquivo CSV com as avaliações",
    type=['csv'],
    help="Aceita decimais com vírgula (2,5) ou ponto (2.5)"
)



if uploaded_file is not None:
    df = ler_csv_com_encoding_e_delimitador(uploaded_file)
    
    if df is None:
        st.stop()
    
    st.subheader("📋 Informações do Arquivo")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Linhas", df.shape[0])
    with col2:
        st.metric("Total de Colunas", df.shape[1])
    with col3:
        colunas_presentes = [col for col in PESOS_FIXOS.keys() if col in df.columns]
        st.metric("Colunas de Avaliação", len(colunas_presentes))
    
    with st.expander("👁️ Ver dados originais do CSV", expanded=False):
        st.dataframe(df, use_container_width=True)
        st.write("**Valores após conversão:**")
        df_display = df.copy()
        for col in PESOS_FIXOS.keys():
            if col in df_display.columns:
                # Mostra se está NULL ou número
                df_display[f"{col}_tipo"] = df_display[col].apply(
                    lambda x: "NULL" if pd.isna(x) else f"número: {x}"
                )
        st.dataframe(df_display)
    
    with st.spinner('⏳ Calculando notas...'):
        df['NOTA_GERENCIAL_CALCULADA'] = df.apply(
            calcular_nota_com_redistribuicao,
            axis=1
        )
    
    st.subheader("✅ Dados com Nota Gerencial Calculada")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("📈 Estatísticas das Notas")
    col1, col2, col3, col4 = st.columns(4)
    
    notas_validas = df['NOTA_GERENCIAL_CALCULADA'].dropna()
    
    if len(notas_validas) > 0:
        with col1:
            st.metric("Média", f"{notas_validas.mean():.2f}")
        with col2:
            st.metric("Maior Nota", f"{notas_validas.max():.2f}")
        with col3:
            st.metric("Menor Nota", f"{notas_validas.min():.2f}")
        with col4:
            st.metric("Total de Avaliações", len(notas_validas))
    
    # ============================================
    # EXPORTAÇÃO PARA EXCEL (XLSX)
    # ============================================
    
    # Cria um buffer de bytes na memória
    buffer = BytesIO()
    
    # Escreve o Excel no buffer
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Notas UGB')
        
        # Opcional: Formata a planilha
        workbook = writer.book
        worksheet = writer.sheets['Notas UGB']
        
        # Formato para números decimais (vírgula como separador)
        formato_decimal = workbook.add_format({'num_format': '#,##0.00'})
        
        # Aplica formato na coluna de nota (última coluna)
        ultima_coluna = len(df.columns) - 1
        worksheet.set_column(ultima_coluna, ultima_coluna, 18, formato_decimal)
        
        # Ajusta largura das colunas
        for idx, col in enumerate(df.columns):
            max_len = max(
                df[col].astype(str).apply(len).max(),
                len(str(col))
            ) + 2
            worksheet.set_column(idx, idx, max_len)
    
    # Retorna o cursor para o início do buffer
    buffer.seek(0)
    
    st.download_button(
        label="📥 Download EXCEL (.xlsx)",
        data=buffer,
        file_name='notas_gerenciais_calculadas.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        help="Planilha Excel com acentos corretos e formatação"
    )
    
else:
    st.info("📂 Faça o upload de um arquivo CSV para começar o cálculo das notas.")
    
    with st.expander("📖 Como preparar seu arquivo CSV"):
        st.markdown("""
        ### Formato do arquivo:
        
        **Colunas necessárias:**
        - GRAFICOS_ATUALIZADOS
        - EXISTEM_PROCEDIMENTOS
        - NOTA_QTDE_SUGESTOES
        - QUADRO_LIMPO
        - POSSUI_VISAO
        - REUNIOES_REALIZADAS
        - ACIDENTES
        - QUALIFICACAO_TECNICA_UGB
        - CHECKLIST_PROCEDIMENTO
        
        **Valores aceitos:**
        - Números inteiros: 0, 10
        - Decimais com vírgula: 2,5 ✅
        - Decimais com ponto: 2.5 ✅
        - Células vazias: tratadas como NULL
        - Texto "NULL": tratado como NULL
        
        **Atenção:**
        - Valor 0 = contribuição zero (neutro)
        - Células vazias = peso redistribuído (não penaliza)
        """)
