import networkx as nx
import pandas as pd
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any, Tuple
import numpy as np
from data_processor import InstagramDataProcessor

class UserGraphAnalyzer:
    """Analizador de grafo para un usuario individual"""
    
    def __init__(self, username: str):
        self.username = username
        self.graph = nx.DiGraph()
        self.data_processor = InstagramDataProcessor()
        self.user_data = None
        
    def load_data(self, data_dir: str) -> bool:
        """Carga y procesa los datos del usuario"""
        self.user_data = self.data_processor.process_user_data(data_dir)
        if not self.user_data:
            return False
        self._build_graph()
        return True
    
    def _build_graph(self) -> None:
        """Construye el grafo social para un usuario"""
        # Agregar usuario principal
        self.graph.add_node(self.username, type='main_user', size=100, color='red')
        
        # Agregar relaciones de seguimiento
        self._add_follow_relationships()
        
        # Agregar interacciones
        self._add_interaction_relationships()
        
        print(f"   📊 Grafo construido: {self.graph.number_of_nodes()} nodos, {self.graph.number_of_edges()} aristas")
    
    def _add_follow_relationships(self) -> None:
        """Agrega relaciones de seguidores y seguidos"""
        # Seguidores
        for follower in self.user_data['followers']:
            self.graph.add_node(follower, type='follower', size=30, color='blue')
            self.graph.add_edge(follower, self.username, relationship='follower', weight=1)
        
        # Seguidos
        for following in self.user_data['following']:
            self.graph.add_node(following, type='following', size=30, color='green')
            self.graph.add_edge(self.username, following, relationship='following', weight=1)
        
        # Relaciones mutuas
        mutual_follows = self.user_data['followers'] & self.user_data['following']
        for user in mutual_follows:
            if self.graph.has_edge(self.username, user):
                self.graph[self.username][user]['mutual'] = True
                self.graph[self.username][user]['relationship'] = 'mutual'
                self.graph[self.username][user]['weight'] = 2  # Mayor peso para relaciones mutuas
    
    def _add_interaction_relationships(self) -> None:
        """Agrega relaciones de interacciones (likes)"""
        # Posts likeados
        for author, count in self.user_data['liked_posts'].items():
            self.graph.add_node(author, type='liked_author', size=20, color='orange')
            self.graph.add_edge(
                self.username, author, 
                relationship='liked_post', 
                weight=count * 0.5,  # Peso basado en frecuencia
                interaction_count=count
            )
        
        # Stories likeados
        for author, count in self.user_data['story_likes'].items():
            if author not in self.graph:
                self.graph.add_node(author, type='story_author', size=20, color='purple')
            self.graph.add_edge(
                self.username, author,
                relationship='liked_story',
                weight=count * 0.3,
                interaction_count=count
            )
    
    def get_analysis(self) -> Dict[str, Any]:
        """Retorna análisis completo del grafo individual"""
        if not self.graph:
            return {}
        
        return {
            'basic_metrics': self._get_basic_metrics(),
            'network_metrics': self._get_network_metrics(),
            'interaction_analysis': self._get_interaction_analysis(),
            'influence_metrics': self._get_influence_metrics()
        }
    
    def _get_basic_metrics(self) -> Dict[str, Any]:
        """Calcula métricas básicas"""
        mutual_follows = self.user_data['followers'] & self.user_data['following']
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'followers_count': len(self.user_data['followers']),
            'following_count': len(self.user_data['following']),
            'mutual_follows': len(mutual_follows),
            'total_interactions': sum(self.user_data['liked_posts'].values()) + sum(self.user_data['story_likes'].values()),
            'follow_ratio': len(self.user_data['followers']) / max(1, len(self.user_data['following']))
        }
    
    def _get_network_metrics(self) -> Dict[str, Any]:
        """Calcula métricas de red"""
        if self.graph.number_of_nodes() == 0:
            return {}
        
        try:
            undirected_graph = self.graph.to_undirected()
            return {
                'density': nx.density(self.graph),
                'avg_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(),
                'avg_clustering': nx.average_clustering(undirected_graph),
                'connected_components': nx.number_connected_components(undirected_graph),
            }
        except Exception as e:
            print(f"Error calculando métricas de red: {e}")
            return {}
    
    def _get_interaction_analysis(self) -> Dict[str, Any]:
        """Analiza patrones de interacción"""
        return {
            'top_liked_authors': Counter(self.user_data['liked_posts']).most_common(10),
            'top_story_authors': Counter(self.user_data['story_likes']).most_common(10),
            'total_liked_authors': len(self.user_data['liked_posts']),
            'total_story_interactions': len(self.user_data['story_likes']),
            'engagement_rate': (sum(self.user_data['liked_posts'].values()) + 
                              sum(self.user_data['story_likes'].values())) / 
                              max(1, len(self.user_data['following']))
        }
    
    def _get_influence_metrics(self) -> Dict[str, Any]:
        """Calcula métricas de influencia"""
        if not self.graph:
            return {}
        
        try:
            degree_centrality = nx.degree_centrality(self.graph)
            user_centrality = degree_centrality.get(self.username, 0)
            
            return {
                'degree_centrality': user_centrality,
                'influence_score': self._calculate_influence_score(),
                'network_reach': self.graph.number_of_nodes() - 1  # Excluyéndose a sí mismo
            }
        except:
            return {}
    
    def _calculate_influence_score(self) -> float:
        """Calcula un score de influencia personalizado"""
        followers_weight = len(self.user_data['followers']) * 0.4
        mutual_weight = len(self.user_data['followers'] & self.user_data['following']) * 0.3
        interaction_weight = (sum(self.user_data['liked_posts'].values()) + 
                             sum(self.user_data['story_likes'].values())) * 0.2
        engagement_weight = self._get_interaction_analysis()['engagement_rate'] * 100 * 0.1
        
        return followers_weight + mutual_weight + interaction_weight + engagement_weight


class MultiUserGraphAnalyzer:
    """Analizador para múltiples usuarios y sus conexiones"""
    
    def __init__(self):
        self.users = {}  # username -> UserGraphAnalyzer
        self.combined_graph = nx.DiGraph()
        
    def add_user(self, username: str, data_dir: str) -> bool:
        """Añade un usuario al análisis"""
        user_analyzer = UserGraphAnalyzer(username)
        if user_analyzer.load_data(data_dir):
            self.users[username] = user_analyzer
            return True
        return False
    
    def build_combined_graph(self) -> None:
        """Construye un grafo combinado con todos los usuarios"""
        self.combined_graph = nx.DiGraph()
        
        # Agregar todos los usuarios y sus conexiones
        for username, analyzer in self.users.items():
            # Agregar nodos y aristas del usuario
            self.combined_graph.add_nodes_from(analyzer.graph.nodes(data=True))
            self.combined_graph.add_edges_from(analyzer.graph.edges(data=True))
        
        print(f"🌐 Grafo combinado: {self.combined_graph.number_of_nodes()} nodos, {self.combined_graph.number_of_edges()} aristas")
    
    def get_connection_analysis(self) -> Dict[str, Any]:
        """Analiza las conexiones entre usuarios"""
        if len(self.users) < 2:
            return {}
        
        user_list = list(self.users.keys())
        analysis = {
            'direct_connections': self._find_direct_connections(),
            'common_connections': self._find_common_connections(),
            'similarity_matrix': self._calculate_similarity_matrix(),
            'bridge_nodes': self._find_bridge_nodes()
        }
        
        return analysis
    
    def _find_direct_connections(self) -> Dict[Tuple[str, str], bool]:
        """Encuentra conexiones directas entre usuarios principales"""
        direct_connections = {}
        user_list = list(self.users.keys())
        
        for i, user1 in enumerate(user_list):
            for j, user2 in enumerate(user_list):
                if i < j:  # Evitar duplicados
                    # Verificar si se siguen mutuamente
                    follows_1_to_2 = user2 in self.users[user1].user_data['following']
                    follows_2_to_1 = user1 in self.users[user2].user_data['following']
                    
                    direct_connections[(user1, user2)] = follows_1_to_2 and follows_2_to_1
        
        return direct_connections
    
    def _find_common_connections(self) -> Dict[str, List[str]]:
        """Encuentra conexiones comunes entre usuarios"""
        common_connections = {}
        user_list = list(self.users.keys())
        
        for i, user1 in enumerate(user_list):
            for j, user2 in enumerate(user_list):
                if i < j:
                    key = f"{user1}-{user2}"
                    # Encontrar seguidores en común
                    common_followers = (self.users[user1].user_data['followers'] & 
                                      self.users[user2].user_data['followers'])
                    # Encontrar seguidos en común
                    common_following = (self.users[user1].user_data['following'] & 
                                      self.users[user2].user_data['following'])
                    # Encontrar autores likeados en común
                    common_liked = (set(self.users[user1].user_data['liked_posts'].keys()) & 
                                  set(self.users[user2].user_data['liked_posts'].keys()))
                    
                    common_connections[key] = {
                        'common_followers': list(common_followers),
                        'common_following': list(common_following),
                        'common_liked_authors': list(common_liked),
                        'total_common': len(common_followers) + len(common_following) + len(common_liked)
                    }
        
        return common_connections
    
    def _calculate_similarity_matrix(self) -> pd.DataFrame:
        """Calcula matriz de similitud entre usuarios"""
        user_list = list(self.users.keys())
        n = len(user_list)
        similarity_matrix = pd.DataFrame(np.zeros((n, n)), index=user_list, columns=user_list)
        
        for i, user1 in enumerate(user_list):
            for j, user2 in enumerate(user_list):
                if i == j:
                    similarity_matrix.iloc[i, j] = 1.0
                else:
                    similarity = self._calculate_user_similarity(user1, user2)
                    similarity_matrix.iloc[i, j] = similarity
        
        return similarity_matrix
    
    def _calculate_user_similarity(self, user1: str, user2: str) -> float:
        """Calcula similitud entre dos usuarios usando coeficiente de Jaccard"""
        # Combinar todos los nodos de cada usuario (excluyendo a sí mismos)
        nodes1 = set(self.users[user1].graph.nodes()) - {user1}
        nodes2 = set(self.users[user2].graph.nodes()) - {user2}
        
        if not nodes1 and not nodes2:
            return 0.0
        
        # Coeficiente de Jaccard
        intersection = len(nodes1 & nodes2)
        union = len(nodes1 | nodes2)
        
        return intersection / union if union > 0 else 0.0
    
    def _find_bridge_nodes(self) -> List[Tuple[str, int]]:
        """Encuentra nodos que conectan a múltiples usuarios (nodos puente)"""
        if not self.combined_graph:
            return []
        
        bridge_scores = {}
        
        for node in self.combined_graph.nodes():
            if node not in self.users:  # No es un usuario principal
                # Contar en cuántos grafos de usuario aparece este nodo
                user_count = sum(1 for analyzer in self.users.values() 
                               if node in analyzer.graph.nodes())
                
                if user_count > 1:  # Aparece en múltiples usuarios
                    bridge_scores[node] = user_count
        
        # Ordenar por relevancia
        return sorted(bridge_scores.items(), key=lambda x: x[1], reverse=True)[:20]
    
    def get_user_relationships_graph(self) -> nx.DiGraph:
        """Crea un grafo simplificado que muestra solo las relaciones entre usuarios principales"""
        relationship_graph = nx.DiGraph()
        
        # Agregar usuarios principales
        for username in self.users.keys():
            relationship_graph.add_node(username, type='main_user', size=100, color='red')
        
        # Agregar conexiones directas
        direct_connections = self._find_direct_connections()
        for (user1, user2), mutual in direct_connections.items():
            if mutual:
                relationship_graph.add_edge(user1, user2, relationship='mutual', weight=2)
                relationship_graph.add_edge(user2, user1, relationship='mutual', weight=2)
            else:
                if user2 in self.users[user1].user_data['following']:
                    relationship_graph.add_edge(user1, user2, relationship='follows', weight=1)
                if user1 in self.users[user2].user_data['following']:
                    relationship_graph.add_edge(user2, user1, relationship='follows', weight=1)
        
        return relationship_graph
    
    def get_common_connections_graph(self, min_common: int = 2) -> nx.DiGraph:
        """Crea un grafo que muestra usuarios principales y sus conexiones comunes más importantes"""
        common_graph = nx.DiGraph()
        
        # Agregar usuarios principales
        for username in self.users.keys():
            common_graph.add_node(username, type='main_user', size=100, color='red')
        
        # Encontrar nodos comunes importantes
        bridge_nodes = self._find_bridge_nodes()
        
        for bridge_node, score in bridge_nodes:
            if score >= min_common:
                common_graph.add_node(bridge_node, type='bridge', size=50, color='orange', 
                                    bridge_score=score)
                
                # Conectar el nodo puente con los usuarios que lo comparten
                for username, analyzer in self.users.items():
                    if bridge_node in analyzer.graph.nodes():
                        common_graph.add_edge(username, bridge_node, 
                                            relationship='shares', weight=score)
        
        return common_graph