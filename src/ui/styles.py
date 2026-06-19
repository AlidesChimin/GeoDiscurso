class Styles:
    # Cores do Tema Premium (Dark Mode)
    BG_MAIN = "#1e1e2e"          # Azul-escuro profundo (Base)
    BG_PANEL = "#181825"         # Tom um pouco mais escuro para painéis (Mantle)
    BG_CARD = "#11111b"          # Mais escuro ainda para cartões ou lista lateral (Crust)
    BG_INPUT = "#313244"         # Cor de fundo para inputs e campos de texto
    
    TEXT_MAIN = "#cdd6f4"        # Texto padrão esbranquiçado
    TEXT_MUTED = "#a6adc8"       # Texto cinza claro para descrições
    TEXT_DARK = "#1e1e2e"        # Texto escuro para contrastar com botões coloridos
    
    PRIMARY = "#89b4fa"          # Azul brilhante
    PRIMARY_HOVER = "#b4befe"    # Azul celeste claro
    SECONDARY = "#cba6f7"        # Lilás/Roxo suave
    SECONDARY_HOVER = "#f5c2e7"  # Rosa suave
    
    SUCCESS = "#a6e3a1"          # Verde suave
    SUCCESS_HOVER = "#94e2d5"    # Verde menta
    
    DANGER = "#f38ba8"           # Vermelho
    DANGER_HOVER = "#eba0ac"     # Vermelho claro
    
    BORDER = "#45475a"           # Borda cinza suave
    BORDER_FOCUS = "#89b4fa"     # Borda em foco (Azul)
    
    SELECTION_BG = "rgba(137, 180, 250, 0.35)" # Destaque de seleção translúcida
    HIGHLIGHT_BG = "#f9e2af"     # Cor para destacar trechos de evocação (Amarelo pastel)
    HIGHLIGHT_FG = "#11111b"     # Texto escuro para o trecho destacado
    
    QSS = f"""
    QMainWindow {{
        background-color: {BG_MAIN};
        color: {TEXT_MAIN};
        font-family: 'Segoe UI', 'Roboto', 'Outfit', Helvetica, sans-serif;
    }}
    
    QDialog {{
        background-color: {BG_PANEL};
        color: {TEXT_MAIN};
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    
    QWidget {{
        color: {TEXT_MAIN};
        font-size: 13px;
    }}
    
    QLabel {{
        color: {TEXT_MAIN};
    }}
    
    QLabel#titleLabel {{
        font-size: 18px;
        font-weight: bold;
        color: {PRIMARY};
        margin-bottom: 5px;
    }}
    
    QLabel#subtitleLabel {{
        font-size: 12px;
        color: {TEXT_MUTED};
    }}
    
    /* Input Fields */
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {{
        background-color: {BG_INPUT};
        color: {TEXT_MAIN};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 8px;
        selection-background-color: {PRIMARY};
        selection-color: {TEXT_DARK};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {BORDER_FOCUS};
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {BG_PANEL};
        color: {TEXT_MAIN};
        border: 1px solid {BORDER};
        selection-background-color: {PRIMARY};
        selection-color: {TEXT_DARK};
    }}
    
    /* List View e Table View */
    QListWidget, QTableWidget, QTreeView {{
        background-color: {BG_CARD};
        color: {TEXT_MAIN};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 5px;
        outline: none;
    }}
    
    QListWidget::item {{
        padding: 10px;
        border-bottom: 1px solid rgba(69, 71, 90, 0.3);
        border-radius: 4px;
        margin-bottom: 2px;
    }}
    
    QListWidget::item:hover {{
        background-color: rgba(137, 180, 250, 0.1);
        color: {PRIMARY};
    }}
    
    QListWidget::item:selected {{
        background-color: {PRIMARY};
        color: {TEXT_DARK};
        font-weight: bold;
    }}
    
    /* Headers de tabelas */
    QHeaderView::section {{
        background-color: {BG_PANEL};
        color: {TEXT_MAIN};
        padding: 6px;
        border: 1px solid {BORDER};
        font-weight: bold;
    }}
    
    QTableWidget::item:selected {{
        background-color: {PRIMARY};
        color: {TEXT_DARK};
    }}
    
    /* Botões */
    QPushButton {{
        background-color: {BG_INPUT};
        color: {TEXT_MAIN};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
        min-height: 20px;
    }}
    
    QPushButton:hover {{
        background-color: {BORDER};
        border-color: {TEXT_MUTED};
    }}
    
    QPushButton:pressed {{
        background-color: {BG_CARD};
    }}
    
    QPushButton#primaryBtn {{
        background-color: {PRIMARY};
        color: {TEXT_DARK};
        border: none;
    }}
    
    QPushButton#primaryBtn:hover {{
        background-color: {PRIMARY_HOVER};
    }}
    
    QPushButton#secondaryBtn {{
        background-color: {SECONDARY};
        color: {TEXT_DARK};
        border: none;
    }}
    
    QPushButton#secondaryBtn:hover {{
        background-color: {SECONDARY_HOVER};
    }}
    
    QPushButton#successBtn {{
        background-color: {SUCCESS};
        color: {TEXT_DARK};
        border: none;
    }}
    
    QPushButton#successBtn:hover {{
        background-color: {SUCCESS_HOVER};
    }}
    
    QPushButton#dangerBtn {{
        background-color: {DANGER};
        color: {TEXT_MAIN};
        border: none;
    }}
    
    QPushButton#dangerBtn:hover {{
        background-color: {DANGER_HOVER};
    }}
    
    /* Scrollbars */
    QScrollBar:vertical {{
        border: none;
        background: {BG_PANEL};
        width: 10px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {BORDER};
        min-height: 20px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {PRIMARY};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        border: none;
        background: {BG_PANEL};
        height: 10px;
        margin: 0px;
    }}
    
    QScrollBar::handle:horizontal {{
        background: {BORDER};
        min-width: 20px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background: {PRIMARY};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        border: none;
        background: none;
        width: 0px;
    }}
    
    /* Splitter */
    QSplitter::handle {{
        background-color: {BORDER};
    }}
    
    QSplitter::handle:horizontal {{
        width: 4px;
    }}
    
    QSplitter::handle:vertical {{
        height: 4px;
    }}
    
    /* Tooltip */
    QToolTip {{
        background-color: {BG_PANEL};
        color: {TEXT_MAIN};
        border: 1px solid {PRIMARY};
        border-radius: 4px;
        padding: 5px;
    }}
    
    /* Tab Widget */
    QTabWidget::pane {{
        border: 1px solid {BORDER};
        border-radius: 6px;
        background-color: {BG_PANEL};
    }}
    
    QTabBar::tab {{
        background-color: {BG_CARD};
        color: {TEXT_MUTED};
        border: 1px solid {BORDER};
        border-bottom-color: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        padding: 8px 16px;
        margin-right: 2px;
    }}
    
    QTabBar::tab:hover {{
        background-color: {BG_INPUT};
        color: {TEXT_MAIN};
    }}
    
    QTabBar::tab:selected {{
        background-color: {BG_PANEL};
        color: {PRIMARY};
        border-bottom-color: {BG_PANEL};
        font-weight: bold;
    }}
    
    /* Group Box */
    QGroupBox {{
        border: 1px solid {BORDER};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 15px;
        font-weight: bold;
        color: {PRIMARY};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        padding: 0 5px;
        background-color: {BG_MAIN};
    }}
    
    /* Menu Bar */
    QMenuBar {{
        background-color: {BG_PANEL};
        color: {TEXT_MAIN};
        border-bottom: 1px solid {BORDER};
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 6px 10px;
        color: {TEXT_MAIN};
    }}
    
    QMenuBar::item:selected {{
        background-color: {BG_INPUT};
        color: {PRIMARY};
        border-radius: 4px;
    }}
    
    QMenu {{
        background-color: {BG_PANEL};
        color: {TEXT_MAIN};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 5px;
    }}
    
    QMenu::item {{
        padding: 6px 25px 6px 20px;
        border-radius: 4px;
        color: {TEXT_MAIN};
    }}
    
    QMenu::item:selected {{
        background-color: {PRIMARY};
        color: {TEXT_DARK};
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: {BORDER};
        margin: 5px 0px;
    }}
    
    /* Disabled State */
    QPushButton:disabled {{
        background-color: #1a1a24;
        color: #585b70;
        border: 1px solid #313244;
    }}
    """
