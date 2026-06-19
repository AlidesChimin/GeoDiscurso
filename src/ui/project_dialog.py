import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from src.database import DatabaseManager
from src.models import Projeto

class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Projeto GeoDiscurso")
        self.resize(500, 450)
        self.project_path = None
        self.db_filepath = None
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Criar Novo Projeto de Pesquisa")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        subtitle = QLabel("Os dados do projeto serão guardados em um banco de dados local na pasta selecionada.")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Nome do projeto
        layout.addWidget(QLabel("Nome do Projeto *"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Análise das Espacialidades Urbanas em Guarapuava")
        layout.addWidget(self.name_input)
        
        # Descrição
        layout.addWidget(QLabel("Descrição"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Uma descrição geral dos objetivos da pesquisa...")
        self.desc_input.setMaximumHeight(80)
        layout.addWidget(self.desc_input)
        
        # Observações Metodológicas
        layout.addWidget(QLabel("Observações Metodológicas"))
        self.method_input = QTextEdit()
        self.method_input.setPlaceholderText("Notas sobre a abordagem de análise de conteúdo, corpus de análise, etc...")
        self.method_input.setMaximumHeight(80)
        layout.addWidget(self.method_input)
        
        # Pasta de Destino
        layout.addWidget(QLabel("Pasta de Destino do Projeto *"))
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("Selecione onde a pasta do projeto será criada...")
        self.browse_btn = QPushButton("Procurar...")
        self.browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)
        
        layout.addSpacing(15)
        
        # Botões de Ação
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.create_btn = QPushButton("Criar Projeto")
        self.create_btn.setObjectName("primaryBtn")
        self.create_btn.clicked.connect(self.create_project)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.create_btn)
        layout.addLayout(btn_layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Diretório para o Projeto")
        if folder:
            self.path_input.setText(folder)

    def create_project(self):
        nome = self.name_input.text().strip()
        base_dir = self.path_input.text().strip()
        
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome do projeto é obrigatório.")
            return
        if not base_dir:
            QMessageBox.warning(self, "Aviso", "A pasta de destino do projeto é obrigatória.")
            return
            
        # Cria a pasta do projeto
        project_folder_name = f"GeoDiscurso {nome}"
        # Higieniza o nome da pasta
        for char in ['/', '\\', '?', '%', '*', ':', '|', '"', '<', '>']:
            project_folder_name = project_folder_name.replace(char, '')
            
        project_root = os.path.join(base_dir, project_folder_name)
        
        if os.path.exists(project_root):
            reply = QMessageBox.question(
                self, "Diretório Existente",
                f"O diretório '{project_folder_name}' já existe. Deseja utilizar este diretório mesmo assim?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        try:
            # Cria a estrutura de pastas do projeto
            os.makedirs(project_root, exist_ok=True)
            os.makedirs(os.path.join(project_root, "entrevistas"), exist_ok=True)
            os.makedirs(os.path.join(project_root, "exportacoes"), exist_ok=True)
            os.makedirs(os.path.join(project_root, "graficos"), exist_ok=True)
            os.makedirs(os.path.join(project_root, "backups"), exist_ok=True)
            
            # Inicializa o banco de dados SQLite no arquivo projeto.geoconteudo
            self.db_filepath = os.path.join(project_root, "projeto.geoconteudo")
            db = DatabaseManager.get_instance()
            db.initialize_db(self.db_filepath)
            
            # Salva os metadados do projeto no banco
            session = db.get_session()
            proj = Projeto(
                nome=nome,
                descricao=self.desc_input.toPlainText().strip(),
                observacoes_metodologicas=self.method_input.toPlainText().strip()
            )
            session.add(proj)
            session.commit()
            
            self.project_path = project_root
            QMessageBox.information(self, "Sucesso", "Projeto criado com sucesso!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível criar o projeto: {str(e)}")
