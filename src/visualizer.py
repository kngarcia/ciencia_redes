import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional
import os
import numpy as np

class GraphVisualizer:
    """Visualizador mejorado de grafos sociales"""
    
    def __init__(self):
        plt.style.use('default')
        sns.set_palette("husl")
        self.colors = {
            'main_user': '#FF6B6B',      # Rojo
            'follower': '#4ECDC4',       # Verde azulado
            'following': '#45B7D1',      # Azul
            'liked_author': '#96CEB4',   # Verde claro
            'story_author': '#FFEAA7',   # Amarillo
            'mutual': '#A593E0',         # Púrpura
            'bridge': '#FFA07A',         # Naranja claro
            'common': '#FF6B6B'          # Rojo para nodos comunes
        }
    
    def plot_individual_network(self, graph: nx.DiGraph, username: str, 
                               highlight_nodes: set = None,
                               save_path: str = None) -> None:
        """Visualización de red individual enfocada en conexiones relevantes"""
        plt.figure(figsize=(14, 10))
        
        # Crear subgrafo con nodos más importantes para reducir ruido
        important_nodes = self._get_important_nodes(graph, username, max_nodes=50)
        subgraph = graph.subgraph(important_nodes)
        
        # Layout mejorado
        pos = nx.spring_layout(subgraph, k=3, iterations=100, seed=42)
        
        # Preparar atributos visuales
        node_colors, node_sizes, edge_colors, edge_widths = self._prepare_visual_attributes(
            subgraph, username, highlight_nodes
        )
        
        # Dibujar el grafo
        nx.draw_networkx_nodes(subgraph, pos, 
                             node_color=node_colors,
                             node_size=node_sizes,
                             alpha=0.9,
                             edgecolors='black',
                             linewidths=0.5)
        
        nx.draw_networkx_edges(subgraph, pos,
                             edge_color=edge_colors,
                             width=edge_widths,
                             alpha=0.7,
                             arrows=True,
                             arrowsize=20,
                             arrowstyle='->')
        
        # Etiquetas selectivas
        labels = self._get_selective_labels(subgraph, username, highlight_nodes)
        nx.draw_networkx_labels(subgraph, pos, labels, font_size=8, font_weight='bold')
        
        plt.title(f"Red Social de {username}\n(Nodos más relevantes)", 
                 fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        
        # Leyenda mejorada
        self._add_enhanced_legend(highlight_nodes is not None)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"💾 Gráfico guardado: {save_path}")
        
        plt.show()
    
    def plot_user_relationships(self, graph: nx.DiGraph, 
                              save_path: str = None) -> None:
        """Visualiza las relaciones directas entre usuarios principales"""
        plt.figure(figsize=(12, 8))
        
        # Usar layout circular para mejor visualización
        pos = nx.circular_layout(graph)
        
        # Dibujar nodos
        node_colors = [self.colors['main_user'] for _ in graph.nodes()]
        node_sizes = [600 for _ in graph.nodes()]
        
        nx.draw_networkx_nodes(graph, pos,
                             node_color=node_colors,
                             node_size=node_sizes,
                             alpha=0.8,
                             edgecolors='darkred',
                             linewidths=2)
        
        # Dibujar aristas
        edge_colors = []
        edge_styles = []
        edge_widths = []
        
        for u, v, data in graph.edges(data=True):
            if data.get('relationship') == 'mutual':
                edge_colors.append(self.colors['mutual'])
                edge_styles.append('solid')
                edge_widths.append(3)
            else:
                edge_colors.append('gray')
                edge_styles.append('dashed')
                edge_widths.append(1)
        
        for i, (u, v) in enumerate(graph.edges()):
            nx.draw_networkx_edges(graph, pos,
                                 edgelist=[(u, v)],
                                 edge_color=edge_colors[i],
                                 style=edge_styles[i],
                                 width=edge_widths[i],
                                 arrows=True,
                                 arrowsize=25,
                                 arrowstyle='->')
        
        # Etiquetas
        nx.draw_networkx_labels(graph, pos, font_size=12, font_weight='bold')
        
        plt.title("Relaciones Directas entre Usuarios", 
                 fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # Leyenda personalizada
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.colors['main_user'], label='Usuario Principal'),
            Patch(facecolor=self.colors['mutual'], label='Relación Mutua'),
            Patch(facecolor='gray', label='Seguimiento Unidireccional')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_common_connections(self, graph: nx.DiGraph,
                              save_path: str = None) -> None:
        """Visualiza usuarios principales y sus conexiones comunes"""
        plt.figure(figsize=(14, 10))
        
        # Separar nodos principales y puente
        main_nodes = [n for n, d in graph.nodes(data=True) if d.get('type') == 'main_user']
        bridge_nodes = [n for n, d in graph.nodes(data=True) if d.get('type') == 'bridge']
        
        # Layout bipartito
        pos = {}
        
        # Posicionar usuarios principales en la parte superior
        for i, node in enumerate(main_nodes):
            pos[node] = (i * 2, 1)
        
        # Posicionar nodos puente en la parte inferior
        for i, node in enumerate(bridge_nodes):
            pos[node] = (i * 2, 0)
        
        # Dibujar nodos principales
        nx.draw_networkx_nodes(graph, pos, nodelist=main_nodes,
                             node_color=[self.colors['main_user']] * len(main_nodes),
                             node_size=800,
                             alpha=0.9,
                             edgecolors='darkred',
                             linewidths=2)
        
        # Dibujar nodos puente
        if bridge_nodes:
            bridge_sizes = [graph.nodes[n].get('bridge_score', 1) * 100 for n in bridge_nodes]
            nx.draw_networkx_nodes(graph, pos, nodelist=bridge_nodes,
                                 node_color=[self.colors['bridge']] * len(bridge_nodes),
                                 node_size=bridge_sizes,
                                 alpha=0.8,
                                 edgecolors='darkorange',
                                 linewidths=1.5)
        
        # Dibujar conexiones
        nx.draw_networkx_edges(graph, pos,
                             edge_color='gray',
                             width=1,
                             alpha=0.6,
                             arrows=False)
        
        # Etiquetas
        labels = {node: node for node in graph.nodes()}
        nx.draw_networkx_labels(graph, pos, labels, font_size=9)
        
        plt.title("Conexiones Comunes entre Usuarios\n(Nodos Puente)", 
                 fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # Leyenda
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.colors['main_user'], label='Usuarios Principales'),
            Patch(facecolor=self.colors['bridge'], label='Nodos Puente (Conexiones Comunes)')
        ]
        plt.legend(handles=legend_elements, loc='upper left')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_similarity_heatmap(self, similarity_matrix: pd.DataFrame,
                              save_path: str = None) -> None:
        """Visualiza matriz de similitud entre usuarios"""
        plt.figure(figsize=(10, 8))
        
        # Crear máscara para la diagonal
        mask = np.zeros_like(similarity_matrix, dtype=bool)
        np.fill_diagonal(mask, True)
        
        # Heatmap
        sns.heatmap(similarity_matrix, 
                   annot=True, 
                   cmap='YlOrRd',
                   square=True,
                   fmt='.3f',
                   cbar_kws={'label': 'Coeficiente de Similitud'},
                   mask=mask)
        
        plt.title('Matriz de Similitud entre Usuarios\n(Coeficiente de Jaccard)', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_metrics_comparison(self, analyses: Dict[str, Dict],
                              save_path: str = None) -> None:
        """Compara métricas entre múltiples usuarios"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        usernames = list(analyses.keys())
        
        # Métricas básicas de red
        metrics_data = {
            'Seguidores': [analyses[u]['basic_metrics']['followers_count'] for u in usernames],
            'Seguidos': [analyses[u]['basic_metrics']['following_count'] for u in usernames],
            'Relaciones Mutuas': [analyses[u]['basic_metrics']['mutual_follows'] for u in usernames]
        }
        
        x = np.arange(len(usernames))
        width = 0.25
        multiplier = 0
        
        for attribute, measurement in metrics_data.items():
            offset = width * multiplier
            rects = axes[0,0].bar(x + offset, measurement, width, label=attribute)
            axes[0,0].bar_label(rects, padding=3)
            multiplier += 1
        
        axes[0,0].set_title('Métricas de Seguimiento', fontweight='bold')
        axes[0,0].set_xticks(x + width, usernames)
        axes[0,0].legend(loc='upper left')
        
        # Interacciones
        interaction_data = {
            'Autores Likeados': [analyses[u]['interaction_analysis']['total_liked_authors'] for u in usernames],
            'Interacciones Stories': [analyses[u]['interaction_analysis']['total_story_interactions'] for u in usernames]
        }
        
        x = np.arange(len(usernames))
        width = 0.35
        multiplier = 0
        
        for attribute, measurement in interaction_data.items():
            offset = width * multiplier
            rects = axes[0,1].bar(x + offset, measurement, width, label=attribute)
            axes[0,1].bar_label(rects, padding=3)
            multiplier += 1
        
        axes[0,1].set_title('Interacciones de Contenido', fontweight='bold')
        axes[0,1].set_xticks(x + width/2, usernames)
        axes[0,1].legend()
        
        # Scores de influencia
        influence_scores = [analyses[u]['influence_metrics']['influence_score'] for u in usernames]
        bars = axes[1,0].bar(usernames, influence_scores, color='lightcoral')
        axes[1,0].bar_label(bars, padding=3)
        axes[1,0].set_title('Score de Influencia', fontweight='bold')
        axes[1,0].set_ylabel('Puntuación')
        
        # Tasa de engagement
        engagement_rates = [analyses[u]['interaction_analysis']['engagement_rate'] for u in usernames]
        bars = axes[1,1].bar(usernames, engagement_rates, color='lightseagreen')
        axes[1,1].bar_label(bars, fmt='%.2f', padding=3)
        axes[1,1].set_title('Tasa de Engagement', fontweight='bold')
        axes[1,1].set_ylabel('Interacciones por usuario seguido')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _get_important_nodes(self, graph: nx.DiGraph, username: str, max_nodes: int = 50) -> List[str]:
        """Selecciona los nodos más importantes para visualización"""
        important_nodes = {username}  # Siempre incluir al usuario principal
        
        # Agregar nodos por tipo de relación (priorizando relaciones más fuertes)
        node_priority = []
        
        for node, data in graph.nodes(data=True):
            if node == username:
                continue
                
            priority = 0
            node_type = data.get('type', '')
            
            # Priorizar por tipo de relación
            if node_type == 'mutual':
                priority = 100
            elif node_type in ['follower', 'following']:
                priority = 80
            elif node_type in ['liked_author', 'story_author']:
                # Priorizar por frecuencia de interacción
                interaction_count = 0
                if graph.has_edge(username, node):
                    edge_data = graph[username][node]
                    interaction_count = edge_data.get('interaction_count', 0)
                priority = 60 + min(interaction_count, 20)  # Máximo 20 de bonus
            
            node_priority.append((node, priority))
        
        # Ordenar por prioridad y tomar los mejores
        node_priority.sort(key=lambda x: x[1], reverse=True)
        top_nodes = [node for node, priority in node_priority[:max_nodes-1]]
        
        return list(important_nodes) + top_nodes
    
    def _prepare_visual_attributes(self, graph: nx.DiGraph, username: str, 
                                 highlight_nodes: set) -> Tuple:
        """Prepara atributos visuales para el grafo"""
        node_colors = []
        node_sizes = []
        edge_colors = []
        edge_widths = []
        
        # Colores y tamaños de nodos
        for node in graph.nodes():
            node_type = graph.nodes[node].get('type', 'other')
            
            if node == username:
                node_colors.append(self.colors['main_user'])
                node_sizes.append(500)
            elif highlight_nodes and node in highlight_nodes:
                node_colors.append(self.colors['common'])
                node_sizes.append(200)
            else:
                node_colors.append(self.colors.get(node_type, '#999999'))
                node_sizes.append(graph.nodes[node].get('size', 30))
        
        # Colores y anchos de aristas
        for u, v in graph.edges():
            edge_data = graph[u][v]
            relationship = edge_data.get('relationship', '')
            weight = edge_data.get('weight', 1)
            
            if relationship == 'mutual':
                edge_colors.append(self.colors['mutual'])
                edge_widths.append(2.5)
            elif relationship in ['follower', 'following']:
                edge_colors.append('blue' if relationship == 'following' else 'green')
                edge_widths.append(1.5)
            else:
                edge_colors.append('gray')
                edge_widths.append(weight * 0.5)
        
        return node_colors, node_sizes, edge_colors, edge_widths
    
    def _get_selective_labels(self, graph: nx.DiGraph, username: str, 
                            highlight_nodes: set) -> Dict[str, str]:
        """Selecciona qué nodos etiquetar para evitar sobrecarga visual"""
        labels = {username: username}  # Siempre etiquetar al usuario principal
        
        # Etiquetar nodos destacados
        if highlight_nodes:
            for node in highlight_nodes:
                if node in graph.nodes():
                    labels[node] = node
        
        # Etiquetar algunos nodos adicionales importantes
        for node in graph.nodes():
            if (node not in labels and 
                graph.nodes[node].get('type') in ['mutual'] and 
                len(labels) < 15):  # Límite de etiquetas
                labels[node] = node
        
        return labels
    
    def _add_enhanced_legend(self, include_common: bool = False) -> None:
        """Añade leyenda mejorada al gráfico"""
        from matplotlib.patches import Patch
        
        legend_elements = [
            Patch(facecolor=self.colors['main_user'], label='Usuario Principal'),
            Patch(facecolor=self.colors['follower'], label='Seguidor'),
            Patch(facecolor=self.colors['following'], label='Seguido'),
            Patch(facecolor=self.colors['mutual'], label='Relación Mutua'),
            Patch(facecolor=self.colors['liked_author'], label='Autor Likeado'),
        ]
        
        if include_common:
            legend_elements.append(Patch(facecolor=self.colors['common'], label='Conexión Común'))
        
        plt.legend(handles=legend_elements, loc='upper right', 
                  bbox_to_anchor=(1.15, 1), borderaxespad=0.)