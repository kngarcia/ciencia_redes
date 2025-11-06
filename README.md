# Analizador de Redes Sociales - Instagram

Descripción:
Sistema de análisis de redes sociales que procesa datos de exportación de Instagram para crear grafos sociales, analizar comportamientos digitales y encontrar conexiones entre múltiples usuarios. Perfecto para análisis de ciencia de redes, sociología digital y estudios de comportamiento en redes sociales.

Funcionalidades Principales
- Análisis Individual por Usuario

    Grafos sociales personalizados para cada usuario

    Métricas de engagement e influencia

    Patrones de interacción (likes, seguimientos, stories)

    Autores más relevantes en su feed

- Análisis Comparativo Multi-Usuario

    Matriz de similitud entre usuarios (Coeficiente de Jaccard)

    Identificación de nodos puente (conexiones comunes)

    Mapa de relaciones directas e indirectas

    Análisis de comunidades y clusters sociales

- Visualizaciones Avanzadas

    Grafos interactivos de redes sociales

    Heatmaps de similitud entre usuarios

    Gráficos comparativos de métricas

    Mapas de conexiones comunes

Instalación y Configuración

Prerrequisitos
bash

Python 3.8+
pip (gestor de paquetes de Python)

1. Clonar o Descargar el Proyecto
bash

git clone <repositorio>
cd instagram_graph_analysis

2. Crear Entorno Virtual (Recomendado)
bash

python -m venv ig_env
source ig_env/bin/activate  # Linux/Mac
# o
ig_env\Scripts\activate    # Windows

3. Instalar Dependencias
bash

pip install -r requirements.txt

Estructura del Proyecto

instagram_graph_analysis/
├── data/                   # Datos de usuarios
│   ├── usuario1/          # Carpeta para cada usuario
│   │   ├── followers_1.json
│   │   ├── following.json
│   │   ├── liked_posts.json
│   │   └── story_likes.json
│   ├── usuario2/
│   └── ...
├── src/                   # Código fuente
│   ├── data_processor.py  # Procesamiento de datos
│   ├── graph_analyzer.py  # Análisis de grafos
│   ├── visualizer.py      # Visualizaciones
│   └── reporter.py        # Generación de reportes
├── outputs/               # Resultados generados
│   ├── graphs/           # Imágenes de grafos
│   ├── reports/          # Reportes en texto
│   └── statistics/       # Datos exportados (CSV)
├── main.py               # Script principal
└── requirements.txt      # Dependencias
