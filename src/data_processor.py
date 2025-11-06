import json
import pandas as pd
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any, Tuple
import os

class InstagramDataProcessor:
    """Procesa los datos JSON de Instagram con manejo mejorado de errores"""
    
    @staticmethod
    def load_json_file(file_path: str) -> Any:
        """Carga un archivo JSON con manejo robusto de errores"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"⚠️ Error cargando {file_path}: {e}")
            return None
    
    @staticmethod
    def extract_followers(data: List[Dict]) -> Set[str]:
        """Extrae usernames de seguidores normalizados"""
        followers = set()
        if not data:
            return followers
            
        for user in data:
            try:
                if user.get('string_list_data'):
                    username = user['string_list_data'][0]['value'].strip().lower()
                    if username:  # Solo agregar si no está vacío
                        followers.add(username)
            except (KeyError, IndexError, AttributeError) as e:
                print(f"Error procesando seguidor: {e}")
                continue
        return followers
    
    @staticmethod
    def extract_following(data: Dict) -> Set[str]:
        """Extrae usernames de seguidos normalizados"""
        following = set()
        if not data or 'relationships_following' not in data:
            return following
            
        for user in data['relationships_following']:
            try:
                username = user['title'].strip().lower()
                if username:
                    following.add(username)
            except (KeyError, AttributeError) as e:
                print(f"Error procesando seguido: {e}")
                continue
        return following
    
    @staticmethod
    def extract_liked_posts(data: Dict) -> Dict[str, int]:
        """Extrae autores de posts likeados y su frecuencia"""
        liked_authors = Counter()
        if not data or 'likes_media_likes' not in data:
            return liked_authors
            
        for like in data['likes_media_likes']:
            try:
                username = like['title'].strip().lower()
                if username:
                    liked_authors[username] += 1
            except (KeyError, AttributeError) as e:
                print(f"Error procesando like: {e}")
                continue
        return liked_authors
    
    @staticmethod
    def extract_story_likes(data: Dict) -> Dict[str, int]:
        """Extrae autores de stories likeados y su frecuencia"""
        story_authors = Counter()
        if not data or 'story_activities_story_likes' not in data:
            return story_authors
            
        for like in data['story_activities_story_likes']:
            try:
                username = like['title'].strip().lower()
                if username:
                    story_authors[username] += 1
            except (KeyError, AttributeError) as e:
                print(f"Error procesando story like: {e}")
                continue
        return story_authors
    
    def process_user_data(self, data_dir: str) -> Dict[str, Any]:
        """Procesa todos los datos de un usuario con validación"""
        print(f"📂 Procesando datos en: {data_dir}")
        
        # Verificar que los archivos existan
        required_files = ['followers_1.json', 'following.json', 'liked_posts.json']
        for file in required_files:
            if not os.path.exists(os.path.join(data_dir, file)):
                print(f"❌ Archivo faltante: {file}")
                return {}
        
        try:
            result = {
                'followers': self.extract_followers(
                    self.load_json_file(os.path.join(data_dir, 'followers_1.json'))
                ),
                'following': self.extract_following(
                    self.load_json_file(os.path.join(data_dir, 'following.json'))
                ),
                'liked_posts': self.extract_liked_posts(
                    self.load_json_file(os.path.join(data_dir, 'liked_posts.json'))
                ),
                'story_likes': self.extract_story_likes(
                    self.load_json_file(os.path.join(data_dir, 'story_likes.json'))
                ) if os.path.exists(os.path.join(data_dir, 'story_likes.json')) else Counter()
            }
            
            # Estadísticas de procesamiento
            print(f"   ✅ Seguidores: {len(result['followers'])}")
            print(f"   ✅ Seguidos: {len(result['following'])}")
            print(f"   ✅ Posts likeados: {sum(result['liked_posts'].values())} de {len(result['liked_posts'])} autores")
            print(f"   ✅ Stories likeados: {sum(result['story_likes'].values())}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error crítico procesando {data_dir}: {e}")
            return {}