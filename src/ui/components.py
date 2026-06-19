from PySide6.QtWidgets import QLineEdit, QCompleter
from PySide6.QtCore import Qt, QStringListModel

class AutocompleteLineEdit(QLineEdit):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        
        self.model = QStringListModel()
        self.completer.setModel(self.model)
        self.setCompleter(self.completer)
        
        if items:
            self.set_items(items)
            
    def set_items(self, items):
        self.model.setStringList(items)
        
    def get_value(self):
        return self.text().strip()

    def show_all_suggestions(self):
        self.completer.setCompletionPrefix(self.text())
        self.completer.complete()

    def focusInEvent(self, e):
        super().focusInEvent(e)
        self.show_all_suggestions()

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.show_all_suggestions()
