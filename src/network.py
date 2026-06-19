import networkx as nx
from src.database import DatabaseManager
from src.models import Evocacao

class NetworkService:
    @staticmethod
    def build_network():
        """
        Gera um objeto networkx.Graph representando a rede de conexões entre 
        Categorias Discursivas e Espacialidades Discursivas baseada em evocações.
        """
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        evocacoes = session.query(Evocacao).all()
        
        # Cria um grafo não direcionado
        G = nx.Graph()
        
        for ev in evocacoes:
            if not ev.categoria or not ev.espacialidade:
                continue
                
            cat_node = f"cat_{ev.categoria_id}"
            esp_node = f"esp_{ev.espacialidade_id}"
            
            # Adiciona os nós com atributos
            if not G.has_node(cat_node):
                G.add_node(cat_node, label=ev.categoria.nome, type="Categoria Discursiva")
            if not G.has_node(esp_node):
                G.add_node(esp_node, label=ev.espacialidade.nome, type="Espacialidade Discursiva")
                
            # Adiciona a aresta ou incrementa o peso
            if G.has_edge(cat_node, esp_node):
                G[cat_node][esp_node]['weight'] += 1
            else:
                G.add_edge(cat_node, esp_node, weight=1, type="Undirected")
                
        return G

    @classmethod
    def get_network_metrics(cls):
        """
        Calcula e retorna métricas básicas do grafo de rede.
        """
        G = cls.build_network()
        
        if len(G.nodes) == 0:
            return {
                "nodes_count": 0,
                "edges_count": 0,
                "density": 0.0,
                "avg_degree": 0.0,
                "most_connected": "Nenhum"
            }
            
        nodes_count = G.number_of_nodes()
        edges_count = G.number_of_edges()
        density = nx.density(G)
        
        # Grau médio dos nós
        degrees = [val for node, val in G.degree()]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0.0
        
        # Encontra o nó com maior grau
        degree_dict = dict(G.degree(weight='weight'))
        most_connected_node = max(degree_dict, key=degree_dict.get) if degree_dict else None
        
        most_connected_label = "Nenhum"
        if most_connected_node:
            most_connected_label = G.nodes[most_connected_node].get('label', most_connected_node)
            most_connected_val = degree_dict[most_connected_node]
            most_connected_label = f"{most_connected_label} (peso total: {most_connected_val})"
            
        return {
            "nodes_count": nodes_count,
            "edges_count": edges_count,
            "density": density,
            "avg_degree": avg_degree,
            "most_connected": most_connected_label
        }
