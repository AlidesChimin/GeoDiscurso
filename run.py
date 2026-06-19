import sys
import os
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    # Habilita suporte a DPI alto se aplicável (padrão no Qt6)
    app = QApplication(sys.argv)
    app.setApplicationName("GeoConteúdo")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("GeoConteudoCorp")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
