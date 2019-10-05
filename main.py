from ui import *
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cgitb
import math
from xml.etree import ElementTree as ET
import time
import xmltodict

cgitb.enable()


class Newlable(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(None, parent)
        self.state = 'edit'
        self.setText('New Note')
        self.setStyleSheet("border-width:2px;border-style: solid; "
                           "border-radius: 15px;border-color: rgb(150, 100, 0);")
        self.setAcceptDrops(True)
        self.setReadOnly(False)
        self.setSelection(0, len(self.text()))
        self.setFocus()
        self.mm = False  # move mode
        self.press = False
        self.tgt = None
        self.draw = False

        # TODO:随输入字数变化大小
        # TODO:修改时不能点光标
        # TODO:保存为xml

    def mouseDoubleClickEvent(self, event):
        self.state = 'edit'
        self.setReadOnly(False)
        self.setAcceptDrops(True)
        self.setFocus()
        self.setStyleSheet("border-width:2px;border-style: solid; "
                           "border-radius: 15px;border-color: rgb(150, 100, 0);")

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Delete:
            if self.state == 'select':
                name = self.objectName()
                if name in win.lines:
                    win.lines.pop(name)
                for k in win.lines:
                    if name in win.lines[k]:
                        win.lines[k].remove(name)
                win.update()
                self.deleteLater()
        else:
            win.keyPressEvent(event)

    def mousePressEvent(self, QMouseEvent):
        self.press = True

    def mouseMoveEvent(self, event):
        if self.press and self.state != 'edit':
            self.mm = True
            if not hasattr(self, 'temp'):
                self.temp = win.inittag(self.x() + 90, self.y() + 90)
                self.temp.setObjectName(self.objectName())
                self.temp.setText(self.text())
                self.setObjectName('temp')
                self.setStyleSheet("border-style:none;background-color:rgb(240,240,240)")

            # if isinstance(temp,Newlable):
            wx = win.x()
            wy = win.y()
            x = event.globalX()
            y = event.globalY()
            self.move(x - wx - 90, y - wy - 90)

            alltag = win.findChildren(QLineEdit)
            for tag in alltag:
                tx = tag.x()
                ty = tag.y()
                distance = math.sqrt((self.x() - tx) ** 2 + (self.y() - ty) ** 2)
                if distance <= 90:
                    if tag not in [self.temp, self]:
                        tag.setStyleSheet("border-width: 0px;border-radius: 15px; border-style: solid;"
                                          "border-color: rgb(0, 0, 0);background-color: gray;")
                        self.tgt = tag
                else:
                    tag.setStyleSheet("border-width: 0px;border-radius: 15px; border-style: solid;"
                                      "border-color: rgb(0, 0, 0);background-color: rgb(240,240,240);")
                    if self.tgt == tag:
                        self.tgt = None

    def mouseReleaseEvent(self, event):
        self.press = False
        if self.state == 'select':
            self.state = 'edit'
            self.setReadOnly(False)
            self.setAcceptDrops(True)
            self.setFocus()
            self.setStyleSheet("border-width:2px;border-style: solid; "
                               "border-radius: 15px;border-color: rgb(150, 100, 0);")

        elif self.state == 'in':
            self.state = 'edit'
            alltag = win.findChildren(QLineEdit)
            for tag in alltag:
                if tag.state == 'select':
                    tag.state = None
                    tag.setStyleSheet("border-width: 0px;border-radius: 15px; border-style: solid;"
                                      "border-color: rgb(0, 0, 0);background-color:rgb(240,240,240)")
                    break
            self.state = 'select'
            self.setStyleSheet("border-width:3px;border-style: solid; "
                               "border-radius: 15px;border-color: rgb(150, 100, 0);")
        # elif self.state == 'edit':
        #     self.setStyleSheet("border-width: 0px;border-radius: 15px; border-style: solid;"
        #                        "border-color: rgb(240,240,240);background-color:rgb(240,240,240)")
        #     self.setReadOnly(True)
        #     self.state = None

        if self.mm:
            self.draw = True
            wx = win.x()
            wy = win.y()
            x = event.globalX()
            y = event.globalY()
            if self.tgt:
                win.drawline_pt(self.temp, self.tgt)
            else:
                self.temp.move(x - wx - 90, y - wy - 90)
                win.update()
                self.tgt = None
                self.mm = False
            self.temp.setReadOnly(True)
            self.temp.state = None
            self.deleteLater()

    def enterEvent(self, event):
        if self.state not in ['select', 'edit']:
            self.state = 'in'
            self.setStyleSheet("border-width:1.5px;border-style: dashed; "
                               "border-radius: 15px;border-color: rgb(0, 0, 0);"
                               "background-color:rgb(240,240,240)")

    def leaveEvent(self, event):
        if self.state not in ['select', 'edit']:
            self.state = None
            self.setStyleSheet("border-width: 0px;border-radius: 15px; border-style: solid;"
                               "border-color: rgb(0, 0, 0);background-color:rgb(240,240,240)")


class Mainwindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Mainwindow, self).__init__(parent)
        self.setupUi(self)
        # self.lines = []
        self.lines = {}
        self.draw = False
        self.lpos = (None, None)
        self.arrows = {}
        self.load = False
        self.arrows_num = 1
        self.num = 1
        self.setMouseTracking(True)
        print(self.hasMouseTracking())
        self.nodes = {}

        self.action_save.triggered.connect(self.savefile)
        self.action_open.triggered.connect(self.openfile)
        self.action_new.triggered.connect(self.newfile)

    def paintEvent(self, event):
        if self.draw and hasattr(self, 'lines'):
            pen = QPainter(self)
            pen.begin(self)
            for s in self.lines:
                for l in self.lines[s]:
                    ss = win.findChild(QLineEdit, s)
                    ee = win.findChild(QLineEdit, l)
                    line = QLineF(ss.x() + 90, ss.y() + 30, ee.x() + 90, ee.y() + 30)
                    line.setLength(line.length())
                    pen.setPen(QPen(Qt.darkRed, 2, Qt.DashLine))
                    pen.drawLine(line)
                    self.drawarrow(pen, line, ss, ee)

    def drawarrow(self, pen, line, s, e):
        v = line.unitVector()
        v.setLength(20)  # 改变单位向量的大小，实际就是改变箭头长度
        v.translate(QPointF(line.dx() / 2, line.dy() / 2))

        n = v.normalVector()  # 法向量
        n.setLength(n.length() * 0.5)  # 这里设定箭头的宽度

        n2 = n.normalVector().normalVector()

        p1 = v.p2()
        p2 = n.p2()
        p3 = n2.p2()

        pen.setPen(QPen(Qt.darkRed, 2, Qt.SolidLine))
        pen.drawPolygon(p1, p2, p3)

        l = min(p1.x(), p2.x(), p3.x())
        r = max(p1.x(), p2.x(), p3.x())
        t = max(p1.y(), p2.y(), p3.y())
        f = min(p1.y(), p2.y(), p3.y())
        value = [l, r, t, f, s, e]
        if value not in self.arrows.values():
            for k in self.arrows:
                if s == self.arrows[k][-2] and s == self.arrows[k][-1]:
                    self.arrows.pop(k)
            self.arrows[self.arrows_num] = value
            self.arrows_num += 1

    def drawline_pt(self, s, e):
        self.draw = True
        # 两点间已有连线
        if e.objectName() in self.lines:
            if s.objectName() in self.lines[e.objectName()]:
                # self.lines[s.objectName()].append(e.objectName())
                # self.lines[e.objectName()].remove(s.objectName())
                # todo:添加反向线
                return 0
        # 无s点记录
        if s.objectName() not in self.lines:
            self.lines[s.objectName()] = [e.objectName()]
        # 有s点记录
        else:
            # 删除现有连线
            if e.objectName() in self.lines[s.objectName()]:
                self.lines[s.objectName()].remove(e.objectName())
            # 添加新连线
            else:
                self.lines[s.objectName()].append(e.objectName())
        self.update()

    def mousePressEvent(self, event):
        alltag = self.findChildren(QLineEdit)
        for tag in alltag:
            if not tag.text():
                tag.deleteLater()
            if tag.state:
                tag.setReadOnly(True)
                tag.setAcceptDrops(False)
                if tag.state == 'edit':
                    tag.setSelection(len(tag.text()), len(tag.text()))
                    tag.setReadOnly(True)
                tag.state = None
                tag.setStyleSheet("border-width: 0px;border-radius: 15px; border-style: solid;"
                                  "border-color: rgb(0, 0, 0);background-color:rgb(240,240,240)")
                break

        for key in self.arrows:
            x = event.x()
            y = event.y()
            if x >= self.arrows[key][0] and x <= self.arrows[key][1] and \
                    y <= self.arrows[key][2] and y >= self.arrows[key][3]:
                new = win.inittag(x, y)
                new.show()
                self.drawline_pt(self.arrows[key][-2], new)
                self.drawline_pt(new, self.arrows[key][-1])
                self.lines[self.arrows[key][-2].objectName()].remove(self.arrows[key][-1].objectName())
                # self.update()
                self.arrows.pop(key)
                return None

    def mouseMoveEvent(self, event):
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

        self.inittag(x - wx, y - wy)

    def inittag(self, x, y):
        name = 'tag' + str(self.num)
        exec('self.%s = Newlable(self)' % name)
        exec('self.%s.setGeometry(x - 90, y - 75, 180, 50)' % name)
        exec('self.%s.show()' % name)
        exec('self.%s.setObjectName("%s")' % (name, name))
        self.nodes[self.num] = {}
        self.num += 1
        return eval('self.%s' % name)

    def modify_txt(self):
        self.tag1.setTextInteractionFlags(Qt.TextEditorInteraction)

    def savefile(self):
        self.nodes = {}
        alltag = self.findChildren(QLineEdit)
        for index, tag in enumerate(alltag):
            self.nodes[tag.objectName()] = {'Info': {'width': str(tag.width()),
                                                     'fontsize': str(tag.fontInfo().pointSize()),
                                                     'name': tag.objectName(),
                                                     'pos': ('%d,%d') % (tag.pos().x(), tag.pos().y())},
                                            'string': tag.text()}
            if tag.objectName() in self.lines:
                cons = ','.join(self.lines[tag.objectName()])
                self.nodes[tag.objectName()]['connects'] = cons
            print(self.nodes[tag.objectName()])

        # 通过信息构造xml
        root = ET.Element('CM_File')  # 创建首节点
        fid = ET.SubElement(root, 'Fid')  # 增加子节点
        fid.text = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        nodes = ET.SubElement(root, 'Nodes')
        for k in self.nodes:
            node = ET.SubElement(nodes, 'Node', attrib=self.nodes[k]['Info'])
            string = ET.SubElement(node, 'String')
            string.text = self.nodes[k]['string']
            connect = ET.SubElement(node, 'Connect')
            if 'connects' in self.nodes[k]:
                connect.text = self.nodes[k]['connects']
            else:
                connect.text = 'None'
        lines = ET.SubElement(root, 'Lines')  # 增加子节点
        for k in self.lines:
            line = ET.SubElement(lines, 'Line', attrib={'head': k})
            line.text = ','.join(self.lines[k])

        w = ET.ElementTree(root)

        FileName, _ = QFileDialog.getSaveFileName(self,"保存概念图", "", "CM Files(*.xml)")

        w.write(FileName, 'utf-8', xml_declaration=True)

    def openfile(self):
        new = NewWindow()


        FileName, _ = QFileDialog.getOpenFileName \
            (new,
             "选取文件",
             "",
             "XML Files (*.xml);;Scap File(*.scap);;All File(*.*)")

        if not FileName:
            return 0

        new.show()
        # new.exec_()

        tree = ET.parse(FileName)
        # 读取点数据
        nodes = tree.find('Nodes')
        for node in nodes:
            info = node.attrib
            x, y = info['pos'].split(',')
            tag = new.inittag(int(x)+90, int(y)+75)   #适应正常初始化，添加偏移量
            tag.setObjectName(info['name'])
            tag.state = None
            tag.setReadOnly(True)
            tag.setSelection(len(tag.text()), len(tag.text()))
            tag.setStyleSheet("border-width: 0px;border-radius: 15px; border-style: solid;"
                              "border-color: rgb(0, 0, 0);background-color:rgb(240,240,240)")
            num = int(info['name'][3:])
            if num > new.num:
                new.num = num
            tag.show()

        new.num+=1     #更新计数器，防止与读取内容冲突

        # 读取线数据
        lines = tree.find('Lines')
        for line in lines:
            head = line.attrib['head']
            tails = line.text.split(',')
            self.lines[head] = tails
        new.draw = True
        new.update()

    def newfile(self):
        new = NewWindow()
        new.show()
        new.exec_()


class NewWindow(Mainwindow):
    def __init__(self, parent=None):
        super(NewWindow, self).__init__(parent)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Mainwindow()
    win.show()
    sys.exit(app.exec_())
