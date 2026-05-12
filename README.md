# TRACE-CLINIC 360

**TRACE-CLINIC 360** es un prototipo académico desarrollado en Python y Streamlit para registrar, consultar y hacer seguimiento a eventos clínicos, quirúrgicos, farmacológicos, logísticos y de seguridad del paciente.

## Propósito

El sistema busca responder de manera trazable:

> ¿Quién hizo qué, cuándo, dónde, con qué elemento y con qué resultado?

## Funcionalidades principales

- Registro de eventos clínicos y quirúrgicos.
- Identificación de paciente o procedimiento.
- Registro de responsable, rol, lugar, acción realizada y resultado.
- Consulta por paciente, procedimiento, insumo, medicamento, equipo o estado.
- Línea de tiempo de eventos.
- Panel de alertas clínicas y quirúrgicas.
- Registro de auditoría.
- Generación de reportes en PDF y CSV.
- Base de datos local con SQLite.
- Datos simulados iniciales para demostración.

## Estructura del repositorio

```text
trace-clinic-360/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── LICENSE
└── docs/
    └── instrucciones_ejecucion.md
```

## Instalación local

1. Clonar el repositorio:

```bash
git clone https://github.com/USUARIO/trace-clinic-360.git
cd trace-clinic-360
```

2. Crear entorno virtual, opcional pero recomendado:

```bash
python -m venv venv
```

3. Activar entorno virtual:

En Windows:

```bash
venv\Scripts\activate
```

En Mac/Linux:

```bash
source venv/bin/activate
```

4. Instalar dependencias:

```bash
pip install -r requirements.txt
```

5. Ejecutar la aplicación:

```bash
streamlit run app.py
```

## Uso en Streamlit Cloud

1. Subir estos archivos a un repositorio de GitHub.
2. Entrar a Streamlit Cloud.
3. Seleccionar el repositorio.
4. Indicar como archivo principal:

```text
app.py
```

5. Desplegar la aplicación.

## Advertencia ética y clínica

Este software es un **prototipo académico y demostrativo**. No debe utilizarse como sistema clínico real sin validación técnica, jurídica, ética, institucional y de seguridad informática.

Para una versión hospitalaria real se requiere:

- Autenticación segura.
- Control real de roles.
- Cifrado de datos.
- Manejo de datos personales sensibles.
- Consentimiento y políticas de privacidad.
- Auditoría protegida contra modificación.
- Validación con usuarios clínicos.
- Evaluación de seguridad del paciente.
- Cumplimiento normativo aplicable.

## Autor

Profesor Anderson Díaz Pérez.

## Licencia

Este proyecto se distribuye bajo licencia MIT para fines académicos, formativos y de investigación.
