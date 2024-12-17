# Banco de la Gente - Dashboard de Reportes

## Descripción
Dashboard interactivo desarrollado con Streamlit para visualizar y analizar datos del programa Banco de la Gente. La aplicación permite monitorear métricas globales, análisis de recupero y gestión de casos rechazados, con visualizaciones geoespaciales por departamentos.

## Características Principales
- **Vista Global**: Análisis general de operaciones y distribución geográfica
- **Análisis de Recupero**: Seguimiento de recuperación de préstamos por año
- **Gestión de Rechazos**: Monitoreo y análisis de casos rechazados
- **Visualización Geoespacial**: Mapas interactivos por departamentos

## Tecnologías Utilizadas
- Python 3.x
- Streamlit
- Pandas
- GeoPandas
- Supabase (almacenamiento de datos)

## Requisitos
```
streamlit
pandas
geopandas
supabase
```

## Instalación
1. Clonar el repositorio
2. Crear un entorno virtual:
   ```bash
   python -m venv entornobanco
   source entornobanco/bin/activate  # En Linux/Mac
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración
1. Crear archivo `.streamlit/secrets.toml` con las credenciales de Supabase:
   ```toml
   [supabase]
   url = "TU_URL_SUPABASE"
   key = "TU_KEY_SUPABASE"
   ```

## Uso
1. Activar el entorno virtual:
   ```bash
   source entornobanco/bin/activate
   ```
2. Ejecutar la aplicación:
   ```bash
   streamlit run app.py
   ```

## Estructura del Proyecto
```
BCOGente/
├── app.py                 # Aplicación principal
├── funciones.py          # Funciones auxiliares
├── requirements.txt      # Dependencias
├── moduls/              # Módulos de la aplicación
│   ├── carga.py         # Carga de datos
│   ├── bco_global.py    # Vista global
│   ├── recupero.py      # Análisis de recupero
│   └── rechazo.py       # Gestión de rechazos
└── .streamlit/          # Configuración de Streamlit
```

## Mantenimiento
- Los datos se actualizan automáticamente desde Supabase
- La aplicación incluye manejo de errores y logging
- Visualizaciones optimizadas para rendimiento

## Soporte
Para reportar problemas o sugerir mejoras, por favor crear un issue en el repositorio.