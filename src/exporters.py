import os
import csv
import pandas as pd
from src.database import DatabaseManager
from src.models import Evocacao, CategoriaDiscursiva, EspacialidadeDiscursiva, Entrevista, Sujeito

class ExportService:
    @staticmethod
    def export_evocations_to_csv(dest_filepath):
        """
        Exporta todas as evocações do projeto atual para um arquivo CSV.
        """
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        evocacoes = session.query(Evocacao).all()
        
        data = []
        for ev in evocacoes:
            sujeito_cod = ev.sujeito.codigo_pseudonimo if ev.sujeito else ""
            entrevista_titulo = ev.entrevista.titulo if ev.entrevista else ""
            entrevista_arquivo = ev.entrevista.nome_arquivo_original if ev.entrevista else ""
            cat_nome = ev.categoria.nome if ev.categoria else ""
            esp_nome = ev.espacialidade.nome if ev.espacialidade else ""
            
            data.append({
                "id": ev.id,
                "entrevista_titulo": entrevista_titulo,
                "entrevista_arquivo": entrevista_arquivo,
                "sujeito_codigo": sujeito_cod,
                "categoria_discursiva": cat_nome,
                "espacialidade_discursiva": esp_nome,
                "trecho_literal": ev.trecho_literal,
                "posicao_inicial": ev.posicao_inicial,
                "posicao_final": ev.posicao_final,
                "elementos": ev.elementos or "",
                "sujeito_da_relacao": ev.sujeito_relacao or "",
                "observacoes_analiticas": ev.observacoes_analiticas or "",
                "data_criacao": ev.data_criacao.strftime("%Y-%m-%d %H:%M:%S") if ev.data_criacao else "",
                "data_edicao": ev.data_edicao.strftime("%Y-%m-%d %H:%M:%S") if ev.data_edicao else ""
            })
            
        df = pd.DataFrame(data)
        
        # Garante que mesmo vazio o DataFrame tenha as colunas corretas
        if df.empty:
            df = pd.DataFrame(columns=[
                "id", "entrevista_titulo", "entrevista_arquivo", "sujeito_codigo", 
                "categoria_discursiva", "espacialidade_discursiva", "trecho_literal", 
                "posicao_inicial", "posicao_final", "elementos", "sujeito_da_relacao", 
                "observacoes_analiticas", "data_criacao", "data_edicao"
            ])
            
        # Exporta com codificação UTF-8 e delimitador ponto e vírgula (padrão em Excel BR)
        df.to_csv(dest_filepath, sep=';', index=False, encoding='utf-8-sig')
        return dest_filepath

    @staticmethod
    def export_gephi_network(nodes_dest_path, edges_dest_path, node_a_field='categoria', node_b_field='espacialidade'):
        """
        Exporta redes para o Gephi (Nós e Arestas) cruzando quaisquer dois campos selecionados.
        Campos suportados: 'categoria', 'espacialidade', 'sujeito', 'entrevista', 'elementos', 'sujeito_relacao', 'evocacao'.
        """
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        evocacoes = session.query(Evocacao).all()
        
        def get_node_data(ev, field_name):
            if field_name == 'categoria':
                if ev.categoria:
                    return [(f"cat:{ev.categoria.nome}", ev.categoria.nome, "Categoria Discursiva")]
            elif field_name == 'espacialidade':
                if ev.espacialidade:
                    return [(f"esp:{ev.espacialidade.nome}", ev.espacialidade.nome, "Espacialidade Discursiva")]
            elif field_name == 'sujeito':
                if ev.sujeito:
                    return [(f"suj:{ev.sujeito.codigo_pseudonimo}", ev.sujeito.codigo_pseudonimo, "Sujeito Entrevistado")]
            elif field_name == 'entrevista':
                if ev.entrevista:
                    return [(f"ent:{ev.entrevista.titulo}", ev.entrevista.titulo, "Entrevista")]
            elif field_name == 'elementos':
                if ev.elementos:
                    parts = [p.strip() for p in ev.elementos.split(',') if p.strip()]
                    return [(f"elem:{p.lower()}", p, "Elemento") for p in parts]
            elif field_name == 'sujeito_relacao':
                if ev.sujeito_relacao:
                    return [(f"sujrel:{ev.sujeito_relacao.lower()}", ev.sujeito_relacao, "Sujeito da Relação")]
            elif field_name == 'evocacao':
                label = f"Evocação {ev.id}: \"{ev.trecho_literal[:25]}...\""
                return [(f"evoc:{ev.id}", label, "Evocação")]
            return []
            
        nodes_dict = {}
        edges_weight = {}
        
        for ev in evocacoes:
            nodes_a = get_node_data(ev, node_a_field)
            nodes_b = get_node_data(ev, node_b_field)
            
            for na_id, na_label, na_type in nodes_a:
                nodes_dict[na_id] = (na_label, na_type)
            for nb_id, nb_label, nb_type in nodes_b:
                nodes_dict[nb_id] = (nb_label, nb_type)
                
            for na_id, _, _ in nodes_a:
                for nb_id, _, _ in nodes_b:
                    if na_id == nb_id:
                        continue
                    # Rede não direcionada: chave ordenada alfabeticamente
                    edge_key = tuple(sorted([na_id, nb_id]))
                    edges_weight[edge_key] = edges_weight.get(edge_key, 0) + 1
                    
        # Gravar Nós
        nodes = []
        for n_id, (n_label, n_type) in nodes_dict.items():
            nodes.append({
                "Id": n_id,
                "Label": n_label,
                "Type": n_type
            })
            
        df_nodes = pd.DataFrame(nodes)
        if df_nodes.empty:
            df_nodes = pd.DataFrame(columns=["Id", "Label", "Type"])
        df_nodes.to_csv(nodes_dest_path, sep=';', index=False, encoding='utf-8-sig')
        
        # Gravar Arestas
        edges = []
        for (source, target), weight in edges_weight.items():
            edges.append({
                "Source": source,
                "Target": target,
                "Weight": weight,
                "Type": "Undirected"
            })
            
        df_edges = pd.DataFrame(edges)
        if df_edges.empty:
            df_edges = pd.DataFrame(columns=["Source", "Target", "Weight", "Type"])
        df_edges.to_csv(edges_dest_path, sep=';', index=False, encoding='utf-8-sig')
        
        return nodes_dest_path, edges_dest_path
