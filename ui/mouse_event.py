# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np

def color_convert(value):
    digit = list(map(str, range(10))) + list("ABCDEF")
    if isinstance(value, tuple):
        string = '#'
        for i in value:
            a1 = i // 16
            a2 = i % 16
            string += digit[a1] + digit[a2]
        return string
    elif isinstance(value, str):
        a1 = digit.index(value[1]) * 16 + digit.index(value[2])
        a2 = digit.index(value[3]) * 16 + digit.index(value[4])
        a3 = digit.index(value[5]) * 16 + digit.index(value[6])
        return (a1, a2, a3)
 

class GraphicsScene(QGraphicsScene):
    def __init__(self, ex, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.ex = ex
        self.modes = ex.modes
        self.mouse_clicked = False
        self.prev_pt = None

        # self.masked_image = None

        # save the points
        self.mask_points = []
        self.sketch_points = []
        self.stroke_points = []

        # save the history of edit
        self.history = []

        # strokes color
        self.stk_color = None

    def reset(self):
        # save the points
        self.mask_points = []
        self.sketch_points = []
        self.stroke_points = []

        # save the history of edit
        self.history = []

        # strokes color
        self.stk_color = None

        self.prev_pt = None

    def mousePressEvent(self, event):
        self.mouse_clicked = True
        if self.modes[3] == 1:
            self.prev_pt = event.scenePos()
            img_pos = (int(self.prev_pt.x()*self.ex.x_ratio), int(self.prev_pt.y()*self.ex.x_ratio))
            print("image position:{}".format(img_pos))
            b = self.ex.origin_mat_img[img_pos[1],img_pos[0],0]
            g = self.ex.origin_mat_img[img_pos[1],img_pos[0],1]
            r = self.ex.origin_mat_img[img_pos[1],img_pos[0],2]
            print("image position:{},color:{}-{}-{}".format(img_pos,r,g,b))
            self.ex.color = color_convert((r,g,b))
            self.ex.pushButton_4.setStyleSheet("background-color: %s;" % self.ex.color)
            self.get_stk_color(self.ex.color)

    def mouseReleaseEvent(self, event):
        self.prev_pt = None
        self.mouse_clicked = False

    def mouseMoveEvent(self, event):
        if self.mouse_clicked:
            if self.modes[0] == 1: # mask mode
                if self.prev_pt:
                    self.drawMask(self.prev_pt, event.scenePos())
                    pts = {}
                    pts['prev'] = (int(self.prev_pt.x()),int(self.prev_pt.y()))
                    pts['curr'] = (int(event.scenePos().x()),int(event.scenePos().y()))
                    self.mask_points.append(pts)
                    self.history.append(0)
                    self.prev_pt = event.scenePos()
                else:
                    self.prev_pt = event.scenePos()
            elif self.modes[1] == 1:    # sketch mode
                if self.prev_pt:
                    self.drawSketch(self.prev_pt, event.scenePos())
                    pts = {}
                    pts['prev'] = (int(self.prev_pt.x()),int(self.prev_pt.y()))
                    pts['curr'] = (int(event.scenePos().x()),int(event.scenePos().y()))
                    self.sketch_points.append(pts)
                    self.history.append(1)
                    self.prev_pt = event.scenePos()
                else:
                    self.prev_pt = event.scenePos()
            elif self.modes[2] == 1:    # stroke
                if self.prev_pt:
                    self.drawStroke(self.prev_pt, event.scenePos())
                    pts = {}
                    pts['prev'] = (int(self.prev_pt.x()),int(self.prev_pt.y()))
                    pts['curr'] = (int(event.scenePos().x()),int(event.scenePos().y()))
                    pts['color'] = self.stk_color
                    self.stroke_points.append(pts)
                    self.history.append(2)
                    self.prev_pt = event.scenePos()
                else:
                    self.prev_pt = event.scenePos()

    def drawMask(self, prev_pt, curr_pt):
        lineItem = QGraphicsLineItem(QLineF(prev_pt, curr_pt))
        lineItem.setPen(QPen(Qt.white, 12, Qt.SolidLine)) # rect
        self.addItem(lineItem)

    def drawSketch(self, prev_pt, curr_pt):
        lineItem = QGraphicsLineItem(QLineF(prev_pt, curr_pt))
        lineItem.setPen(QPen(Qt.black, 1, Qt.SolidLine)) # rect
        self.addItem(lineItem)

    def drawStroke(self, prev_pt, curr_pt):
        lineItem = QGraphicsLineItem(QLineF(prev_pt, curr_pt))
        lineItem.setPen(QPen(QColor(self.stk_color), 4, Qt.SolidLine)) # rect
        self.addItem(lineItem)

    def get_stk_color(self, color):
        self.stk_color = color

    def erase_prev_pt(self):
        self.prev_pt = None

    def reset_items(self):
        for i in range(len(self.items())):
            item = self.items()[0]
            self.removeItem(item)
        
    def undo(self):
        if len(self.items())>1:
            if len(self.items())>=9:
                for i in range(8):
                    item = self.items()[0]
                    self.removeItem(item)
                    if self.history[-1] == 0:
                        self.mask_points.pop()
                        self.history.pop()
                    elif self.history[-1] == 1:
                        self.sketch_points.pop()
                        self.history.pop()
                    elif self.history[-1] == 2:
                        self.stroke_points.pop()
                        self.history.pop()
                    elif self.history[-1] == 3:
                        self.history.pop()
            else:
                for i in range(len(self.items())-1):
                    item = self.items()[0]
                    self.removeItem(item)
                    if self.history[-1] == 0:
                        self.mask_points.pop()
                        self.history.pop()
                    elif self.history[-1] == 1:
                        self.sketch_points.pop()
                        self.history.pop()
                    elif self.history[-1] == 2:
                        self.stroke_points.pop()
                        self.history.pop()
                    elif self.history[-1] == 3:
                        self.history.pop()
