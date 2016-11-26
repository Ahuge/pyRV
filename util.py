def lerp(a, b, t):
    """
    math_util.lerp
    """
    return a + (b - a) * t


class Color(object):
    def __init__(self, r, g, b, a=None):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            for attr in [self.r, self.g, self.b, self.a]:
                attr *= other
        elif isinstance(other, Color):
            self.r *= other.r
            self.g *= other.g
            self.b *= other.b
            self.a *= other.a
        else:
            raise ValueError("Cannot multiply a Color against a %s" % type(other))
        return self


class TBox(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class BBox(object):
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1


class Configuration(object):
    def __init__(
            self,
            lastOpenDir           =     "",
            lastLUTDir            =     "",
            bg                    =     Color(0, 0, 0, 0),
            fg                    =     Color(0, 0, 0, 0),
            bgErr                 =     Color(0, 0, 0, 0),
            fgErr                 =     Color(0, 0, 0, 0),
            bgFeedback            =     Color(0, 0, 0, 0),
            fgFeedback            =     Color(0, 0, 0, 0),
            textEntryTextSize     =     0.0,
            inspectorTextSize     =     0.0,
            infoTextSize          =     0.0,
            wipeFade              =     0.0,
            wipeFadeProximity     =     0.0,
            wipeGrabProximity     =     0.0,
            wipeInfoTextSize      =     0.0,
            msFrameTextSize       =     0.0,
            tlFrameTextSize       =     0.0,
            tlBoundsTextSize      =     0.0,
            tlBoundsColor         =     Color(0, 0, 0, 0),
            tlRangeColor          =     Color(0, 0, 0, 0),
            tlCacheColor          =     Color(0, 0, 0, 0),
            tlCacheFullColor      =     Color(0, 0, 0, 0),
            tlInOutCapsColor      =     Color(0, 0, 0, 0),
            tlMarkedColor         =     Color(0, 0, 0, 0),
            tlSkipColor           =     Color(0, 0, 0, 0),
            tlSkipTextColor       =     Color(0, 0, 0, 0),
            matteColor            =     Color(0, 0, 0, 0),
            bgVCR                 =     Color(0, 0, 0, 0),
            fgVCR                 =     Color(0, 0, 0, 0),
            bgTlVCR               =     Color(0, 0, 0, 0),
            bgVCRButton           =     Color(0, 0, 0, 0),
            hlVCRButton           =     Color(0, 0, 0, 0),
            pdfReader             =     "",
            htmlReader            =     "",
            os                    =     "",
            bevelMargin           =     0,
            menuBarCreationFunc   =     None,
            renderImageSpace      =     (0, 0, 0, 0),
            renderViewSpace       =     (0, 0, 0, 0)
    ):

        super(Configuration, self).__init__()
        self.lastOpenDir = lastOpenDir
        self.lastLUTDir = lastLUTDir
        self.bg = bg
        self.fg = fg
        self.bgErr = bgErr
        self.fgErr = fgErr
        self.bgFeedback = bgFeedback
        self.fgFeedback = fgFeedback
        self.textEntryTextSize = textEntryTextSize
        self.inspectorTextSize = inspectorTextSize
        self.infoTextSize = infoTextSize
        self.wipeFade = wipeFade
        self.wipeFadeProximity = wipeFadeProximity
        self.wipeGrabProximity = wipeGrabProximity
        self.wipeInfoTextSize = wipeInfoTextSize
        self.msFrameTextSize = msFrameTextSize
        self.tlFrameTextSize = tlFrameTextSize
        self.tlBoundsTextSize = tlBoundsTextSize
        self.tlBoundsColor = tlBoundsColor
        self.tlRangeColor = tlRangeColor
        self.tlCacheColor = tlCacheColor
        self.tlCacheFullColor = tlCacheFullColor
        self.tlInOutCapsColor = tlInOutCapsColor
        self.tlMarkedColor = tlMarkedColor
        self.tlSkipColor = tlSkipColor
        self.tlSkipTextColor = tlSkipTextColor
        self.matteColor = matteColor
        self.bgVCR = bgVCR
        self.fgVCR = fgVCR
        self.bgTlVCR = bgTlVCR
        self.bgVCRButton = bgVCRButton
        self.hlVCRButton = hlVCRButton
        self.pdfReader = pdfReader
        self.htmlReader = htmlReader
        self.os = os
        self.bevelMargin = bevelMargin
        self.menuBarCreationFunc = menuBarCreationFunc
        self.renderImageSpace = renderImageSpace
        self.renderViewSpace = renderViewSpace
