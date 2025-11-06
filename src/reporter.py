import pandas as pd
from typing import Dict, Any, List
import os
from datetime import datetime

class AnalysisReporter:
    """Genera reportes de análisis comparativo para múltiples usuarios"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generate_comprehensive_report(self, multi_analyzer, 
                                   output_dir: str = "outputs/reports") -> str:
        """Genera reporte completo para múltiples usuarios"""
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        report_path = os.path.join(output_dir, f"analisis_completo_{self.timestamp}.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            self._write_header(f, multi_analyzer)
            self._write_user_profiles(f, multi_analyzer)
            self._write_connection_analysis(f, multi_analyzer)
            self._write_similarity_analysis(f, multi_analyzer)
            self._write_recommendations(f, multi_analyzer)
        
        return report_path
    
    def _write_header(self, f, multi_analyzer) -> None:
        """Escribe la cabecera del reporte"""
        f.write("=" * 80 + "\n")
        f.write("ANÁLISIS COMPLETO DE REDES SOCIALES - INSTAGRAM\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("INFORMACIÓN DEL ANÁLISIS:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Usuarios analizados: {', '.join(multi_analyzer.users.keys())}\n")
        f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total de nodos en red combinada: {multi_analyzer.combined_graph.number_of_nodes()}\n")
        f.write(f"Total de conexiones: {multi_analyzer.combined_graph.number_of_edges()}\n\n")
    
    def _write_user_profiles(self, f, multi_analyzer) -> None:
        """Escribe perfiles individuales de cada usuario"""
        f.write("PERFILES INDIVIDUALES DE USUARIOS:\n")
        f.write("=" * 50 + "\n")
        
        for username, analyzer in multi_analyzer.users.items():
            analysis = analyzer.get_analysis()
            basic = analysis['basic_metrics']
            interaction = analysis['interaction_analysis']
            influence = analysis['influence_metrics']
            
            f.write(f"\n👤 {username.upper()}:\n")
            f.write("-" * 30 + "\n")
            
            # Métricas de red
            f.write("📊 MÉTRICAS DE RED:\n")
            f.write(f"   • Seguidores: {basic['followers_count']}\n")
            f.write(f"   • Siguiendo: {basic['following_count']}\n")
            f.write(f"   • Relaciones mutuas: {basic['mutual_follows']}\n")
            f.write(f"   • Ratio seguimiento: {basic['follow_ratio']:.2f}\n")
            f.write(f"   • Densidad de red: {analysis['network_metrics'].get('density', 0):.3f}\n")
            
            # Interacciones
            f.write("\n❤️  INTERACCIONES:\n")
            f.write(f"   • Autores likeados: {interaction['total_liked_authors']}\n")
            f.write(f"   • Total likes dados: {sum(analyzer.user_data['liked_posts'].values())}\n")
            f.write(f"   • Stories interactuados: {interaction['total_story_interactions']}\n")
            f.write(f"   • Tasa de engagement: {interaction['engagement_rate']:.2f}\n")
            
            # Influencia
            f.write("\n⭐ INFLUENCIA:\n")
            f.write(f"   • Score de influencia: {influence['influence_score']:.1f}\n")
            f.write(f"   • Alcance de red: {influence['network_reach']} usuarios\n")
            f.write(f"   • Centralidad: {influence.get('degree_centrality', 0):.3f}\n")
            
            # Contenido más interactuado
            if interaction['top_liked_authors']:
                f.write("\n🏆 AUTORES MÁS LIKEADOS:\n")
                for author, count in interaction['top_liked_authors'][:5]:
                    f.write(f"   • {author} ({count} likes)\n")
            
            f.write("\n")
    
    def _write_connection_analysis(self, f, multi_analyzer) -> None:
        """Escribe análisis de conexiones entre usuarios"""
        f.write("ANÁLISIS DE CONEXIONES ENTRE USUARIOS:\n")
        f.write("=" * 50 + "\n\n")
        
        connection_analysis = multi_analyzer.get_connection_analysis()
        
        # Conexiones directas
        f.write("🔗 CONEXIONES DIRECTAS:\n")
        direct_connections = connection_analysis.get('direct_connections', {})
        if direct_connections:
            for (user1, user2), mutual in direct_connections.items():
                if mutual:
                    f.write(f"   • {user1} ↔ {user2} (RELACIÓN MUTUA) 🔄\n")
                else:
                    # Verificar dirección
                    if user2 in multi_analyzer.users[user1].user_data['following']:
                        f.write(f"   • {user1} → {user2} (sigue)\n")
                    if user1 in multi_analyzer.users[user2].user_data['following']:
                        f.write(f"   • {user2} → {user1} (sigue)\n")
        else:
            f.write("   No hay conexiones directas entre usuarios principales\n")
        
        f.write("\n")
        
        # Conexiones comunes
        f.write("🤝 CONEXIONES COMUNES:\n")
        common_connections = connection_analysis.get('common_connections', {})
        
        for pair_key, connections in common_connections.items():
            user1, user2 = pair_key.split('-')
            total_common = connections['total_common']
            
            f.write(f"\n   {user1} & {user2}:\n")
            f.write(f"   • Puntuación de similitud: {total_common} puntos comunes\n")
            
            if connections['common_following']:
                f.write(f"   • Seguidos en común: {len(connections['common_following'])}\n")
                if len(connections['common_following']) <= 5:
                    f.write(f"     {', '.join(connections['common_following'])}\n")
            
            if connections['common_followers']:
                f.write(f"   • Seguidores en común: {len(connections['common_followers'])}\n")
            
            if connections['common_liked_authors']:
                f.write(f"   • Autores likeados en común: {len(connections['common_liked_authors'])}\n")
                if len(connections['common_liked_authors']) <= 3:
                    f.write(f"     {', '.join(connections['common_liked_authors'])}\n")
        
        f.write("\n")
        
        # Nodos puente
        f.write("🌉 NODOS PUENTE (Conexiones más importantes):\n")
        bridge_nodes = connection_analysis.get('bridge_nodes', [])
        
        if bridge_nodes:
            for node, score in bridge_nodes[:10]:  # Top 10
                f.write(f"   • {node} (conecta {score} usuarios)\n")
        else:
            f.write("   No se encontraron nodos puente significativos\n")
        
        f.write("\n")
    
    def _write_similarity_analysis(self, f, multi_analyzer) -> None:
        """Escribe análisis de similitud"""
        f.write("ANÁLISIS DE SIMILITUD:\n")
        f.write("=" * 50 + "\n\n")
        
        connection_analysis = multi_analyzer.get_connection_analysis()
        similarity_matrix = connection_analysis.get('similarity_matrix')
        
        if similarity_matrix is not None:
            f.write("📈 MATRIZ DE SIMILITUD (Coeficiente de Jaccard):\n\n")
            
            # Formatear matriz para texto
            users = similarity_matrix.index.tolist()
            f.write("       " + " ".join(f"{user:>10}" for user in users) + "\n")
            
            for i, user1 in enumerate(users):
                f.write(f"{user1:>6} ")
                for j, user2 in enumerate(users):
                    if i == j:
                        f.write("      -     ")
                    else:
                        similarity = similarity_matrix.loc[user1, user2]
                        f.write(f"  {similarity:7.3f}  ")
                f.write("\n")
            
            f.write("\n")
            
            # Encontrar pares más similares
            max_similarity = 0
            best_pair = (None, None)
            
            for i, user1 in enumerate(users):
                for j, user2 in enumerate(users):
                    if i < j:
                        similarity = similarity_matrix.loc[user1, user2]
                        if similarity > max_similarity:
                            max_similarity = similarity
                            best_pair = (user1, user2)
            
            if best_pair[0]:
                f.write(f"🎯 PAR MÁS SIMILAR: {best_pair[0]} & {best_pair[1]}\n")
                f.write(f"   Similitud: {max_similarity:.1%}\n")
                
                # Interpretación
                if max_similarity > 0.3:
                    f.write("   ✅ ALTA SIMILITUD: Comparten intereses y círculos sociales similares\n")
                elif max_similarity > 0.1:
                    f.write("   ⚠️  SIMILITUD MODERADA: Algunos intereses en común\n")
                else:
                    f.write("   🔄 BAJA SIMILITUD: Círculos sociales e intereses diferentes\n")
        
        f.write("\n")
    
    def _write_recommendations(self, f, multi_analyzer) -> None:
        """Escribe recomendaciones basadas en el análisis"""
        f.write("RECOMENDACIONES Y HALLAZGOS:\n")
        f.write("=" * 50 + "\n\n")
        
        connection_analysis = multi_analyzer.get_connection_analysis()
        bridge_nodes = connection_analysis.get('bridge_nodes', [])
        common_connections = connection_analysis.get('common_connections', {})
        
        f.write("💡 RECOMENDACIONES ESTRATÉGICAS:\n")
        
        # Recomendaciones basadas en nodos puente
        if bridge_nodes:
            f.write("\n🔍 BASADO EN CONEXIONES COMUNES:\n")
            top_bridges = bridge_nodes[:5]
            for node, score in top_bridges:
                f.write(f"   • Consideren interactuar con {node} (conexión fuerte entre {score} usuarios)\n")
        
        # Recomendaciones basadas en similitud
        if common_connections:
            f.write("\n🤝 BASADO EN INTERESES COMPARTIDOS:\n")
            for pair_key, connections in common_connections.items():
                if connections['common_liked_authors']:
                    user1, user2 = pair_key.split('-')
                    common_authors = connections['common_liked_authors'][:3]
                    f.write(f"   • {user1} y {user2}: Comparten interés en {', '.join(common_authors)}\n")
        
        # Recomendaciones generales
        f.write("\n📈 RECOMENDACIONES GENERALES:\n")
        f.write("   • Fomenten interacciones con conexiones comunes para fortalecer la red\n")
        f.write("   • Exploren contenido de los nodos puente para descubrir intereses compartidos\n")
        f.write("   • Consideren seguir a usuarios que siguen múltiples miembros del grupo\n")
        f.write("   • Interactúen con el contenido de conexiones comunes para aumentar engagement\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("¡Análisis completado! Revise los gráficos generados para visualizaciones.\n")
        f.write("=" * 80 + "\n")

    def generate_csv_exports(self, multi_analyzer,
                           output_dir: str = "outputs/statistics") -> Dict[str, str]:
        """Exporta datos a varios archivos CSV para análisis adicional"""
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        exports = {}
        
        # Exportar métricas de usuarios
        user_data = []
        for username, analyzer in multi_analyzer.users.items():
            analysis = analyzer.get_analysis()
            basic = analysis['basic_metrics']
            interaction = analysis['interaction_analysis']
            influence = analysis['influence_metrics']
            
            user_data.append({
                'Usuario': username,
                'Seguidores': basic['followers_count'],
                'Seguidos': basic['following_count'],
                'Relaciones_Mutuas': basic['mutual_follows'],
                'Ratio_Seguimiento': basic['follow_ratio'],
                'Autores_Likeados': interaction['total_liked_authors'],
                'Total_Likes': sum(analyzer.user_data['liked_posts'].values()),
                'Stories_Interactuados': interaction['total_story_interactions'],
                'Tasa_Engagement': interaction['engagement_rate'],
                'Score_Influencia': influence['influence_score'],
                'Alcance_Red': influence['network_reach']
            })
        
        user_df = pd.DataFrame(user_data)
        user_csv_path = os.path.join(output_dir, f"metricas_usuarios_{self.timestamp}.csv")
        user_df.to_csv(user_csv_path, index=False, encoding='utf-8')
        exports['user_metrics'] = user_csv_path
        
        # Exportar matriz de similitud
        connection_analysis = multi_analyzer.get_connection_analysis()
        similarity_matrix = connection_analysis.get('similarity_matrix')
        
        if similarity_matrix is not None:
            sim_csv_path = os.path.join(output_dir, f"matriz_similitud_{self.timestamp}.csv")
            similarity_matrix.to_csv(sim_csv_path, encoding='utf-8')
            exports['similarity_matrix'] = sim_csv_path
        
        # Exportar nodos puente
        bridge_nodes = connection_analysis.get('bridge_nodes', [])
        if bridge_nodes:
            bridge_df = pd.DataFrame(bridge_nodes, columns=['Nodo', 'Usuarios_Conectados'])
            bridge_csv_path = os.path.join(output_dir, f"nodos_puente_{self.timestamp}.csv")
            bridge_df.to_csv(bridge_csv_path, index=False, encoding='utf-8')
            exports['bridge_nodes'] = bridge_csv_path
        
        return exports