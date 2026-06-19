import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import func
from src.database import DatabaseManager
from src.models import Evocacao, CategoriaDiscursiva, EspacialidadeDiscursiva

class ChartService:
    # Cores harmoniosas (estilo moderno/clean)
    PRIMARY_COLOR = '#3a86c8'
    SECONDARY_COLOR = '#8338ec'
    BACKGROUND_COLOR = '#1e1e2e'
    TEXT_COLOR = '#cdd6f4'
    ACCENT_COLOR = '#ff006e'

    @staticmethod
    def _apply_style(fig, ax, is_dark=True):
        """Aplica estilos modernos e limpos aos gráficos."""
        if is_dark:
            fig.patch.set_facecolor('#181825')
            ax.set_facecolor('#1e1e2e')
            ax.spines['bottom'].set_color('#585b70')
            ax.spines['left'].set_color('#585b70')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(colors='#cdd6f4', which='both')
            ax.yaxis.label.set_color('#cdd6f4')
            ax.xaxis.label.set_color('#cdd6f4')
            ax.title.set_color('#cdd6f4')
            plt.grid(True, linestyle='--', alpha=0.1, color='#cdd6f4')
        else:
            fig.patch.set_facecolor('#ffffff')
            ax.set_facecolor('#f8f9fa')
            ax.spines['bottom'].set_color('#ced4da')
            ax.spines['left'].set_color('#ced4da')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(colors='#212529', which='both')
            ax.yaxis.label.set_color('#212529')
            ax.xaxis.label.set_color('#212529')
            ax.title.set_color('#212529')
            plt.grid(True, linestyle='--', alpha=0.3, color='#ced4da')

    @classmethod
    def generate_category_frequency_chart(cls, dest_image_path, is_dark=True):
        """
        Gera um gráfico de barras com a frequência de categorias discursivas e salva em arquivo.
        """
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        # Consulta frequências
        results = (
            session.query(CategoriaDiscursiva.nome, func.count(Evocacao.id))
            .join(Evocacao, Evocacao.categoria_id == CategoriaDiscursiva.id)
            .group_by(CategoriaDiscursiva.nome)
            .order_by(func.count(Evocacao.id).desc())
            .all()
        )
        
        fig, ax = plt.subplots(figsize=(8, 5))
        cls._apply_style(fig, ax, is_dark)
        
        if not results:
            ax.text(0.5, 0.5, 'Nenhuma evocação registrada ainda.', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, color=cls.TEXT_COLOR if is_dark else '#212529', fontsize=12)
            ax.set_title("Frequência de Categorias Discursivas")
        else:
            nomes, frequencias = zip(*results)
            # Limita a mostrar as top 15 se forem muitas
            nomes = nomes[:15]
            frequencias = frequencias[:15]
            
            y_pos = np.arange(len(nomes))
            bars = ax.barh(y_pos, frequencias, align='center', color=cls.PRIMARY_COLOR, alpha=0.9, height=0.6)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(nomes)
            ax.invert_yaxis()  # top-down
            ax.set_xlabel('Frequência (Número de Evocações)')
            ax.set_title('Categorias Discursivas mais Frequentes')
            
            # Adiciona rótulos de valores nas pontas das barras
            for bar in bars:
                width = bar.get_width()
                ax.annotate(f'{int(width)}',
                            xy=(width, bar.get_y() + bar.get_height() / 2),
                            xytext=(5, 0),  # 5 points horizontal offset
                            textcoords="offset points",
                            ha='left', va='center',
                            color=cls.TEXT_COLOR if is_dark else '#212529',
                            fontweight='bold')
                            
        plt.tight_layout()
        os.makedirs(os.path.dirname(dest_image_path), exist_ok=True)
        plt.savefig(dest_image_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        return dest_image_path

    @classmethod
    def generate_spatiality_frequency_chart(cls, dest_image_path, is_dark=True):
        """
        Gera um gráfico de barras com a frequência de espacialidades discursivas e salva em arquivo.
        """
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        # Consulta frequências
        results = (
            session.query(EspacialidadeDiscursiva.nome, func.count(Evocacao.id))
            .join(Evocacao, Evocacao.espacialidade_id == EspacialidadeDiscursiva.id)
            .group_by(EspacialidadeDiscursiva.nome)
            .order_by(func.count(Evocacao.id).desc())
            .all()
        )
        
        fig, ax = plt.subplots(figsize=(8, 5))
        cls._apply_style(fig, ax, is_dark)
        
        if not results:
            ax.text(0.5, 0.5, 'Nenhuma evocação registrada ainda.', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, color=cls.TEXT_COLOR if is_dark else '#212529', fontsize=12)
            ax.set_title("Frequência de Espacialidades Discursivas")
        else:
            nomes, frequencias = zip(*results)
            nomes = nomes[:15]
            frequencias = frequencias[:15]
            
            y_pos = np.arange(len(nomes))
            bars = ax.barh(y_pos, frequencias, align='center', color=cls.SECONDARY_COLOR, alpha=0.9, height=0.6)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(nomes)
            ax.invert_yaxis()
            ax.set_xlabel('Frequência (Número de Evocações)')
            ax.set_title('Espacialidades Discursivas mais Frequentes')
            
            for bar in bars:
                width = bar.get_width()
                ax.annotate(f'{int(width)}',
                            xy=(width, bar.get_y() + bar.get_height() / 2),
                            xytext=(5, 0),
                            textcoords="offset points",
                            ha='left', va='center',
                            color=cls.TEXT_COLOR if is_dark else '#212529',
                            fontweight='bold')
                            
        plt.tight_layout()
        os.makedirs(os.path.dirname(dest_image_path), exist_ok=True)
        plt.savefig(dest_image_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        return dest_image_path

    @classmethod
    def get_crossover_matrix(cls):
        """
        Retorna a matriz de cruzamento (Pandas DataFrame) entre Categoria Discursiva e Espacialidade Discursiva.
        """
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        # Buscar todas as categorias, espacialidades e evocações
        cats = session.query(CategoriaDiscursiva.nome).all()
        esps = session.query(EspacialidadeDiscursiva.nome).all()
        evocs = session.query(Evocacao).all()
        
        cat_names = sorted([c[0] for c in cats])
        esp_names = sorted([e[0] for e in esps])
        
        # Criar matriz vazia
        matrix = pd.DataFrame(0, index=cat_names, columns=esp_names)
        
        for ev in evocs:
            if ev.categoria and ev.espacialidade:
                c_name = ev.categoria.nome
                e_name = ev.espacialidade.nome
                if c_name in matrix.index and e_name in matrix.columns:
                    matrix.loc[c_name, e_name] += 1
                    
        return matrix

    @classmethod
    def generate_crossover_matrix_heatmap(cls, dest_image_path, is_dark=True):
        """
        Gera e salva uma representação visual (heatmap) da matriz de cruzamento.
        """
        matrix = cls.get_crossover_matrix()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        cls._apply_style(fig, ax, is_dark)
        
        if matrix.empty or matrix.sum().sum() == 0:
            ax.text(0.5, 0.5, 'Nenhum cruzamento de evocações registrado ainda.', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, color=cls.TEXT_COLOR if is_dark else '#212529', fontsize=12)
            ax.set_title("Matriz de Cruzamento (Categorias x Espacialidades)")
        else:
            # Heatmap com cores modernas
            cmap = 'plasma' if is_dark else 'YlOrRd'
            im = ax.imshow(matrix.values, cmap=cmap, aspect='auto')
            
            # Adicionar barras de cores
            cbar = ax.figure.colorbar(im, ax=ax)
            cbar.ax.tick_params(colors=cls.TEXT_COLOR if is_dark else '#212529')
            cbar.ax.set_ylabel("Frequência de Evocações", rotation=-90, va="bottom", color=cls.TEXT_COLOR if is_dark else '#212529')
            
            # Configurar rótulos
            ax.set_xticks(np.arange(len(matrix.columns)))
            ax.set_yticks(np.arange(len(matrix.index)))
            ax.set_xticklabels(matrix.columns, rotation=45, ha="right", rotation_mode="anchor")
            ax.set_yticklabels(matrix.index)
            
            # Adicionar anotações numéricas nas células
            for i in range(len(matrix.index)):
                for j in range(len(matrix.columns)):
                    val = matrix.values[i, j]
                    # Cor do texto dependendo da intensidade
                    text_color = "black" if not is_dark or val > (matrix.values.max() / 2) else "white"
                    ax.text(j, i, f"{int(val)}",
                            ha="center", va="center", color=text_color, fontweight='bold')
            
            ax.set_title("Matriz de Cruzamento: Categorias vs Espacialidades")
            
        plt.tight_layout()
        os.makedirs(os.path.dirname(dest_image_path), exist_ok=True)
        plt.savefig(dest_image_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        return dest_image_path
