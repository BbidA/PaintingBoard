import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QAction

from dollar_1 import recognizeShape
from shape_base import Shape, Line, saveShapeTo, loadShape


class MyBoard(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.shape = Shape()
        self.current_line = Line()

        self.label = QLabel(self)
        self.init_ui()

    def init_ui(self):
        self.label.setAlignment(Qt.AlignTop)

        # init actions
        save_action = QAction('save', self)
        load_action = QAction('load', self)
        resample_action = QAction('resample', self)

        save_action.triggered.connect(self.__saveShape)
        load_action.triggered.connect(self.__loadShape)
        resample_action.triggered.connect(self.resample)

        # set menu bar
        menu_bar = self.menuBar()
        save = menu_bar.addMenu('save')
        save.addAction(save_action)
        read = menu_bar.addMenu('read')
        read.addAction(load_action)
        resample_menu = menu_bar.addMenu('resample')
        resample_menu.addAction(resample_action)

        self.setGeometry(300, 300, 350, 200)
        self.setWindowTitle('Event Object')
        self.show()

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        painter.setPen(pen)

        # draw previous points and lines
        for line in self.shape.lines:
            self.__drawPoints(line, painter)
            # draw line to make it look more good
            # self.__drawLineBetweenPoints(line, painter)

        # draw current line
        self.__drawPoints(self.current_line, painter)
        self.__drawLineBetweenPoints(self.current_line, painter)

        painter.end()

    def mouseMoveEvent(self, e):
        self.current_line.addPoint(e.x(), e.y())

        self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            # create new line and add it to the shape
            self.shape.addLine(self.current_line)
            self.current_line = Line()
            # show tag of current shape
            self.__show_shape_tag()

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.__clear_board()
            self.update()

    @staticmethod
    def __drawLineBetweenPoints(line, painter):
        for i in range(1, line.points_number()):
            painter.drawLine(line.get_q_point(i), line.get_q_point(i - 1))

    @staticmethod
    def __drawPoints(line, painter):
        for point in line.q_points:
            painter.drawPoint(point)

    def __show_shape_tag(self):
        self.label.setText(self.shape.tag)

    def __saveShape(self):
        target = QFileDialog.getSaveFileName(self, 'Save Shape', 'shape')
        if target[0]:
            saveShapeTo(target[0], self.shape)

    def __loadShape(self):
        source = QFileDialog.getOpenFileName(self, 'Load Shape', 'shape')
        if source[0]:
            self.shape = loadShape(source[0])
            self.current_line.clear()
            self.__show_shape_tag()
            self.update()

    def __clear_board(self):
        self.shape.clear_lines()
        self.current_line.clear()
        self.label.setText('')

    def resample(self):
        points = recognizeShape(self.shape)
        self.shape = Shape.from_points(points)
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = MyBoard()
    sys.exit(app.exec_())
