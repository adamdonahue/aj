import broom
import tempfile
import time
import webbrowser

# TODO: Introduce base class for Editable framework widgets.
#       Better, use external widget classes!

class Label(object):
    def __init__(self, label):
        self.label = label

    def rendered(self):
        return '<b>%s</b>' % self.label

class Field(object):
    def __init__(self, value=None, callbacks={}):
        self.value = value

        # TODO: Determine callbacks (onChange, etc.).
        self.callbacks = callbacks

    def rendered(self):
        return '<form><input type="text" value="%s"></input></form>' % self.value

class HL(object):
    def __init__(self, children):
        # TODO: Make support fields.
        self.children = children

    def rendered(self):
        ret = '<table><tr>{}</tr><table>'
        rendered = []
        for child in self.children:
            rendered.append(child.rendered())
        return ret.format("".join(rendered))

class VL(object):
    def __init__(self, children):
        self.children = children

    def rendered(self):
        ret = '<table><tr><td>{}</td></table>'
        rendered = []
        for child in self.children:
            rendered.append(child.rendered())
        return ret.format("".join(rendered))

class Button(object):
    def __init__(self, label, callbacks={}):
        self.label = label

        # TODO: Determine callbacks (onClick, etc.).
        self.callbacks = callbacks

    def rendered(self):
        return '<button type="button">%s</button>' % self.label

class Frame(object):

    def __init__(self, title, child=[]):
        self.title = title
        self.child = child      # TODO: Support multiple children?

    def rendered(self):
        ret = '<html><title>{0}</title><body><h1>{0}</h1>{1}</body></html>'
        return ret.format(self.title, self.child.rendered())

class EditableMixin(object):
    """Adds .edit() to any BroomDBObject, enabling basic editing
    functionality.

    """
    def edit(self):
        frame = Frame(self.EditableTitle(), VL(self.EditableFields()))
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            f.write(frame.rendered())
        webbrowser.open_new("file:///" + f.name)

    def EditableTitle(self):
        return 'Edit %s (ID: %s)' % (self.__tablename__, self.id)

    def EditableFields(self):
        # TODO: Move database columns to stored fields, and use
        #       stored fields here.
        ret = []
        for field in self._databaseFields:
            ret.append(HL([Label(field), Field(getattr(self, field))]))
        ret.append(VL([Button("Save"), Button("Cancel")]))
        return ret
