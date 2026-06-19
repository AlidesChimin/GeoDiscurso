import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QListWidget, QListWidgetItem, QTextEdit, QPushButton, 
    QMessageBox, QFileDialog, QTabWidget, QLabel, QTableWidget, 
    QTableWidgetItem, QMenu, QGroupBox, QFormLayout, QDialog, QComboBox
)
from PySide6.QtGui import QTextCursor, QTextCharFormat, QColor, QAction
from PySide6.QtCore import Qt, QSize
from PySide6.QtSvgWidgets import QSvgWidget  # opcional se tivéssemos svg
import matplotlib.pyplot as plt

from src.database import DatabaseManager
from src.models import Entrevista, Evocacao, Projeto, Sujeito
from src.importers import ImportService
from src.exporters import ExportService
from src.charts import ChartService
from src.network import NetworkService

from src.ui.project_dialog import NewProjectDialog
from src.ui.subject_dialog import SubjectManagerDialog
from src.ui.coding_dialog import CodingDialog
from src.ui.styles import Styles

class GephiExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exportar Rede para Gephi - Cruzamento de Campos")
        self.resize(450, 220)
        
        layout = QVBoxLayout(self)
        
        # Opções de campos para nós
        self.fields = [
            ("Categoria Discursiva", "categoria"),
            ("Espacialidade Discursiva", "espacialidade"),
            ("Sujeito Entrevistado", "sujeito"),
            ("Entrevista", "entrevista"),
            ("Elementos da Relação", "elementos"),
            ("Sujeito da Relação", "sujeito_relacao"),
            ("Evocação (Trecho)", "evocacao")
        ]
        
        layout.addWidget(QLabel("Selecione os dois campos que deseja cruzar no Grafo:"))
        
        form_layout = QFormLayout()
        
        self.combo_a = QComboBox()
        for label, val in self.fields:
            self.combo_a.addItem(label, val)
        # Seleciona Categoria por padrão
        self.combo_a.setCurrentIndex(0)
            
        self.combo_b = QComboBox()
        for label, val in self.fields:
            self.combo_b.addItem(label, val)
        # Seleciona Espacialidade por padrão (para manter o cruzamento padrão ativo inicialmente)
        self.combo_b.setCurrentIndex(1)
        
        form_layout.addRow("Nó A:", self.combo_a)
        form_layout.addRow("Nó B:", self.combo_b)
        layout.addLayout(form_layout)
        
        layout.addSpacing(15)
        
        # Botões de confirmação
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn = QPushButton("Exportar Rede")
        self.ok_btn.setObjectName("primaryBtn")
        self.ok_btn.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)
        
    def get_selected_fields(self):
        return self.combo_a.currentData(), self.combo_b.currentData()

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sobre o GeoDiscurso")
        self.resize(550, 480)
        
        layout = QVBoxLayout(self)
        
        # Campo de texto (Read Only)
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        
        text = (
            "GeoDiscurso\n"
            "Sistema de Análise de Conteúdo Geográfica\n\n"
            "O GeoDiscurso é um aplicativo desktop desenvolvido para apoiar pesquisas qualitativas em Geografia "
            "que utilizam análise de conteúdo. O sistema permite criar projetos de pesquisa, importar entrevistas, "
            "visualizar o texto integral, selecionar trechos, registrar evocações e associá-las a categorias "
            "discursivas, elementos, sujeitos da relação e espacialidades discursivas.\n\n"
            "A finalidade do aplicativo é organizar o processo de codificação qualitativa, preservar a rastreabilidade "
            "entre o trecho original da entrevista e a interpretação analítica, gerar tabelas de apoio, produzir "
            "gráficos de frequência e exportar dados relacionais para softwares como o Gephi.\n\n"
            "A concepção metodológica parte da análise de conteúdo sistematizada por Laurence Bardin e de sua "
            "adaptação à pesquisa geográfica por meio da codificação dupla entre categoria discursiva e "
            "espacialidade discursiva. Nesse sentido, o aplicativo foi pensado para auxiliar o pesquisador a "
            "relacionar o que é dito, por quem é dito, sobre quem é dito e em qual espacialidade discursiva a "
            "evocação se situa.\n\n"
            "Concepção metodológica:\n"
            "Prof. Dr. Alides Baptista Chimin Junior\n"
            "Programa de Pós Graduação em Geografia\n"
            "Universidade Estadual do Centro Oeste, UNICENTRO\n\n"
            "Desenvolvimento:\n"
            "Software desenvolvido com apoio de inteligência artificial no ambiente Antigravity, sob coordenação "
            "metodológica de Prof. Dr. Alides Baptista Chimin Junior.\n\n"
            "Versão:\n"
            "0.1.0\n\n"
            "Licença:\n"
            "Código aberto sob a GNU General Public License (GPL)\n\n"
            "Ano:\n"
            "2026"
        )
        
        self.text_area.setPlainText(text)
        self.text_area.setStyleSheet("font-size: 13px; line-height: 1.4;")
        layout.addWidget(self.text_area)
        
        # Botão Fechar
        btn_layout = QHBoxLayout()
        self.close_btn = QPushButton("Fechar")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project_root = None
        self.active_project = None
        self.selected_interview = None
        
        self.setWindowTitle("GeoDiscurso - Análise de Conteúdo Qualitativa Geográfica")
        self.resize(1200, 750)
        
        # Carrega folha de estilo premium
        self.setStyleSheet(Styles.QSS)
        
        self.init_menu()
        self.init_ui()
        self.update_project_ui_state()

    def init_menu(self):
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("Arquivo")
        
        new_proj_action = QAction("Novo Projeto...", self)
        new_proj_action.setShortcut("Ctrl+N")
        new_proj_action.triggered.connect(self.new_project)
        file_menu.addAction(new_proj_action)
        
        open_proj_action = QAction("Abrir Projeto...", self)
        open_proj_action.setShortcut("Ctrl+O")
        open_proj_action.triggered.connect(self.open_project_dialog)
        file_menu.addAction(open_proj_action)
        
        self.close_proj_action = QAction("Fechar Projeto", self)
        self.close_proj_action.triggered.connect(self.close_project)
        file_menu.addAction(self.close_proj_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Gerenciar
        self.manage_menu = menubar.addMenu("Gerenciar")
        
        subjects_action = QAction("Sujeitos Entrevistados...", self)
        subjects_action.triggered.connect(self.manage_subjects)
        self.manage_menu.addAction(subjects_action)
        
        # Menu Análise e Exportação
        self.analysis_menu = menubar.addMenu("Análise e Exportação")
        
        export_csv_action = QAction("Exportar Evocações (CSV)...", self)
        export_csv_action.triggered.connect(self.export_evocations_csv)
        self.analysis_menu.addAction(export_csv_action)
        
        export_gephi_action = QAction("Exportar Rede para Gephi (CSV)...", self)
        export_gephi_action.triggered.connect(self.export_gephi_network)
        self.analysis_menu.addAction(export_gephi_action)
        
        # Botão/Ação Sobre na barra de menus
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self.show_about_dialog)
        menubar.addAction(about_action)
        
        self.analysis_menu.addSeparator()
        
        gen_charts_action = QAction("Gerar Gráficos e Matriz...", self)
        gen_charts_action.triggered.connect(self.generate_project_reports)
        self.analysis_menu.addAction(gen_charts_action)

    def init_ui(self):
        # Widget Central
        self.central_tab_widget = QTabWidget()
        self.setCentralWidget(self.central_tab_widget)
        
        # ABA 1: Painel Principal de Análise (Dividido em 3 colunas)
        self.analysis_tab = QWidget()
        self.central_tab_widget.addTab(self.analysis_tab, "Leitura e Codificação")
        
        analysis_layout = QHBoxLayout(self.analysis_tab)
        analysis_layout.setContentsMargins(10, 10, 10, 10)
        
        # Splitter principal de 3 colunas
        self.splitter = QSplitter(Qt.Horizontal)
        analysis_layout.addWidget(self.splitter)
        
        # --- 1. Lateral Esquerda: Lista de Entrevistas ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_title = QLabel("Entrevistas")
        left_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #89b4fa;")
        left_layout.addWidget(left_title)
        
        self.import_btn = QPushButton("+ Importar Entrevista")
        self.import_btn.setObjectName("primaryBtn")
        self.import_btn.clicked.connect(self.import_interview)
        left_layout.addWidget(self.import_btn)
        
        self.interview_list = QListWidget()
        self.interview_list.currentItemChanged.connect(self.on_interview_selected)
        left_layout.addWidget(self.interview_list)
        
        self.splitter.addWidget(left_widget)
        
        # --- 2. Painel Central: Leitor de Entrevista e Análise ---
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        self.interview_title_label = QLabel("Selecione uma entrevista na lateral")
        self.interview_title_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        center_layout.addWidget(self.interview_title_label)
        
        self.text_reader = QTextEdit()
        self.text_reader.setReadOnly(True)
        self.text_reader.setPlaceholderText("O texto da entrevista selecionada aparecerá aqui. Selecione um trecho com o mouse para codificar.")
        self.text_reader.setStyleSheet("background-color: #11111b; padding: 15px; font-size: 14px; line-height: 1.6;")
        center_layout.addWidget(self.text_reader)
        
        # Botão de Ação "Analisar trecho"
        self.analyze_btn = QPushButton("Analisar trecho")
        self.analyze_btn.setObjectName("secondaryBtn")
        self.analyze_btn.setMinimumHeight(40)
        self.analyze_btn.setStyleSheet("font-size: 14px;")
        self.analyze_btn.clicked.connect(self.analyze_selected_text)
        center_layout.addWidget(self.analyze_btn)
        
        self.splitter.addWidget(center_widget)
        
        # --- 3. Lateral Direita: Evocações Codificadas ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        right_title = QLabel("Evocações na Entrevista")
        right_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #cba6f7;")
        right_layout.addWidget(right_title)
        
        self.evocation_list = QListWidget()
        self.evocation_list.itemClicked.connect(self.on_evocation_clicked)
        # Menu de contexto para editar/excluir
        self.evocation_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.evocation_list.customContextMenuRequested.connect(self.show_evocation_context_menu)
        right_layout.addWidget(self.evocation_list)
        
        self.splitter.addWidget(right_widget)
        
        # Ajusta tamanhos iniciais das colunas (20%, 55%, 25%)
        self.splitter.setSizes([220, 600, 280])
        
        # ABA 2: Estatísticas e Visualizações
        self.reports_tab = QWidget()
        self.central_tab_widget.addTab(self.reports_tab, "Relatórios e Visualizações")
        
        self.init_reports_ui()

    def init_reports_ui(self):
        reports_layout = QHBoxLayout(self.reports_tab)
        
        # Lateral esquerda com controles de relatório
        control_panel = QGroupBox("Ações de Visualização")
        control_layout = QVBoxLayout(control_panel)
        
        self.btn_gen_all = QPushButton("Atualizar Dados e Gráficos")
        self.btn_gen_all.setObjectName("primaryBtn")
        self.btn_gen_all.clicked.connect(self.generate_project_reports)
        control_layout.addWidget(self.btn_gen_all)
        
        self.btn_open_exp_dir = QPushButton("Abrir Pasta de Exportações")
        self.btn_open_exp_dir.clicked.connect(self.open_exportations_dir)
        control_layout.addWidget(self.btn_open_exp_dir)
        
        control_layout.addSpacing(15)
        control_layout.addWidget(QLabel("Métricas de Rede (NetworkX):"))
        
        self.metrics_form = QWidget()
        metrics_form_layout = QFormLayout(self.metrics_form)
        metrics_form_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_net_nodes = QLabel("-")
        metrics_form_layout.addRow("Total de Nós:", self.lbl_net_nodes)
        self.lbl_net_edges = QLabel("-")
        metrics_form_layout.addRow("Total de Arestas:", self.lbl_net_edges)
        self.lbl_net_density = QLabel("-")
        metrics_form_layout.addRow("Densidade:", self.lbl_net_density)
        self.lbl_net_degree = QLabel("-")
        metrics_form_layout.addRow("Grau Médio:", self.lbl_net_degree)
        self.lbl_net_most_conn = QLabel("-")
        self.lbl_net_most_conn.setWordWrap(True)
        metrics_form_layout.addRow("Mais Conectado:", self.lbl_net_most_conn)
        
        control_layout.addWidget(self.metrics_form)
        control_layout.addStretch()
        
        reports_layout.addWidget(control_panel, 1)
        
        # Painel da direita com abas de gráficos e tabelas
        self.results_tabs = QTabWidget()
        
        # Aba de matriz de cruzamento
        self.matrix_tab = QWidget()
        matrix_layout = QVBoxLayout(self.matrix_tab)
        self.matrix_table = QTableWidget()
        matrix_layout.addWidget(QLabel("Matriz de Cruzamento: Categorias Discursivas vs Espacialidades Discursivas"))
        matrix_layout.addWidget(self.matrix_table)
        self.results_tabs.addTab(self.matrix_tab, "Matriz de Cruzamento")
        
        # Aba de imagem do gráfico de categorias
        self.cat_chart_tab = QWidget()
        cat_chart_layout = QVBoxLayout(self.cat_chart_tab)
        self.cat_chart_lbl = QLabel("Clique em 'Atualizar Dados e Gráficos' para gerar o gráfico.")
        self.cat_chart_lbl.setAlignment(Qt.AlignCenter)
        self.cat_chart_lbl.setStyleSheet("background-color: #11111b; border-radius: 6px;")
        cat_chart_layout.addWidget(self.cat_chart_lbl)
        self.results_tabs.addTab(self.cat_chart_tab, "Gráfico Categorias")
        
        # Aba de imagem do gráfico de espacialidades
        self.esp_chart_tab = QWidget()
        esp_chart_layout = QVBoxLayout(self.esp_chart_tab)
        self.esp_chart_lbl = QLabel("Clique em 'Atualizar Dados e Gráficos' para gerar o gráfico.")
        self.esp_chart_lbl.setAlignment(Qt.AlignCenter)
        self.esp_chart_lbl.setStyleSheet("background-color: #11111b; border-radius: 6px;")
        esp_chart_layout.addWidget(self.esp_chart_lbl)
        self.results_tabs.addTab(self.esp_chart_tab, "Gráfico Espacialidades")
        
        # Aba de heatmap
        self.heatmap_tab = QWidget()
        heatmap_layout = QVBoxLayout(self.heatmap_tab)
        self.heatmap_lbl = QLabel("Clique em 'Atualizar Dados e Gráficos' para ver a matriz gráfica.")
        self.heatmap_lbl.setAlignment(Qt.AlignCenter)
        self.heatmap_lbl.setStyleSheet("background-color: #11111b; border-radius: 6px;")
        heatmap_layout.addWidget(self.heatmap_lbl)
        self.results_tabs.addTab(self.heatmap_tab, "Heatmap Cruzamento")
        
        reports_layout.addWidget(self.results_tabs, 3)

    def update_project_ui_state(self):
        """Habilita ou desabilita botões/menus dependendo se um projeto está aberto."""
        is_open = self.active_project is not None
        
        self.close_proj_action.setEnabled(is_open)
        self.manage_menu.setEnabled(is_open)
        self.analysis_menu.setEnabled(is_open)
        
        self.import_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        
        self.central_tab_widget.setTabEnabled(1, is_open) # Aba de relatórios
        
        if is_open:
            self.setWindowTitle(f"GeoDiscurso - {self.active_project.nome} [{self.project_root}]")
        else:
            self.setWindowTitle("GeoDiscurso - Sem Projeto Aberto")
            self.interview_list.clear()
            self.text_reader.clear()
            self.evocation_list.clear()
            self.interview_title_label.setText("Abra ou crie um projeto para começar")

    def new_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.project_root = dialog.project_path
            self.load_project_data()

    def open_project_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Projeto GeoDiscurso", "", "Projeto GeoDiscurso (projeto.geoconteudo)"
        )
        if file_path:
            self.project_root = os.path.dirname(file_path)
            try:
                db = DatabaseManager.get_instance()
                db.initialize_db(file_path)
                self.load_project_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro ao abrir projeto", f"Não foi possível abrir o projeto:\n{str(e)}")

    def load_project_data(self):
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        # Carrega o primeiro projeto (deve haver apenas um por arquivo)
        proj = session.query(Projeto).first()
        if not proj:
            QMessageBox.warning(self, "Aviso", "O arquivo do projeto parece estar vazio ou corrompido.")
            return
            
        self.active_project = proj
        self.update_project_ui_state()
        self.refresh_interview_list()

    def close_project(self):
        self.active_project = None
        self.project_root = None
        self.selected_interview = None
        
        db = DatabaseManager.get_instance()
        db.close()
        
        self.update_project_ui_state()

    def refresh_interview_list(self):
        self.interview_list.clear()
        
        if not self.active_project:
            return
            
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        entrevistas = session.query(Entrevista).order_by(Entrevista.titulo).all()
        for ent in entrevistas:
            item = QListWidgetItem(ent.titulo)
            item.setData(Qt.UserRole, ent.id)
            self.interview_list.addItem(item)

    def import_interview(self):
        if not self.project_root:
            QMessageBox.warning(self, "Aviso", "Por favor, crie um novo projeto ou abra um projeto existente antes de importar entrevistas.")
            return
            
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Importar Entrevistas", "", "Documentos Suportados (*.txt *.docx)"
        )
        
        if not file_paths:
            return
            
        # Pergunta se quer vincular a um sujeito agora
        db = DatabaseManager.get_instance()
        session = db.get_session()
        subjects = session.query(Sujeito).all()
        
        sujeito_id = None
        if subjects:
            # Pop-up simples ou permite vincular depois. 
            # Para manter simples no MVP, permitiremos vincular ao codificar trechos.
            pass
            
        imported_count = 0
        errors = []
        for path in file_paths:
            try:
                ImportService.import_interview(path, self.project_root, sujeito_id)
                imported_count += 1
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {str(e)}")
                
        if imported_count > 0:
            self.refresh_interview_list()
            
        if errors:
            QMessageBox.warning(self, "Importação Concluída com Alertas", 
                                f"Importados: {imported_count} arquivo(s).\n\nErros:\n" + "\n".join(errors))
        else:
            QMessageBox.information(self, "Sucesso", f"Sucesso! {imported_count} entrevista(s) importada(s).")

    def on_interview_selected(self, current, previous):
        if not current:
            self.selected_interview = None
            self.text_reader.clear()
            self.interview_title_label.setText("Selecione uma entrevista")
            self.evocation_list.clear()
            return
            
        ent_id = current.data(Qt.UserRole)
        
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        entrevista = session.query(Entrevista).filter(Entrevista.id == ent_id).first()
        if entrevista:
            self.selected_interview = entrevista
            self.interview_title_label.setText(entrevista.titulo)
            
            # Carrega o texto
            self.text_reader.setPlainText(entrevista.texto_extraido)
            
            # Limpa qualquer destaque
            self.text_reader.setExtraSelections([])
            
            # Atualiza lista de evocações
            self.refresh_evocations_list()

    def refresh_evocations_list(self):
        self.evocation_list.clear()
        
        if not self.selected_interview:
            return
            
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        # Sincroniza a sessão e limpa cache para ler dados novos do banco
        session.commit()
        
        evocacoes = session.query(Evocacao).filter(
            Evocacao.entrevista_id == self.selected_interview.id
        ).order_by(Evocacao.posicao_inicial).all()
        
        print(f"[DEBUG] Evocações para entrevista {self.selected_interview.id}: {len(evocacoes)}")
        
        for ev in evocacoes:
            # Item da lista
            cat_name = ev.categoria.nome if ev.categoria else "Sem Categoria"
            esp_name = ev.espacialidade.nome if ev.espacialidade else "Sem Espacialidade"
            
            label = f"[{cat_name} | {esp_name}]\n\"{ev.trecho_literal[:45]}...\""
            
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, ev.id)
            self.evocation_list.addItem(item)

    def analyze_selected_text(self):
        if not self.project_root:
            QMessageBox.warning(self, "Aviso", "Por favor, crie um novo projeto ou abra um projeto existente antes de analisar trechos.")
            return
        if not self.selected_interview:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione uma entrevista primeiro.")
            return
            
        cursor = self.text_reader.textCursor()
        selected_text = cursor.selectedText().strip()
        
        # Corrige caractere de quebra de parágrafo do Qt se houver
        selected_text = selected_text.replace('\u2029', '\n')
        
        if not selected_text:
            QMessageBox.warning(self, "Aviso", "Selecione um trecho de texto da entrevista para analisar.")
            return
            
        pos_start = cursor.selectionStart()
        pos_end = cursor.selectionEnd()
        
        dialog = CodingDialog(
            entrevista_id=self.selected_interview.id,
            trecho_literal=selected_text,
            posicao_inicial=pos_start,
            posicao_final=pos_end,
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            self.refresh_evocations_list()
            # Destaca a nova evocação criada
            self.highlight_text(pos_start, pos_end)

    def on_evocation_clicked(self, item):
        if not item:
            return
            
        evocacao_id = item.data(Qt.UserRole)
        
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        ev = session.query(Evocacao).filter(Evocacao.id == evocacao_id).first()
        if ev:
            # Destaca e foca no trecho
            self.highlight_text(ev.posicao_inicial, ev.posicao_final)

    def highlight_text(self, start, end):
        # Limpa seleções extras
        self.text_reader.setExtraSelections([])
        
        # Cria cursor para selecionar a faixa de texto
        cursor = self.text_reader.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        
        # Posiciona a visualização (scroll) no trecho
        self.text_reader.setTextCursor(cursor)
        self.text_reader.ensureCursorVisible()
        
        # Define seleção extra com cor amarela brilhante para destacar
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor(Styles.HIGHLIGHT_BG))
        selection.format.setForeground(QColor(Styles.HIGHLIGHT_FG))
        selection.cursor = cursor
        
        self.text_reader.setExtraSelections([selection])

    def show_evocation_context_menu(self, position):
        item = self.evocation_list.itemAt(position)
        if not item:
            return
            
        evocacao_id = item.data(Qt.UserRole)
        
        menu = QMenu()
        edit_action = menu.addAction("Editar Evocação...")
        delete_action = menu.addAction("Excluir Evocação")
        
        action = menu.exec(self.evocation_list.viewport().mapToGlobal(position))
        
        if action == edit_action:
            self.edit_evocation(evocacao_id)
        elif action == delete_action:
            self.delete_evocation(evocacao_id)

    def edit_evocation(self, evocacao_id):
        db = DatabaseManager.get_instance()
        session = db.get_session()
        ev = session.query(Evocacao).filter(Evocacao.id == evocacao_id).first()
        
        if ev:
            dialog = CodingDialog(
                entrevista_id=ev.entrevista_id,
                trecho_literal=ev.trecho_literal,
                posicao_inicial=ev.posicao_inicial,
                posicao_final=ev.posicao_final,
                evocacao=ev,
                parent=self
            )
            if dialog.exec() == QDialog.Accepted:
                self.refresh_evocations_list()
                self.highlight_text(ev.posicao_inicial, ev.posicao_final)

    def delete_evocation(self, evocacao_id):
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            "Tem certeza que deseja excluir esta evocação?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            db = DatabaseManager.get_instance()
            session = db.get_session()
            ev = session.query(Evocacao).filter(Evocacao.id == evocacao_id).first()
            if ev:
                session.delete(ev)
                session.commit()
                self.refresh_evocations_list()
                self.text_reader.setExtraSelections([]) # Limpa seleções

    def manage_subjects(self):
        dialog = SubjectManagerDialog(self)
        dialog.exec()

    # --- Métodos de Exportação e Relatórios ---
    
    def export_evocations_csv(self):
        if not self.project_root:
            return
            
        dest_dir = os.path.join(self.project_root, "exportacoes")
        dest_file = os.path.join(dest_dir, "todas_as_evocacoes.csv")
        
        # Permite ao usuário alterar o nome do arquivo se desejar
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exportar Evocações para CSV", dest_file, "Arquivos CSV (*.csv)"
        )
        
        if filepath:
            try:
                ExportService.export_evocations_to_csv(filepath)
                QMessageBox.information(self, "Sucesso", f"Evocações exportadas com sucesso para:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Erro na Exportação", f"Erro ao exportar arquivo: {str(e)}")

    def export_gephi_network(self):
        if not self.project_root:
            return
            
        dialog = GephiExportDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
            
        field_a, field_b = dialog.get_selected_fields()
        
        if field_a == field_b:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione campos diferentes para os Nós A e B para formar a rede.")
            return
            
        dest_dir = os.path.join(self.project_root, "exportacoes")
        nodes_default = os.path.join(dest_dir, f"gephi_nodes_{field_a}_vs_{field_b}.csv")
        edges_default = os.path.join(dest_dir, f"gephi_edges_{field_a}_vs_{field_b}.csv")
        
        try:
            ExportService.export_gephi_network(nodes_default, edges_default, field_a, field_b)
            QMessageBox.information(
                self, "Sucesso", 
                f"Rede ({field_a} vs {field_b}) exportada com sucesso!\n\nNós: {os.path.basename(nodes_default)}\nArestas: {os.path.basename(edges_default)}\n\nNa pasta: {dest_dir}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro na Exportação de Rede", f"Erro ao exportar rede: {str(e)}")

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def open_exportations_dir(self):
        if self.project_root:
            dest_dir = os.path.join(self.project_root, "exportacoes")
            import webbrowser
            webbrowser.open(f"file://{dest_dir}")

    def generate_project_reports(self):
        if not self.project_root:
            return
            
        try:
            # Caminhos dos gráficos a serem salvos na pasta 'graficos/' do projeto
            graphics_dir = os.path.join(self.project_root, "graficos")
            cat_chart_path = os.path.join(graphics_dir, "frequencia_categorias.png")
            esp_chart_path = os.path.join(graphics_dir, "frequencia_espacialidades.png")
            heatmap_path = os.path.join(graphics_dir, "heatmap_cruzamento.png")
            
            # 1. Gera imagens via Matplotlib
            ChartService.generate_category_frequency_chart(cat_chart_path, is_dark=True)
            ChartService.generate_spatiality_frequency_chart(esp_chart_path, is_dark=True)
            ChartService.generate_crossover_matrix_heatmap(heatmap_path, is_dark=True)
            
            # 2. Carrega as imagens geradas na interface
            from PySide6.QtGui import QPixmap
            
            self.cat_chart_lbl.setPixmap(QPixmap(cat_chart_path).scaled(
                600, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            self.esp_chart_lbl.setPixmap(QPixmap(esp_chart_path).scaled(
                600, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            self.heatmap_lbl.setPixmap(QPixmap(heatmap_path).scaled(
                600, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            
            # 3. Carrega matriz de cruzamento textual na tabela
            matrix = ChartService.get_crossover_matrix()
            self.load_matrix_table(matrix)
            
            # 4. Carrega métricas da rede via NetworkX
            metrics = NetworkService.get_network_metrics()
            self.lbl_net_nodes.setText(str(metrics["nodes_count"]))
            self.lbl_net_edges.setText(str(metrics["edges_count"]))
            self.lbl_net_density.setText(f"{metrics['density']:.4f}")
            self.lbl_net_degree.setText(f"{metrics['avg_degree']:.2f}")
            self.lbl_net_most_conn.setText(metrics["most_connected"])
            
            QMessageBox.information(
                self, "Sucesso", 
                "Relatórios, gráficos e matriz gerados e atualizados com sucesso!\nSalvos em: " + graphics_dir
            )
            
            # Muda para a aba de relatórios
            self.central_tab_widget.setCurrentIndex(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro ao gerar relatórios", f"Erro no processamento dos gráficos e matriz:\n{str(e)}")

    def load_matrix_table(self, df):
        self.matrix_table.clear()
        self.matrix_table.setRowCount(0)
        self.matrix_table.setColumnCount(0)
        
        if df.empty:
            self.matrix_table.setColumnCount(1)
            self.matrix_table.setRowCount(1)
            self.matrix_table.setItem(0, 0, QTableWidgetItem("Nenhum dado disponível ainda."))
            return
            
        self.matrix_table.setColumnCount(len(df.columns))
        self.matrix_table.setRowCount(len(df.index))
        
        self.matrix_table.setHorizontalHeaderLabels(df.columns)
        self.matrix_table.setVerticalHeaderLabels(df.index)
        
        for i, row in enumerate(df.index):
            for j, col in enumerate(df.columns):
                val = df.loc[row, col]
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                # Pinta células com valor > 0 de lilás suave para destaque
                if val > 0:
                    item.setBackground(QColor("rgba(203, 166, 247, 0.25)"))
                self.matrix_table.setItem(i, j, item)
                
        self.matrix_table.resizeColumnsToContents()
        self.matrix_table.resizeRowsToContents()
