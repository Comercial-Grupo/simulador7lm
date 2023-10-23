import streamlit as st
import pandas as pd
import numpy as np
import streamlit_antd_components as sac
from babel.numbers import format_currency

def conversor_moeda_brasil(amount):
    return format_currency(amount, 'BRL', locale='pt_BR')

def ExcecaoError(a,b):
    try:
        W0 = a/b
    except:
        W0 = 0
    return W0

st.set_page_config(page_title="7LM-GPT app", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
st.title("Ferramenta | Corretor | 7LM-GPT 💬🧠")



# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "user_name" not in st.session_state:
    st.session_state.user_name = []    
    st.session_state.user_name.append({"preco":"", "garantido":"", "sinal":""})
    
if "dados_financeiros" not in st.session_state:
    st.session_state.dados_financeiros = []  

if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False
    st.session_state.horizontal = True


caixa = st.container()

with st.sidebar:
    st.image("https://7lm.com.br/wp-content/uploads/2023/03/logo_branca_aprovada_final_slogan.svg")
    st.title("Corretor | 7LM-GPT 💬🧠")
    st.markdown("Simulador de propostas e bônus de vendas para o corretor")
    lg = []
    #with st.expander("🔐 Login"):
      #  ident = st.text_input("ID", type="password")  



sac.divider(label='Comercial | 7LM', align='center')

def safe_execute(default, exception, function, *args):
    try:
        return function(*args)
    except exception as e:
        print(f"Erro detectado: {str(e)}")
        return default

flow = sac.steps(
    items=[
        sac.StepsItem(title='Otimização Plano',disabled=False),
        sac.StepsItem(title='Escolher Unidade',disabled=True),
        sac.StepsItem(title='Resultado Final',disabled=True)
    ], format_func='title'
)

# Definindo a tabela de preços e garantidos
dict_tabela = {
    "preco": {
        "AGL25": {"Garden": 215000, "Padrao": 180000, "Com Varanda": 180000},
        "AGL28": {"Garden": 215000, "Padrao": 190000, "Com Varanda": 196000},
        "FSA06": {"Garden": 218000, "Padrao": 210000, "Com Varanda": 212000},
        "FSA07": {"Garden": 218000, "Padrao": 210000, "Com Varanda": 212000},
        "FSA09": {"Garden": 218000, "Padrao": 195000, "Com Varanda": 200000},
    },
    "garantido": {
        "AGL25": {"Garden": 150000, "medio": 142000, "minimo": 150000},
        "AGL28": {"Garden": 150000, "medio": 142000, "minimo": 134000},
        "FSA06": {"Garden": 150000, "medio": 160000, "minimo": 150000},
        "FSA07": {"Garden": 150000, "medio": 160000, "minimo": 150000},
        "FSA09": {"Garden": 150000, "medio": 145000, "minimo": 137000},
    },
}


def CalculoBonus(real_preco, real_garantido, real_sinal, meta_preco):
    A0 = np.round(real_garantido/real_preco,2)
    A1 = np.round(real_preco/meta_preco-1,2)
    A2 = np.round(real_sinal/real_preco,2)
    A3 = {"garantido":A0, "preco":A1, "sinal":A2}
    return A3


BONUS = {"GARANTIDO":{0.73:300, 0.75: 400, 0.77:500},
         "PREÇO":{0.025:300, 0.04: 400, 0.05:500},
         "ENTRADA":{0.02:300, 0.03: 400, 0.04:500}}


def get_bonus(coeficiente, tipo_bonus):
    for threshold, bonus in sorted(BONUS[tipo_bonus].items(), reverse=True):
        if coeficiente >= threshold:
            return bonus
    return 0

def CalculoBonus(real_preco, real_garantido, real_sinal, meta_preco):
    A0 = np.round(real_garantido/real_preco, 2)
    A1 = np.round(real_preco/meta_preco - 1, 2)
    A2 = np.round(real_sinal/real_preco, 2)
    
    bonus_garantido = get_bonus(A0, 'GARANTIDO')
    bonus_preco = get_bonus(A1, 'PREÇO')
    bonus_entrada = get_bonus(A2, 'ENTRADA')
    
    A3 = {"garantido": bonus_garantido, "preco": bonus_preco, "sinal": bonus_entrada}
    return A3

def simula_bonus(dict_tabela, real_preco, real_garantido, real_sinal):
    resultados = []
    for unidade, valores in dict_tabela['preco'].items():
        for tipo_preco, meta_preco in valores.items():
            for tipo_garantido, meta_garantido in dict_tabela['garantido'][unidade].items():
                if tipo_garantido in ['Garden', 'medio']:  # só processa os tipos 'Garden' e 'medio'
                    coeficientes = CalculoBonus(real_preco, real_garantido, real_sinal, meta_preco)
                    var_percentual_preco = ((real_preco - meta_preco) / meta_preco) * 100
                    var_percentual_garantido = (real_garantido / real_preco) * 100
                    var_percentual_entrada = ((real_sinal / real_preco)) * 100
                    resultados.append({
                        'Unidade': unidade,
                        'Tipo Preco': tipo_preco,
                        'Tipo Garantido': tipo_garantido,
                        'Real Preco': real_preco,
                        'Meta Preco': meta_preco,
                        'Var% Preco': var_percentual_preco,
                        'Bonus Preco': coeficientes['preco'],
                        'Real Garantido': real_garantido,
                        #'Meta Garantido': meta_garantido,
                        'Var% Garantido': var_percentual_garantido,
                        'Bonus Garantido': coeficientes['garantido'],
                        'Real Sinal': real_sinal,
                        'Var% Entrada': var_percentual_entrada,
                        'Bonus Entrada': coeficientes['sinal']
                    })

    df_resultados_simulacao = pd.DataFrame(resultados)
    df_resultados_simulacao["Total_Bônus"] = df_resultados_simulacao["Bonus Preco"]+df_resultados_simulacao["Bonus Garantido"]+df_resultados_simulacao["Bonus Entrada"]
    df_resultados_simulacao_V0 = df_resultados_simulacao.sort_values(by=["Total_Bônus"], ascending=False)
    return df_resultados_simulacao_V0


# Definindo a função limitador
def limitador(var):
    if var < 0:
        return 0
    elif var > 1500:
        return 1500
    else:
        return var

def conversor_moeda_brasil(my_value):
    a = '{:,.2f}'.format(float(my_value))
    b = a.replace(',','v')
    c = b.replace('.',',')
    return c.replace('v','.')

def ChequeMoradiaCheck(valor):
    if valor == "R$ 42mil":
        resposta = 42000
    else:
        resposta = 45600
    return resposta

def tratarcoeficiente(valor):
    A0 = str(valor)
    A1 = A0.replace(",",".")
    A2 = float(A1)
    return A2


if flow == "Otimização Plano":
    c1, c2, c3, c4 = st.columns((2,2,2, 2))
    with c1:
        EMPREENDIMENTO = st.selectbox("EMPREENDIMENTO:", options=["AGL25","AGL28","FSA06","FSA07","FSA09"])
        TIPOLOGIA = st.selectbox("TIPOLOGIA:", options=["Garden","Padrao","Com Varanda"])
       
        
    with c2:
        VGV = st.text_input("VALOR DE VENDA:", disabled=True, value=dict_tabela["preco"][EMPREENDIMENTO][TIPOLOGIA])
        GARANTIDO_TAB = st.text_input("GARANTIDO MÍN:", disabled=True, value=dict_tabela["garantido"][EMPREENDIMENTO]["minimo"])
        corretor_input = st.text_input("NOME CORRETOR: ")
        
        
    sac.divider(label='PLANO PGTO | PRÉ | PÓS', align='center')
    plano1, plano2, plano3, plano4, plano5 = st.columns((2,2,1,1,2))
    
    with plano1:
        TIPO_000 = st.selectbox("SINAL", options=["ATO","MENSAIS PÓS","ANUAL","SEMESTRAL","TRIMESTRAL"], disabled=True)
        TIPO_001 = st.selectbox("TIPO PGTO 1:", options=["MENSAIS PRÉ","MENSAIS PÓS","ANUAL","SEMESTRAL","TRIMESTRAL"], disabled=True)
        TIPO_002 = st.selectbox("TIPO PGTO 2:", options=["MENSAIS PÓS","MENSAIS PRÉ","ANUAL","SEMESTRAL","TRIMESTRAL"], disabled=True)
        TIPO_003 = st.selectbox("TIPO PGTO 3:", options=["ANUAL","MENSAIS PRÉ","ANUAL","SEMESTRAL","TRIMESTRAL"], disabled=True)
        TIPO_004 = st.selectbox("TIPO PGTO 4:", options=["SEMESTRAL","MENSAIS PRÉ","ANUAL","SEMESTRAL","TRIMESTRAL"], disabled=True)
        TIPO_005 = st.selectbox("TIPO PGTO 5:", options=["TRIMESTRAL","MENSAIS PRÉ","ANUAL","SEMESTRAL","TRIMESTRAL"], disabled=True)
        
        
    with plano2:
        VALOR_TP_000 = st.text_input("SINAL :", disabled=False,value=0.00)
        VALOR_TP_001 = st.text_input("VALOR TP 001:", disabled=False,value=0.00)
        VALOR_TP_002 = st.text_input("VALOR TP 002:", disabled=False,value=0.00)
        VALOR_TP_003 = st.text_input("VALOR TP 003:", disabled=False,value=0.00)
        VALOR_TP_004 = st.text_input("VALOR TP 004:", disabled=False,value=0.00)
        VALOR_TP_005 = st.text_input("VALOR TP 005:", disabled=False,value=0.00)
      

    with plano3:
        dict_tipo = {"MENSAIS PRÉ":"Máx 24x pré","MENSAIS PÓS":"Máx 36x pós","ANUAL":"Máx 4x","SEMESTRAL":"Máx 6x","TRIMESTRAL":"Máx 6x"}
        QTD_000 = st.text_input("QTD SINAL:", disabled=False, value=1)
        QTD_001 = st.text_input("QTD TP_001:", disabled=False, placeholder=dict_tipo[TIPO_001], value=24)
        QTD_002 = st.text_input("QTD TP_002:", disabled=False, placeholder=dict_tipo[TIPO_002], value=36)
        QTD_003 = st.text_input("QTD TP_003:", disabled=False, placeholder=dict_tipo[TIPO_003], value=0)
        QTD_004 = st.text_input("QTD TP_004:", disabled=False, placeholder=dict_tipo[TIPO_004], value=0)
        QTD_005 = st.text_input("QTD TP_005:", disabled=False, placeholder=dict_tipo[TIPO_005], value=0)

    with plano4:
        TOTAL_TIPO000 = np.round(float(VALOR_TP_000)* int(QTD_000),2)
        TOTAL_TIPO001 = np.round(float(VALOR_TP_001)* int(QTD_001),2)
        TOTAL_TIPO002 = np.round(float(VALOR_TP_002)* int(QTD_002),2)
        TOTAL_TIPO003 = np.round(float(VALOR_TP_003)* int(QTD_003),2)
        TOTAL_TIPO004 = np.round(float(VALOR_TP_004)* int(QTD_004),2)
        TOTAL_TIPO005 = np.round(float(VALOR_TP_005)* int(QTD_005),2)
        
        TOTAL_TP_000 = st.text_input("TOTAL SINAL", value=TOTAL_TIPO000, disabled=True)
        TOTAL_TP_001 = st.text_input("TOTAL TP_001", value=TOTAL_TIPO001, disabled=True)
        TOTAL_TP_002 = st.text_input("TOTAL TP_002", value=TOTAL_TIPO002, disabled=True)
        TOTAL_TP_003 = st.text_input("TOTAL TP_003", value=TOTAL_TIPO003, disabled=True)
        TOTAL_TP_004 = st.text_input("TOTAL TP_004", value=TOTAL_TIPO004, disabled=True)
        TOTAL_TP_005 = st.text_input("TOTAL TP_005", value=TOTAL_TIPO005, disabled=True)
        

    with plano5:
        import datetime
        DATE_TP_000 = st.date_input("DATA SINAL")
        DATE_TP_001 = st.date_input("DATA TP_001")
        RANGE_DATA = pd.date_range(DATE_TP_001,periods=int(QTD_001),freq="M")
        DATE_TP_002 = st.text_input("DATA TP_002",value=RANGE_DATA[-1].strftime("%Y/%m/%d"))
        DATE_TP_003 = st.text_input("DATA TP_003")
        DATE_TP_004 = st.text_input("DATA TP_004")
        DATE_TP_005 = st.text_input("DATA TP_005")



    sac.divider(label='FINANCIAMENTO | SUBSÍDIO | FGTS', align='center')
    f1, f2, f3, f4 = st.columns((2,2,2,2))
    with f1:
        FINANCIAMENTO = st.text_input("FINANCIAMENTO:", value=0.0)
    with f2:
        SUBSIDIO = st.text_input("SUBSIDIO:", value=0.0)
    with f3:
        FGTS = st.text_input("FGTS:", value=0.0)
    with f4:
        CHEQUE = st.radio("CHEQUE:",options=["0,00", "42.000,00", "45.800,00"])
        dict_cheque = {"0,00":0, "42.000,00":42000, "45.800,00":45800}
    
    
    
    PLANO_TOTAL_PGTO = float(FINANCIAMENTO) + float(SUBSIDIO) + float(FGTS) + dict_cheque[CHEQUE] + float(TOTAL_TIPO000) + float(TOTAL_TIPO001) + float(TOTAL_TIPO002) + float(TOTAL_TIPO003) + float(TOTAL_TIPO004) + float(TOTAL_TIPO005)
    GARANTIFO_PLANO_REAL = float(FINANCIAMENTO) + float(SUBSIDIO) + float(FGTS) + float(VALOR_TP_000)
    
    SALDO002 = GARANTIFO_PLANO_REAL-float(GARANTIDO_TAB)
    if SALDO002 > 0:
        GAR = f"{conversor_moeda_brasil(SALDO002)} 🟢"
    else:
        GAR= f"{conversor_moeda_brasil(SALDO002)} 🔴"
    
    with c3:
        PLANO_PGTO = st.text_input("PLANO PGTO:", disabled=True, value=conversor_moeda_brasil(PLANO_TOTAL_PGTO))
        GARANTIDO_REAL= st.text_input("GARANTIDO REAL:", disabled=True, value=conversor_moeda_brasil(GARANTIFO_PLANO_REAL))
        
        cc1, cc2, cc3, cc4 = st.columns((0.1, 2, 2, 2))
        
        with cc2.expander("Coeficientes: "):
            A0 = ExcecaoError(GARANTIFO_PLANO_REAL, PLANO_TOTAL_PGTO)
            COEF1 = float(0.73)
            COEF2 = float(0.75)
            COEF3 = float(0.77)
            
            if A0 < COEF1:
                IPERF = 0
            elif A0 > COEF1 and A0 <=COEF2:
                IPERF = 300
            elif A0 > COEF2 and A0 <=COEF3:
                IPERF = 400
            elif A0 > COEF3:
              IPERF = 500
            else:
                IPERF = 500
                
            IP = st.text_input("IP Gar:", disabled=True, value=conversor_moeda_brasil(IPERF))
            
        with cc3.expander("Coeficientes:"):
            A1 = (PLANO_TOTAL_PGTO/float(VGV))-1
            #st.write(A1)
            COEF11 = float(0.025)
            COEF21 = float(0.040)
            COEF31 = float(0.050)
            
            if A1 < COEF11:
                IPERF1 = 0
            elif A1 > COEF11 and A1 <=COEF21:
                IPERF1 = 300
            elif A1 > COEF21 and A1 <=COEF31:
                IPERF1 = 400
            elif A1 > COEF31:
                IPERF1 = 500
            else:
                IPERF1 = 500
               
            IP1 = st.text_input("IP Preço:", disabled=True, value=conversor_moeda_brasil(IPERF1))
            
        with cc4.expander("Coeficientes:  "):
            A2 = ExcecaoError(float(VALOR_TP_000), PLANO_TOTAL_PGTO)
            COEF12 = float(0.02)
            COEF22 = float(0.03)
            COEF32 = float(0.04)
            
            if A2 < COEF12:
                IPERF12 = 0
            elif A2 > COEF12 and A2 <=COEF22:
                IPERF12 = 300
            elif A2 > COEF22 and A2 <=COEF32:
                IPERF12 = 400
            elif A2 > COEF32:
                IPERF12 = 500
            else:
                IPERF12 = 500
                
            IP2 = st.text_input("IP Sinal:", disabled=True, value=conversor_moeda_brasil(IPERF12))
        
    with c4:
        SALDO001 = PLANO_TOTAL_PGTO-float(VGV)
        if SALDO001 > 0:
            POSITIVO = f"{conversor_moeda_brasil(SALDO001)} 🟢"
        else:
            POSITIVO = f"{conversor_moeda_brasil(SALDO001)} 🔴"

        SALDO_PGTO = st.text_input("Gap Plano pgto:", disabled=True, value=POSITIVO)
        SALDO_GARANTIDO = st.text_input("Gap Garantido:", disabled=True, value=GAR)
    
        c11, c12, c13, c14 = st.columns((0.1, 2, 2, 2))
        
        with c12:
            with st.expander("Indicadores:"):
                IP11 = st.text_input("Metric Gar:", disabled=True, value=np.round(A0,3))
        with c13:
            with st.expander("Indicadores:  "):
                IP12 = st.text_input("Metric Preço:", disabled=True, value=np.round(A1,3))
        with c14:
            with st.expander("Indicadores:   "):
                IP13 = st.text_input("Metric Sinal:", disabled=True, value=np.round(A2,4))
            
    df = pd.DataFrame()
    df["EMP"] = [EMPREENDIMENTO]
    df["TIPOLOGIA"] = [TIPOLOGIA]
    df["VGV"] = [VGV]
    df["TIPO_000"] = [TIPO_000]
    df["TOTAL_TIPO000"] = [TOTAL_TIPO000]
    df["TIPO_001"] = [TIPO_001]
    df["TOTAL_TIPO001"] = [TOTAL_TIPO001]
    df["TIPO_002"] = [TIPO_002]
    df["TOTAL_TIPO002"] = [TOTAL_TIPO002]
    df["TIPO_003"] = [TIPO_003]
    df["TOTAL_TIPO003"] = [TOTAL_TIPO003]
    df["TIPO_004"] = [TIPO_004]
    df["TOTAL_TIPO004"] = [TOTAL_TIPO004]
    df["TIPO_005"] = [TIPO_005]
    df["TOTAL_TIPO005"] = [TOTAL_TIPO005]

    #st.dataframe(df.T)

from babel.numbers import format_currency
def conversor_moeda_brasil(amount):
    return format_currency(amount, 'BRL', locale='pt_BR')

import secrets

def gerar_token(quantidade_bytes=3):
    # Gera um token seguro aleatório
    token = secrets.token_hex(quantidade_bytes)
    return token

# Gera um token usando o padrão de 16 bytes (o que resulta em uma string de 32 caracteres hexadecimais)
token_aleatorio = gerar_token()



html_corpo_email = """
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ccc;
            background: #f9f9f9;
            border-radius: 10px
        }}
        .header, .footer {{
            text-align: center;
            background: #00AAE0; /* Cor atualizada aqui */
            color: #fff;
            padding: 15px 2px;
            border-radius: 10px
        }}
        .content {{
            padding: 20px;
            border-radius: 10px
        }}
        .content p {{
            margin-bottom: 10px;
            border-radius: 10px
        }}
        .content p strong {{
            display: block;
            color: #555;
            border-radius: 10px
        }}
        .logo {{
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 50%; /* Ajuste conforme necessário */
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://7lm.com.br/wp-content/uploads/2023/03/logo_branca_aprovada_final_slogan.svg" class="logo" alt="Logomarca" style="width: 110px">  
            <h1>Solicitação de Aprovação de Venda</h1>
        </div>
        <div class="content">
            <p>Solicitação de Aprovação de Venda | Proposta: {token}</p>
            <p>Corretor: {corretor}</p>
            <p>Empreendimento: {empreendimento}</p>
            <p>Tipologia: {tipologia}</p>
            <p>Valor Tabela: {vgv}</p>
            <p>Proposta: {Proposta}</p>
            <p>Sinal: {plano_pgto}</p>
            <p>Mensais Pré: {mensais_pre}</p>
            <p>Mensais Pós: {mensais_pos}</p>
            
            <p>Anuais: {Anuais}</p>
            <p>Semestrais: {Semestrais}</p>
            <p>Trimestrais: {Trimestrais}</p>
            
            <p>Garantido Real: {garantido_real}</p>
            <p>Gap Plano de Pagamento: {gap_plano_pgto}</p>
            <p>Gap Garantido: {gap_garantido}</p>
            <p>Total Bônus: {total_bonus}</p>
        </div>
        <div class="footer">
            <p><em>Este é um e-mail gerado automaticamente, por favor não responda.</em></p>
        </div>
    </div>
</body>
</html>
"""


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_solicitacao_aprovacao(dados_resumo, email_destinatario):
    # Configurações de e-mail e lógica de envio permanecem inalteradas...
    smtp_servidor = "smtp.office365.com"
    smtp_porta = 587
    smtp_usuario = "automacao@grupoimerge.com.br"
    smtp_senha = "Acesso@123"
    
    # Criação da mensagem de e-mail
    mensagem = MIMEMultipart()
    mensagem['From'] = smtp_usuario
    mensagem['To'] = email_destinatario  # Substitua pelo e-mail do destinatário real
    mensagem['Subject'] = "Solicitação de Aprovação de Venda"   
    
    corpo_email = html_corpo_email.format(
        token=dados_resumo.get('Token', 'Não especificado'),
        corretor=dados_resumo.get('Corretor', 'Não especificado'),
        empreendimento = dados_resumo.get('Empreendimento', 'Não especificado'),
        tipologia = dados_resumo.get('Tipologia', 'Não especificado'),
        vgv = dados_resumo.get('Valor Tabela', 'Não especificado'),
        Proposta = dados_resumo.get('Proposta', 'Não especificado'),
        plano_pgto = dados_resumo.get('Plano de Pagamento', 'Não especificado'),
        mensais_pre = dados_resumo.get('Mensais Pré', 'Não especificado'),
        mensais_pos = dados_resumo.get('Mensais Pós', 'Não especificado'),
        
        Anuais = dados_resumo.get('Anuais', 'Não especificado'),
        Semestrais= dados_resumo.get('Semestrais', 'Não especificado'),
        Trimestrais = dados_resumo.get('Trimestrais', 'Não especificado'),
        
        garantido_real = dados_resumo.get('Garantido_Real', 'Não especificado'),
        gap_plano_pgto = dados_resumo.get('Gap_Plano_de_Pagamento', 'Não especificado'),
        gap_garantido = dados_resumo.get('Gap_Garantido', 'Não especificado'),
        total_bonus = dados_resumo.get('Total Bônus', 'Não especificado')
    )
    # Enviando o e-mail
    mensagem.attach(MIMEText(corpo_email, 'html'))
    try:
        servidor = smtplib.SMTP(smtp_servidor, smtp_porta)
        servidor.starttls()
        servidor.login(smtp_usuario, smtp_senha)
        servidor.sendmail(mensagem['From'], mensagem['To'], mensagem.as_string())
        servidor.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# Suponho que você esteja coletando esses dados de algum lugar; certifique-se de que eles estão corretos.
dados_resumo = {
    "Token":token_aleatorio,
    "Corretor": corretor_input,  # Substitua por corretor_input se estiver coletando do usuário
    "Empreendimento": EMPREENDIMENTO,  # Substitua por EMPREENDIMENTO se estiver coletando do usuário
    "Tipologia": TIPOLOGIA,  # Substitua por TIPOLOGIA se estiver coletando do usuário
    "Valor Tabela": conversor_moeda_brasil(VGV),  # Substitua por VGV se estiver coletando do usuário
    "Proposta": conversor_moeda_brasil(PLANO_TOTAL_PGTO),
    "Plano de Pagamento":conversor_moeda_brasil(VALOR_TP_000),
    "Mensais Pré":f"{conversor_moeda_brasil(VALOR_TP_001)} em {QTD_001}x com a primeira para o dia: {DATE_TP_001}",
    "Mensais Pós":f"{conversor_moeda_brasil(VALOR_TP_002)} em {QTD_002}x com a primeira para o dia: {DATE_TP_002}",
    "Anuais":f"{conversor_moeda_brasil(VALOR_TP_003)} em {QTD_003}x com a primeira para o dia: {DATE_TP_003}",
    
    "Semestrais":f"{conversor_moeda_brasil(VALOR_TP_004)} em {QTD_004}x com a primeira para o dia: {DATE_TP_004}",
    "Trimestrais":f"{conversor_moeda_brasil(VALOR_TP_005)} em {QTD_005}x com a primeira para o dia: {DATE_TP_005}",
    "Plano_de_Pagamento": 0,  # Substitua por valor real
    "Garantido_Real": conversor_moeda_brasil(GARANTIFO_PLANO_REAL),  # Substitua por GARANTIDO_REAL se estiver coletando do usuário
    "Gap_Plano_de_Pagamento":SALDO_PGTO,#"Informação do Gap do Plano de Pagamento",  # Substitua por SALDO_PGTO se estiver coletando do usuário
    "Gap_Garantido":SALDO_GARANTIDO,#GAR ,# "Informação do Gap Garantido",  # Substitua por SALDO_GARANTIDO se estiver coletando do usuário
    "Total_Bônus": "Valor do Total de Bônus"  # Substitua por valor real
}

with st.sidebar.expander("Solicitação:"):
    email = st.text_input("Email")
    btn_enviar = st.button("Enviar e-mail")

    if btn_enviar and email:  # Verifica se o botão foi pressionado e se o e-mail não está vazio
        enviar_solicitacao_aprovacao(dados_resumo, email)
        st.success("E-mail enviado com sucesso!")
    elif btn_enviar:  # Se o botão foi pressionado, mas nenhum e-mail foi fornecido
        st.error("Por favor, forneça um endereço de e-mail válido.")


