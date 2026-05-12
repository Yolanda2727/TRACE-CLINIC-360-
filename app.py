import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import uuid
from datetime import datetime
from fpdf import FPDF

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="TRACE-CLINIC 360",
    page_icon="🏥",
    layout="wide"
)

DB_NAME = "trace_clinic.db"


# =========================================================
# FUNCIONES DE BASE DE DATOS
# =========================================================

def conectar_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def crear_tablas():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id_evento TEXT PRIMARY KEY,
            fecha_hora TEXT NOT NULL,
            paciente_procedimiento TEXT NOT NULL,
            tipo_trazabilidad TEXT NOT NULL,
            responsable TEXT NOT NULL,
            rol TEXT NOT NULL,
            lugar TEXT NOT NULL,
            accion_realizada TEXT NOT NULL,
            elemento_asociado TEXT,
            resultado TEXT NOT NULL,
            estado TEXT NOT NULL,
            prioridad TEXT NOT NULL,
            observaciones TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auditoria (
            id_auditoria TEXT PRIMARY KEY,
            fecha_hora TEXT NOT NULL,
            usuario TEXT NOT NULL,
            rol TEXT NOT NULL,
            accion TEXT NOT NULL,
            detalle TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def insertar_evento(evento):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO eventos (
            id_evento, fecha_hora, paciente_procedimiento, tipo_trazabilidad,
            responsable, rol, lugar, accion_realizada, elemento_asociado,
            resultado, estado, prioridad, observaciones
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        evento["id_evento"],
        evento["fecha_hora"],
        evento["paciente_procedimiento"],
        evento["tipo_trazabilidad"],
        evento["responsable"],
        evento["rol"],
        evento["lugar"],
        evento["accion_realizada"],
        evento["elemento_asociado"],
        evento["resultado"],
        evento["estado"],
        evento["prioridad"],
        evento["observaciones"]
    ))

    conn.commit()
    conn.close()


def cargar_eventos():
    conn = conectar_db()
    df = pd.read_sql_query("SELECT * FROM eventos ORDER BY fecha_hora DESC", conn)
    conn.close()
    return df


def insertar_auditoria(usuario, rol, accion, detalle):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO auditoria (
            id_auditoria, fecha_hora, usuario, rol, accion, detalle
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "AUD-" + str(uuid.uuid4())[:8].upper(),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        usuario,
        rol,
        accion,
        detalle
    ))

    conn.commit()
    conn.close()


def cargar_auditoria():
    conn = conectar_db()
    df = pd.read_sql_query("SELECT * FROM auditoria ORDER BY fecha_hora DESC", conn)
    conn.close()
    return df


def generar_id_evento():
    return "EVT-" + str(uuid.uuid4())[:8].upper()


# =========================================================
# DATOS SIMULADOS INICIALES
# =========================================================

def insertar_datos_simulados():
    df = cargar_eventos()

    if len(df) == 0:
        datos = [
            {
                "id_evento": generar_id_evento(),
                "fecha_hora": "2026-05-12 08:30:00",
                "paciente_procedimiento": "Paciente 001 - Apendicectomia",
                "tipo_trazabilidad": "Procedimiento quirurgico",
                "responsable": "Instrumentador quirurgico",
                "rol": "Instrumentador quirurgico",
                "lugar": "Quirofano 1",
                "accion_realizada": "Preparacion de mesa quirurgica",
                "elemento_asociado": "Caja de laparotomia",
                "resultado": "Instrumental completo y verificado",
                "estado": "Cerrado",
                "prioridad": "Baja",
                "observaciones": "Sin novedad"
            },
            {
                "id_evento": generar_id_evento(),
                "fecha_hora": "2026-05-12 09:10:00",
                "paciente_procedimiento": "Paciente 001 - Apendicectomia",
                "tipo_trazabilidad": "Medicamento",
                "responsable": "Enfermeria",
                "rol": "Enfermeria",
                "lugar": "Quirofano 1",
                "accion_realizada": "Administracion de antibiotico profilactico",
                "elemento_asociado": "Cefazolina 1 g",
                "resultado": "Medicamento administrado correctamente",
                "estado": "Cerrado",
                "prioridad": "Media",
                "observaciones": "Sin reaccion adversa inmediata"
            },
            {
                "id_evento": generar_id_evento(),
                "fecha_hora": "2026-05-12 10:00:00",
                "paciente_procedimiento": "Paciente 002 - Colecistectomia",
                "tipo_trazabilidad": "Equipo biomedico",
                "responsable": "Ingenieria biomedica",
                "rol": "Ingenieria biomedica",
                "lugar": "Quirofano 2",
                "accion_realizada": "Verificacion de torre laparoscopica",
                "elemento_asociado": "Torre laparoscopica",
                "resultado": "Falla detectada en fuente de luz",
                "estado": "Critico",
                "prioridad": "Alta",
                "observaciones": "Se requiere cambio de equipo antes de iniciar procedimiento"
            }
        ]

        for evento in datos:
            insertar_evento(evento)


# =========================================================
# FUNCIONES DE PDF
# =========================================================

def limpiar_texto(texto):
    if pd.isna(texto):
        return ""

    texto = str(texto)

    reemplazos = {
        "°": " grados",
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
        "ñ": "n", "Ñ": "N",
        "¿": "", "¡": "",
        "–": "-", "—": "-"
    }

    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)

    return texto


def generar_pdf(df, nombre_archivo="reporte_trace_clinic.pdf"):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "TRACE-CLINIC 360 - Reporte de Trazabilidad", ln=True, align="C")

    pdf.set_font("Arial", "", 10)
    pdf.ln(5)
    pdf.multi_cell(0, 8, f"Fecha de generacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.ln(3)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, f"Total de eventos incluidos: {len(df)}", ln=True)
    pdf.ln(4)

    for _, row in df.iterrows():
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 8, limpiar_texto(f"Evento: {row['id_evento']}"), ln=True)

        pdf.set_font("Arial", "", 9)

        texto = (
            f"Fecha y hora: {row['fecha_hora']}\n"
            f"Paciente/Procedimiento: {row['paciente_procedimiento']}\n"
            f"Tipo de trazabilidad: {row['tipo_trazabilidad']}\n"
            f"Responsable: {row['responsable']}\n"
            f"Rol: {row['rol']}\n"
            f"Lugar: {row['lugar']}\n"
            f"Accion realizada: {row['accion_realizada']}\n"
            f"Elemento asociado: {row['elemento_asociado']}\n"
            f"Resultado: {row['resultado']}\n"
            f"Estado: {row['estado']}\n"
            f"Prioridad: {row['prioridad']}\n"
            f"Observaciones: {row['observaciones']}\n"
        )

        pdf.multi_cell(0, 6, limpiar_texto(texto))
        pdf.ln(3)

    pdf.output(nombre_archivo)
    return nombre_archivo


# =========================================================
# INICIALIZACIÓN
# =========================================================

crear_tablas()
insertar_datos_simulados()


# =========================================================
# BARRA LATERAL
# =========================================================

st.sidebar.title("🏥 TRACE-CLINIC 360")
st.sidebar.markdown("Sistema de trazabilidad clinica y quirurgica")

usuario = st.sidebar.text_input(
    "Usuario responsable",
    value="Dr. Anderson Diaz Perez"
)

rol = st.sidebar.selectbox(
    "Rol",
    [
        "Administrador",
        "Medico",
        "Instrumentador quirurgico",
        "Enfermeria",
        "Farmacia",
        "Central de esterilizacion",
        "Ingenieria biomedica",
        "Auditor de calidad"
    ]
)

menu = st.sidebar.radio(
    "Menu principal",
    [
        "Inicio",
        "Registrar evento",
        "Consultar trazabilidad",
        "Linea de tiempo",
        "Panel de alertas",
        "Auditoria",
        "Reporte",
        "Auditoria tecnica del sistema"
    ]
)


# =========================================================
# PANTALLA DE INICIO
# =========================================================

if menu == "Inicio":
    st.title("TRACE-CLINIC 360")
    st.subheader("Sistema para trazabilidad clinica, quirurgica y hospitalaria")

    df = cargar_eventos()

    st.markdown("""
    Esta aplicacion permite registrar y consultar eventos relacionados con pacientes,
    procedimientos, medicamentos, insumos, equipos biomedicos y procesos quirurgicos.

    Su pregunta central es:

    **Quien hizo que, cuando, donde, con que elemento y con que resultado.**
    """)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Eventos registrados", len(df))
    col2.metric("Eventos criticos", len(df[df["estado"] == "Critico"]))
    col3.metric("Eventos cerrados", len(df[df["estado"] == "Cerrado"]))
    col4.metric("Alta prioridad", len(df[df["prioridad"] == "Alta"]))

    st.info("Este prototipo usa SQLite como base de datos local para conservar los registros durante la ejecucion.")


# =========================================================
# REGISTRAR EVENTO
# =========================================================

elif menu == "Registrar evento":
    st.title("📝 Registro de evento clinico")

    with st.form("form_evento"):
        col1, col2 = st.columns(2)

        with col1:
            paciente = st.text_input(
                "Paciente o procedimiento",
                placeholder="Ejemplo: Paciente 003 - Cesarea"
            )

            tipo = st.selectbox(
                "Tipo de trazabilidad",
                [
                    "Paciente",
                    "Procedimiento clinico",
                    "Procedimiento quirurgico",
                    "Insumo",
                    "Medicamento",
                    "Equipo biomedico",
                    "Proceso quirurgico",
                    "Evento adverso",
                    "Otro"
                ]
            )

            responsable = st.text_input("Responsable de la accion", value=usuario)

            lugar = st.text_input(
                "Lugar",
                placeholder="Ejemplo: Quirofano 1, UCI, farmacia, central de esterilizacion"
            )

        with col2:
            accion = st.text_area("Accion realizada")
            elemento = st.text_input("Elemento asociado", placeholder="Ejemplo: lote, equipo, medicamento, insumo")
            resultado = st.text_area("Resultado")

            estado = st.selectbox(
                "Estado",
                ["Abierto", "En seguimiento", "Cerrado", "Critico"]
            )

            prioridad = st.selectbox(
                "Prioridad",
                ["Baja", "Media", "Alta"]
            )

            observaciones = st.text_area("Observaciones")

        enviar = st.form_submit_button("Registrar evento")

        if enviar:
            campos_obligatorios = {
                "Paciente o procedimiento": paciente,
                "Responsable": responsable,
                "Lugar": lugar,
                "Accion realizada": accion,
                "Resultado": resultado
            }

            campos_faltantes = [campo for campo, valor in campos_obligatorios.items() if not valor.strip()]

            if campos_faltantes:
                st.error("Faltan campos obligatorios: " + ", ".join(campos_faltantes))
            else:
                nuevo_evento = {
                    "id_evento": generar_id_evento(),
                    "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "paciente_procedimiento": paciente,
                    "tipo_trazabilidad": tipo,
                    "responsable": responsable,
                    "rol": rol,
                    "lugar": lugar,
                    "accion_realizada": accion,
                    "elemento_asociado": elemento,
                    "resultado": resultado,
                    "estado": estado,
                    "prioridad": prioridad,
                    "observaciones": observaciones
                }

                insertar_evento(nuevo_evento)

                insertar_auditoria(
                    usuario,
                    rol,
                    "Registro de evento",
                    f"Se registro el evento {nuevo_evento['id_evento']} para {paciente}"
                )

                st.success(f"Evento registrado correctamente: {nuevo_evento['id_evento']}")


# =========================================================
# CONSULTAR TRAZABILIDAD
# =========================================================

elif menu == "Consultar trazabilidad":
    st.title("🔎 Consulta de trazabilidad")

    df = cargar_eventos()

    col1, col2, col3 = st.columns(3)

    with col1:
        filtro_tipo = st.selectbox(
            "Filtrar por tipo",
            ["Todos"] + sorted(df["tipo_trazabilidad"].unique().tolist())
        )

    with col2:
        filtro_estado = st.selectbox(
            "Filtrar por estado",
            ["Todos"] + sorted(df["estado"].unique().tolist())
        )

    with col3:
        busqueda = st.text_input("Buscar por paciente, insumo, medicamento, equipo o procedimiento")

    df_filtrado = df.copy()

    if filtro_tipo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["tipo_trazabilidad"] == filtro_tipo]

    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["estado"] == filtro_estado]

    if busqueda:
        busqueda_lower = busqueda.lower()
        df_filtrado = df_filtrado[
            df_filtrado.apply(
                lambda row: busqueda_lower in " ".join(row.astype(str)).lower(),
                axis=1
            )
        ]

    st.dataframe(df_filtrado, use_container_width=True)

    if st.button("Registrar auditoria de esta consulta"):
        insertar_auditoria(
            usuario,
            rol,
            "Consulta de trazabilidad",
            f"Consulta realizada con filtro tipo={filtro_tipo}, estado={filtro_estado}, busqueda={busqueda}"
        )
        st.success("Consulta registrada en auditoria.")


# =========================================================
# LINEA DE TIEMPO
# =========================================================

elif menu == "Linea de tiempo":
    st.title("⏱️ Linea de tiempo del evento clinico")

    df = cargar_eventos()

    if len(df) == 0:
        st.warning("No hay eventos registrados.")
    else:
        df["fecha_hora"] = pd.to_datetime(df["fecha_hora"])
        df["fin_evento"] = df["fecha_hora"] + pd.Timedelta(minutes=10)

        seleccion = st.selectbox(
            "Seleccione paciente o procedimiento",
            sorted(df["paciente_procedimiento"].unique().tolist())
        )

        df_filtrado = df[df["paciente_procedimiento"] == seleccion].sort_values("fecha_hora")

        st.dataframe(df_filtrado, use_container_width=True)

        fig = px.timeline(
            df_filtrado,
            x_start="fecha_hora",
            x_end="fin_evento",
            y="accion_realizada",
            color="estado",
            hover_data=[
                "responsable",
                "rol",
                "lugar",
                "elemento_asociado",
                "resultado",
                "prioridad",
                "observaciones"
            ],
            title=f"Linea de tiempo: {seleccion}"
        )

        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)


# =========================================================
# PANEL DE ALERTAS
# =========================================================

elif menu == "Panel de alertas":
    st.title("🚨 Panel de alertas clinicas y quirurgicas")

    df = cargar_eventos()

    eventos_criticos = df[df["estado"] == "Critico"]
    eventos_abiertos = df[df["estado"] == "Abierto"]
    eventos_seguimiento = df[df["estado"] == "En seguimiento"]
    eventos_alta = df[df["prioridad"] == "Alta"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Eventos criticos", len(eventos_criticos))
    col2.metric("Eventos abiertos", len(eventos_abiertos))
    col3.metric("En seguimiento", len(eventos_seguimiento))
    col4.metric("Alta prioridad", len(eventos_alta))

    if len(eventos_criticos) > 0:
        st.error("Existen eventos criticos que requieren revision inmediata.")
        st.dataframe(eventos_criticos, use_container_width=True)
    else:
        st.success("No hay eventos criticos registrados.")

    st.subheader("Eventos abiertos o en seguimiento")
    st.dataframe(
        pd.concat([eventos_abiertos, eventos_seguimiento]),
        use_container_width=True
    )

    st.subheader("Eventos de alta prioridad")
    st.dataframe(eventos_alta, use_container_width=True)


# =========================================================
# AUDITORIA
# =========================================================

elif menu == "Auditoria":
    st.title("🧾 Registro de auditoria")

    st.markdown("""
    Este modulo permite revisar quien realizo acciones relevantes dentro del sistema,
    cuando las realizo, con que rol y sobre que registro.
    """)

    df_auditoria = cargar_auditoria()
    st.dataframe(df_auditoria, use_container_width=True)


# =========================================================
# REPORTE
# =========================================================

elif menu == "Reporte":
    st.title("📄 Generacion de reporte")

    df = cargar_eventos()

    if len(df) == 0:
        st.warning("No hay eventos para generar reporte.")
    else:
        seleccion = st.selectbox(
            "Seleccione el paciente o procedimiento para generar reporte",
            ["Todos"] + sorted(df["paciente_procedimiento"].unique().tolist())
        )

        if seleccion != "Todos":
            df_reporte = df[df["paciente_procedimiento"] == seleccion]
        else:
            df_reporte = df

        st.dataframe(df_reporte, use_container_width=True)

        if st.button("Generar reporte PDF"):
            archivo = generar_pdf(df_reporte)

            insertar_auditoria(
                usuario,
                rol,
                "Generacion de reporte PDF",
                f"Se genero reporte para {seleccion}"
            )

            with open(archivo, "rb") as f:
                st.download_button(
                    label="Descargar reporte PDF",
                    data=f,
                    file_name=archivo,
                    mime="application/pdf"
                )

        csv = df_reporte.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Descargar reporte en CSV",
            data=csv,
            file_name="reporte_trace_clinic.csv",
            mime="text/csv"
        )


# =========================================================
# AUDITORIA TECNICA DEL SISTEMA
# =========================================================

elif menu == "Auditoria tecnica del sistema":
    st.title("🛡️ Auditoria tecnica del prototipo")

    st.markdown("""
    Esta seccion muestra los principales puntos de control del prototipo.
    """)

    auditoria_tecnica = pd.DataFrame([
        {
            "Componente": "Base de datos",
            "Estado actual": "SQLite local",
            "Riesgo": "Medio",
            "Recomendacion": "Migrar a PostgreSQL o Supabase para version institucional"
        },
        {
            "Componente": "Autenticacion",
            "Estado actual": "No implementada",
            "Riesgo": "Alto",
            "Recomendacion": "Implementar login seguro, contrasenas cifradas y roles reales"
        },
        {
            "Componente": "Auditoria",
            "Estado actual": "Tabla de auditoria basica",
            "Riesgo": "Medio",
            "Recomendacion": "Proteger auditoria contra edicion y eliminacion"
        },
        {
            "Componente": "Proteccion de datos",
            "Estado actual": "Parcial",
            "Riesgo": "Alto",
            "Recomendacion": "Usar codigos de pacientes, cifrado y minimizacion de datos"
        },
        {
            "Componente": "Reportes",
            "Estado actual": "PDF y CSV",
            "Riesgo": "Bajo",
            "Recomendacion": "Mejorar reporte con firma, version y responsable"
        },
        {
            "Componente": "Alertas",
            "Estado actual": "Basadas en estado y prioridad",
            "Riesgo": "Medio",
            "Recomendacion": "Crear reglas automaticas por vencimiento, lote, falla o evento adverso"
        },
        {
            "Componente": "Interoperabilidad",
            "Estado actual": "No implementada",
            "Riesgo": "Medio",
            "Recomendacion": "Evaluar HL7/FHIR en fases posteriores"
        }
    ])

    st.dataframe(auditoria_tecnica, use_container_width=True)

    st.warning("Este prototipo es academico y demostrativo. No debe usarse todavia como sistema clinico real.")
