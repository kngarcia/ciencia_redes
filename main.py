#!/usr/bin/env python3
"""
Script principal para análisis de grafos sociales de Instagram - MÚLTIPLES USUARIOS
"""

import os
import sys
from typing import Dict, List

# Agregar src al path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from graph_analyzer import MultiUserGraphAnalyzer, UserGraphAnalyzer
    from visualizer import GraphVisualizer
    from reporter import AnalysisReporter
    HAS_MODULES = True
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    HAS_MODULES = False

def setup_directories() -> Dict[str, str]:
    """Configura la estructura de directorios"""
    BASE_DIR = os.path.dirname(__file__)
    
    directories = {
        'base': BASE_DIR,
        'data': os.path.join(BASE_DIR, "data"),
        'outputs': os.path.join(BASE_DIR, "outputs"),
        'graphs': os.path.join(BASE_DIR, "outputs", "graphs"),
        'reports': os.path.join(BASE_DIR, "outputs", "reports"),
        'statistics': os.path.join(BASE_DIR, "outputs", "statistics")
    }
    
    # Crear directorios necesarios
    for dir_path in directories.values():
        os.makedirs(dir_path, exist_ok=True)
    
    return directories

def get_user_configurations() -> Dict[str, str]:
    """
    Configuración de usuarios a analizar.
    MODIFICA ESTE DICCIONARIO para agregar más usuarios.
    """
    return {
        'Kevin': 'data/user1',
        'Nicolas': 'data/user2',
        'Sara': 'data/user3',
        # 'usuario4': 'data/user4',
        # Agrega más usuarios según necesites
    }

def main():
    """Función principal"""
    print("🌐 ANALIZADOR DE REDES SOCIALES - INSTAGRAM")
    print("=" * 50 + "\n")
    
    if not HAS_MODULES:
        print("❌ No se pudieron cargar los módulos necesarios")
        sys.exit(1)
    
    # Configurar directorios
    dirs = setup_directories()
    print("📁 Directorios configurados:")
    for name, path in dirs.items():
        print(f"   ✅ {name}: {path}")
    
    # Obtener configuración de usuarios
    users = get_user_configurations()
    print(f"\n👥 Usuarios a analizar: {len(users)}")
    for username, data_dir in users.items():
        full_path = os.path.join(dirs['base'], data_dir)
        exists = os.path.exists(full_path)
        status = "✅" if exists else "❌"
        print(f"   {status} {username}: {full_path}")
    
    if not users:
        print("❌ No hay usuarios configurados para analizar")
        sys.exit(1)
    
    try:
        # 1. INICIALIZAR ANALIZADOR MULTIUSUARIO
        print("\n" + "="*50)
        print("1. CARGANDO DATOS DE USUARIOS")
        print("="*50)
        
        multi_analyzer = MultiUserGraphAnalyzer()
        users_loaded = 0
        
        for username, data_dir in users.items():
            full_data_dir = os.path.join(dirs['base'], data_dir)
            print(f"\n📥 Cargando datos de {username}...")
            
            if multi_analyzer.add_user(username, full_data_dir):
                users_loaded += 1
                print(f"   ✅ {username} cargado exitosamente")
            else:
                print(f"   ❌ Error cargando {username}")
        
        if users_loaded < 2:
            print(f"\n❌ Se necesitan al menos 2 usuarios para el análisis. Cargados: {users_loaded}")
            sys.exit(1)
        
        print(f"\n✅ Todos los usuarios cargados: {users_loaded}/{len(users)}")
        
        # 2. CONSTRUIR GRAFO COMBINADO
        print("\n" + "="*50)
        print("2. CONSTRUYENDO RED COMBINADA")
        print("="*50)
        
        multi_analyzer.build_combined_graph()
        connection_analysis = multi_analyzer.get_connection_analysis()
        
        print("📊 Análisis de conexiones completado:")
        print(f"   • Nodos en red combinada: {multi_analyzer.combined_graph.number_of_nodes()}")
        print(f"   • Conexiones totales: {multi_analyzer.combined_graph.number_of_edges()}")
        print(f"   • Nodos puente identificados: {len(connection_analysis.get('bridge_nodes', []))}")
        
        # 3. GENERAR VISUALIZACIONES
        print("\n" + "="*50)
        print("3. GENERANDO VISUALIZACIONES")
        print("="*50)
        
        visualizer = GraphVisualizer()
        
        # Obtener nodos comunes para destacar
        bridge_nodes = set([node for node, score in connection_analysis.get('bridge_nodes', [])])
        
        # 3.1 Gráficos individuales de cada usuario
        print("\n📈 Generando gráficos individuales...")
        for username, analyzer in multi_analyzer.users.items():
            print(f"   🎨 Creando red de {username}...")
            visualizer.plot_individual_network(
                analyzer.graph,
                username,
                bridge_nodes,
                os.path.join(dirs['graphs'], f"red_individual_{username}.png")
            )
        
        # 3.2 Gráfico de relaciones directas entre usuarios
        print("\n🔗 Generando gráfico de relaciones directas...")
        relationship_graph = multi_analyzer.get_user_relationships_graph()
        visualizer.plot_user_relationships(
            relationship_graph,
            os.path.join(dirs['graphs'], "relaciones_usuarios.png")
        )
        
        # 3.3 Gráfico de conexiones comunes
        print("🌉 Generando gráfico de conexiones comunes...")
        common_graph = multi_analyzer.get_common_connections_graph()
        visualizer.plot_common_connections(
            common_graph,
            os.path.join(dirs['graphs'], "conexiones_comunes.png")
        )
        
        # 3.4 Heatmap de similitud
        print("📊 Generando matriz de similitud...")
        similarity_matrix = connection_analysis.get('similarity_matrix')
        if similarity_matrix is not None:
            visualizer.plot_similarity_heatmap(
                similarity_matrix,
                os.path.join(dirs['graphs'], "matriz_similitud.png")
            )
        
        # 3.5 Comparación de métricas
        print("📋 Generando comparación de métricas...")
        analyses = {username: analyzer.get_analysis() for username, analyzer in multi_analyzer.users.items()}
        visualizer.plot_metrics_comparison(
            analyses,
            os.path.join(dirs['graphs'], "comparacion_metricas.png")
        )
        
        # 4. GENERAR REPORTES
        print("\n" + "="*50)
        print("4. GENERANDO REPORTES")
        print("="*50)
        
        reporter = AnalysisReporter()
        
        # 4.1 Reporte completo
        print("📄 Generando reporte completo...")
        report_path = reporter.generate_comprehensive_report(
            multi_analyzer,
            dirs['reports']
        )
        
        # 4.2 Exportar datos CSV
        print("💾 Exportando datos a CSV...")
        csv_exports = reporter.generate_csv_exports(
            multi_analyzer,
            dirs['statistics']
        )
        
        # 5. RESUMEN FINAL
        print("\n" + "="*50)
        print("✅ ANÁLISIS COMPLETADO")
        print("="*50)
        
        print(f"\n🎯 RESULTADOS PRINCIPALES:")
        print(f"   • Usuarios analizados: {users_loaded}")
        print(f"   • Red total: {multi_analyzer.combined_graph.number_of_nodes()} nodos")
        print(f"   • Conexiones identificadas: {multi_analyzer.combined_graph.number_of_edges()}")
        
        # Estadísticas de similitud
        if similarity_matrix is not None:
            user_list = list(multi_analyzer.users.keys())
            similarities = []
            for i, user1 in enumerate(user_list):
                for j, user2 in enumerate(user_list):
                    if i < j:
                        sim = similarity_matrix.loc[user1, user2]
                        similarities.append(sim)
            
            if similarities:
                avg_similarity = sum(similarities) / len(similarities)
                max_similarity = max(similarities)
                print(f"   • Similitud promedio: {avg_similarity:.1%}")
                print(f"   • Similitud máxima: {max_similarity:.1%}")
        
        print(f"\n📁 ARCHIVOS GENERADOS:")
        print(f"   📊 Reporte completo: {report_path}")
        for export_name, export_path in csv_exports.items():
            print(f"   💾 {export_name}: {export_path}")
        print(f"   🎨 Gráficos: {dirs['graphs']}")
        
        print(f"\n💡 RECOMENDACIÓN:")
        print("   Revise el reporte completo y los gráficos para entender las conexiones")
        print("   entre los usuarios y identificar oportunidades de interacción.")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL ANÁLISIS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()