from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QTabWidget, QWidget, QFormLayout
)
from PySide6.QtCore import Qt
from src.database import DatabaseManager
from src.models import Sujeito

class SubjectEditDialog(QDialog):
    def __init__(self, sujeito=None, parent=None):
        super().__init__(parent)
        self.sujeito = sujeito
        self.setWindowTitle("Cadastrar/Editar Sujeito Entrevistado")
        self.resize(600, 500)
        self.init_ui()
        if self.sujeito:
            self.load_subject_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        self.title_label = QLabel("Ficha do Sujeito Entrevistado")
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label)
        
        # Abas para organizar muitos campos
        self.tabs = QTabWidget()
        
        # Aba 1: Perfil Sociodemográfico
        tab1 = QWidget()
        layout_tab1 = QFormLayout(tab1)
        
        self.cod_input = QLineEdit()
        self.cod_input.setPlaceholderText("Ex: SUJ_001 ou Pseudônimo")
        layout_tab1.addRow("Código / Pseudônimo *", self.cod_input)
        
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Opcional")
        layout_tab1.addRow("Nome Completo", self.nome_input)
        
        self.idade_spin = QSpinBox()
        self.idade_spin.setRange(0, 150)
        self.idade_spin.setValue(0)
        layout_tab1.addRow("Idade", self.idade_spin)
        
        self.genero_input = QLineEdit()
        self.genero_input.setPlaceholderText("Ex: Masculino, Feminino, Não-binário")
        layout_tab1.addRow("Gênero", self.genero_input)
        
        self.sexualidade_input = QLineEdit()
        self.sexualidade_input.setPlaceholderText("Ex: Heterossexual, Homossexual")
        layout_tab1.addRow("Sexualidade", self.sexualidade_input)
        
        self.raca_input = QLineEdit()
        self.raca_input.setPlaceholderText("Ex: Branca, Parda, Preta, Indígena")
        layout_tab1.addRow("Raça / Cor", self.raca_input)
        
        self.escolaridade_input = QLineEdit()
        self.escolaridade_input.setPlaceholderText("Ex: Ensino Médio Completo, Superior")
        layout_tab1.addRow("Escolaridade", self.escolaridade_input)
        
        self.renda_input = QLineEdit()
        self.renda_input.setPlaceholderText("Ex: 2 salários mínimos, R$ 3.000")
        layout_tab1.addRow("Renda Mensal", self.renda_input)
        
        self.filhos_spin = QSpinBox()
        self.filhos_spin.setRange(0, 20)
        self.filhos_spin.setValue(0)
        layout_tab1.addRow("Número de Filhos", self.filhos_spin)
        
        self.tabs.addTab(tab1, "Perfil Geral")
        
        # Aba 2: Localização / Espacialidade
        tab2 = QWidget()
        layout_tab2 = QFormLayout(tab2)
        
        self.municipio_input = QLineEdit()
        layout_tab2.addRow("Município", self.municipio_input)
        
        self.bairro_input = QLineEdit()
        layout_tab2.addRow("Bairro", self.bairro_input)
        
        self.vila_input = QLineEdit()
        layout_tab2.addRow("Vila / Comunidade", self.vila_input)
        
        self.rua_input = QLineEdit()
        layout_tab2.addRow("Rua", self.rua_input)
        
        self.num_input = QLineEdit()
        layout_tab2.addRow("Número", self.num_input)
        
        self.tabs.addTab(tab2, "Geografia / Local")
        
        # Aba 3: Dados Relativos ao Ocorrido / Autor / Vítima
        tab3 = QWidget()
        layout_tab3 = QFormLayout(tab3)
        
        self.autor_input = QLineEdit()
        layout_tab3.addRow("Autor (Pseudônimo/Código)", self.autor_input)
        
        self.idade_autor_spin = QSpinBox()
        self.idade_autor_spin.setRange(0, 150)
        self.idade_autor_spin.setValue(0)
        layout_tab3.addRow("Idade do Autor", self.idade_autor_spin)
        
        self.sexo_autor_input = QLineEdit()
        layout_tab3.addRow("Sexo do Autor", self.sexo_autor_input)
        
        self.bairro_autor_input = QLineEdit()
        layout_tab3.addRow("Bairro do Autor", self.bairro_autor_input)
        
        self.escolaridade_autor_input = QLineEdit()
        layout_tab3.addRow("Escolaridade do Autor", self.escolaridade_autor_input)
        
        self.reincidencia_autor_input = QLineEdit()
        layout_tab3.addRow("Reincidência do Autor", self.reincidencia_autor_input)
        
        self.reincidencia_vitima_input = QLineEdit()
        layout_tab3.addRow("Reincidência da Vítima", self.reincidencia_vitima_input)
        
        self.registro_input = QLineEdit()
        self.registro_input.setPlaceholderText("Ex: BO número...")
        layout_tab3.addRow("Registro/Protocolo", self.registro_input)
        
        self.ano_spin = QSpinBox()
        self.ano_spin.setRange(1900, 2100)
        self.ano_spin.setValue(2026)
        layout_tab3.addRow("Ano", self.ano_spin)
        
        self.tabs.addTab(tab3, "Contexto / Autor")
        
        layout.addWidget(self.tabs)
        
        # Botões
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Salvar")
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.clicked.connect(self.save_data)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def load_subject_data(self):
        s = self.sujeito
        self.cod_input.setText(s.codigo_pseudonimo)
        self.nome_input.setText(s.nome_opcional or "")
        self.idade_spin.setValue(s.idade or 0)
        self.genero_input.setText(s.genero or "")
        self.sexualidade_input.setText(s.sexualidade or "")
        self.raca_input.setText(s.raca_cor or "")
        self.escolaridade_input.setText(s.escolaridade or "")
        self.renda_input.setText(s.renda or "")
        self.filhos_spin.setValue(s.filhos or 0)
        
        self.municipio_input.setText(s.municipio or "")
        self.bairro_input.setText(s.bairro or "")
        self.vila_input.setText(s.vila or "")
        self.rua_input.setText(s.rua or "")
        self.num_input.setText(s.numero or "")
        
        self.autor_input.setText(s.autor or "")
        self.idade_autor_spin.setValue(s.idade_autor or 0)
        self.sexo_autor_input.setText(s.sexo_autor or "")
        self.bairro_autor_input.setText(s.bairro_autor or "")
        self.escolaridade_autor_input.setText(s.escolaridade_autor or "")
        self.reincidencia_autor_input.setText(s.reincidencia_autor or "")
        self.reincidencia_vitima_input.setText(s.reincidencia_vitima or "")
        self.registro_input.setText(s.registro or "")
        self.ano_spin.setValue(s.ano or 2026)

    def save_data(self):
        cod = self.cod_input.text().strip()
        if not cod:
            QMessageBox.warning(self, "Aviso", "O campo Código/Pseudônimo é obrigatório.")
            return
            
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        # Se for um novo sujeito, verifica colisão de pseudônimo
        if not self.sujeito:
            exist = session.query(Sujeito).filter(Sujeito.codigo_pseudonimo == cod).first()
            if exist:
                QMessageBox.warning(self, "Aviso", f"Já existe um sujeito cadastrado com o código '{cod}'.")
                return
            s = Sujeito()
        else:
            # Editando existente
            s = session.query(Sujeito).filter(Sujeito.id == self.sujeito.id).first()
            if s.codigo_pseudonimo != cod:
                exist = session.query(Sujeito).filter(Sujeito.codigo_pseudonimo == cod).first()
                if exist:
                    QMessageBox.warning(self, "Aviso", f"Já existe outro sujeito cadastrado com o código '{cod}'.")
                    return
        
        s.codigo_pseudonimo = cod
        s.nome_opcional = self.nome_input.text().strip() or None
        s.idade = self.idade_spin.value() if self.idade_spin.value() > 0 else None
        s.genero = self.genero_input.text().strip() or None
        s.sexualidade = self.sexualidade_input.text().strip() or None
        s.raca_cor = self.raca_input.text().strip() or None
        s.escolaridade = self.escolaridade_input.text().strip() or None
        s.renda = self.renda_input.text().strip() or None
        s.filhos = self.filhos_spin.value()
        
        s.municipio = self.municipio_input.text().strip() or None
        s.bairro = self.bairro_input.text().strip() or None
        s.vila = self.vila_input.text().strip() or None
        s.rua = self.rua_input.text().strip() or None
        s.numero = self.num_input.text().strip() or None
        
        s.autor = self.autor_input.text().strip() or None
        s.idade_autor = self.idade_autor_spin.value() if self.idade_autor_spin.value() > 0 else None
        s.sexo_autor = self.sexo_autor_input.text().strip() or None
        s.bairro_autor = self.bairro_autor_input.text().strip() or None
        s.escolaridade_autor = self.escolaridade_autor_input.text().strip() or None
        s.reincidencia_autor = self.reincidencia_autor_input.text().strip() or None
        s.reincidencia_vitima = self.reincidencia_vitima_input.text().strip() or None
        s.registro = self.registro_input.text().strip() or None
        s.ano = self.ano_spin.value()
        
        if not self.sujeito:
            session.add(s)
            
        try:
            session.commit()
            QMessageBox.information(self, "Sucesso", "Sujeito de pesquisa salvo com sucesso!")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar o sujeito: {str(e)}")

class SubjectManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciar Sujeitos Entrevistados")
        self.resize(800, 500)
        self.init_ui()
        self.load_subjects()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Sujeitos de Pesquisa Cadastrados")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Código/Pseudônimo", "Gênero", "Idade", "Município", "Bairro"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        # Ações
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Adicionar...")
        self.add_btn.setObjectName("primaryBtn")
        self.add_btn.clicked.connect(self.add_subject)
        
        self.edit_btn = QPushButton("Editar Selecionado...")
        self.edit_btn.setObjectName("secondaryBtn")
        self.edit_btn.clicked.connect(self.edit_subject)
        
        self.del_btn = QPushButton("Excluir...")
        self.del_btn.setObjectName("dangerBtn")
        self.del_btn.clicked.connect(self.delete_subject)
        
        self.close_btn = QPushButton("Fechar")
        self.close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

    def load_subjects(self):
        self.table.setRowCount(0)
        db = DatabaseManager.get_instance()
        session = db.get_session()
        
        subjects = session.query(Sujeito).order_by(Sujeito.codigo_pseudonimo).all()
        
        for i, s in enumerate(subjects):
            self.table.insertRow(i)
            # Armazena o objeto sujeito no primeiro item da linha para facilidade
            id_item = QTableWidgetItem(str(s.id))
            id_item.setData(Qt.UserRole, s.id) # Guarda ID
            self.table.setItem(i, 0, id_item)
            self.table.setItem(i, 1, QTableWidgetItem(s.codigo_pseudonimo or ""))
            self.table.setItem(i, 2, QTableWidgetItem(s.genero or ""))
            self.table.setItem(i, 3, QTableWidgetItem(str(s.idade) if s.idade else ""))
            self.table.setItem(i, 4, QTableWidgetItem(s.municipio or ""))
            self.table.setItem(i, 5, QTableWidgetItem(s.bairro or ""))

    def add_subject(self):
        dialog = SubjectEditDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_subjects()

    def edit_subject(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um sujeito na tabela para editar.")
            return
            
        sujeito_id = self.table.item(selected, 0).data(Qt.UserRole)
        db = DatabaseManager.get_instance()
        session = db.get_session()
        sujeito = session.query(Sujeito).filter(Sujeito.id == sujeito_id).first()
        
        if sujeito:
            dialog = SubjectEditDialog(sujeito=sujeito, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.load_subjects()

    def delete_subject(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um sujeito na tabela para excluir.")
            return
            
        sujeito_id = self.table.item(selected, 0).data(Qt.UserRole)
        sujeito_cod = self.table.item(selected, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o sujeito '{sujeito_cod}'?\nIsso removerá ou desvinculará suas entrevistas e evocações associadas.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            db = DatabaseManager.get_instance()
            session = db.get_session()
            sujeito = session.query(Sujeito).filter(Sujeito.id == sujeto_id).first()
            if sujeito:
                session.delete(sujeito)
                session.commit()
                self.load_subjects()
                QMessageBox.information(self, "Sucesso", "Sujeito excluído com sucesso.")
