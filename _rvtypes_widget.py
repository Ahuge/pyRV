from rv.rvtypes import MinorMode
from rv import commands, runtime
from .util import TBox, Configuration


class Widget(MinorMode):
    class Button:
        def __init__(self):
            self._x = 0.0
            self._y = 0.0
            self._w = 0.0
            self._h = 0.0
            self._callback = None
            self._near = False

        def inside(self, x, y):
            return self._x <= x <= (self._x + self._w) and self._y <= y <= (self._y + self._w)

    def __init__(self):
        super(Widget, self).__init__()
        self._multiple = False
        self._config = Configuration()
        self._x = 0.0
        self._y = 0.0
        self._w = 0.0
        self._h = 0.0
        self._downPoint = TBox(0, 0)
        self._dragging = False
        self._inCloseArea = False
        self._containsPointer = False
        self._buttons = []
        self._whichMargin = 0

    def init(self, name, globalBindings, overrideBindings, menu=None, sortKey=None, ordering=0, multiple=None):
        super(Widget, self).init(name, globalBindings, overrideBindings, menu, sortKey, ordering)
        if multiple is None:
            self._whichMargin = -1
        else:
            self._multiple = multiple

    def toggle(self):
        self._active = not self._active

        commands.writeSetting("Tools", "show_" + self._modeName, self._active)
        if self._active:
            commands.activateMode(self._modeName)
        else:
            commands.deactivateMode(self._modeName)
            self.updateMargins(False)

        commands.redraw()
        commands.sendInternalEvent("mode-toggles", "%s|%s" % (self._modeName, self._active), "Mode")

    def updateMargins(self, activated):
        #  Below api push/pop is required because setMargins() causes
        #  margins-changed event to be sent which then triggers arbitrary mu
        #  code, which could of course allocate memory.
        runtime.gc.push_api(0)

        try:
            if activated:
                if self._whichMargin != -1:
                    margins = commands.margins()
                    margin_value = self.requiredMarginValue()
                    if margins[self._whichMargin] < margin_value:
                        margins[self._whichMargin] = margin_value
                        commands.setMargins(margins)
            else:
                if self._whichMargin != -1:
                    margins = [-1.0, -1.0, -1.0, -1.0]
                    margins[self._whichMargin] = 0
                    commands.setMargins(margins)
                    commands.setMargins(margins, True)
        finally:
            runtime.gc.pop_api()

    def updateBounds(self, min_point, max_point):
        self._x = min_point.x
        self._y = min_point.y
        self._w = max_point.x - self._x
        self._h = max_point.y - self._y
        if commands.isModeActive(self._modeName) and self._dragging:
            commands.setEventTableBBox(self._modeName, "global", min_point, max_point)
            self.updateMargins(True)

    def contains(self, point):
        if self._x <= point.x <= (self._x + self._w) and self._y <= point.y <= (self._y + self._h):
            return True
        return False

    def requiredMarginValue(self):
        size = commands.viewSize()
        if self._whichMargin == -1:
            return 0.0
        elif self._whichMargin == 0:
            return self._x + self._w
        elif self._whichMargin == 1:
            return size.x - self._x
        elif self._whichMargin == 2:
            return size.y - self._y
        elif self._whichMargin == 3:
            return self._y + self._h
        else:
            return 0.0

    def drawInMargin(self, which):
        self._whichMargin = which

    def layout(self, event):
        pass

    def render(self, event):
        pass
