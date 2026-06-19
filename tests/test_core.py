import os
import unittest
import tempfile
import shutil
import csv
from datetime import datetime

from src.database import DatabaseManager
from src.models import Projeto, Entrevista, Sujeito, CategoriaDiscursiva, EspacialidadeDiscursiva, Evocacao
from src.importers import ImportService
from src.exporters import ExportService

class TestGeoConteudoCore(unittest.TestCase):
    def setUp(self):
        # Cria diretório temporário para simular o projeto
        self.test_dir = tempfile.mkdtemp()
        self.project_root = os.path.join(self.test_dir, "GeoConteudo Teste")
        os.makedirs(self.project_root, exist_ok=True)
        os.makedirs(os.path.join(self.project_root, "entrevistas"), exist_ok=True)
        os.makedirs(os.path.join(self.project_root, "exportacoes"), exist_ok=True)
        os.makedirs(os.path.join(self.project_root, "graficos"), exist_ok=True)
        os.makedirs(os.path.join(self.project_root, "backups"), exist_ok=True)
        
        self.db_filepath = os.path.join(self.project_root, "projeto.geoconteudo")
        
        # Inicializa o banco de dados de teste
        self.db = DatabaseManager.get_instance()
        self.db.initialize_db(self.db_filepath)
        self.session = self.db.get_session()

    def tearDown(self):
        # Fecha sessão e conexão do banco
        self.db.close()
        # Remove a pasta temporária
        shutil.rmtree(self.test_dir)

    def test_1_create_project(self):
        """Teste de criação do projeto e escrita de metadados no banco."""
        proj = Projeto(
            nome="Projeto Teste",
            descricao="Descrição de teste",
            observacoes_metodologicas="Método qualitativo"
        )
        self.session.add(proj)
        self.session.commit()
        
        saved_proj = self.session.query(Projeto).first()
        self.assertIsNotNone(saved_proj)
        self.assertEqual(saved_proj.nome, "Projeto Teste")
        self.assertEqual(saved_proj.descricao, "Descrição de teste")
        self.assertTrue(os.path.exists(self.db_filepath))
        self.assertTrue(os.path.exists(os.path.join(self.project_root, "entrevistas")))

    def test_2_import_interview_txt(self):
        """Teste de importação de entrevista a partir de arquivo TXT."""
        # Cria arquivo TXT temporário para teste
        txt_path = os.path.join(self.test_dir, "entrevista_joao.txt")
        texto_conteudo = "Eu moro no bairro Centro e sinto que a praça central é um espaço de lazer importante."
        
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(texto_conteudo)
            
        # Realiza a importação
        entrevista = ImportService.import_interview(txt_path, self.project_root)
        
        self.assertIsNotNone(entrevista)
        self.assertEqual(entrevista.titulo, "Entrevista Joao")
        self.assertEqual(entrevista.texto_extraido, texto_conteudo)
        
        # Verifica se copiou o arquivo físico
        copied_filepath = os.path.join(self.project_root, entrevista.caminho_relativo_arquivo)
        self.assertTrue(os.path.exists(copied_filepath))
        
        # Verifica no banco
        db_ent = self.session.query(Entrevista).filter(Entrevista.id == entrevista.id).first()
        self.assertIsNotNone(db_ent)
        self.assertEqual(db_ent.titulo, "Entrevista Joao")

    def test_3_create_subjects_categories_and_spatialities(self):
        """Teste de cadastro de Sujeito, Categorias e Espacialidades."""
        # Cadastro de Sujeito
        suj = Sujeito(
            codigo_pseudonimo="SUJ_TESTE_01",
            genero="Feminino",
            idade=35,
            municipio="Guarapuava",
            bairro="Bonsucesso"
        )
        self.session.add(suj)
        
        # Cadastro de Categoria
        cat = CategoriaDiscursiva(
            nome="Lazer Urbano",
            descricao="Espaços destinados ao divertimento e sociabilidade."
        )
        self.session.add(cat)
        
        # Cadastro de Espacialidade
        esp = EspacialidadeDiscursiva(
            nome="Praça Central",
            descricao="A praça principal do município como centralidade."
        )
        self.session.add(esp)
        self.session.commit()
        
        db_suj = self.session.query(Sujeito).filter(Sujeito.codigo_pseudonimo == "SUJ_TESTE_01").first()
        db_cat = self.session.query(CategoriaDiscursiva).filter(CategoriaDiscursiva.nome == "Lazer Urbano").first()
        db_esp = self.session.query(EspacialidadeDiscursiva).filter(EspacialidadeDiscursiva.nome == "Praça Central").first()
        
        self.assertIsNotNone(db_suj)
        self.assertIsNotNone(db_cat)
        self.assertIsNotNone(db_esp)
        self.assertEqual(db_suj.idade, 35)

    def test_4_create_evocation(self):
        """Teste de criação de evocação e indexação de trechos."""
        # Insere dados de suporte
        suj = Sujeito(codigo_pseudonimo="SUJ_01")
        cat = CategoriaDiscursiva(nome="Categoria A")
        esp = EspacialidadeDiscursiva(nome="Espaço X")
        
        ent = Entrevista(
            titulo="Entrevista de Teste",
            nome_arquivo_original="teste.txt",
            caminho_relativo_arquivo="entrevistas/teste.txt",
            texto_extraido="Minha casa fica perto do rio Jordão, onde costumo caminhar."
        )
        self.session.add_all([suj, cat, esp, ent])
        self.session.commit()
        
        # Cria a evocação
        trecho = "rio Jordão"
        pos_ini = ent.texto_extraido.find(trecho)
        pos_fim = pos_ini + len(trecho)
        
        evoc = Evocacao(
            entrevista_id=ent.id,
            sujeito_id=suj.id,
            categoria_id=cat.id,
            espacialidade_id=esp.id,
            trecho_literal=trecho,
            posicao_inicial=pos_ini,
            posicao_final=pos_fim,
            elementos="rio, caminhada",
            sujeito_relacao="própria pessoa",
            observacoes_analiticas="Natureza e lazer próximo de casa"
        )
        self.session.add(evoc)
        self.session.commit()
        
        db_evoc = self.session.query(Evocacao).filter(Evocacao.trecho_literal == trecho).first()
        self.assertIsNotNone(db_evoc)
        self.assertEqual(db_evoc.posicao_inicial, pos_ini)
        self.assertEqual(db_evoc.posicao_final, pos_fim)
        self.assertEqual(db_evoc.categoria.nome, "Categoria A")
        self.assertEqual(db_evoc.espacialidade.nome, "Espaço X")

    def test_5_export_to_csv(self):
        """Teste de exportação de evocações para arquivo CSV."""
        # Prepara um ambiente populado
        suj = Sujeito(codigo_pseudonimo="SUJ_EXPORT")
        cat = CategoriaDiscursiva(nome="Cat Export")
        esp = EspacialidadeDiscursiva(nome="Esp Export")
        ent = Entrevista(
            titulo="Entrevista Export",
            nome_arquivo_original="export.txt",
            caminho_relativo_arquivo="entrevistas/export.txt",
            texto_extraido="Texto de teste para exportar dados."
        )
        self.session.add_all([suj, cat, esp, ent])
        self.session.commit()
        
        evoc = Evocacao(
            entrevista_id=ent.id,
            sujeito_id=suj.id,
            categoria_id=cat.id,
            espacialidade_id=esp.id,
            trecho_literal="teste para exportar",
            posicao_inicial=9,
            posicao_final=27,
            elementos="dados",
            sujeito_relacao="nenhum",
            observacoes_analiticas="Observação teste"
        )
        self.session.add(evoc)
        self.session.commit()
        
        # Exporta
        export_csv_path = os.path.join(self.project_root, "exportacoes", "todas_as_evocacoes.csv")
        ExportService.export_evocations_to_csv(export_csv_path)
        
        self.assertTrue(os.path.exists(export_csv_path))
        
        # Abre o CSV e confere dados
        with open(export_csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            rows = list(reader)
            
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["sujeito_codigo"], "SUJ_EXPORT")
            self.assertEqual(rows[0]["categoria_discursiva"], "Cat Export")
            self.assertEqual(rows[0]["espacialidade_discursiva"], "Esp Export")
            self.assertEqual(rows[0]["trecho_literal"], "teste para exportar")

if __name__ == '__main__':
    unittest.main()
