
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import altair as alt
import pandas as pd
import streamlit as st

from consultar_s3 import consultar_telemetria
from historico_s3 import consultar_historico
from detector import detectar_anomalias
from agente_ia import analisar_telemetria


# ============================================================
# CONFIGURACOES
# ============================================================

st.set_page_config(
    page_title="IoT Agent | Monitoring",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

FUSO = ZoneInfo("America/Maceio")

TEMP_MIN = 20
TEMP_MAX = 35
UMIDADE_MIN = 40
UMIDADE_MAX = 80

INTERVALO_ATUALIZACAO = 10
INTERVALO_HISTORICO = 60


# ============================================================
# IDENTIDADE VISUAL
# ============================================================

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
    }

    .stApp {
        background: #0B1220;
        color: #E2E8F0;
    }

    [data-testid="stHeader"] {
        background: #0B1220;
    }

    [data-testid="stSidebar"] {
        background: #111C2E;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    h1, h2, h3 {
        color: #F1F5F9 !important;
        letter-spacing: -0.025em;
    }

    h1 {
        font-weight: 700 !important;
    }

    [data-testid="stMetric"] {
        background: #172338;
        border: 1px solid #29374B;
        border-radius: 12px;
        padding: 20px;
        min-height: 135px;
    }

    [data-testid="stMetricLabel"] {
        color: #94A3B8;
    }

    [data-testid="stMetricValue"] {
        color: #F1F5F9;
        font-weight: 650;
    }

    div.stButton > button {
        background: #2563EB;
        border: 1px solid #3B82F6;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        min-height: 42px;
    }

    div.stButton > button:hover {
        background: #1D4ED8;
        border-color: #60A5FA;
        color: white;
    }

    div[data-testid="stAlert"] {
        border-radius: 8px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #29374B;
        border-radius: 8px;
    }

    hr {
        border-color: #29374B;
    }

    .iot-subtitle {
        color: #94A3B8;
        font-size: 0.92rem;
        margin-top: -12px;
        margin-bottom: 20px;
    }

    .iot-section-label {
        color: #94A3B8;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .iot-status {
        display: inline-block;
        border-radius: 6px;
        padding: 7px 12px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }

    .iot-status-normal {
        color: #86EFAC;
        background: #123A30;
        border: 1px solid #276749;
    }

    .iot-status-alerta {
        color: #FCA5A5;
        background: #44232B;
        border: 1px solid #7F3643;
    }

    .iot-alert {
        background: #281D28;
        border-left: 3px solid #F87171;
        padding: 13px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
        color: #FECACA;
        font-size: 0.92rem;
    }

    .iot-info {
        color: #94A3B8;
        font-size: 0.85rem;
    }

    .iot-footer {
        color: #64748B;
        font-size: 0.78rem;
        padding-top: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FUNCOES AUXILIARES
# ============================================================

def agora():
    return datetime.now(timezone.utc)


def preparar_historico(leituras):
    colunas = [
        "timestamp",
        "temperatura",
        "umidade"
    ]

    if not leituras:
        return pd.DataFrame(columns=colunas)

    df = pd.DataFrame(leituras)

    if not all(coluna in df.columns for coluna in colunas):
        raise ValueError(
            "Historico sem os campos obrigatorios."
        )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
        errors="coerce"
    )

    df["temperatura"] = pd.to_numeric(
        df["temperatura"],
        errors="coerce"
    )

    df["umidade"] = pd.to_numeric(
        df["umidade"],
        errors="coerce"
    )

    df = df.dropna(
        subset=colunas
    ).copy()

    df["timestamp"] = df["timestamp"].dt.tz_convert(
        FUSO
    )

    return df.sort_values(
        "timestamp"
    ).reset_index(drop=True)


def formatar_data(timestamp):
    if not timestamp:
        return "Nao informado"

    momento = datetime.fromisoformat(
        str(timestamp).replace("Z", "+00:00")
    )

    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=timezone.utc)

    return momento.astimezone(FUSO).strftime(
        "%d/%m/%Y %H:%M:%S"
    )


def atualizar_leitura():
    """
    Atualiza apenas a leitura mais recente.

    Nao executa o Qwen3 automaticamente.
    """

    dados = consultar_telemetria()

    st.session_state.telemetria = dados
    st.session_state.ultima_atualizacao = agora()


def atualizar_historico():
    """
    Sincroniza o historico completo do S3.
    """

    leituras = consultar_historico()

    st.session_state.historico = preparar_historico(
        leituras
    )

    st.session_state.ultima_sincronizacao = agora()


def atualizar_tudo():
    atualizar_leitura()
    atualizar_historico()


def historico_precisa_atualizar():
    ultima = st.session_state.ultima_sincronizacao

    if ultima is None:
        return True

    segundos = (agora() - ultima).total_seconds()

    return segundos >= INTERVALO_HISTORICO


def contar_alertas(df):
    return sum(
        detectar_anomalias(
            linha.temperatura,
            linha.umidade
        )["status"] == "ALERTA"
        for linha in df.itertuples()
    )


def grafico_historico(df, coluna, minimo, maximo, titulo):
    dados_grafico = df[
        ["timestamp", coluna]
    ].rename(
        columns={coluna: "valor"}
    ).copy()

    linha = alt.Chart(dados_grafico).mark_line(
        color="#38BDF8",
        strokeWidth=2.5,
        point=True
    ).encode(
        x=alt.X(
            "timestamp:T",
            title="Data e hora"
        ),
        y=alt.Y(
            "valor:Q",
            title=titulo,
            scale=alt.Scale(zero=False)
        ),
        tooltip=[
            alt.Tooltip(
                "timestamp:T",
                title="Horario",
                format="%d/%m/%Y %H:%M:%S"
            ),
            alt.Tooltip(
                "valor:Q",
                title=titulo,
                format=".1f"
            )
        ]
    )

    limite_minimo = alt.Chart(
        pd.DataFrame({"limite": [minimo]})
    ).mark_rule(
        color="#F59E0B",
        strokeDash=[5, 5],
        strokeWidth=1.5
    ).encode(
        y="limite:Q"
    )

    limite_maximo = alt.Chart(
        pd.DataFrame({"limite": [maximo]})
    ).mark_rule(
        color="#F87171",
        strokeDash=[5, 5],
        strokeWidth=1.5
    ).encode(
        y="limite:Q"
    )

    grafico = (
        linha + limite_minimo + limite_maximo
    ).properties(
        height=290
    ).configure_axis(
        labelColor="#94A3B8",
        titleColor="#CBD5E1",
        gridColor="#29374B",
        domainColor="#475569"
    ).configure_view(
        stroke=None
    )

    st.altair_chart(
        grafico,
        use_container_width=True
    )

    st.caption(
        f"Limite minimo: {minimo} | "
        f"Limite maximo: {maximo}"
    )


# ============================================================
# SESSION STATE
# ============================================================

valores_iniciais = {
    "telemetria": None,
    "historico": pd.DataFrame(),
    "analise": None,
    "analise_timestamp": None,
    "ultima_atualizacao": None,
    "ultima_sincronizacao": None,
    "atualizacao_automatica": True,
    "erro_consulta": None
}

for chave, valor in valores_iniciais.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor


# ============================================================
# CABECALHO E CONTROLES
# ============================================================

col_titulo, col_controle = st.columns(
    [3, 1],
    vertical_alignment="center"
)

with col_titulo:
    st.title("IoT Agent")

    st.markdown(
        '<div class="iot-subtitle">'
        'Industrial Monitoring & Intelligence'
        '</div>',
        unsafe_allow_html=True
    )

with col_controle:
    st.caption("Fonte de dados: Amazon S3")

    st.toggle(
        "Atualizacao automatica",
        key="atualizacao_automatica"
    )

    atualizar_manual = st.button(
        "Atualizar dados",
        use_container_width=True
    )

st.divider()


# ============================================================
# CARGA INICIAL E ATUALIZACAO MANUAL
# ============================================================

if atualizar_manual or st.session_state.telemetria is None:
    try:
        with st.spinner("Consultando Amazon S3..."):
            atualizar_tudo()

        st.session_state.erro_consulta = None

    except Exception as erro:
        st.session_state.erro_consulta = str(erro)

        if st.session_state.telemetria is None:
            st.error(
                "Nao foi possivel carregar os dados: "
                + str(erro)
            )
            st.stop()


# ============================================================
# FRAGMENTO COM ATUALIZACAO AUTOMATICA
# ============================================================

@st.fragment(run_every="10s")
def painel_monitoramento():
    """
    Atualiza a leitura a cada 10 segundos quando
    a atualizacao automatica estiver ativada.

    O historico e sincronizado a cada 60 segundos.
    """

    if st.session_state.atualizacao_automatica:
        try:
            atualizar_leitura()

            if historico_precisa_atualizar():
                atualizar_historico()

            st.session_state.erro_consulta = None

        except Exception as erro:
            st.session_state.erro_consulta = str(erro)

    if st.session_state.erro_consulta:
        st.warning(
            "Falha na ultima consulta ao S3. "
            "Exibindo os dados disponiveis."
        )

        with st.expander("Detalhes da falha"):
            st.code(st.session_state.erro_consulta)

    dados = st.session_state.telemetria
    df = st.session_state.historico

    if dados is None:
        st.info("Aguardando telemetria.")
        return

    temperatura = float(dados["temperatura"])
    umidade = float(dados["umidade"])

    resultado = detectar_anomalias(
        temperatura,
        umidade
    )

    status = resultado["status"]

    # --------------------------------------------------------
    # MONITORAMENTO ATUAL
    # --------------------------------------------------------

    st.markdown(
        '<div class="iot-section-label">'
        'Monitoramento atual'
        '</div>',
        unsafe_allow_html=True
    )

    col_dispositivo, col_status = st.columns(
        [3, 1],
        vertical_alignment="center"
    )

    with col_dispositivo:
        st.write(
            "**Dispositivo:** "
            + str(dados.get("dispositivo", "Desconhecido"))
        )

        st.caption(
            "Ultima medicao: "
            + formatar_data(dados.get("timestamp"))
        )

    with col_status:
        classe = (
            "iot-status-normal"
            if status == "NORMAL"
            else "iot-status-alerta"
        )

        st.markdown(
            f'<span class="iot-status {classe}">'
            f'{status}'
            '</span>',
            unsafe_allow_html=True
        )

    col_temp, col_umidade, col_alertas = st.columns(3)

    with col_temp:
        st.metric(
            "Temperatura",
            f"{temperatura:.1f} °C"
        )

    with col_umidade:
        st.metric(
            "Umidade relativa",
            f"{umidade:.1f}%"
        )

    with col_alertas:
        st.metric(
            "Anomalias ativas",
            len(resultado["alertas"])
        )

    if st.session_state.ultima_atualizacao:
        horario = (
            st.session_state.ultima_atualizacao
            .astimezone(FUSO)
            .strftime("%H:%M:%S")
        )

        st.caption(
            f"Ultima consulta ao S3: {horario} | "
            f"Atualizacao automatica: "
            f"{'ativa' if st.session_state.atualizacao_automatica else 'desativada'}"
        )

    # --------------------------------------------------------
    # ALERTAS
    # --------------------------------------------------------

    st.divider()
    st.subheader("Deteccao automatica")

    if status == "NORMAL":
        st.success(
            "Todos os parametros estao dentro dos limites."
        )

    else:
        st.markdown(
            '<div class="iot-section-label">'
            'Ocorrencias identificadas'
            '</div>',
            unsafe_allow_html=True
        )

        for alerta in resultado["alertas"]:
            st.markdown(
                '<div class="iot-alert">'
                + alerta
                + '</div>',
                unsafe_allow_html=True
            )

    # --------------------------------------------------------
    # HISTORICO
    # --------------------------------------------------------

    st.divider()
    st.subheader("Historico de telemetria")

    if df.empty:
        st.info(
            "Nenhum registro historico encontrado."
        )

    else:
        total = len(df)
        quantidade_alertas = contar_alertas(df)

        percentual_alertas = (
            quantidade_alertas / total * 100
            if total
            else 0
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total de leituras",
                total
            )

        with col2:
            st.metric(
                "Leituras com alerta",
                quantidade_alertas
            )

        with col3:
            st.metric(
                "Taxa de alertas",
                f"{percentual_alertas:.1f}%"
            )

        col_grafico_temp, col_grafico_umidade = (
            st.columns(2)
        )

        with col_grafico_temp:
            st.markdown("#### Temperatura")

            grafico_historico(
                df,
                coluna="temperatura",
                minimo=TEMP_MIN,
                maximo=TEMP_MAX,
                titulo="Temperatura (°C)"
            )

        with col_grafico_umidade:
            st.markdown("#### Umidade relativa")

            grafico_historico(
                df,
                coluna="umidade",
                minimo=UMIDADE_MIN,
                maximo=UMIDADE_MAX,
                titulo="Umidade (%)"
            )

        with st.expander(
            "Consultar registros detalhados"
        ):
            tabela = df.copy()

            tabela["timestamp"] = (
                tabela["timestamp"]
                .dt.strftime("%d/%m/%Y %H:%M:%S")
            )

            st.dataframe(
                tabela,
                use_container_width=True,
                hide_index=True
            )


painel_monitoramento()


# ============================================================
# ANALISE INTELIGENTE
# ============================================================

st.divider()
st.subheader("Analise inteligente")

st.caption(
    "Modelo local: Qwen3 8B | "
    "Execucao via Ollama"
)

if st.button(
    "Executar analise com IA",
    use_container_width=True
):
    dados = st.session_state.telemetria

    if dados is None:
        st.warning(
            "Nenhuma telemetria disponivel para analise."
        )

    else:
        with st.spinner(
            "Processando telemetria com Qwen3..."
        ):
            st.session_state.analise = analisar_telemetria(
                float(dados["temperatura"]),
                float(dados["umidade"])
            )

            st.session_state.analise_timestamp = (
                dados.get("timestamp")
            )


if st.session_state.analise is not None:
    analise = st.session_state.analise

    dados = st.session_state.telemetria

    if (
        dados is not None
        and st.session_state.analise_timestamp
        != dados.get("timestamp")
    ):
        st.info(
            "Esta analise corresponde a uma leitura anterior. "
            "Execute uma nova analise para atualizar o resultado."
        )

    if analise["ia_disponivel"] is False:
        st.warning(
            "Modelo indisponivel. "
            "A deteccao deterministica permanece ativa."
        )

    with st.container(border=True):
        st.markdown(
            analise["analise_ia"]
        )


# ============================================================
# RODAPE
# ============================================================

st.divider()

st.markdown(
    '<div class="iot-footer">'
    'IoT Agent | FastAPI / Amazon S3 / Python / '
    'Ollama / Qwen3 8B'
    '</div>',
    unsafe_allow_html=True
)
