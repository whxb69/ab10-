from ui import *
from findui import *
from newtags import *
from undo import *

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cgitb
import math
from xml.etree import ElementTree as ET
import time
import os
import PyQt5.sip
import sip

cgitb.enable()


class Newlabel(QLineEdit):
    stateChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(None, parent)
        self.textChanged.connect(self.widthchange)
        self.stateChanged.connect(self.stateChangeEvent)
        self.state = 'edit'
        self.setText('New Note')
        self.sheet = {
            'None':
            "border-width:0px;border-style: None; "
            "border-radius: 15px;background-color:rgb(240,240,240)",
            'edit':
            "border-width:2px;border-style: solid; "
            "border-radius: 15px;border-color: rgb(150, 100, 0);",
            'Bedit':
            "border: 1px solid red,4px solid black",
            'in':
            "border-width:1.5px;border-style: dashed; "
            "border-radius: 15px;border-color: rgb(0, 0, 0);"
            "background-color:rgb(240,240,240)",
            'B':
            "border-width:3px;border-style: solid; "
            "border-radius: 15px;border-color: rgb(0, 0, 0);"
            "background-color:rgb(240,240,240)",
            'select':
            "border-width:3px;border-style: solid; "
            "border-radius: 15px;border-color: rgb(150, 100, 0);",
            'Bselect':
            "border: 3px solid black;"
            "outline: 5px solid red;",
            'crash':
            "border-width: 0px;border-radius: 15px; border-style: solid;"
            "border-color: rgb(0, 0, 0);background-color: gray;",
            'Bcrash':
            "border-width: 5px;border-radius: 15px; border-style: solid;"
            "border-color: rgb(0, 0, 0);background-color: gray;",
            'move':
            "border-width:0px;border-radius: 15px;"
            "border-color: rgb(0, 0, 0);background-color:rgb(240,240,240)"
        }
        self.setStyleSheet(self.sheet['edit'])
        # self.setAcceptDrops(True)
        # self.setDragEnabled(True)
        self.setAlignment(Qt.AlignCenter)
        self.mm = False  # move mode
        self.press = False
        self.tgt = None
        self.draw = False
        self.Bstate = False
        self.setMinimumWidth(tagw)
        # self.temp = None
        # self.opos = None

        self.window = self.parentWidget()

    def widthchange(self):
        # tag宽度自适应
        length = self.fontMetrics().width(self.text())
        if self.text():
            s_size = length / len(self.text())
        try:
            self.resize(length + 2 * s_size, self.height())
        except:
            pass

    def stateChangeEvent(self, state):
        if not state:
            self.state = state
            self.setFocusPolicy(Qt.NoFocus)
            if self.selectedText():
                self.setSelection(0, 0)
            self.setStyleSheet(self.sheet['None'])
            self.setGraphicsEffect(None)
            self.setReadOnly(True)
        elif state == 'in':
            self.state = state
            self.setFocusPolicy(Qt.NoFocus)
            self.setStyleSheet(self.sheet[state])
            self.setReadOnly(True)
        elif state == 'select':
            self.state = state
            self.setFocusPolicy(Qt.NoFocus)
            if self.Bstate:
                self.setStyleSheet(self.sheet['select'])
                effect = QGraphicsDropShadowEffect()
                effect.setOffset(0, 0)
                effect.setBlurRadius(20)
                effect.setColor(Qt.red)
                self.setGraphicsEffect(effect)
            else:
                self.setStyleSheet(self.sheet[state])
            if self not in self.window.selects:
                self.window.selects.append(self)
        elif state == 'edit':
            if self in self.window.selects:
                self.window.selects.remove(self)
            self.state = state
            self.setDragEnabled(True)
            self.setFocusPolicy(Qt.StrongFocus)
            self.setSelection(len(self.text()), len(self.text()))
            if self.Bstate:
                self.setStyleSheet(self.sheet['Bedit'])
                effect = QGraphicsDropShadowEffect()
                effect.setOffset(0, 0)
                effect.setBlurRadius(20)
                effect.setColor(Qt.green)
                self.setGraphicsEffect(effect)
            else:
                self.setStyleSheet(self.sheet[state])
            self.setReadOnly(False)
            self.setSelection(len(self.text()), len(self.text()))
        elif state == 'crash':
            self.state = state
            self.setStyleSheet(self.sheet[state])
            self.setReadOnly(True)

        if self.Bstate:
            self.setStyleSheet(self.sheet['B'])

    def changeEvnet(self, evnet):
        # 需要保存信号
        self.window.changed = True

    def contextMenuEvent(self, event):
        if self.window.selects:
            [tag.stateChanged.emit(None) for tag in self.window.selects]
        self.stateChanged.emit('select')
        menu = QMenu(self)
        newlink = menu.addAction('&新建连接标签')
        newlink.triggered.connect(lambda: self.window.newlink(self, event))
        newlinks = menu.addAction('&新建多连接标签')
        newlinks.triggered.connect(lambda: self.window.newlink(self, event))
        if len(self.window.selects) < 2:
            newlinks.setEnabled(False)
        else:
            newlink.setEnabled(False)

        menu.addSeparator()
        cut = menu.addAction("&剪切")
        cut.triggered.connect(self.window.cutTag)
        copy = menu.addAction("&复制")
        copy.triggered.connect(self.window.copyTag)

        menu.addSeparator()
        reset = menu.addAction("&还原")
        reset.triggered.connect(self.B_fun)

        Bcase = menu.addAction("&Bcase")
        Bcase.triggered.connect(self.B_fun)

        Del = menu.addAction('&删除')
        Del.triggered.connect(self.del_fun)
        menu.exec_(event.globalPos())

    # def keyPressEvent(self, event):
    #     #tag删除

    #     else:
    #         self.window.keyReleaseEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.state == 'edit':
                super().mousePressEvent(event)
            self.press = True
            self.window.press = True

    def moveEvent(self, event):
        if self.window.press:
            if not self.window.move_head:
                for tag in self.window.selects:
                    if hasattr(tag, 'temp'):
                        self.window.move_head = tag
            else:
                if len(self.window.selects
                       ) > 1 and self == self.window.move_head:
                    if not self.window.selects_dis:
                        for tag in self.window.selects:
                            self.window.selects_dis[tag] = {
                                'x': tag.x() - self.x(),
                                'y': tag.y() - self.y()
                            }
                    for tag in self.window.selects:
                        if tag != self:
                            # 触发位移时定义占位tag
                            if not hasattr(tag, 'temp'):
                                tag.temp = tag.window.inittag(
                                    tag.x() + tagw / 2,
                                    tag.y() + tagh * 3 / 2,
                                    mode='temp')
                                tag.temp.setObjectName(tag.objectName())
                                tag.temp.setText(tag.text())
                                tag.state = None
                                tag.stateChanged.emit(tag.state)
                                if tag.Bstate:
                                    tag.temp.setStyleSheet(tag.sheet['B'])
                                    tag.temp.Bstate = True
                                else:
                                    tag.temp.setStyleSheet('None')
                            tag.setObjectName('temp')
                            tag.state = None
                            tag.stateChanged.emit(tag.state)

                            tag.move(
                                self.x() + self.window.selects_dis[tag]['x'],
                                self.y() + self.window.selects_dis[tag]['y'])

    def mouseMoveEvent(self, event):
        if self.state == 'edit' and not self.window.selects:
            super().mouseMoveEvent(event)
        if self.press and self.state != 'edit':
            self.mm = True#移动模式开启
            if not hasattr(self, 'temp'):
                # 触发位移时定义占位tag
                self.temp = self.window.inittag(self.x() + tagw / 2,
                                                self.y() + tagh * 3 / 2,
                                                mode='temp')
                self.temp.setObjectName(self.objectName())
                self.temp.setText(self.text())
                self.temp.setReadOnly(True)
                self.temp.setAcceptDrops(False)
                if self.Bstate:
                    self.temp.setStyleSheet(self.sheet['B'])
                    self.temp.Bstate = True
                else:
                    self.temp.setStyleSheet('None')
                self.temp.setObjectName(self.objectName())
                self.setObjectName('temp')
                self.state = None
                self.stateChanged.emit(self.state)

            wx = self.window.x()
            wy = self.window.y()
            x = event.globalX()
            y = event.globalY()
            self.move(x - wx - tagw / 2, y - wy - tagh * 3 / 2)

            alltag = self.window.findChildren(Newlabel)
            for tag in alltag:
                tx = tag.x()
                ty = tag.y()
                rect = QRect(
                    QPoint(tx, ty),
                    QPoint(tx + 3 / 2 * tag.width(),
                           ty + 3 / 2 * tag.height()))
                point = QPoint(
                    event.globalX() - self.window.x(),
                    event.globalY() - self.window.y() - tag.height() / 2)
                if rect.contains(point):
                    tgt_n = [self.temp, self]
                    tgt_n.extend(self.window.selects)  # 不可做tgt集合
                    if tag not in tgt_n:
                        if tag.Bstate:
                            tag.setStyleSheet(tag.sheet['Bcrash'])
                        else:
                            tag.setStyleSheet(tag.sheet['crash'])
                        self.tgt = tag
                    else:
                        tag.setStyleSheet(tag.sheet['None'])
                else:
                    if tag.Bstate:
                        tag.setStyleSheet(tag.sheet['B'])
                    else:
                        tag.setStyleSheet(tag.sheet['None'])
                    if self.tgt == tag:
                        self.tgt = None

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.state == 'edit':
                super().mouseReleaseEvent(event)
            self.press = False
            self.window.press = False
            if self.state == 'select':
                self.state = 'edit'
                self.stateChanged.emit(self.state)
            elif self.state == 'in':
                alltag = self.window.findChildren(Newlabel)
                for tag in alltag:
                    if tag.state in ['select', 'edit'] and tag != self:
                        tag.state = None
                        tag.stateChanged.emit(None)
                        break
                self.state = 'select'
                self.stateChanged.emit(self.state)

                # release结束移动
            if self.mm:
                self.draw = True
                wx = self.window.x()
                wy = self.window.y()
                x = event.globalX()
                y = event.globalY()
                if self.tgt:
                    # 连接后画线
                    llist = []
                    #多对一连线
                    if self.window.selects:
                        for tag in self.window.selects:
                            self.window.drawline_pt(tag.temp, self.tgt)
                            llist.append(
                                [tag.temp.objectName(),
                                 self.tgt.objectName()])
                        cmd = UndoDrawLine(self.window, llist, True)
                    #一对一连线
                    else:
                        self.window.drawline_pt(self.temp, self.tgt)
                        llist.append(
                            [self.temp.objectName(),
                             self.tgt.objectName()])
                        cmd = UndoDrawLine(self.window, llist, True)
                    self.window.undostack.push(cmd)
                    # 设置边框
                    if self.tgt.Bstate:
                        self.tgt.setStyleSheet(self.temp.sheet['B'])
                    else:
                        self.tgt.setStyleSheet(self.tgt.sheet['None'])
                else:
                    # 非连接 移动tag
                    if len(self.window.selects) > 1:
                        tlist = {}
                        for tag in self.window.selects:
                            tlist[tag.temp.objectName()] = {
                                'obj': tag.temp,
                                'x': tag.temp.x(),
                                'y': tag.temp.y(),
                                'nx': tag.x(),
                                'ny': tag.y()
                            }
                            tag.temp.move(tag.x(), tag.y())
                            tag.temp.stateChanged.emit(None)
                            if tag.temp.Bstate:
                                tag.temp.setStyleSheet(self.temp.sheet['B'])

                    else:
                        #tilst为撤销需要数据
                        tlist = {
                            self.temp.objectName(): {
                                'obj': self.temp,
                                'x': self.temp.x(),
                                'y': self.temp.y(),
                                'nx': self.x(),
                                'ny': self.y()
                            }
                        }
                        self.temp.move(x - wx - tagw / 2,
                                       y - wy - tagh * 3 / 2)
                        self.tgt = None
                        self.mm = False

                    cmd = UndoMove(self.window, tlist, Newlabel, True)
                    self.window.undostack.push(cmd)

                self.temp.stateChanged.emit(None)
                if self.temp.Bstate:
                    self.temp.setStyleSheet(self.temp.sheet['B'])
                self.deltag(True)#删除占位tag
            # 删除占位tag
            tagToDel = self.window.findChildren(Newlabel, 'temp')  #找到待删除tag
            if tagToDel:
                for tag in tagToDel:
                    tag.deltag(True)
            self.window.update()
            #多选情况 重置select列表
            if self.window.selects != [self] \
                    and self.state == 'select':
                self.window.selects = []

            # alltag = self.window.findChildren(Newlabel)
            # for tag in alltag:
            #     tag.stateChanged.emit(None)

    # def dropEvent(self, event):
    #     pass
    #     #TODO: 当前drop待优化 和press共同优化
    def enterEvent(self, event):
        if self.state not in ['select', 'edit']:
            self.state = 'in'
            self.stateChanged.emit(self.state)
            # if not self.Bstate:
            #     self.setStyleSheet(self.sheet[self.state])
            # else:
            #     self.setStyleSheet(self.sheet['B'])

    def leaveEvent(self, event):
        if self.state not in ['select', 'edit']:
            self.state = None
            self.stateChanged.emit(None)

    def B_fun(self):
        if not self.Bstate:
            self.Bstate = True
            self.setStyleSheet(self.sheet['B'])
        else:
            self.Bstate = False
            self.stateChanged.emit(self.state)

    def deltag(self, temp=False):
        #删除连线数据
        if self.objectName() in self.window.lines:
            self.window.lines.pop(self.objectName())
        #删除箭头数据
        keys = []  # 待删除arrows索引
        if self.window.arrows:
            for key, value in self.window.arrows.items():
                if self in value:
                    keys.append(key)
        [self.window.arrows.pop(key) for key in keys]
        #清清除select列表信息
        if self in self.window.selects:
            self.window.selects.remove(self)
        self.deleteLater()
        sip.delete(self)
        self.window.update()

        # 更新logo状态
        alltag = self.window.findChildren(Newlabel)
        if len(alltag) == 0:
            self.window.logo.move(self.window.width() * 0.4,
                                  self.window.height() * 7 / 16)
            self.window.logo.show()

    def del_fun(self):
        if self.window.selects:
            for tag in self.window.selects:
                tag.deltag()
        self.window.selects = []
        # else:
        #     self.deltag()


class Mainwindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Mainwindow, self).__init__(parent)
        self.setupUi(self)
        # TODO:创建滚动条
        # self.scroll = QScrollArea()
        # self.scroll.setWidget(self)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        # self.lines = []
        self.setWindowTitle("Concept map")

        # 标签、连线、箭头信息
        self.lines = {}
        self.draw = False
        self.lpos = (None, None)
        self.arrows = {}
        self.nodes = {}
        self.arrows_num = 1
        self.num = 1

        self.load = False
        self.setMouseTracking(True)
        self.window = self
        self.press = False
        self.filename = None
        self.changed = False
        self.setAcceptDrops(True)
        self.press_s = None
        self.selects = []
        self.selects_dis = {}  # 选中tag的距离数据
        self.move_head = None

        # self.scroll_area = QScrollArea(self)
        # self.scroll_area.setWidget(self.centralwidget)
        # self.scroll_area.resize(self.width(),self.height())
        # self.scroll_area.setWidgetResizable(True)
        # self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.sb.sliderMoved.connect(self.test)

        # alt键按下
        self.alt_mode = False

        # 记录剪切数据
        self.cuts = []
        self.cutsx = []
        self.cutsy = []

        # 记录复制信息
        self.copys = {}
        self.copysx = {}
        self.copysy = {}

        self.lines_temp = {}  # 剪切时暂存line数据
        self.setAcceptDrops(True)

        self.undostack = QUndoStack()
        self.action_redo = self.undostack.createRedoAction(self, "重做")
        self.action_redo.setShortcut("Ctrl+Shift+Z")

        # 文件菜单
        self.action_save.triggered.connect(
            lambda: self.savefile(self.filename))
        self.action_saveas.triggered.connect(self.saveasfile)
        self.action_open.triggered.connect(self.openfile)
        self.action_new.triggered.connect(self.newfile)

        # 编辑菜单
        m_edit = self.menubar.addMenu('编辑')
        m_edit.addAction(self.action_undo)  # 撤销
        m_edit.addAction(self.action_redo)  #重做
        m_edit.addSeparator()
        m_edit.addAction(self.action_cut)  # 剪切
        m_edit.addAction(self.action_copy)  # 复制
        m_edit.addAction(self.action_paste)  # 粘贴
        m_edit.addSeparator()
        m_edit.addAction(self.action_delete)  # 删除
        m_edit.addAction(self.action_find)  # 查找
        m_edit.addAction(self.action_selectall)  # 全选

        self.action_undo.triggered.connect(self.undo_fun)
        self.action_cut.triggered.connect(self.cutTag)
        self.action_copy.triggered.connect(self.copyTag)
        self.action_paste.triggered.connect(self.pasteTag)
        self.action_delete.triggered.connect(self.deleteTag)
        self.action_find.triggered.connect(self.findAndReplace)
        self.action_selectall.triggered.connect(self.selectAll)

        # 标签菜单
        m_note = self.menubar.addMenu('标签')
        m_note.addAction(self.action_newtag)
        m_note.addAction(self.action_newtags)

        self.action_newtag.triggered.connect(
            lambda: self._inittag(self.width() / 2,
                                  self.height() / 2))
        self.action_newtags.triggered.connect(self.newtags)

        # tag拖动框
        self.label_tag = Dlabel(self)
        self.label_tag.setObjectName('tag')
        self.label_tag.setGeometry(
            QtCore.QRect(0, 0.25 * self.screenHeight, 20,
                         0.5 * self.screenHeight))

        # rel拖动框
        self.label_rel = Dlabel(self)
        self.label_rel.setObjectName('rel')
        self.label_rel.setGeometry(
            QtCore.QRect(self.screenWidth - 20, 0.25 * self.screenHeight, 20,
                         0.5 * self.screenHeight))

        # 设置快捷键
        QShortcut(QKeySequence("Ctrl+A"), self, self.selectAll)
        QShortcut(QKeySequence("Ctrl+C"), self, self.copyTag)
        QShortcut(QKeySequence("Ctrl+X"), self, self.cutTag)
        QShortcut(QKeySequence("Ctrl+V"), self, self.pasteTag)
        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo_fun)
        # QShortcut(QKeySequence("Ctrl+Shift+Z"), self, self.redo_fun)

        self.cmdstack = []

    def undo_fun(self):
        self.undostack.undo()
        # for i in range(self.undostack.count()):
        #     print(self.undostack.command(i))
        # print('-' * 20)

    def redo_fun(self):
        print(self.undostack.currentIndex())
        self.action_redo

    def test(self):
        print(self.sb.value())
        self.scroll_area.scrollContentsBy(500, self.sb.value())

    def resizeEvent(self, event):
        # 保持Dlabel相对方位和大小
        self.label_tag.resize(20, 0.5 * self.height())
        self.label_tag.move(0, 0.25 * self.height())
        self.label_rel.resize(20, 0.5 * self.height())
        self.label_rel.move(self.width() - 20, 0.25 * self.height())
        self.logo.move(self.width() * 0.35, self.height() * 7 / 16)
        # self.scroll_area.resize(self.width(), self.height())

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction(self.action_undo)
        menu.addAction(self.action_redo)
        menu.addSeparator()

        new = menu.addAction('&新建')
        new.triggered.connect(lambda: self._inittag(event.x(), event.y()))
        # delete = menu.addAction('&删除')
        menu.addSeparator()
        # cut = menu.addAction('&剪切')
        # copy = menu.addAction('&复制')
        paste = menu.addAction('&粘贴')
        selall = menu.addAction('&全选')
        paste.triggered.connect(self.pasteTag)
        selall.triggered.connect(self.selectAll)
        menu.exec_(event.globalPos())

    def closeEvent(self, event):
        # 画布有变动
        if self.changed:
            messageBox = QMessageBox()
            messageBox.setWindowTitle('Concept Map')
            messageBox.setText('是否保存对文件的更改')
            messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No
                                          | QMessageBox.Cancel)
            buttonY = messageBox.button(QMessageBox.Yes)
            buttonY.setText('是')
            buttonN = messageBox.button(QMessageBox.No)
            buttonN.setText('否')
            buttonN = messageBox.button(QMessageBox.Cancel)
            buttonN.setText('取消')
            messageBox.exec_()

            if messageBox.clickedButton() == buttonY:
                if not self.filename:  # 新文件
                    res = self.saveasfile()
                    if not res:
                        event.ignore()  # 未完成保存等同取消
                else:  # 已有文件
                    self.savefile(self.filename)
            elif messageBox.clickedButton() == buttonN:
                event.ignore()  # 不保存
            else:
                pass  # 取消

    def paintEvent(self, event):
        pen = QPainter(self)
        if not pen.isActive():
            pen.begin(self)

        if self.draw and hasattr(self, 'lines'):
            for s in self.lines:
                for l in self.lines[s]:
                    ss = self.window.findChild(QLineEdit, s)
                    ee = self.window.findChild(QLineEdit, l)
                    if ss and ee:
                        line = QLineF(ss.x() + ss.width() / 2,
                                      ss.y() + ss.height() / 2,
                                      ee.x() + ee.width() / 2,
                                      ee.y() + ee.height() / 2)
                        line.setLength(line.length())
                        pen.setPen(QPen(Qt.darkRed, 2, Qt.DashLine))
                        pen.drawLine(line)
                        self.drawarrow(pen, line, ss, ee)

        if hasattr(self, 'press_e'):
            if self.press_s and self.press and self.press_e:
                alltag = self.findChildren(Newlabel)
                for index, tag in enumerate(alltag):
                    area = QRect(
                        QPoint(tag.x(), tag.y()),
                        QPoint(tag.x() + tag.width(),
                               tag.y() + tag.height()))
                    if area.contains(self.press_s):
                        return None
                pen.setPen(QPen(Qt.black, 1, Qt.DashLine))
                scene = QGraphicsScene()
                scene.setSceneRect(0, 0, self.width(), self.height())
                rect = QRectF(self.press_s, self.press_e)
                pen.drawRect(rect)

    def drawarrow(self, pen, line, s, e):
        v = line.unitVector()
        v.setLength(15)  # 改变单位向量的大小，实际就是改变箭头长度
        v.translate(QPointF(line.dx() / 2, line.dy() / 2))

        n = v.normalVector()  # 法向量
        n.setLength(n.length() * 0.5)  # 这里设定箭头的宽度

        n2 = n.normalVector().normalVector()

        p1 = v.p2()
        p2 = n.p2()
        p3 = n2.p2()

        pen.setPen(QPen(Qt.darkRed, 2, Qt.SolidLine))
        pen.drawPolygon(p1, p2, p3)

        # 记录箭头位置和头尾节点
        l = min(p1.x(), p2.x(), p3.x())
        r = max(p1.x(), p2.x(), p3.x())
        t = max(p1.y(), p2.y(), p3.y())
        f = min(p1.y(), p2.y(), p3.y())
        value = [l, r, t, f, s, e]
        if value not in self.arrows.values():
            for k in self.arrows:
                if s == self.arrows[k][-2] and s == self.arrows[k][-1]:
                    self.arrows.pop(k)
                    # 遍历中删除产生问题
            self.arrows[self.arrows_num] = value
            self.arrows_num += 1

    def drawline_pt(self, s, e):
        self.draw = True
        #检查传入的参数 可能是tag或tag对应objectName 均转换为objectName
        if isinstance(s, str):
            sname = s
        else:
            sname = s.objectName()

        if isinstance(e, str):
            ename = e
        else:
            ename = e.objectName()

        # 两点间已有连线,改为反向
        if ename in self.lines:
            if sname in self.lines[ename]:
                if sname not in self.lines:
                    self.lines[sname] = [ename]
                else:
                    self.lines[sname].append(ename)
                self.lines[ename].remove(sname)
        # 无s点记录
        if sname not in self.lines:
            self.lines[sname] = [ename]
        # 有s点记录
        else:
            # 删除现有连线
            if ename in self.lines[sname]:
                self.lines[sname].remove(ename)
            # 添加新连线
            else:
                self.lines[sname].append(ename)
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteTags()
        elif event.key() == Qt.Key_Alt:
            self.alt_mode = True

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Alt:
            self.alt_mode = False

    def mousePressEvent(self, event):
        # 标记按下和坐标
        if event.button() == Qt.LeftButton:
            self.press = True
            self.press_s = event.pos()

            # 重置移动数据
            self.selects = []
            self.selects_dis = {}
            self.move_head = None    #群体位移时的主触发tag

            alltag = self.findChildren(Newlabel)
            for tag in alltag:
                # 删除无内容tag
                if not tag.text():
                    tag.deltag()
                else:
                    if tag.state:
                        tag.setReadOnly(True)
                        tag.setAcceptDrops(False)
                        if tag.state == 'edit':
                            if tag.x() < event.globalX() - self.x() and event.globalX() - self.x() < tag.x() + tagw \
                                    and tag.y() < event.globalY() - self.y() and event.globalY() - self.y() < tag.y() + tagw / 2:
                                return None
                            else:
                                tag.state = None
                                tag.stateChanged.emit(None)
                        # if not tag.Bstate:
                        #     tag.setStyleSheet(tag.sheet['None'])
                        # else:
                        #     tag.setStyleSheet(tag.sheet['B'])
                    # break

        # 点击箭头新建中间结点
        for key in self.arrows:
            x = event.x()
            y = event.y()
            if x >= self.arrows[key][0] and x <= self.arrows[key][1] and \
                    y <= self.arrows[key][2] and y >= self.arrows[key][3]:
                new = self.window.inittag(x, y)
                tinfo = {'obj': new, 'x': x, 'y': y, 'name': new.objectName()}
                cmd = UndoArrowtag(self, tinfo,
                                   self.arrows[key][-2].objectName(),
                                   self.arrows[key][-1].objectName(), True)
                self.undostack.push(cmd)
                new.show()
                self.drawline_pt(self.arrows[key][-2], new)
                self.drawline_pt(new, self.arrows[key][-1])
                self.lines[self.arrows[key][-2].objectName()].remove(
                    self.arrows[key][-1].objectName())
                self.arrows.pop(key)
                return None

    def mouseReleaseEvent(self, event):
        self.press = False
        alltag = self.findChildren(Newlabel)

        # 检查并更新各tag状态
        for tag in alltag:
            if not tag.text():
                tag.deltag()
                continue
            tag.state = None
            tag.stateChanged.emit(None)
            tag.setReadOnly(True)
            tag.press = False

        # 选中框选范围内tag
        if self.press_s and hasattr(self, 'press_e'):
            if self.press_e:
                area = QRect(self.press_s, self.press_e)
                self.press = False
                self.press_s = None
                self.press_e = None
                self.update()
                self.selects = []
                for tag in alltag:
                    if area.contains(tag.x() + tagw / 2, tag.y() + tagh / 2):
                        self.selects.append(tag)
                        tag.state = 'select'
                        tag.stateChanged.emit(tag.state)

    def mouseMoveEvent(self, event):
        if self.press:
            self.press_e = event.pos()
            self.update()
        else:
            # 识别箭头
            self.press_s = None
            x = event.x()
            y = event.y()
            flag = False
            if len(self.arrows) > 0:
                for key in self.arrows:
                    if x >= self.arrows[key][0] and x <= self.arrows[key][1] and \
                            y <= self.arrows[key][2] and y >= self.arrows[key][3]:
                        flag = True
                    else:
                        pass
            if flag:
                self.setCursor(QCursor(Qt.PointingHandCursor))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseDoubleClickEvent(self, event):
        wx = self.x()
        wy = self.y()
        x = event.globalX()
        y = event.globalY()

        self._inittag(x - wx, y - wy)

    #拖放生成新标签
    def dropEvent(self, event):
        self.setFocusPolicy(Qt.StrongFocus)
        texts = event.mimeData().text().split('\n')
        tlist = {}
        for text in texts:
            new = self.inittag(event.pos().x(), event.pos().y())
            tlist[new.objectName()] = {
                'obj': new,
                'x': new.x(),
                'y': new.y(),
                'B': new.Bstate
            }
            new.setText(text)
            if self.alt_mode:
                new.Bstate = True
            new.stateChanged.emit(None)
            new.show()
        cmd = UndoInitTag(self, tlist, first=True)
        self.undostack.push(cmd)

    def dragEnterEvent(self, event):
        self.window.setCursor(QCursor(Qt.DragCopyCursor))
        # 接受事件 将事件转到dropevent
        event.accept()

    def _inittag(self, x, y, name=None, mode=None, mmode='h'):
        tag = self.inittag(x, y, name, mode, mmode)
        tlist = {
            tag.objectName(): {
                'obj': tag,
                'x': tag.x(),
                'y': tag.y(),
                'B': tag.Bstate
            }
        }
        cmd = UndoInitTag(self.window, tlist, first=True)
        self.undostack.push(cmd)

    def inittag(self, x, y, name=None, mode=None, mmode='h'):
        '''
        新建tag
        :param mode: 是否调整坐标
        :param mmode: 坐标调整模式
        :return: 新tag
        '''
        alltag = self.findChildren(Newlabel)
        for tag in alltag:
            if tag.objectName() == name:
                return 0
        if not mode:
            target = QPoint(x, y)
            alltag = self.findChildren(Newlabel)
            for tag in alltag:
                area = QRect(
                    QPoint(tag.x(), tag.y()),
                    QPoint(tag.x() + tag.width(),
                           tag.y() + tag.height() * 2))
                if area.contains(target):
                    if mmode == 'w':
                        x += tagw
                    elif mmode == '-w':
                        x -= tagw
                    elif mmode == 'x':
                        x += tagw / 2
                        y += tagh / 2
                    elif mmode == 'h':
                        y += tagh
                    target = QPoint(x, y)

        self.changed = True
        if not name:
            name = 'tag' + str(self.num)
        exec('self.%s = Newlabel(self)' % name)
        exec('self.%s.setGeometry(x - %d, y - %d, %d, %d)' %
             (name, tagw / 2, tagh * 3 / 2, tagw, tagh))
        exec('self.%s.show()' % name)
        exec('self.%s.setObjectName("%s")' % (name, name))
        self.nodes[self.num] = {}
        self.num += 1

        alltag = self.findChildren(Newlabel)
        if len(alltag) > 0:
            self.window.logo.hide()

        if eval('self.%s' % name):
            tag = eval('self.%s' % name)

        return eval('self.%s' % name)

    def newlink(self, tag, event):
        x = event.globalX() - self.x() + 2 * tagw
        y = event.globalY() - self.y() + 2 * tagh
        newtag = self.inittag(x, y)
        llist = []
        if len(self.selects) < 2:
            self.drawline_pt(tag, newtag)
            llist.append(tag.objectName())
        else:
            for tag in self.selects:
                self.drawline_pt(tag, newtag)
                llist.append(tag.objectName())

        ninfo = {'name': newtag.objectName(), 'x': newtag.x(), 'y': newtag.y()}
        cmd = UndoNewlink(self, ninfo, llist, True)
        self.undostack.push(cmd)

    # 另存为
    def saveasfile(self):
        self.filename = self.savefile()
        if self.filename:
            self.setWindowTitle("Concept map - " +
                                os.path.basename(self.filename))
        return self.filename

    # 保存
    def savefile(self, filename=None):
        if not filename:
            FileName, _ = QFileDialog.getSaveFileName(self, "保存概念图", "",
                                                      "CM Files(*.xml)")
            if not FileName:
                return None
        else:
            FileName = filename

        self.nodes = {}
        alltag = self.findChildren(Newlabel)

        # 提取信息
        for index, tag in enumerate(alltag):
            self.nodes[tag.objectName()] = {
                'Info': {
                    'Width': str(tag.width()),
                    'FontSize': str(tag.fontInfo().pointSize()),
                    'ID': tag.objectName(),
                    'Position': ('%d,%d') % (tag.pos().x(), tag.pos().y()),
                    'Bstate': str(tag.Bstate)
                },
                'string': tag.text()
            }
            if tag.objectName() in self.lines:
                cons = ','.join(self.lines[tag.objectName()])
                self.nodes[tag.objectName()]['connects'] = cons

        # 通过信息构造xml
        root = ET.Element('CM_File')  # 创建首节点
        fid = ET.SubElement(root, 'Fid')  # 增加子节点
        fid.text = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        nodes = ET.SubElement(root, 'Notes')
        for k in self.nodes:
            node = ET.SubElement(nodes, 'Note', attrib=self.nodes[k]['Info'])
            string = ET.SubElement(node, 'String')
            string.text = self.nodes[k]['string']
            connect = ET.SubElement(node, 'ConnectedNoteIDs')
            if 'connects' in self.nodes[k]:
                connect.text = self.nodes[k]['connects']
            else:
                connect.text = 'None'

        w = ET.ElementTree(root)

        w.write(FileName, 'utf-8', xml_declaration=True)
        self.setWindowTitle('Concept map - ' + os.path.basename(FileName))
        return FileName

    #打开文件
    def openfile(self):
        alltag = self.window.findChildren(Newlabel)
        if len(alltag) == 0:  # 当前无标签 在原窗口打开
            new = self
        else:  # 当前有标签 新建窗口
            self.new = Mainwindow()
            self.new.move(self.x() + 100, self.y() + 100)
            new = self.new

        FileName, _ = QFileDialog.getOpenFileName \
            (new,
             "选取文件",
             "",
             "XML Files (*.xml);;Scap File(*.scap);;All File(*.*)")

        if not FileName:
            return 0
        else:
            if self.filename == FileName:
                return 0
            else:
                cur = self
                while hasattr(cur, 'father'):
                    cur = cur.father
                    if cur.filename == FileName:
                        cur.setWindowState(Qt.WindowActive)
                        return 0
                while hasattr(cur, 'new'):
                    cur = cur.new
                    if cur.filename == FileName:
                        cur.setWindowState(Qt.WindowActive)
                        return 0

            new.filename = FileName
            new.setWindowTitle("Concept map - " +
                               os.path.basename(new.filename))

        tree = ET.parse(FileName)
        # 读取点数据
        nodes = tree.find('Notes')
        for node in nodes:
            info = node.attrib
            x, y = info['Position'].split(',')
            tag = new.inittag(
                int(float(x)) + tagw / 2,
                int(float(y)) + (tagh * 3 / 2))  # 适应正常初始化，添加偏移量

            nid = info['ID']
            if 'tag' not in nid:
                num = int(nid)
                nid = 'tag' + str(nid)
            else:
                num = int(nid[3:])
            tag.setText(node.find('String').text)
            tag.setObjectName(nid)
            tag.state = None
            tag.stateChanged.emit(None)

            # 更新tag计数 防止计数冲突
            if num > new.num:
                new.num = num

            # 获取链接信息
            cons_n = node.find('ConnectedNoteIDs')

            if cons_n != None:
                cons_t = cons_n.text
                if cons_t not in ['None', None]:
                    cons = cons_t.split(',')
                    temp_n = []
                    if '-' in cons_t:  # 适应sapple文件格式
                        for c in cons:
                            if '-' in c:
                                sn, en = [int(n) for n in c.split('-')]
                                ns = [
                                    'tag' + str(n) for n in range(sn, en + 1)
                                ]
                                temp_n += ns
                            else:
                                temp_n.append('tag' + c)
                        cons = temp_n
                    else:
                        if 'tag' not in cons_t:
                            for c in cons:
                                temp_n.append('tag' + c.strip())
                            cons = temp_n
                    new.lines[nid] = cons

            try:
                if info['Bstate'] == 'True':
                    tag.Bstate = True
                    tag.setStyleSheet(tag.sheet['B'])
            except:
                if node.find('Appearance').find(
                        'Border').attrib['Weight'] != '0':
                    tag.Bstate = True
                    tag.setStyleSheet(tag.sheet['B'])

            tag.show()

        new.num += 1  # 更新计数器，防止与读取内容冲突
        new.draw = True
        new.update()
        new.show()

    #新建文件
    def newfile(self):
        self.new = Mainwindow()
        self.new.father = self
        self.new.move(self.x() + 100, self.y() + 100)
        self.new.show()

    #剪切
    def cutTag(self):
        # 记录剪切数据
        self.cuts = {}
        self.cut_lines = {}

        # 记录撤销数据
        dlist = {}
        llist = []
        # 剪切多个tag
        if len(self.selects) > 1:
            for index, tag in enumerate(self.selects):
                # 记录点
                self.cuts[index] = {
                    'x': tag.x() - self.selects[0].x(),
                    'y': tag.y() - self.selects[0].y()
                }
                dlist[tag.objectName()] = {'x': tag.x(), 'y': tag.y()}
                # 记录连线
                if tag.objectName() in self.lines:
                    self.cut_lines[index] = []
                    for tag_e in self.lines[tag.objectName()]:
                        if self.window.findChild(Newlabel,
                                                 tag_e) in self.selects:
                            tgt = self.window.findChild(Newlabel, tag_e)
                            self.cut_lines[index].append(
                                self.selects.index(tgt))
                            llist.append([tag.objectName(), tgt.objectName()])
            # TODO:先遍历一遍后又遍历删除 需要优化
            while self.selects:
                self.selects[-1].deltag()
        # 剪切单个tag
        else:
            tag = self.selects[0]
            if tag.objectName() in self.lines:
                self.lines.pop(tag.objectName())
            for line in self.lines:
                if tag.objectName() in self.lines[line]:
                    self.lines[line].remove(tag.objectName())
            self.cuts[0] = {'x': 0, 'y': 0}
            dlist[tag.objectName()] = {'x': tag.x(), 'y': tag.y()}
            tag.deltag()
        self.update()
        cmd = UndoDelTag(self, dlist, llist, True)
        self.undostack.push(cmd)

        if self.copys:
            self.copys = {}
            self.copy_lines = {}

    #复制
    def copyTag(self):
        self.copys = {}
        self.copy_lines = {}
        if self.selects:
            for index, tag in enumerate(self.selects):
                # 记录点
                self.copys[index] = {
                    'x': tag.x() - self.selects[0].x(),
                    'y': tag.y() - self.selects[0].y(),
                    'text': tag.text(),
                    'Bstate': tag.Bstate
                }
                # 记录连线
                if tag.objectName() in self.lines:
                    self.copy_lines[index] = []
                    for tag_e in self.lines[tag.objectName()]:
                        if self.window.findChild(Newlabel,
                                                 tag_e) in self.selects:
                            tgt = self.window.findChild(Newlabel, tag_e)
                            self.copy_lines[index].append(
                                self.selects.index(tgt))

            if self.cuts:
                self.cuts = []
                self.cutsx = []
                self.cutsy = []

    def pasteTag(self):
        self.selects = []
        # 剪切到粘贴
        if self.cuts:
            news = {}  # 存储新tag
            tlist = {}
            llist = []
            # 复制tag
            for tag in self.cuts:
                new = self.inittag(self.width() / 2 + self.cuts[tag]['x'],
                                   self.height() / 2 + self.cuts[tag]['y'],
                                   mmode='x')

                new.stateChanged.emit(None)
                tlist[new.objectName()] = {
                    'obj': new,
                    'x': new.x(),
                    'y': new.y(),
                    'B': new.Bstate
                }
                new.show()
                news[tag] = new
            # 复制连线信息
            for tag in news:
                if tag in self.cut_lines:
                    for tag_e in self.cut_lines[tag]:
                        self.drawline_pt(news[tag], news[tag_e])
                        llist.append(
                            [news[tag].objectName(), news[tag_e].objectName()])
            self.update()
            cmd = UndoPaste(self, tlist, llist, True)
            self.undostack.push(cmd)

        # 复制到粘贴
        if self.copys:
            news = {}  # 存储新tag
            tlist = {}
            llist = []
            # 复制tag
            for tag in self.copys:
                new = self.inittag(self.width() / 2 + self.copys[tag]['x'],
                                   self.height() / 2 + self.copys[tag]['y'],
                                   mmode='x')

                # 不能复制全部属性，则其他需复制属性待添加
                new.setText(self.copys[tag]['text'])
                new.Bstate = self.copys[tag]['Bstate']

                new.stateChanged.emit(None)
                tlist[new.objectName()] = {
                    'obj': new,
                    'x': new.x(),
                    'y': new.y(),
                    'B': new.Bstate
                }
                new.show()
                news[tag] = new
            # 复制连线信息
            for tag in news:
                if tag in self.copy_lines:
                    for tag_e in self.copy_lines[tag]:
                        self.drawline_pt(news[tag], news[tag_e])
                        llist.append(
                            [news[tag].objectName(), news[tag_e].objectName()])
            self.update()
            cmd = UndoInitTag(self, tlist, llist, first=True)
            self.undostack.push(cmd)

    def deleteTag(self, name):
        if name:
            tag = self.findChild(Newlabel, name)
            tag.deltag()
        else:
            if self.selects:
                while self.selects:
                    self.selects[-1].deltag()

    def deleteTags(self):
        alltag = self.findChildren(Newlabel)
        dlist = {}
        llist = []
        for tag in alltag:
            if tag.state == 'select':
                dlist[tag.objectName()] = {'x': tag.x(), 'y': tag.y()}
                name = tag.objectName()
                if name in self.lines:
                    for end in self.lines[name]:
                        llist.append([name, end])
                    self.lines.pop(name)
                for k in self.lines:
                    if name in self.lines[k]:
                        llist.append([k, name])
                        self.lines[k].remove(name)
                # 更新连线
                self.update()
                # 删除节点
                tag.deltag()
        cmd = UndoDelTag(self, dlist, llist, True)
        self.undostack.push(cmd)

    def findAndReplace(self):
        findDia = Find_D(self)
        findDia.exec_()

    def selectAll(self):
        alltag = self.window.findChildren(Newlabel)
        for tag in alltag:
            tag.stateChanged.emit('select')

    def newtags(self):
        NewDia = New_D(self)
        NewDia.exec_()


class Dlabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(None, parent)
        self.window = self.parentWidget()
        self.setAcceptDrops(True)
        self.setStyleSheet(
            "border-width:0px;border-style: None; "
            "border-radius: 15px;background-color:rgb(240,240,240)")

    def leaveEvent(self, event):
        self.setStyleSheet(
            "border-width:0px;border-style: None; "
            "border-radius: 15px;background-color:rgb(240,240,240)")
        self.window.setCursor(QCursor(Qt.ArrowCursor))

    def dropEvent(self, event):
        text = event.mimeData().text()
        texts = text.split('\n')
        tlist = {}
        if self.objectName() == 'tag':# tag生成
            for index, tag in enumerate(texts):
                new = self.window.inittag(self.width() + tagw / 2,
                                          self.y() + (index + 1) * 80,
                                          mmode='w')
                # new.move(self.width() + 20, self.y() + (index + 1) * 80)
                new.setStyleSheet(new.sheet['B'])
                new.Bstate = True
                new.state = None
                new.stateChanged.emit(None)
                new.setText(tag)
                tlist[new.objectName()] = {
                    'obj': new,
                    'x': new.x(),
                    'y': new.y(),
                    'B': True
                }
            cmd = UndoInitTag(self.window, tlist, first=True)
            self.window.undostack.push(cmd)
        else:# rel生成
            for index, tag in enumerate(texts):
                new = self.window.inittag(self.window.width() - self.width() -
                                          tagw,
                                          self.y() + (index + 1) * 80,
                                          mmode='-w')
                # new.move(self.window.width() - self.width() - tagw, self.y() + (index + 1) * 80)
                new.setStyleSheet(new.sheet['None'])
                new.setReadOnly(True)
                new.state = None
                new.stateChanged.emit(None)
                new.setText(tag)
                tlist[new.objectName()] = {
                    'obj': new,
                    'x': new.x(),
                    'y': new.y(),
                    'B': new.Bstate
                }
            cmd = UndoInitTag(self.window, tlist, first=True)
            self.window.undostack.push(cmd)

    def dragLeaveEvent(self, event):
        self.setStyleSheet(
            "border-width:0px;border-style: None; "
            "border-radius: 15px;background-color:rgb(240,240,240)")
        self.window.setCursor(QCursor(Qt.ArrowCursor))

    def dragEnterEvent(self, event):
        self.setStyleSheet("border-width:0px;border-style: None; "
                           "border-radius: 15px;background-color:grey")
        self.window.setCursor(QCursor(Qt.DragCopyCursor))
        # 接受事件 将事件转到dropevent
        event.accept()


class New_D(QDialog, New_Form):
    def __init__(self, parent=None):
        super(New_D, self).__init__(parent)
        self.setupUi(app)
        self.window = self.parentWidget()
        self.btn_yes.clicked.connect(self.news)
        self.btn_no.clicked.connect(lambda: self.close())

    def news(self):
        num = self.spinBox.value()
        tlist = {}
        for _ in range(num):
            tag = self.window.inittag(self.window.width() / 2,
                                      self.window.height() / 2)
            tlist[tag.objectName()] = {
                'obj': tag,
                'x': tag.x(),
                'y': tag.y(),
                'B': tag.Bstate
            }

        cmd = UndoInitTag(self.window, tlist, first=True)
        self.window.undostack.push(cmd)

        self.close()


class Find_D(QDialog, Find_Form):
    def __init__(self, parent=None):
        super(Find_D, self).__init__(parent)
        self.setupUi(app)
        self.window = self.parentWidget()
        self.get_all.setChecked(True)
        self.btn_next.clicked.connect(lambda: self.find(mode='N'))
        self.btn_prev.clicked.connect(lambda: self.find(mode='P'))
        self.btn_reall.clicked.connect(lambda: self.replace(all_=True))
        self.btn_replace.clicked.connect(lambda: self.replace())

        self.cur_find = -1

    '''
    查找
    mode:查找下一个或上一个 ['N','P']
    '''
    def find(self, mode):
        alltag = self.window.findChildren(Newlabel)
        #确定查找范围 由单选框决定
        if self.get_sel.isChecked():
            tags = self.window.selects
        else:
            tags = alltag
        tgt = self.line_find.text()
        allres = []
        for tag in tags:
            if tgt in tag.text():
                res = tag.text().find(tgt)
                #匹配同一tag中全部结果
                while res != -1:
                    allres.append([tag, res])
                    res = tag.text().find(tgt, res + 1)#从当前匹配的下一字符再次寻找

        # 定位目标tag和index
        def setres():
            if allres:
                tag, index = allres[self.cur_find]
                for t in alltag:
                    t.stateChanged.emit(None)
                tag.stateChanged.emit('edit')
                tag.setSelection(index, len(tgt))

        # 更改当前查找索引索引
        if mode == 'N':#查找下一个
            self.cur_find += 1
            if self.cur_find > len(allres) - 1:
                self.cur_find = 0
            setres()

        else:#查找上一个
            self.cur_find -= 1
            if self.cur_find < 0:
                self.cur_find = len(allres) - 1
            setres()

    def replace(self, all_=False):
        alltag = self.window.findChildren(Newlabel)
        #确定替换范围
        if self.get_sel.isChecked():
            tags = self.window.selects
        else:
            tags = alltag

        # 获取替换源和目标
        ori = self.line_find.text()
        tgt = self.line_find_2.text()

        cur_rpc = []
        if all_:
            for tag in tags:
                if ori in tag.text():
                    new_t = tag.text().replace(ori, tgt, 1)
                    tag.setText(new_t)
        else:
            for tag in alltag:
                tag.stateChanged.emit(None)
                if ori in tag.text():
                    res = tag.text().find(ori)
                    if not cur_rpc:
                        cur_rpc.extend([tag, res])
                        break
            
            if cur_rpc:
                tag, index = cur_rpc
                new_t = tag.text().replace(ori,tgt,1) #新文本
                tag.setText(new_t)
                tag.stateChanged.emit('edit')
                tag.setSelection(index, len(tgt))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tagw = 180 * math.sqrt(app.desktop().width() / 3840)
    tagh = 50 * math.sqrt(app.desktop().height() / 2160)
    win = Mainwindow()
    win.show()
    sys.exit(app.exec_())
