import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from scipy import stats
import time
from fpdf import FPDF
import unicodedata

# ==========================================
# 0. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(layout="wide", page_title="Terminal Análisis CATL (300750.SZ)")

st.markdown("""
<style>
    :root {
        --bg-dark: #0d1117;
        --panel-bg: #161b22;
        --text-main: #c9d1d9;
        --text-muted: #8b949e;
        --accent-blue: #58a6ff;
        --accent-green: #3fb950;
        --accent-red: #f85149;
        --border-color: #30363d;
    }
    .stApp { background-color: var(--bg-dark); color: var(--text-main); }
    div.stExpander, div.css-1r6slb0, div.block-container { color: var(--text-main); }
    .custom-panel {
        background-color: var(--panel-bg); border: 1px solid var(--border-color);
        border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    .header-container { padding-bottom: 20px; border-bottom: 1px solid var(--border-color); margin-bottom: 20px; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 600; }
    .metric-value { font-size: 28px; font-weight: bold; margin: 10px 0; }
    .green-text { color: var(--accent-green); }
    .red-text { color: var(--accent-red); }
    .blue-text { color: var(--accent-blue); }
    .muted-text { color: var(--text-muted); font-size: 14px;}
    .status-badge {
        display: inline-block; padding: 5px 10px; border-radius: 20px; 
        font-size: 12px; font-weight: bold; background-color: var(--accent-green); color: #fff;
    }
    .verdict-panel {
        text-align: center; padding: 30px; background: linear-gradient(145deg, #161b22, #0d1117); 
        border: 2px solid var(--border-color); border-radius: 12px;
    }
    #verdict-result { font-size: 48px; font-weight: bold; text-transform: uppercase; margin: 15px 0; text-shadow: 0 0 20px rgba(255,255,255,0.2); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 0.5 VENTANAS DE ALERTA Y SEGURIDAD (GATEKEEPERS)
# ==========================================

# Inicializar variables en la memoria de la sesión
if 'indicaciones_leidas' not in st.session_state:
    st.session_state.indicaciones_leidas = False
if 'quiz_aprobado' not in st.session_state:
    st.session_state.quiz_aprobado = False
if 'mensaje_error' not in st.session_state:
    st.session_state.mensaje_error = False

# --- VENTANA 1: INDICACIONES ---
if not st.session_state.indicaciones_leidas:
    st.markdown("<h2 style='text-align: center; color: var(--accent-blue);'>⚠️ Alerta: Indicaciones de Uso</h2>", unsafe_allow_html=True)
    
    st.info("""
    **Indicaciones:**
    1. Debes valorar el riesgo geopolítico de la compañía (+ -).
    2. A partir de los gráficos de análisis tecnico, debes decidir tu postura (bajista, neutral o alcista)
    3. El calculo de Beta, análisis DuPont y test de acidez, son alimentados en tiempo real, asi como la cotización de la acción.
    """)
    
    # Botón centrado para continuar
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Entendido", use_container_width=True):
            st.session_state.indicaciones_leidas = True
            st.rerun() # Recarga la página para pasar a la siguiente pantalla
            
    st.stop() # Detiene la ejecución para que no se vea el resto de la app

# --- VENTANA 2: QUIZ DE SEGURIDAD ---
if st.session_state.indicaciones_leidas and not st.session_state.quiz_aprobado:
    st.markdown("<h2 style='text-align: center; color: var(--accent-red);'>🔒 Verificación de Acceso</h2>", unsafe_allow_html=True)
    
    st.markdown("<h4 style='text-align: center;'>Antes de continuar...</h4>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white;'>Equipo mas grande en la historia del futbol :</h3>", unsafe_allow_html=True)
    st.write("") # Espacio
    
    # --- NUEVO: CSS para hacer el texto de las respuestas azul claro y negrita ---
    st.markdown("""
        <style>
        div[data-testid="stButton"] button p {
            color: #58a6ff !important; /* Azul claro (Accent Blue del tema) */
            font-weight: bold !important;
            font-size: 16px !important;
        }
        /* Opcional: Que el borde del botón también haga juego con el azul al pasar el ratón */
        div[data-testid="stButton"] button:hover {
            border-color: #58a6ff !important;
            color: #58a6ff !important;
        }
        </style>
    """, unsafe_allow_html=True)
    # -----------------------------------------------------------------------------
    
    # Contenedor vacío para mostrar los emojis dinámicamente
    espacio_mensaje = st.empty()
    
    # Función para manejar la respuesta
    def procesar_respuesta(es_correcta):
        if es_correcta:
            # Mostramos la cara feliz gigante
            espacio_mensaje.markdown("<h1 style='text-align: center; font-size: 100px;'>😌👑 SIIIIIIU!</h1>", unsafe_allow_html=True)
            time.sleep(2) # Espera segundo
            espacio_mensaje.empty() # Borra la cara feliz
            st.session_state.quiz_aprobado = True
            st.rerun() # Entra a la aplicación principal
        else:
            # Mostramos la ceja levantada y el texto
            espacio_mensaje.markdown("""
                <h1 style='text-align: center; font-size: 80px;'>🤨</h1>
                <h3 style='text-align: center; color: var(--accent-red);'>En serio!!!?</h3>
            """, unsafe_allow_html=True)
            time.sleep(1) # Espera 1 segundo
            espacio_mensaje.empty() # Borra el mensaje de error para que vuelva a intentar

    # Botones de opciones
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        if st.button("a. Barcelona", use_container_width=True): procesar_respuesta(False)
    with col_b:
        if st.button("b. Espanyol", use_container_width=True): procesar_respuesta(False)
    with col_c:
        if st.button("c. Real Madrid", use_container_width=True): procesar_respuesta(True)
    with col_d:
        if st.button("d. Bayern", use_container_width=True): procesar_respuesta(False)

    st.stop() # Detiene la ejecución hasta que responda bien
    
# A PARTIR DE AQUÍ COMIENZA A EJECUTARSE TU APLICACIÓN FINANCIERA (Sección 1 en adelante)
# ==========================================
# 1. MOTOR DE DATOS DE 3 CAPAS
# ==========================================
TICKER_CATL_PRIMARY = "300750.SZ"
TICKER_MKT_PRIMARY = "000300.SS" 
TICKER_CATL_PROXY = "LIT"
TICKER_MKT_PROXY = "ASHR"

@st.cache_data(ttl=3600)
def load_single_ticker(ticker, days_back=365*2):
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty: return None
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.droplevel(1)
        return data
    except:
        return None

def fetch_with_fallbacks(primary_ticker, proxy_ticker, days_back=365*2):
    df = load_single_ticker(primary_ticker, days_back)
    if df is not None and len(df) > 50: return df, f"Real ({primary_ticker})", 1
    df_proxy = load_single_ticker(proxy_ticker, days_back)
    if df_proxy is not None and len(df_proxy) > 50: return df_proxy, f"Proxy ETF ({proxy_ticker})", 2
    return None, "Falla", 3

def generate_simulated_data(base_price, vol, days=730):
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=days)
    returns = np.random.normal(0.0001, vol, days)
    price_path = base_price * (1 + returns).cumprod()
    return pd.DataFrame({
        'Open': price_path * np.random.uniform(0.99, 1.01, days),
        'High': price_path * np.random.uniform(1.0, 1.02, days),
        'Low': price_path * np.random.uniform(0.98, 1.0, days),
        'Close': price_path,
        'Volume': np.random.randint(1000000, 10000000, days)
    }, index=dates)

def get_integrated_data():
    df_catl, source_catl, layer_catl = fetch_with_fallbacks(TICKER_CATL_PRIMARY, TICKER_CATL_PROXY)
    df_mkt, source_mkt, layer_mkt = fetch_with_fallbacks(TICKER_MKT_PRIMARY, TICKER_MKT_PROXY)
    
    # --- CAPA DE EXTRACCIÓN FUNDAMENTAL TIEMPO REAL ---
    try:
        catl_info = yf.Ticker(TICKER_CATL_PRIMARY).info
        # YFinance devuelve el ROE como decimal (ej. 0.1856), lo multiplicamos por 100
        fund_roe = catl_info.get('returnOnEquity', 0.1856) * 100
        fund_acid = catl_info.get('quickRatio', 1.35)
        fund_source = "Tiempo Real"
    except:
        fund_roe = 18.56
        fund_acid = 1.35
        fund_source = "Estático (Respaldo)"
    # --------------------------------------------------

    if layer_catl == 3 or layer_mkt == 3:
        st.error("⚠️ Activando Capa 3: Simulación Estadística.")
        df_catl = generate_simulated_data(170, 0.025)
        df_mkt = generate_simulated_data(3500, 0.015)
        source_info = "Simulación Determinística"
    else:
        if layer_catl == 2 or layer_mkt == 2:
            st.warning(f"⚠️ Usando Capa 2: Proxy ETFs ({source_catl} y {source_mkt}).")
        source_info = f"{source_catl} vs {source_mkt}"

    current_price = df_catl['Close'].iloc[-1]
    p_change = (df_catl['Close'].iloc[-1] / df_catl['Close'].iloc[-2] - 1) * 100
    return df_catl, df_mkt, current_price, p_change, source_info, fund_roe, fund_acid, fund_source

with st.spinner('Sincronizando terminal y descargando fundamentales...'):
    df_catl, df_mkt, cur_price, cur_change, data_source, FUND_ROE, FUND_ACID, fund_source = get_integrated_data()

# ==========================================
# 2. CÁLCULOS FINANCIEROS Y BETA DINÁMICA
# ==========================================
def calculate_beta_returns(df_stock, df_market, days=365):
    end_date = df_stock.index.max()
    start_date = end_date - timedelta(days=days)
    s_slice = df_stock.loc[start_date:end_date, 'Close']
    m_slice = df_market.loc[start_date:end_date, 'Close']
    s_returns = s_slice.pct_change().dropna()
    m_returns = m_slice.pct_change().dropna()
    aligned_data = pd.merge(s_returns, m_returns, left_index=True, right_index=True, suffixes=('_s', '_m'))
    aligned_data.columns = ['Stock_Returns', 'Market_Returns']
    x = aligned_data['Market_Returns'].values
    y = aligned_data['Stock_Returns'].values
    if len(x) < 20: return 1.0, 0, 0, 0, 0, aligned_data
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return slope, intercept, r_value**2, p_value, std_err, aligned_data

beta_val, beta_intercept, r2_val, p_val, std_err, returns_df = calculate_beta_returns(df_catl, df_mkt)

def apply_technicals(df):
    temp_df = df.copy()
    ma20 = temp_df['Close'].rolling(window=20).mean()
    std20 = temp_df['Close'].rolling(window=20).std()
    temp_df['BB_Up'] = ma20 + (std20 * 2)
    temp_df['BB_Dn'] = ma20 - (std20 * 2)
    temp_df['BB_MA'] = ma20
    delta = temp_df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    temp_df['RSI'] = 100 - (100 / (1 + rs))
    exp1 = temp_df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = temp_df['Close'].ewm(span=26, adjust=False).mean()
    temp_df['MACD'] = exp1 - exp2
    temp_df['MACD_Signal'] = temp_df['MACD'].ewm(span=9, adjust=False).mean()
    temp_df['MACD_Hist'] = temp_df['MACD'] - temp_df['MACD_Signal']
    return temp_df

df_catl_tech = apply_technicals(df_catl)

# ==========================================
# 3. INTERFAZ Y HEADER
# ==========================================
change_class = "green-text" if cur_change >= 0 else "red-text"
logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/CATL_logo.svg/512px-CATL_logo.svg.png"

st.markdown(f"""
<div class="header-container">
    <div class="logo-container">
        <img src="{logo_url}" class="company-logo" alt="CATL Logo">
    </div>
    <div>
        <h1>Análisis Cuantitativo y de Riesgo: CATL</h1>
        <p class="muted-text">Ticker Analizado: 300750.SZ | Índice: CSI 300</p>
        <p style="font-size: 20px; font-weight: bold;">Precio Actual: ¥{cur_price:.2f} | 
           Variación: <span class="{change_class}">{cur_change:.2f}%</span></p>
        <div style="margin-top: 10px;">
            <span class="status-badge" style="font-size: 14px;">Cotización: {data_source}</span>
            <span class="status-badge" style="font-size: 14px; background-color: var(--accent-blue);">Fundamentales: {fund_source}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
# ==========================================
# 4. PANELES DE CONTENIDO (4 TABS NUEVOS)
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["1. Perfil y Riesgos", "2. Análisis Técnico y Beta", "3. Análisis Fundamental", "4. Teorías de Divisas", "5. Veredicto de Riesgo"])

# --- TAB 1: PERFIL Y GEOPOLÍTICA ---
with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="custom-panel">
            <h3>1. Introducción a la Compañía</h3>
            <p><strong>CATL</strong> 1. Perfil Corporativo

Es el mayor fabricante mundial de baterías de iones de litio para vehículos eléctricos (EV). Posee aproximadamente el 37% de la cuota de mercado global, consolidándose como líder absoluto del sector. Es proveedor estratégico de fabricantes automotrices globales como Tesla, BMW, Volkswagen y Ford Motor Company.
Su posición la convierte en un actor sistémico dentro de la transición energética global.

Ventaja competitiva clave: innovación química, liderazgo en baterías LFP (Litio-Fosfato de hierro), más seguras y con menor costo. El desarrollo de baterías de iones de sodio es una alternativa estratégica ante riesgos de suministro de litio. 
Posee gran poder de negociación frente a OEMs automotrices y participa directamente en la cadena de suministro de minerales críticos (litio, níquel, cobalto), reduciendo la volatilidad de costos y mayor resiliencia ante shocks de commodities.

Riesgos claves: alta exposición a China. Tensiones China–EE.UU. pueden afectar acceso a mercados o tecnología. Riesgo regulatorio de concentración de clientes dependencia significativa de grandes OEMs, presión sobre márgenes por poder negociador de fabricantes automotrices, posible disrupción por baterías de estado sólido u otras químicas emergentes y riesgo de commodities Volatilidad en precios de litio y níquel, aunque mitigado parcialmente por integración vertical.
El conflicto en la region del oeste asiatico incrementa el riesgo por la dependencia China del suministro de recursos energeticos, y asi mismo, podría tener impacto en la transición a energias verdes, aumentando la volatilidad de CATL.

Posicionamiento Estratégico: CATL no es solo un fabricante de baterías; es un activo estratégico dentro de la infraestructura de electrificación global. Su liderazgo en cuota de mercado (~37%) le otorga: Ventaja en costos, capacidad de inversión en I+D y crea barreras de entrada significativas a nuevos entrantes.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="custom-panel"><h3>2. Distribución de Ingresos</h3></div>', unsafe_allow_html=True)
        fig_donut = go.Figure(data=[go.Pie(labels=['Baterías EV', 'Almacenamiento', 'Materiales', 'Otros'], values=[70, 15, 10, 5], hole=.6, marker_colors=['#58a6ff', '#3fb950', '#f85149', '#8b949e'])])
        fig_donut.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#8b949e'), showlegend=False)
        st.plotly_chart(fig_donut, use_container_width=True)
    with col3:
        st.markdown("""
        <div class="custom-panel">
            <h3>3. Riesgos Geopolíticos</h3>
            <ul><li><strong>El conflicto abierto entre EE.UU., Israel e Irán representa un riesgo bidireccional para CATL. <strong>Amenazas:</strong> Disrupción en rutas marítimas críticas y encarecimiento drástico de los fletes globales, afectando la estructura de costos operativos. <strong>Oportunidades:</strong> Un shock petrolero aceleraría la transición forzosa hacia la movilidad eléctrica, disparando la demanda de sus baterías. Para mitigar la vulnerabilidad de la cadena de suministro en África y Medio Oriente, CATL deberá estrechar urgentemente lazos estratégicos con proveedores de minerales en el Triángulo del Litio y latitudes americanas, garantizando un abastecimiento resiliente.</li></ul>
        </div>
        """, unsafe_allow_html=True)
        
        # El slider ahora está identado dentro de col3
        st.markdown("#### 🎛️ Evaluación de Riesgo Geopolítico (Ponderación 25%)")
        geo_risk_input = st.slider("Ajusta el impacto esperado (Negativo 🔴 -> Positivo 🟢)", -10, 10, 2, 1)

# --- TAB 2: ANÁLISIS TÉCNICO Y BETA ---
with tab2:
    st.markdown('<div class="custom-panel"><h3>4. Análisis Técnico Interactivo</h3></div>', unsafe_allow_html=True)
    tf_map = {"3 Meses": 90, "6 Meses": 180, "1 Año": 365, "Todo": 730}
    selected_tf = st.select_slider("Temporalidad", options=list(tf_map.keys()), value="6 Meses")
    df_plot = df_catl_tech.iloc[-tf_map[selected_tf]:]
    
    fig_tech = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.1, 0.2, 0.2])
    fig_tech.add_trace(go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name='Precio'), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=df_plot.index, y=df_plot['BB_Up'], line=dict(color='rgba(173,216,230,0.5)', width=1), name='BB Up'), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=df_plot.index, y=df_plot['BB_Dn'], line=dict(color='rgba(173,216,230,0.5)', width=1), fill='tonexty', fillcolor='rgba(173,216,230,0.1)', name='BB Dn'), row=1, col=1)
    vol_c = ['#3fb950' if r['Close'] >= r['Open'] else '#f85149' for _, r in df_plot.iterrows()]
    fig_tech.add_trace(go.Bar(x=df_plot.index, y=df_plot['Volume'], marker_color=vol_c, opacity=0.5, name='Volumen'), row=2, col=1)
    fig_tech.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MACD'], line=dict(color='#58a6ff'), name='MACD'), row=3, col=1)
    fig_tech.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MACD_Signal'], line=dict(color='#f85149', dash='dot'), name='Señal'), row=3, col=1)
    hist_c = ['#3fb950' if v >= 0 else '#f85149' for v in df_plot['MACD_Hist']]
    fig_tech.add_trace(go.Bar(x=df_plot.index, y=df_plot['MACD_Hist'], marker_color=hist_c, name='Hist'), row=3, col=1)
    fig_tech.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], line=dict(color='#FF00FF'), name='RSI'), row=4, col=1)
    fig_tech.add_hline(y=70, line_dash="dash", line_color="rgba(248,81,73,0.5)", row=4, col=1)
    fig_tech.add_hline(y=30, line_dash="dash", line_color="rgba(63,185,80,0.5)", row=4, col=1)

    fig_tech.update_layout(height=600, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10), hovermode='x unified', showlegend=False, xaxis=dict(rangeslider=dict(visible=False)))
    st.plotly_chart(fig_tech, use_container_width=True)
    
    st.markdown("### 🎛️ Evaluación de Sentimiento Técnico (Ponderación 20%)")
    chart_analysis_input = st.radio("Con base en los indicadores (MACD, RSI, Bandas), define tu postura técnica:", ("Bajista (Bearish) 🔴", "Neutral ⚪", "Alcista (Bullish) 🟢"), index=1)

    col_b1, col_b2 = st.columns([2, 1])
    with col_b1:
        st.markdown('<div class="custom-panel"><h4>Regresión de Beta (1 Año)</h4></div>', unsafe_allow_html=True)
        fig_beta = go.Figure()
        fig_beta.add_trace(go.Scatter(x=returns_df['Market_Returns'], y=returns_df['Stock_Returns'], mode='markers', marker=dict(color='#58a6ff', opacity=0.5, size=6), name='Retornos'))
        x_range = np.linspace(returns_df['Market_Returns'].min(), returns_df['Market_Returns'].max(), 100)
        fig_beta.add_trace(go.Scatter(x=x_range, y=beta_intercept + beta_val * x_range, mode='lines', line=dict(color='#f85149', width=2), name='Regresión'))
        signo = "+" if beta_intercept >= 0 else "-"
        fig_beta.add_annotation(x=0.05, y=0.95, xref="paper", yref="paper", text=f"R_CATL = {beta_intercept:.4f} {signo} {beta_val:.2f} * R_MKT<br>R² = {r2_val:.3f}", showarrow=False, align="left", bgcolor="rgba(22,27,34,0.8)", font=dict(color="#fff"))
        fig_beta.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, margin=dict(t=10, b=30, l=30, r=10), showlegend=False)
        st.plotly_chart(fig_beta, use_container_width=True)
    with col_b2:
        st.markdown(f"""
        <div class="custom-panel" style="height: 400px;">
            <h4>Beta Dinámica</h4>
            <div class="metric-value blue-text">{beta_val:.2f}</div>
            <p>Si el mercado se mueve 1%, el activo analizado tenderá a moverse un {beta_val:.2f}%.</p>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 3: ANÁLISIS FUNDAMENTAL ---
with tab3:
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        st.markdown(f"""
        <div class="custom-panel">
            <h3>Análisis DuPont (ROE)</h3>
            <p>El modelo DuPont desglosa la rentabilidad sobre el patrimonio (ROE) en tres factores fundamentales, permitiendo entender exactamente de dónde proviene la rentabilidad de la empresa:</p>
            <ul>
                <li><strong>Margen Neto:</strong> Eficiencia operativa.</li>
                <li><strong>Rotación de Activos:</strong> Eficiencia en la generación de ventas.</li>
                <li><strong>Multiplicador de Capital:</strong> Grado de apalancamiento financiero.</li>
            </ul>
            <div style="background: rgba(88, 166, 255, 0.1); border-left: 4px solid var(--accent-blue); padding: 15px; font-family: monospace; font-size: 15px; margin: 20px 0;">
                ROE = Margen Neto × Rotación Activos × Multiplicador Capital
            </div>
            <div class="metric-value green-text">{FUND_ROE:.2f}%</div>
            <p class="muted-text">Fuente: {fund_source}. Indica una rentabilidad robusta y eficiente para la industria.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_f2:
        st.markdown(f"""
        <div class="custom-panel">
            <h3>Ratio de Liquidez: Test de Acidez</h3>
            <p>El Test Ácido (Quick Ratio) es una métrica de solvencia extrema. Mide la capacidad de la empresa para cumplir con sus obligaciones financieras a corto plazo utilizando únicamente sus activos más líquidos, descartando los inventarios.</p>
            <div style="background: rgba(88, 166, 255, 0.1); border-left: 4px solid var(--accent-blue); padding: 15px; font-family: monospace; font-size: 15px; margin: 20px 0;">
                Test Ácido = (Activo Corriente - Inventarios) / Pasivo Corriente
            </div>
            <div class="metric-value green-text">{FUND_ACID:.2f}</div>
            <p class="muted-text">Fuente: {fund_source}. Al ser mayor que 1.0, indica liquidez suficiente para operar sin riesgo de insolvencia a corto plazo.</p>
        </div>
        """, unsafe_allow_html=True)
        FUND_ROE = 18.56
        
# --- TAB 4: TEORÍA DE DIVISAS ---
with tab4:
    st.markdown("""
    <div class="custom-panel">
        <h3>Teoría de Divisas: Circuito cerrado</h3>
        <p>Para un gigante exportador como CATL, las fluctuaciones del EUR/CNY y USD/CNY son vitales. Analizamos el entorno actual mediante la conexión de tres teorías fundamentales:

FLUJO LÓGICO INTEGRADO:

1. Inflación (Diferencial) ↑
   ↓
2. Tipos de Interés Nominal ↑ (Efecto Fisher)
   ↓
3. La Moneda se deprecia para ajustar el poder de compra (Paridad Poder Adquisitivo - PPA)
   ↓
4. La expectativa de depreciación compensa el diferencial de tipos (Paridad Tipos de Interés - PTI)

Aplicación a CATL (UE vs China): Si la Eurozona mantiene una inflación más alta que China, el BCE debe mantener tipos altos (Fisher). A largo plazo, el Euro debería depreciarse frente al Yuan (PPA). En el mercado forward, el Euro cotizará con descuento para anular la ventaja del tipo de interés europeo (PTI). Un Yuan fuerte encarece las baterías de CATL para las automotrices europeas o japonesas.</p>
        <p><strong>Explicación de la IRP:</strong> Establece que la diferencia en los tipos de interés entre dos países debe ser igual a la diferencia entre el tipo de cambio a plazo (forward) y el tipo de cambio al contado (spot). Si esto no se cumple, existiría una oportunidad de arbitraje libre de riesgo.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="custom-panel">
        <h4>Prueba de Conocimiento:</h4>
        <p>¿Por qué la Interest Rate Parity (IRP) es considerada la teoría más precisa para explicar la determinación del tipo de cambio en el corto plazo?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Adaptación a Streamlit del Quiz interactivo
    opcion_irp = st.radio(
        "Selecciona tu respuesta:",
        [
            "A) Porque predice a la perfección los shocks inflacionarios europeos a largo plazo.",
            "B) Porque se fundamenta en una condición de no arbitraje basada en tasas de interés y tipos de cambio forward observables en el mercado.",
            "C) Porque predice con exactitud absoluta la dirección del tipo de cambio spot en cualquier horizonte temporal."
        ],
        index=None # Para que ninguna opción salga marcada por defecto
    )

    if opcion_irp:
        if opcion_irp.startswith("B"):
            st.success("¡Correcto! Buen entendimiento conceptual.")
        else:
            st.error("Respuesta Incorrecta. Revisa IRP y vuelve a intentarlo.")

            
# --- TAB 5: VEREDICTO DE RIESGO ---
with tab5:
    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    with c_m1: st.metric("Beta Dinámica (40%)", f"{beta_val:.2f}")
    with c_m2: st.metric("Técnico (20%)", chart_analysis_input.split()[0])
    with c_m3: st.metric("Geopolítico (25%)", f"{geo_risk_input} / 10")
    with c_m4: st.metric("Acidez (15%)", f"{FUND_ACID}")

    if beta_val > 1.5: beta_score = -1.0
    elif beta_val > 1.2: beta_score = -0.3
    elif beta_val < 0.8: beta_score = 0.8
    else: beta_score = 1.0
    
    geo_score = geo_risk_input / 10.0
    tech_map = {"Bajista (Bearish) 🔴": -1, "Neutral ⚪": 0, "Alcista (Bullish) 🟢": 1}
    tech_score = tech_map[chart_analysis_input]
    acid_score = 1.0 if FUND_ACID > 1 else -0.5
    
    final_score = (beta_score * 0.40) + (geo_score * 0.25) + (tech_score * 0.20) + (acid_score * 0.15)
    
    if final_score >= 0.4:
        v, c, r = "COMPRAR", "var(--accent-green)", "No asumas riesgos que el mercado no asume; los fundamentales (ROE 18.56%) y el análisis técnico compensan la volatilidad."
    elif final_score <= -0.2:
        v, c, r = "VENDER", "var(--accent-red)", "Riesgo excesivo. La Beta o el sentimiento negativo no compensan la inversión."
    else:
        v, c, r = "MANTENER", "#d29922", "Incertidumbre. Fuerzas contrapuestas sugieren vigilar el activo antes de tomar acción."

    st.markdown(f"""
    <div class="verdict-panel">
        <h3>CONCLUSIÓN FINAL PONDERADA</h3>
        <div id="verdict-result" style="color: {c};">{v}</div>
        <p style="color: #8b949e;">Puntaje Algorítmico: {final_score:.3f} (-1 a 1)</p>
        <p>{r}</p>
    </div>
    """, unsafe_allow_html=True)
    
    df_n_catl = (df_catl['Close'].iloc[-365:] / df_catl['Close'].iloc[-365]) * 100
    df_n_mkt = (df_mkt['Close'].iloc[-365:] / df_mkt['Close'].iloc[-365]) * 100












