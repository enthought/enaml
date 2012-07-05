

if __name__ == '__main__':
    import enaml
    from enaml.qt.qt_local_application import QtLocalApplication

    with enaml.imports():
        from foo import SomeMain

    app = QtLocalApplication()

    view = SomeMain()
    view.publish()

    app.mainloop()

