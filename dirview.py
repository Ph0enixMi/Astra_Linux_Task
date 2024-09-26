import sys, time

from PyQt5.QtCore import (QCommandLineOption, QCommandLineParser, QCoreApplication, QDir, QT_VERSION_STR, QStandardPaths, QSortFilterProxyModel, Qt)
from PyQt5.QtWidgets import (QApplication, QFileIconProvider, QFileSystemModel, QTreeView, QWidget, QMainWindow, QLineEdit, QPushButton, QGridLayout, QMessageBox)


class Window(QMainWindow):
    def __init__(self, app):
        super(Window, self).__init__()
        QCoreApplication.setApplicationVersion(QT_VERSION_STR)
        self.setWindowTitle('Dir View')
        self.resize(1000, 600)

        self._createGrid()

        self._createParser(app)
        try:
            self.rootPath = self.parser.positionalArguments().pop(0)
        except IndexError:
            self.rootPath = None

        self._createModel()

        self._createTree()


    def _createGrid(self):
        self.cental_widget = QWidget()
        self.setCentralWidget(self.cental_widget)
        self.cental_widget.setContentsMargins(0, 0, 0, 0)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText('Введите текст...')

        self.btn_update = QPushButton()
        self.btn_update.setText('Поиск')
        self.btn_update.clicked.connect(self._btn_update_click)

        self.btn_clear = QPushButton()
        self.btn_clear.setText('Очистить')
        self.btn_clear.clicked.connect(self._btn_clear_click)

        self.grid = QGridLayout()

        self.grid.addWidget(self.line_edit, 0, 0)
        self.grid.addWidget(self.btn_update, 0, 1)
        self.grid.addWidget(self.btn_clear, 0, 2)

        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(0)

        self.cental_widget.setLayout(self.grid)


    def _createParser(self, app):
        self.parser = QCommandLineParser()
        self.parser.setApplicationDescription("Qt Dir View Example")
        self.parser.addHelpOption()
        self.parser.addVersionOption()

        self.dontUseCustomDirectoryIconsOption = QCommandLineOption('c',"Set QFileIconProvider.DontUseCustomDirectoryIcons")
        self.parser.addOption(self.dontUseCustomDirectoryIconsOption)
        self.parser.addPositionalArgument('directory', "The directory to start in.")

        self.parser.process(app)

    
    def _createModel(self):
        self.model = QFileSystemModel()

        self.home_directory = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        self.model.setRootPath(self.home_directory)
        self.model.setFilter(QDir.AllDirs | QDir.Files | QDir.Hidden)

        if self.parser.isSet(self.dontUseCustomDirectoryIconsOption):
            self.model.iconProvider().setOptions(QFileIconProvider.DontUseCustomDirectoryIcons)

        self.model.directoryLoaded.connect(self._on_directory_loaded)


    def _createTree(self):
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        if self.rootPath is not None:
            rootIndex = self.model.index(QDir.cleanPath(self.rootPath))
            if rootIndex.isValid():
                self.tree.setRootIndex(rootIndex)
        self.tree.setRootIndex(self.model.index(self.home_directory))

        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)

        availableSize = QApplication.desktop().availableGeometry(self.tree).size()
        self.tree.resize(availableSize / 2)
        self.tree.setColumnWidth(0, int(self.tree.width() / 3))

        self.grid.addWidget(self.tree, 1, 0, 1, 3)


    def _on_directory_loaded(self, path):
        index = self.model.index(path)
        num_rows = self.model.rowCount(index)
        print(num_rows)


    def _btn_update_click(self):
        filter_text = self.line_edit.text().lower()
        if not filter_text:
            QMessageBox.warning(self, 'Предупреждение', 'Введите текст в поле')
            return

        self._show_matching_rows(self.model.index(''), filter_text)


    def _show_matching_rows(self, parent_index, filter_text):
        for row in range(self.model.rowCount(parent_index)):
            index = self.model.index(row, 0, parent_index)
            file_name = self.model.fileName(index).lower()

            if filter_text in file_name:
                self.tree.setRowHidden(row, parent_index, False)
            else:
                self.tree.setRowHidden(row, parent_index, True)

            self._show_matching_rows(index, filter_text)


    def _btn_clear_click(self):
        self.line_edit.clear()
        self._show_all_rows(self.model.index(''))


    def _show_all_rows(self, parent_index):
        for row in range(self.model.rowCount(parent_index)):
            index = self.model.index(row, 0, parent_index)
            self.tree.setRowHidden(row, parent_index, False)
            self._show_all_rows(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window(app)

    win.show()
    sys.exit(app.exec_())
