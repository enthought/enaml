#!/usr/bin/env python
import sys
import math
from PySide import QtCore, QtGui, QtOpenGL
from PySide.QtOpenGL import QGLShader, QGLShaderProgram
import Image
import numpy as np
import time
try:
    from OpenGL import GL, GLUT, GLU
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
                            "PyOpenGL must be installed to run this example.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)


vertex_shader = '''
attribute highp vec4 vertex;
void main(void)
{
    gl_TexCoord[0] = gl_MultiTexCoord0;
    gl_Position = ftransform();
}
'''

fragment_shader = '''
uniform sampler2D image;
uniform float opacity;

void main(void)
{
    vec4 color = texture2D(image ,gl_TexCoord[0].st);
    //color.a *= opacity;
    gl_FragColor = color;
}
'''


class Texture(object):
    def __init__(self, width, height, buffer, format=GL.GL_RGBA, border=0, pixel_type=GL.GL_UNSIGNED_BYTE):
        self.width = height
        self.height = width
        self.buffer = buffer
        self.format = format
        self.border = border
        self.pixel_type = pixel_type


class Layer(object):
    def __init__(self, x, y, texture, level=0, texture_format=GL.GL_RGBA, x_offset=0, y_offset=0, opacity=1.0):
        self.x, self.y = x, y
        t1 = time.time()
        self.id = GL.glGenTextures(1)
        self.upload(texture, level=0, texture_format=GL.GL_RGBA, x_offset=0, y_offset=0)
        t2 = time.time()
        print 'texture_upload', t2 - t1
        self.opacity = opacity

    def upload(self, texture, level=0, texture_format=GL.GL_RGBA, x_offset=0, y_offset=0):
        self.width = texture.width
        self.height = texture.height
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.id)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexEnvf(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_MODULATE)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, level, texture_format, texture.width, texture.height, texture.border, texture.format, texture.pixel_type, None)
        GL.glTexSubImage2D(GL.GL_TEXTURE_2D, level, x_offset, y_offset, texture.width, texture.height, texture.format, texture.pixel_type, texture.buffer)

    def render(self, width, height, program, uniforms):
        #program.setUniformValue('uniforms['opacity']', self.opacity)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        GL.glLoadIdentity()

        GLU.gluOrtho2D(0, width, height, 0)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()

        GL.glLoadIdentity()
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.id)

        GL.glBegin(GL.GL_POLYGON)

        GL.glTexCoord2f(0, 0)
        GL.glVertex2f(self.x, self.y)

        GL.glTexCoord2f(0, 1)
        GL.glVertex2f(self.x, self.y + self.height)

        GL.glTexCoord2f(1, 1)
        GL.glVertex2f(self.x + self.width, self.y + self.height)

        GL.glTexCoord2f(1, 0)
        GL.glVertex2f(self.x + self.width, self.y)

        GL.glEnd()

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPopMatrix()

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPopMatrix()


def make_layer(filename, x, y, in_format=GL.GL_RGBA, out_format=GL.GL_RGBA):
    image = np.asarray(Image.open(filename))
    texture = Texture(image.shape[0], image.shape[1], image, format=in_format)
    layer = Layer(x, y, texture=texture, texture_format=out_format)
    return layer


class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)

    def initializeGL(self):
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_CULL_FACE)
        GL.glDisable (GL.GL_STENCIL_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendEquation(GL.GL_FUNC_ADD)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        self.initShaders()
        self.layers = []
        for i in range(30):
            self.layers.append(make_layer('layer_one.png', 0, 0))
        self.layers.append(make_layer('layer_two.png', 50, 0))
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glClearColor(1, 0.5, 0.5, 1.0)
        self.orientCamera()

    def paintGL(self):
        t1 = time.time()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.program.bind()
        uniforms = {}
        uniforms['opacity'] = self.program.uniformLocation('opacity')
        for layer in self.layers:
            layer.render(self.width(), self.height(), self.program, uniforms)
        self.program.release()
        t2 = time.time()
        print 'draw_call', t2 - t1

    def paintTeapot(self):
        self.program.bind()
        GL.glPushAttrib(GL.GL_POLYGON_BIT)
        GL.glFrontFace(GL.GL_CW)
        GL.glColor3f(0.2, 0.2, 0.5)
        GLUT.glutSolidTeapot(3.0)
        self.program.release()
        GL.glPopAttrib()

    def orientCamera(self):
        return
        GL.glPushAttrib(GL.GL_TRANSFORM_BIT)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluOrtho2D(0, self.width(), self.height(), 0)
        GL.glPopAttrib()

    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)
        self.orientCamera()

    def initShaders(self):
        self.vertex_shader = QtOpenGL.QGLShader(QGLShader.Vertex)
        self.vertex_shader.compileSourceCode(vertex_shader)
        self.fragment_shader = QGLShader(QGLShader.Fragment)
        self.fragment_shader.compileSourceCode(fragment_shader)
        self.program = QGLShaderProgram(self.context())
        self.program.addShader(self.vertex_shader)
        self.program.addShader(self.fragment_shader)
        self.program.link()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main_window = QtGui.QMainWindow()
    gl_widget = GLWidget()
    main_window.setCentralWidget(gl_widget)
    main_window.resize(1920, 1200)
    main_window.show()
    sys.exit(app.exec_())
