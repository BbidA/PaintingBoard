import copy
import pickle
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QAction, QLineEdit, QPushButton

import dollar_1
from dollar_1 import recognize_shape
from shape_base import Shape, Line


class MyBoard(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.shape = Shape()
        self.current_line = Line()
        self.templates = []
        self.debug = True

        self.label = QLabel(self)
        self.input_label = QLineEdit(self)
        self.button = QPushButton('Sure', self)

        self.init_ui()

    def init_ui(self):
        self.label.setAlignment(Qt.AlignTop)
        self.input_label.move(0, 180)
        self.input_label.resize(50, 20)
        self.button.clicked.connect(self.input_tag)
        self.button.resize(50, 20)
        self.button.move(55, 180)

        # init actions
        save_action = QAction('save', self)
        load_action = QAction('load', self)

        add_to_templates = QAction('Add to templates', self)
        save_templates = QAction('Save templates', self)
        load_templates = QAction('Load templates', self)

        save_action.triggered.connect(self.__saveShape)
        load_action.triggered.connect(self.__loadShape)
        add_to_templates.triggered.connect(self.add_current_shape_to_templates)
        save_templates.triggered.connect(self.save_templates)
        load_templates.triggered.connect(self.load_templates)

        # debug actions
        resample = QAction('resample', self)
        resample.triggered.connect(self.do_resample)

        rotate = QAction('rotate', self)
        rotate.triggered.connect(self.rotate_to_zero)

        scale = QAction('scale', self)
        scale.triggered.connect(self.scale_to_square)

        translate = QAction('translate', self)
        translate.triggered.connect(self.translate_to_origin)

        # set menu bar
        menu_bar = self.menuBar()

        save = menu_bar.addMenu('save')
        save.addAction(save_action)
        save.addAction(add_to_templates)
        save.addAction(save_templates)

        read = menu_bar.addMenu('read')
        read.addAction(load_action)
        read.addAction(load_templates)

        debug = menu_bar.addMenu('debug')
        debug.addAction(resample)
        debug.addAction(rotate)
        debug.addAction(scale)
        debug.addAction(translate)

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
            if not self.debug:
                self.__drawLineBetweenPoints(line, painter)

        # draw current line
        self.__drawPoints(self.current_line, painter)
        if not self.debug:
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
            self.recognize()

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
            save_object(target[0], self.shape)

    def __loadShape(self):
        source = QFileDialog.getOpenFileName(self, 'Load Shape', 'shape')
        if source[0]:
            self.shape = load_object(source[0])
            self.current_line.clear()
            self.__show_shape_tag()
            self.update()

    def __clear_board(self):
        self.shape.clear()
        self.current_line.clear()
        self.label.setText('')

    def add_current_shape_to_templates(self):
        self.templates.append(copy.deepcopy(self.shape))

    def save_templates(self):
        target = QFileDialog.getSaveFileName(self, 'Save Templates', 'templates')
        if target[0]:
            save_object(target[0], self.templates)

    def load_templates(self):
        source = QFileDialog.getOpenFileName(self, 'Load Templates')
        if source[0]:
            templates = load_object(source[0])
            if not isinstance(templates, list):
                raise ValueError('Not templates loaded')
            self.templates = templates

    def input_tag(self):
        self.shape.tag = self.input_label.text()
        self.__show_shape_tag()

    def recognize(self):
        matched_shape = recognize_shape(self.shape, self.templates)
        self.shape.tag = matched_shape.tag
        self.__show_shape_tag()

    def do_resample(self):
        new_points = dollar_1.resample(self.shape.points, dollar_1.resample_points_num)
        self.shape = Shape.from_points(new_points)
        self.update()

    def rotate_to_zero(self):
        new_points = dollar_1.rotate_to_zero(self.shape.points)
        self.shape = Shape.from_points(new_points)
        self.update()

    def scale_to_square(self):
        new_points = dollar_1.scale_to_square(self.shape.points, dollar_1.reference_square_size)
        # w, h = dollar_1.bounding_box(self.shape.points)
        # print('width is {}, height is {}'.format(w, h))
        self.shape = Shape.from_points(new_points)
        self.update()

    def translate_to_origin(self):
        new_points = dollar_1.translate_to_origin(self.shape.points)
        self.shape = Shape.from_points(new_points)
        self.update()


def save_object(path, shape):
    target = open(path, 'wb')
    pickle.dump(shape, target)


def load_object(path):
    source = open(path, 'rb')
    return pickle.load(source)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = MyBoard()
    sys.exit(app.exec_())
