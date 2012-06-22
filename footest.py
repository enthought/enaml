

if __name__ == '__main__':
    import enaml
    from enaml.qt.qt_local_application import QtLocalApplication

    app = QtLocalApplication()

    with enaml.imports():
        from foo import SomeMain

    view = SomeMain()

    view.prepare()

    app.run()

