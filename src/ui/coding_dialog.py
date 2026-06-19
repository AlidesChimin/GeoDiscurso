from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QLineEdit, QPushButton, QComboBox, QMessageBox, QCompleter
)
from PySide6.QtCore import Qt
from src.database import DatabaseManager
from src.models import (
    Evocacao, CategoriaDiscursiva, EspacialidadeDiscursiva, Sujeito
)
from src.ui.components import AutocompleteLineEdit
from src.ui.subject_dialog import SubjectEditDialog

class CodingDialog(QDialog):
    def __init__(self, entrevista_id, trecho_literal, posicao_inicial, posicao_final, evocacao=None, parent=None):
        super().__init__(parent)
        self.entrevista_id = entrevista_id
        self.trecho_literal = trecho_literal
        self.posicao_inicial = posicao_inicial
        self.posicao_final = posicao_final
        self.evocacao = evocacao # Se fornecido, modo de edição
        
        self.db = DatabaseManager.get_instance()
        self.session = self.db.get_session()
        
        # Modo de edição
        if self.evocacao:
            self.setWindowTitle("Editar Evocação")
        else:
            self.setWindowTitle("Nova Evocação - Codificar Trecho")
            
        self.resize(600, 550)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Codificação Discursiva")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # Trecho Literal (Read-Only)
        layout.addWidget(QLabel("Trecho Literal Selecionado:"))
        self.text_preview = QTextEdit()
        self.text_preview.setPlainText(self.trecho_literal)
        self.text_preview.setReadOnly(True)
        self.text_preview.setMaximumHeight(80)
        self.text_preview.setStyleSheet("background-color: #2b2b36; font-style: italic;")
        layout.addWidget(self.text_preview)
        
        # Sujeito Entrevistado
        layout.addWidget(QLabel("Sujeito Entrevistado:"))
        suj_layout = QHBoxLayout()
        self.sujeito_combo = QComboBox()
        self.add_sujeito_btn = QPushButton("+ Novo")
        self.add_sujeito_btn.setFixedWidth(70)
        self.add_sujeito_btn.clicked.connect(self.quick_add_subject)
        suj_layout.addWidget(self.sujeito_combo)
        suj_layout.addWidget(self.add_sujeito_btn)
        layout.addLayout(suj_layout)
        
        # Buscar itens para Autocompletar
        existing_cats = [c.nome for c in self.session.query(CategoriaDiscursiva).order_by(CategoriaDiscursiva.nome).all()]
        existing_esps = [e.nome for e in self.session.query(EspacialidadeDiscursiva).order_by(EspacialidadeDiscursiva.nome).all()]
        
        # Elementos existentes (extrai termos separados por vírgula no banco)
        evocs = self.session.query(Evocacao.elementos).filter(Evocacao.elementos.isnot(None)).all()
        elements_set = set()
        for ev in evocs:
            if ev[0]:
                parts = [p.strip() for p in ev[0].split(',') if p.strip()]
                elements_set.update(parts)
        existing_elements = sorted(list(elements_set))
        
        # Sujeitos da relação existentes no banco
        suj_rels = self.session.query(Evocacao.sujeito_relacao).filter(Evocacao.sujeito_relacao.isnot(None)).distinct().all()
        existing_suj_rels = sorted([sr[0] for sr in suj_rels if sr[0]])
        
        # Categoria Discursiva
        layout.addWidget(QLabel("Categoria Discursiva *"))
        self.cat_input = AutocompleteLineEdit(existing_cats)
        self.cat_input.setPlaceholderText("Comece a digitar a categoria... (será criada se não existir)")
        layout.addWidget(self.cat_input)
        
        # Espacialidade Discursiva
        layout.addWidget(QLabel("Espacialidade Discursiva *"))
        self.esp_input = AutocompleteLineEdit(existing_esps)
        self.esp_input.setPlaceholderText("Comece a digitar a espacialidade... (será criada se não existir)")
        layout.addWidget(self.esp_input)
        
        # Elementos
        layout.addWidget(QLabel("Elementos"))
        self.elements_input = AutocompleteLineEdit(existing_elements)
        self.elements_input.setPlaceholderText("Elementos presentes na relação espacial (Ex: praça, avenida, rio)...")
        layout.addWidget(self.elements_input)
        
        # Sujeito da Relação
        layout.addWidget(QLabel("Sujeito da Relação"))
        self.suj_rel_input = AutocompleteLineEdit(existing_suj_rels)
        self.suj_rel_input.setPlaceholderText("Quem é o outro na relação evocada? (Ex: policial, vizinho, comerciante)...")
        layout.addWidget(self.suj_rel_input)
        
        # Observações Analíticas
        layout.addWidget(QLabel("Observações Analíticas"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notas teóricas, reflexões, conexões com conceitos geográficos...")
        self.notes_input.setMaximumHeight(80)
        layout.addWidget(self.notes_input)
        
        layout.addSpacing(15)
        
        # Botões de Ação
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Salvar Evocação")
        self.save_btn.setObjectName("successBtn")
        self.save_btn.clicked.connect(self.save_evocation)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def load_data(self):
        # Carrega sujeitos no ComboBox
        self.refresh_subjects()
        
        if self.evocacao:
            # Modo edição: preenche os campos
            # Encontra o index do sujeito
            if self.evocacao.sujeito_id:
                for i in range(self.sujeito_combo.count()):
                    if self.sujeito_combo.itemData(i) == self.evocacao.sujeito_id:
                        self.sujeito_combo.setCurrentIndex(i)
                        break
            
            self.cat_input.setText(self.evocacao.categoria.nome if self.evocacao.categoria else "")
            self.esp_input.setText(self.evocacao.espacialidade.nome if self.evocacao.espacialidade else "")
            self.elements_input.setText(self.evocacao.elementos or "")
            self.suj_rel_input.setText(self.evocacao.sujeito_relacao or "")
            self.notes_input.setPlainText(self.evocacao.observacoes_analiticas or "")

    def refresh_subjects(self):
        self.sujeito_combo.clear()
        self.sujeito_combo.addItem("Sem Sujeito Vinculado", None)
        
        subjects = self.session.query(Sujeito).order_by(Sujeito.codigo_pseudonimo).all()
        for s in subjects:
            label = s.codigo_pseudonimo
            if s.nome_opcional:
                label += f" ({s.nome_opcional})"
            self.sujeito_combo.addItem(label, s.id)
            
        # Torna o combobox editável e pesquisável
        self.sujeito_combo.setEditable(True)
        self.sujeito_combo.setInsertPolicy(QComboBox.NoInsert)
        if self.sujeito_combo.completer():
            self.sujeito_combo.completer().setFilterMode(Qt.MatchContains)
            self.sujeito_combo.completer().setCompletionMode(QCompleter.PopupCompletion)

    def quick_add_subject(self):
        dialog = SubjectEditDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_subjects()
            # Seleciona o recém-criado sujeito (que será o último ou com ID mais alto, ou podemos buscar por pseudônimo)
            # Vamos simplesmente selecionar o último adicionado
            if self.sujeito_combo.count() > 1:
                self.sujeito_combo.setCurrentIndex(self.sujeito_combo.count() - 1)

    def save_evocation(self):
        cat_name = self.cat_input.get_value()
        esp_name = self.esp_input.get_value()
        
        if not cat_name:
            QMessageBox.warning(self, "Aviso", "O campo Categoria Discursiva é obrigatório.")
            return
        if not esp_name:
            QMessageBox.warning(self, "Aviso", "O campo Espacialidade Discursiva é obrigatório.")
            return
            
        # Obter sujeito selecionado
        sujeito_id = self.sujeito_combo.currentData()
        
        # 1. Resolver Categoria Discursiva (busca case-insensitive)
        categoria = self.session.query(CategoriaDiscursiva).filter(
            CategoriaDiscursiva.nome.collate('NOCASE') == cat_name
        ).first()
        
        if not categoria:
            categoria = CategoriaDiscursiva(nome=cat_name, descricao="Criada automaticamente durante codificação.")
            self.session.add(categoria)
            self.session.flush() # flush para obter ID
            
        # 2. Resolver Espacialidade Discursiva (busca case-insensitive)
        espacialidade = self.session.query(EspacialidadeDiscursiva).filter(
            EspacialidadeDiscursiva.nome.collate('NOCASE') == esp_name
        ).first()
        
        if not espacialidade:
            espacialidade = EspacialidadeDiscursiva(nome=esp_name, descricao="Criada automaticamente durante codificação.")
            self.session.add(espacialidade)
            self.session.flush()
            
        # 3. Salvar Evocação
        if self.evocacao:
            # Editando existente
            ev = self.session.query(Evocacao).filter(Evocacao.id == self.evocacao.id).first()
            # Atualiza campos
            ev.categoria_id = categoria.id
            ev.espacialidade_id = espacialidade.id
            ev.sujeito_id = sujeito_id
            ev.elementos = self.elements_input.text().strip() or None
            ev.sujeito_relacao = self.suj_rel_input.text().strip() or None
            ev.observacoes_analiticas = self.notes_input.toPlainText().strip() or None
        else:
            # Nova evocação
            ev = Evocacao(
                entrevista_id=self.entrevista_id,
                sujeito_id=sujeito_id,
                categoria_id=categoria.id,
                espacialidade_id=espacialidade.id,
                trecho_literal=self.trecho_literal,
                posicao_inicial=self.posicao_inicial,
                posicao_final=self.posicao_final,
                elementos=self.elements_input.text().strip() or None,
                sujeito_relacao=self.suj_rel_input.text().strip() or None,
                observacoes_analiticas=self.notes_input.toPlainText().strip() or None
            )
            self.session.add(ev)
            
        try:
            self.session.commit()
            self.accept()
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar a evocação: {str(e)}")
