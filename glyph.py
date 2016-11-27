"""

//
//  Glyphs and other drawing code not related to RV specifically
//

module: glyph {
use gl;
use glu;
use math;
use math_util;
use io;
use rvtypes;
use commands;
require gltext;
//
//  Higher order glyph functions
//
"""
import math
from OpenGL.GL import *
from OpenGL.GLU import gluOrtho2D

from rv import commands

import gltext
from .util import lerp, Color, BBox, TBox


class GlyphNamespace(object):
    class AbstractGlyph(object):
        def __init__(self, glyph):
            super(GlyphNamespace.AbstractGlyph, self).__init__()
            self.glyph = glyph

        def __call__(self, outline):
            return

        def __and__(self, other):
            """
            operator: & (Glyph; Glyph a, Glyph b)
            {
                \: (void; bool outline)
                {
                    a(outline);
                    b(outline);
                };
            }
            """
            return GlyphNamespace.GlyphJoiner(self, other)

    class GlyphJoiner(AbstractGlyph):
        def __init__(self, *glyphs):
            super(GlyphNamespace.GlyphJoiner, self).__init__(glyphs[0])
            self.glyphs = glyphs

        def __call__(self, outline):
            for glyph in self.glyphs:
                glyph(outline)

    class XformedGlyph(AbstractGlyph):
        def __init__(self, glyph, angle, translate=None, scale=1.0):
            super(GlyphNamespace.XformedGlyph, self).__init__(glyph)
            self.angle = angle
            self.scale = scale
            self.translate = translate or TBox(0, 0)

        def __call__(self, outline):
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glRotate(self.angle, 0, 0, 1)
            glScale(self.scale, self.scale, self.scale)
            if self.translate.x or self.translate.y:
                glTranslate(self.translate.x, self.translate.y, 0.0)
            self.glyph(outline)
            glPopMatrix()

    class ColoredGlyph(AbstractGlyph):
        def __init__(self, glyph, color):
            super(GlyphNamespace.ColoredGlyph, self).__init__(glyph)
            self.color = color

        def __call__(self, outline):
            glColor(self.color)
            self.glyph(outline)

    @classmethod
    def xformedGlyph(cls, glyph, translate=None, angle=0, scale=1.0):
        """
        \: xformedGlyph (Glyph; Glyph g, float angle, float scale=1.0)
        {
            \: (void; bool outline)
            {
                glMatrixMode(GL_MODELVIEW);
                glPushMatrix();
                glRotate(angle, 0, 0, 1);
                glScale(scale, scale, scale);
                g(outline);
                glPopMatrix();
            };
        }

        \: xformedGlyph (Glyph; Glyph g, Point tran, float angle, float scale=1.0)
        {
            \: (void; bool outline)
            {
                glMatrixMode(GL_MODELVIEW);
                glPushMatrix();
                glRotate(angle, 0, 0, 1);
                glScale(scale, scale, scale);
                glTranslate(tran.x, tran.y, 0.0);
                g(outline);
                glPopMatrix();
            };
        }
        """
        return cls.XformedGlyph(glyph=glyph, angle=angle, translate=translate, scale=scale)

    @classmethod
    def coloredGlyph(cls, glyph, color):
        """
        \: coloredGlyph (Glyph; Glyph g, Color c)
        {
            \: (void; bool outline)
            {
                glColor(c);
                g(outline);
            };
        }
        """
        return cls.ColoredGlyph(glyph=glyph, color=color)

    @classmethod
    def drawRect(cls, glenum, ax, ay, bx, by, cx, cy, dx, dy):
        """
        //
        //  Primitive glyph functions
        //

        \: drawRect (void; int glenum, Vec2 a, Vec2 b, Vec2 c, Vec2 d)
        {
            glBegin(glenum);
            glVertex(a);
            glVertex(b);
            glVertex(c);
            glVertex(d);
            glEnd();
        }
        """
        glBegin(glenum)
        glVertex(ax, ay)
        glVertex(bx, by)
        glVertex(cx, cy)
        glVertex(dx, dy)
        glEnd()

    @classmethod
    def drawCircleFan(cls, x, y, width, start, end, increment, outline=False):
        """
        \: drawCircleFan (void; float x, float y, float w,
                          float start, float end,
                          float ainc, bool outline = false)
        {
            let a0 = start * pi * 2.0,
                a1 = end * pi * 2.0;

            glBegin(if outline then GL_LINE_STRIP else GL_TRIANGLE_FAN);
            if (!outline) glVertex(x, y);

            for (float a = a0; a < a1; a+= ainc)
            {
                glVertex(sin(a) * w + x, cos(a) * w + y);
            }

            glVertex(sin(a1) * w + x, cos(a1) * w + y);
            glEnd();
        }
        """
        rad_start = start * math.pi * 2.0
        rad_end = end * math.pi * 2.0

        if outline:
            glBegin(GL_LINE_STRIP)
        else:
            glBegin(GL_TRIANGLE_FAN)
            glVertex(x, y)

        for x in range(int(rad_end / increment)):
            glVertex(math.sin(rad_start) * width + x, math.cos(rad_start) * width + y)
            rad_start += increment

        glVertex(math.sin(rad_end) * width + x, math.cos(end) * width + y)
        glEnd()

    @classmethod
    def triangleGlyph(cls, outline):
        """
        \: triangleGlyph (void; bool outline)
        {
            glBegin(if outline then GL_LINE_LOOP else GL_TRIANGLES);
            glVertex(-0.5, 0);
            glVertex(0.5, -0.5);
            glVertex(0.5, 0.5);
            glEnd();
        }
        """
        glBegin(GL_LINE_LOOP if outline else GL_TRIANGLES)
        glVertex(-0.5, 0)
        glVertex(0.5, -0.5)
        glVertex(0.5, 0.5)
        glEnd()

    @classmethod
    def circleGlyph(cls, outline):
        """
        \: circleGlyph (void; bool outline)
        {
            drawCircleFan(0, 0, 0.5, 0.0, 1.0, .3, outline);
        }
        """
        return cls.drawCircleFan(0, 0, 0.5, 0.0, 1.0, .3, outline)

    @classmethod
    def squareGlyph(cls, outline):
        """
        \: squareGlyph (void; bool outline)
        {
            glBegin(if outline then GL_LINE_LOOP else GL_QUADS);
            glVertex(-0.5, -0.5);
            glVertex(0.5, -0.5);
            glVertex(0.5, 0.5);
            glVertex(-0.5, 0.5);
            glEnd();
        }
        """
        glBegin(GL_LINE_LOOP if outline else GL_QUADS)
        glVertex(-0.5, -0.5)
        glVertex(0.5, -0.5)
        glVertex(0.5, 0.5)
        glVertex(-0.5, 0.5)
        glEnd()

    @classmethod
    def pauseGlyph(cls, outline):
        """
        \: pauseGlyph (void; bool outline)
        {
            glPushAttrib(GL_POLYGON_BIT);
            if (outline) glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
            glBegin(GL_QUADS);
            glVertex(-0.5, -0.5);
            glVertex(-0.1, -0.5);
            glVertex(-0.1, 0.5);
            glVertex(-0.5, 0.5);

            glVertex(0.1, -0.5);
            glVertex(0.5, -0.5);
            glVertex(0.5, 0.5);
            glVertex(0.1, 0.5);
            glEnd();
            glPopAttrib();
        }
        """
        glPushAttrib(GL_POLYGON_BIT)
        if outline:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBegin(GL_QUADS)
        glVertex(-0.5, -0.5)
        glVertex(-0.1, -0.5)
        glVertex(-0.1, 0.5)
        glVertex(-0.5, 0.5)

        glVertex(0.1, -0.5)
        glVertex(0.5, -0.5)
        glVertex(0.5, 0.5)
        glVertex(0.1, 0.5)
        glEnd()
        glPopAttrib()

    @classmethod
    def advanceGlyph(cls, outline):
        """
        \: advanceGlyph (void; bool outline)
        {
            glBegin(if outline then GL_LINE_LOOP else GL_TRIANGLES);
            glVertex(-0.5, 0);
            glVertex(0.2, -0.5);
            glVertex(0.2, 0.5);
            glEnd();

            glBegin(if outline then GL_LINE_LOOP else GL_QUADS);
            glVertex(0.3, -0.5);
            glVertex(0.5, -0.5);
            glVertex(0.5, 0.5);
            glVertex(0.3, 0.5);
            glEnd();
        }
        """
        glBegin(GL_LINE_LOOP if outline else GL_TRIANGLES)
        glVertex(-0.5, 0)
        glVertex(0.2, -0.5)
        glVertex(0.2, 0.5)
        glEnd()

        glBegin(GL_LINE_LOOP if outline else GL_QUADS)
        glVertex(0.3, -0.5)
        glVertex(0.5, -0.5)
        glVertex(0.5, 0.5)
        glVertex(0.3, 0.5)
        glEnd()

    @classmethod
    def rgbGlyph(cls, outline):
        """
        \: rgbGlyph (void; bool outline)
        {
            glColor(1,0,0,1); drawCircleFan(0, 0, 0.5, 0.0, 0.33, .3, outline);
            glColor(0,1,0,1); drawCircleFan(0, 0, 0.5, 0.33, 0.66, .3, outline);
            glColor(0,0,1,1); drawCircleFan(0, 0, 0.5, 0.66, 1.0, .3, outline);
        }
        """
        glColor(1, 0, 0, 1)
        cls.drawCircleFan(0, 0, 0.5, 0.0, 0.33, .3, outline)
        glColor(0, 1, 0, 1)
        cls.drawCircleFan(0, 0, 0.5, 0.33, 0.66, .3, outline)
        glColor(0, 0, 1, 1)
        cls.drawCircleFan(0, 0, 0.5, 0.66, 1.0, .3, outline)

    @classmethod
    def drawXGlyph(cls, outline):
        """
        \: drawXGlyph (void; bool outline)
        {
            // Yeah, this is a little weird
            drawCloseButton(0, 0, 0.75, Color(.3,.2,0,1), Color(1,.6,0,1));
        }
        """
        cls.drawCloseButton(0, 0, 0.75, Color(0.3, 0.2, 0, 1), Color(1, 0.6, 0, 1))

    @classmethod
    def circleLerpGlyph(cls, start, outline):
        """
        \: circleLerpGlyph (void; float start, bool outline)
        {
            let ch = 1;

            for (float q = ch; q >= start; q *= 0.9)
            {
                let a = math.cbrt(1.0 - q/ch);
                glColor(Color(.2, 1, 1, 1) * a);
                drawCircleFan(0, 0, q, 0.0, 1.0, .1, true);
            }
        }
        """
        def cube_root(v):
            return v ** (1. / 3)

        check = 1
        current_value = 1
        while current_value >= start:
            var = 1.0 - (current_value / check)
            scalar = cube_root(var)
            glColor(Color(.2, 1, 1, 1) * scalar)
            cls.drawCircleFan(0, 0, current_value, 0.0, 1.0, .1, True)
            current_value *= 0.9

    @classmethod
    def tformCircle(cls, outline):
        """
        \: tformCircle (void; bool outline)
        {
            glMatrixMode(GL_MODELVIEW);
            glPushMatrix();
            glScale(0.2333, 0.2333, 0.2333);
            circleGlyph(outline);
            glPopMatrix();
        }
        """
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glScale(0.2333, 0.2333, 0.2333)
        cls.circleGlyph(outline)
        glPopMatrix()

    @classmethod
    def tformTriangle(cls, angle, outline):
        """
        \: tformTriangle (void; float angle, bool outline)
        {
            glMatrixMode(GL_MODELVIEW);
            glPushMatrix();
            glRotate(angle, 0, 0, 1);
            glScale(0.25, 0.25, 0.25);
            glTranslate(-1.3, 0.0, 0.0);
            triangleGlyph(outline);
            glPopMatrix();
        }
        """
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glRotate(angle, 0, 0, 1)
        glScale(0.25, 0.25, 0.25)
        glTranslate(-1.3, 0.0, 0.0)
        cls.triangleGlyph(outline)
        glPopMatrix()

    @classmethod
    def translateIconGlyph(cls, outline):
        """
        \: translateIconGlyph (void; bool outline)
        {
            tformCircle(outline);

            for (float a = 0.0; a <= 360.0; a += 90.0)
            {
                tformTriangle(a, outline);
            }
        }
        """
        cls.tformCircle(outline)
        current_angle = 0.0
        _max = 360.0
        inc = 90.0
        for count in range(int(_max / inc)):
            cls.tformTriangle(current_angle, outline)
            current_angle += (count * inc)

    @classmethod
    def translateXIconGlyph(cls, outline):
        """
        \: translateXIconGlyph (void; bool outline)
        {
            tformCircle(outline);

            for (float a = 90.0; a <= 360.0; a += 180.0)
            {
                tformTriangle(a, outline);
            }
        }
        """
        cls.tformCircle(outline)
        current_angle = 90.0
        _max = 360.0
        inc = 180.0
        for count in range(int(_max / inc)):
            cls.tformTriangle(current_angle, outline)
            current_angle += (count * inc)

    @classmethod
    def translateYIconGlyph(cls, outline):
        """
        \: translateYIconGlyph (void; bool outline)
        {
            tformCircle(outline);

            for (float a = 0.0; a <= 360.0; a += 180.0)
            {
                tformTriangle(a, outline);
            }
        }
        """
        cls.tformCircle(outline)
        current_angle = 0.0
        _max = 360.0
        inc = 180.0
        for count in range(int(_max / inc)):
            cls.tformTriangle(current_angle, outline)
            current_angle += (count * inc)

    @classmethod
    def lower_bounds(cls, array, n):
        """
        \: lower_bounds (int; int[] array, int n)
        {
            \: f (int; int[] array, int n, int i, int i0, int i1)
            {
                if (array[i] <= n)
                {
                    if (i+1 == array.size() || array[i+1] > n)
                    {
                        return i;
                    }
                    else
                    {
                        return f(array, n, (i + i1) / 2, i, i1);
                    }
                }
        
                if i == 0 then -1 else f(array, n, (i + i0) / 2, i0, i);
            }
        
            f(array, n, array.size() / 2, 0, array.size());
        }
        """
        def get_bounds(arr, num, middle_index, previous_index, end_index):
            if len(arr) >= middle_index and arr[middle_index] <= num:
                if middle_index+1 == len(arr) or arr[middle_index+1] > num:
                    return middle_index
                else:
                    return get_bounds(arr, num, (middle_index + end_index) / 2, middle_index, end_index)

            if middle_index == 0:
                return -1
            else:
                return get_bounds(arr, num, (middle_index + previous_index) / 2, previous_index, middle_index)

        return get_bounds(array, n, len(array) / 2, 0, len(array))

    @classmethod
    def drawTextWithCartouche(cls, x, y, text, size, text_color, bg_color, glyph=None, glyph_color=None):
        """
        \: drawTextWithCartouche (BBox; float x, float y, string text,
                                  float textsize, Color textcolor,
                                  Color bgcolor,
                                  Glyph g = nil,
                                  Color gcolor = Color(.2,.2,.2,1))
        {
            gltext.size(textsize);
            if (g neq nil) text = "   " + text;

            let b = gltext.bounds(text),
                w = b[2] + b[0],
                a = gltext.ascenderHeight(),
                d = gltext.descenderDepth(),
                mx = (a - d) * .05,
                x0 = x - mx,
                x1 = x + w + mx,
                y0 = y + d - mx,
                y1 = y + a + mx,
                rad = (y1 - y0) * 0.5,
                ymid = (y1 + y0) * 0.5;

            //print("%s, %s, %s\n" % (a, d, b));

            glColor(bgcolor);
            glBegin(GL_POLYGON);
            glVertex(x0, y0);
            glVertex(x1, y0);
            glVertex(x1, y1);
            glVertex(x0, y1);
            glEnd();

            drawCircleFan(x0, ymid, rad, 0.5, 1.0, .3);
            drawCircleFan(x1, ymid, rad, 0.0, 0.5, .3);

            glColor(bgcolor * 0.8);
            glPushAttrib(GL_ENABLE_BIT);
            glEnable(GL_LINE_SMOOTH);
            glEnable(GL_BLEND);
            //glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
            glLineWidth(1.0);
            drawCircleFan(x0, ymid, rad, 0.5, 1.0, .3, true);
            drawCircleFan(x1, ymid, rad, 0.0, 0.5, .3, true);
            glBegin(GL_LINES);
            glVertex(x0, y0);
            glVertex(x1, y0);
            glVertex(x1, y1);
            glVertex(x0, y1);
            glEnd();

            if (g neq nil)
            {
                glColor(gcolor);
                draw(g, x, ymid, 0, rad, false);
                glEnable(GL_LINE_SMOOTH);
                glColor(gcolor * 0.8);
                draw(g, x, ymid, 0, rad, true);
            }


            glPopAttrib();

            gltext.color(textcolor);
            gltext.writeAt(x, y, text);

            return BBox(x0 - rad, y0, x1 + rad, y1);
        }
        """
        if glyph_color is None:
            glyph_color = Color(0.2, 0.2, 0.2, 1)

        gltext.size(size)
        if glyph is not None:
            text = "   " + text

        bounds = gltext.bounds(text)
        width = bounds[2] + bounds[0]
        ascender_height = gltext.ascenderHeight()
        decender_depth = gltext.descenderDepth()
        margin = (ascender_height - decender_depth) * 0.5
        x0 = x - margin
        x1 = x + width + margin
        y0 = y + decender_depth - margin
        y1 = y + ascender_height + margin
        rad = (y1 - y0) * 0.5
        y_middle = (y1 + y0) * 0.5

        glColor(bg_color)
        glBegin(GL_POLYGON)
        glVertex(x0, y0)
        glVertex(x1, y0)
        glVertex(x1, y1)
        glVertex(x0, y1)
        glEnd()

        cls.drawCircleFan(x0, y_middle, rad, 0.5, 1.0, .3)
        cls.drawCircleFan(x1, y_middle, rad, 0.0, 0.5, .3)

        glColor(bg_color * 0.8)
        glPushAttrib(GL_ENABLE_BIT)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(1.0)
        cls.drawCircleFan(x0, y_middle, rad, 0.5, 1.0, .3, True)
        cls.drawCircleFan(x1, y_middle, rad, 0.0, 0.5, .3, True)
        glBegin(GL_LINES)
        glVertex(x0, y0)
        glVertex(x1, y0)
        glVertex(x1, y1)
        glVertex(x0, y1)
        glEnd()

        if glyph is not None:
            glColor(glyph_color)
            cls.draw(glyph, x, y_middle, 0, rad, False)
            glEnable(GL_LINE_SMOOTH)
            glColor(glyph_color * 0.8)
            cls.draw(glyph, x, y_middle, 0, rad, True)
            
        glPopAttrib()
        gltext.color(text_color)
        gltext.writeAt(x, y, text)

        return BBox(x0 - rad, y0, x1 + rad, y1)

    @classmethod
    def setupProjection(cls, w, h):
        """
        \: setupProjection (void; float w, float h)
        {
            glMatrixMode(GL_PROJECTION);
            glLoadIdentity();
            gluOrtho2D(0.0, w-1, 0.0, h-1);
        
            glMatrixMode(GL_MODELVIEW);
            glLoadIdentity();
        }
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0.0, w - 1, 0.0, h - 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    @classmethod
    def fitTextInBox(cls, text, width, height):
        """
        \: fitTextInBox (int; string text, int w, int h)
        {
            int textSize = 64, lastUpperBound = 2048, lastLowerBound = 4;
            int bw, bh;
        
            if (text eq nil || text.size() == 0)
            {
                throw exception("ERROR: fitTextInBox: empty string.");
            }
        
            int count = 0;
            do
            {
                gltext.size(textSize);
                let b  = gltext.bounds(text);
                bw = b[0] + b[2];
                bh = b[1] + b[3];
                if (bw > w || bh > h)
                {
                    lastUpperBound = textSize;
                    textSize = (textSize + lastLowerBound)/2;
                }
                else
                {
                    lastLowerBound = textSize;
                    textSize = (textSize + lastUpperBound)/2;
                }
                count += 1;
            }
            while (bw > w || bh > h || (lastUpperBound - lastLowerBound) > 1);
        
            return textSize - 2;
        }
        
        """
        def bound_math(size, upper, lower):
            gltext.size(size)
            bounds = gltext.bounds(text)
            bwidth = bounds[0] + bounds[2]
            bheight = bounds[1] + bounds[3]
            if bwidth > width or bheight > height:
                upper = size
                size = (size + lower) / 2
            else:
                lower = size
                size = (size + upper) / 2
            return size, upper, lower, bwidth, bheight
        
        text_size = 64
        last_upper_bound = 2048
        last_lower_bound = 4
        
        if not text:
            raise Exception("ERROR: fitTextInBox: empty string.")
        
        count = 0
        result = bound_math(text_size, last_upper_bound, last_lower_bound)
        text_size, last_upper_bound, last_lower_bound, bound_height, bound_width = result

        while bound_width > width or bound_height > height or (last_upper_bound - last_lower_bound > 1):
            result = bound_math(text_size, last_upper_bound, last_lower_bound)
            text_size, last_upper_bound, last_lower_bound, bound_height, bound_width = result
            count += 1

        return text_size - 2

    @classmethod
    def fitNameValuePairsInBox(cls, pairs, margin, width, height):
        """
        \: fitNameValuePairsInBox (int;
                                   StringPair[] pairs,
                                   int margin, int w, int h)
        {
            int textSize = 64, lastUpperBound = 2048, lastLowerBound = 4;
            vector float[2] tbox;
        
            if (pairs.size() == 0)
            {
                throw exception("ERROR: fitNameValuePairsInBox: empty pairs.");
            }
        
            int count = 0;
            do
            {
                gltext.size(textSize);
                tbox = nameValuePairBounds(pairs, margin)._0;
                if (tbox.x > w || tbox.y > h)
                {
                    lastUpperBound = textSize;
                    textSize = (textSize + lastLowerBound)/2;
                }
                else
                {
                    lastLowerBound = textSize;
                    textSize = (textSize + lastUpperBound)/2;
                }
                count += 1;
            }
            while (tbox.x > w || tbox.y > h || (lastUpperBound - lastLowerBound) > 1);
        
            return textSize - 2;
        }
        
        """
        def pair_bounds(size, title_names, prev_lower_bound, prev_upper_bound, w, h):
            gltext.size(size)
            _pair_bound = cls.nameValuePairBounds(title_names, margin)
            if _pair_bound:
                box = _pair_bound[0]
            else:
                raise Exception("ERROR: fintNameValuePairsInBox: nameValuePairBounds empty.")
            
            if box.x > w or box.y > h:
                prev_upper_bound = size
                size = (size + prev_lower_bound) / 2
            else:
                prev_lower_bound = size
                size = (size + prev_upper_bound) / 2
            
            return size, prev_lower_bound, prev_upper_bound, box

        text_size = 64
        last_upper_bound = 2048
        last_lower_bound = 4
                
        if not len(pairs):
            raise Exception("ERROR: fitNameValuePairsInBox: empty pairs.")
        
        result = pair_bounds(text_size, pairs, last_lower_bound, last_upper_bound, width, height)
        text_size, last_lower_bound, last_upper_bound, tbox = result
        while tbox.x > width or tbox.y > height or (last_upper_bound - last_lower_bound > 1):

            result = pair_bounds(text_size, pairs, last_lower_bound, last_upper_bound, width, height)
            text_size, last_lower_bound, last_upper_bound, tbox = result
        
        return text_size - 2

    @classmethod
    def drawRoundedBox(cls, x0, y0, x1, y1, margin, bg, fg):
        """
        \: drawRoundedBox (void;
                           int x0, int y0,
                           int x1, int y1,
                           int m,
                           Color c,
                           Color oc)
        {
            glColor(c);
            glBegin(GL_QUADS);
            glVertex(x0, y0);
            glVertex(x1, y0);
            glVertex(x1, y1);
            glVertex(x0, y1);

            glVertex(x0 - m, y0 + m);
            glVertex(x0, y0 + m);
            glVertex(x0, y1 - m);
            glVertex(x0 - m, y1 - m);

            glVertex(x1, y0 + m);
            glVertex(x1 + m, y0 + m);
            glVertex(x1 + m, y1 - m);
            glVertex(x1, y1 - m);
            glEnd();

            drawCircleFan(x0, y0 + m, m, 0.5, 0.75, .3);
            drawCircleFan(x1, y0 + m, m, 0.25, 0.5, .3);
            drawCircleFan(x1, y1 - m, m, 0.0, 0.25, .3);
            drawCircleFan(x0, y1 - m, m, 0.75, 1.0, .3);

            glPushAttrib(GL_ENABLE_BIT);

            glColor(oc);
            glEnable(GL_LINE_SMOOTH);
            glEnable(GL_POLYGON_SMOOTH);
            glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
            glHint (GL_LINE_SMOOTH_HINT, GL_NICEST);
            glEnable(GL_BLEND);
            glLineWidth(3.0);

            drawCircleFan(x0, y0 + m, m, 0.5, 0.75, .3, true);
            drawCircleFan(x1, y0 + m, m, 0.25, 0.5, .3, true);
            drawCircleFan(x1, y1 - m, m, 0.0, 0.25, .3, true);
            drawCircleFan(x0, y1 - m, m, 0.75, 1.0, .3, true);

            glBegin(GL_LINES);
            glVertex(x0, y0);
            glVertex(x1, y0);
            glVertex(x1, y1);
            glVertex(x0, y1);
            glVertex(x0 - m, y0 + m);
            glVertex(x0 - m, y1 - m);
            glVertex(x1 + m, y0 + m);
            glVertex(x1 + m, y1 - m);
            glEnd();
            glLineWidth(1.0);
            glPopAttrib();
        }
        """
        glColor(bg)
        glBegin(GL_QUADS)
        glVertex(x0, y0)
        glVertex(x1, y0)
        glVertex(x1, y1)
        glVertex(x0, y1)

        glVertex(x0 - margin, y0 + margin)
        glVertex(x0, y0 + margin)
        glVertex(x0, y1 - margin)
        glVertex(x0 - margin, y1 - margin)

        glVertex(x1, y0 + margin)
        glVertex(x1 + margin, y0 + margin)
        glVertex(x1 + margin, y1 - margin)
        glVertex(x1, y1 - margin)
        glEnd()

        cls.drawCircleFan(x0, y0 + margin, margin, 0.5, 0.75, .3)
        cls.drawCircleFan(x1, y0 + margin, margin, 0.25, 0.5, .3)
        cls.drawCircleFan(x1, y1 - margin, margin, 0.0, 0.25, .3)
        cls.drawCircleFan(x0, y1 - margin, margin, 0.75, 1.0, .3)

        glPushAttrib(GL_ENABLE_BIT)

        glColor(fg)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_BLEND)
        glLineWidth(3.0)

        cls.drawCircleFan(x0, y0 + margin, margin, 0.5, 0.75, .3, True)
        cls.drawCircleFan(x1, y0 + margin, margin, 0.25, 0.5, .3, True)
        cls.drawCircleFan(x1, y1 - margin, margin, 0.0, 0.25, .3, True)
        cls.drawCircleFan(x0, y1 - margin, margin, 0.75, 1.0, .3, True)

        glBegin(GL_LINES)
        glVertex(x0, y0)
        glVertex(x1, y0)
        glVertex(x1, y1)
        glVertex(x0, y1)
        glVertex(x0 - margin, y0 + margin)
        glVertex(x0 - margin, y1 - margin)
        glVertex(x1 + margin, y0 + margin)
        glVertex(x1 + margin, y1 - margin)
        glEnd()
        glLineWidth(1.0)
        glPopAttrib()

    @classmethod
    def drawDropRegions(cls, w, h, x, y, margin, descriptors):
        """
        \: drawDropRegions (int;
                            int w,
                            int h,
                            int x,
                            int y,
                            int margin,
                            string[] descriptors)
        {
            let m  = margins(),
                bsize = (h - m[2] - m[3]) / descriptors.size(),
                inregion = -1;

            for_index (i; descriptors)
            {
                gltext.size(20);

                let y0 = bsize * i + margin + m[3],
                    x0 = m[0] + margin,
                    y1 = bsize * (i+1) - margin + m[3],
                    x1 = w - margin - m[1],
                    t  = descriptors[i],
                    b  = gltext.bounds(t),
                    tw = b[2] + b[0],
                    active = y >= y0 && y <= y1,
                    fg = if active then Color(1,1,1,1) else Color(.5, .5, .5, 1),
                    bg = Color(0, 0, 0, .85);

                drawRoundedBox(x0, y0, x1, y1, 10, bg, fg);

                if (active) inregion = i;

                gltext.color(fg);
                gltext.writeAt((x1 - x0 - tw) * .5 + x0,
                               math_util.lerp(y0, y1, 0.5),
                               t);
            }

            inregion;
        }
        """

        current_margins = commands.margins()
        base_size = (h - current_margins[2] - current_margins[3]) / len(descriptors)
        inregion = -1

        for index, descriptor in enumerate(descriptors):
            gltext.size(20)

            y0 = base_size * index + margin + current_margins[3]
            x0 = current_margins[0] + margin
            y1 = base_size * (index + 1) - margin + current_margins[3]
            x1 = w - margin - current_margins[1]

            bounds = gltext.bounds(descriptor)
            total_width = bounds[2] + bounds[0]
            active = y0 <= y <= y1
            fg = Color(1, 1, 1, 1) if active else Color(0.5, 0.5, 0.5, 1)
            bg = Color(0, 0, 0, 0.85)

            cls.drawRoundedBox(x0, y0, x1, y1, 10, bg, fg)
            if active:
                inregion = index

            gltext.color(fg)

            write_x = (x1 - x0 - total_width) * 0.5 + x0
            write_y = lerp(y0, y1, 0.5)

            gltext.writeAt(write_x, write_y, descriptor)
        return inregion

    @classmethod
    def nameValuePairBounds(cls, pairs, margin):
        """
        \: nameValuePairBounds (NameValueBounds; (string,string)[] pairs, int margin)
        {
            let nw      = 0,
                vw      = 0,
                h       = 0,
                a       = gltext.ascenderHeight(),
                d       = gltext.descenderDepth(),
                th      = a - d,
                x0      = -d,
                x1      = -d,
                y0      = -margin,
                y1      = margin,
                nbounds = float[4][](),
                vbounds = float[4][]();

            for_each (a; pairs)
            {
                let (name, value) = a,
                    bn            = gltext.bounds(name),
                    bv            = gltext.bounds(value);

                nbounds.push_back(bn);
                vbounds.push_back(bv);

                nw = max(nw, bn[2] + bn[0]);
                vw = max(vw, bv[2] + bv[1]);
                h += th;
            }

            x1 += nw + vw;
            y1 += h;

            (Vec2(x1-x0, y1-y0), nbounds, vbounds, nw);
        }

        """
        name_width = 0
        value_width = 0
        height = 0
        ascender_height = gltext.ascenderHeight()
        descender_depth = gltext.descenderDepth()
        text_height = ascender_height - descender_depth
        x0 = - descender_depth
        x1 = x0
        y0 = -margin
        y1 = margin
        name_bounds = []
        value_bounds = []

        for pair in pairs:
            name, value = pair
            bounds_name = gltext.bounds(name)
            bounds_value = gltext.bounds(value)

            name_bounds.append(bounds_name)
            value_bounds.append(bounds_value)
            name_width = max([name_width, bounds_name[2] + bounds_name[0]])
            value_width = max([value_width, bounds_value[2] + bounds_value[0]])
            height += text_height

        x1 += (name_width + value_width)
        y1 += height

        return TBox(x1-x0, y1-y0), name_bounds, value_bounds, name_width

    @classmethod
    def expandNameValuePairs(cls, pairs):
        """
        \: expandNameValuePairs (StringPair[]; StringPair[] pairs)
        {
            StringPair[] newPairs;

            \: reverse (string[]; string[] s)
            {
                string[] n;
                for (int i=s.size()-1; i >= 0; i--) n.push_back(s[i]);
                n;
            }

            for_each (p; pairs)
            {
                let (name, value) = p;
            //  Don't collapse multiple newlines
            value = regex.replace("\r\n", value, "\n");
            value = regex.replace("\n\n", value, "\n \n");
                let lines = string.split(value, "\n\r");

                if (lines.size() > 1)
                {
                    for_each (line; reverse(lines.rest()))
                    {
                        if (line != "") newPairs.push_back(StringPair("", line));
                    }

                    if (lines[0] != "") newPairs.push_back(StringPair(name, lines[0]));
                }
                else
                {
                    newPairs.push_back(p);
                }
            }

            newPairs;
        }
        """
        new_pairs = []

        for pair in pairs:
            pair_name, pair_value = pair
            pair_value = pair_value.replace("\r\n", "\n").replace("\n\n", "\n \n")

            lines = pair_value.split("\n\r")
            if lines:
                for line in reversed(lines[1:]):
                    if line:
                        new_pairs.append(("", line))
                if lines[0]:
                    new_pairs.append((pair_name, lines[0]))
            else:
                new_pairs.append(pair)
        return new_pairs

    @classmethod
    def drawNameValuePairs(cls, pairs, fg, bg, x, y, margin, maxw=0, maxh=0, minw=0, minh=0, no_box=False):
        """
        \: drawNameValuePairs (NameValueBounds;
                               StringPair[] pairs,
                               Color fg, Color bg,
                               int x, int y, int margin,
                               int maxw=0, int maxh=0,
                               int minw=0, int minh=0,
                               bool nobox=false)
        {
            m := margin;    // alias

            let (tbox, nbounds, vbounds, nw) = nameValuePairBounds(pairs, m);

            let vw      = 0,
                h       = 0,
                a       = gltext.ascenderHeight(),
                d       = gltext.descenderDepth(),
                th      = a - d;

            float
                x0      = x - d,
                y0      = y - m,
                x1      = tbox.x + x0,
                y1      = tbox.y + y0;

            let xs = x1 - x0,
                ys = y1 - y0;

            if (minw > 0 && xs < minw) x1 = x0 + minw;
            if (minh > 0 && ys < minh) y1 = y0 + minh;
            if (maxw > 0 && xs > maxw ) x1 = x0 + maxw;
            if (maxh > 0 && ys > maxh ) y1 = y0 + maxh;

            tbox.x = x1 - x0;   // adjust
            tbox.y = y1 - y0;

            glEnable(GL_BLEND);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

            if (!nobox) drawRoundedBox(x0, y0, x1, y1, m, bg, fg * Color(.5,.5,.5,.5));

            glColor(fg * Color(1,1,1,.25));
            glBegin(GL_LINES);
            glVertex(x + nw + m/4, y0 + m/2);
            glVertex(x + nw + m/4, y1 - m/2);
            glEnd();

            for_index (i; pairs)
            {
                let (n, v)  = pairs[i],
                    bn      = nbounds[i],
                    bv      = vbounds[i],
                    tw      = bn[2] + bn[0];

                gltext.color(fg - Color(0,0,0,.25));
                gltext.writeAt(x + (nw - tw), y, n);
                gltext.color(fg);
                gltext.writeAt(x + nw + m/2, y, v);
                y += th;
                //if (i == s - 3) y+= m/2;
            }

            glDisable(GL_BLEND);

            (tbox, nbounds, vbounds, nw);
        }

        """

        margin_copy = margin
        tbox, name_bounds, value_bounds, name_width = cls.nameValuePairBounds(pairs, margin_copy)

        ascender_height = gltext.ascenderHeight()
        descender_depth = gltext.descenderDepth()
        text_height = ascender_height - descender_depth

        x0 = x - descender_depth
        y0 = y - margin_copy
        x1 = tbox.x + x0
        y1 = tbox.y + y0

        x_size = x1 - x0
        y_size = y1 - y0

        if 0 < minw and x_size < minw:
            x1 = x0 + minw
        if 0 < minh and y_size < minh:
            y1 = y0 + minh
        if 0 < maxw < x_size:
            x1 = x0 + maxw
        if 0 < maxh < y_size:
            y1 = y0 + maxh

        tbox.x = x1 - x0
        tbox.y = y1 - y0

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        if not no_box:
            cls.drawRoundedBox(x0, y0, x1, y1, margin_copy, bg, fg * Color(0.5, 0.5, 0.5, 0.5))
        glColor(fg * Color(1, 1, 1, 0.25))
        glBegin(GL_LINES)
        glVertex(x + name_width + margin_copy / 4, y0 + margin_copy / 2)
        glVertex(x + name_width + margin_copy / 4, y1 + margin_copy / 2)
        glEnd()

        for index, pair in enumerate(pairs):
            name, value = pair
            bounds_name = name_bounds[index]
            text_width = bounds_name[2] + bounds_name[0]

            gltext.color(fg - Color(0, 0, 0, 0.25))
            gltext.writeAt(x + (name_width - text_width), y, name)
            gltext.color(fg)
            gltext.write(x + name_width + margin_copy/2, y, value)
            y += text_height
            # if (index == s - 3):
            #     y += margin_copy/2

        glDisable(GL_BLEND)
        return tbox, name_bounds, value_bounds, name_width

    @classmethod
    def drawCloseButton(cls, x, y, radius, bg, fg):
        """
        \: drawCloseButton (void; float x, float y, float radius,
                            Color bg, Color fg)
        {
            let r2 = radius / 2;

            glEnable(GL_BLEND);
            glEnable(GL_LINE_SMOOTH);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
            glLineWidth(2.0);
            glColor(bg);
            drawCircleFan(x, y, radius, 0, 1, .3);
            glColor(fg);
            drawCircleFan(x, y, radius, 0, 1, .3, true);

            glBegin(GL_LINES);
            glVertex(x - r2, y - r2);
            glVertex(x + r2, y + r2);
            glVertex(x - r2, y + r2);
            glVertex(x + r2, y - r2);
            glEnd();
        }
        """

        half_radius = radius / 2

        glEnable(GL_BLEND)
        glEnable(GL_LINE_SMOOTH)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2.0)
        glColor(bg)
        cls.drawCircleFan(x, y, radius, 0, 1, .3)
        glColor(fg)
        cls.drawCircleFan(x, y, radius, 0, 1, .3, True)

        glBegin(GL_LINES)
        glVertex(x - half_radius, y - half_radius)
        glVertex(x + half_radius, y + half_radius)
        glVertex(x - half_radius, y + half_radius)
        glVertex(x + half_radius, y - half_radius)
        glEnd()

    @classmethod
    def draw(cls, glyph, x, y, angle, size, outline):
        """
        \: draw (Glyph g, float x, float y, float angle, float size, bool outline)
        {
            glMatrixMode(GL_MODELVIEW);
            glPushMatrix();
            glLoadIdentity();
            glTranslate(x, y, 0);
            glRotate(angle, 0, 0, 1);
            glScale(size, size, size);
            g(outline);
            glPopMatrix();
        }
        """
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glTranslate(x, y, 0)
        glRotate(angle, 0, 0, 1)
        glScale(size, size, size)
        glyph(outline)
        glPopMatrix()
        pass
