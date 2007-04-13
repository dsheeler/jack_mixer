#!/usr/bin/env python
#
# This file is part of jack_mixer
#
# Copyright (C) 2006 Nedko Arnaudov <nedko@arnaudov.name>
#  
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.

import gtk

class meter(gtk.DrawingArea):
    def __init__(self, scale):
        gtk.DrawingArea.__init__(self)

        self.scale = scale

        self.connect("expose-event", self.on_expose)
        self.connect("size-request", self.on_size_request)
        self.connect("size_allocate", self.on_size_allocate)

        self.color_bg = gtk.gdk.Color(0,0,0)
        self.color_value = gtk.gdk.Color(int(65535 * 0.8), int(65535 * 0.7), 0)
        self.color_mark = gtk.gdk.Color(int(65535 * 0.2), int(65535 * 0.2), int(65535 * 0.2))
        self.width = 0
        self.height = 0

    def on_expose(self, widget, event):
        cairo_ctx = widget.window.cairo_create()

        # set a clip region for the expose event
        cairo_ctx.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cairo_ctx.clip()

        self.draw(cairo_ctx)

        return False

    def on_size_allocate(self, widget, allocation):
        #print allocation.x, allocation.y, allocation.width, allocation.height
        self.width = float(allocation.width)
        self.height = float(allocation.height)
        self.font_size = 10

    def on_size_request(self, widget, requisition):
        #print "size-request, %u x %u" % (requisition.width, requisition.height)
        requisition.width = 20
        return

    def invalidate_all(self):
        self.queue_draw_area(0, 0, int(self.width), int(self.height))

    def draw_background(self, cairo_ctx):
        cairo_ctx.set_source_color(self.color_bg)
        cairo_ctx.rectangle(0, 0, self.width, self.height)
        cairo_ctx.fill()

        cairo_ctx.set_source_color(self.color_mark)
        cairo_ctx.select_font_face("Fixed")
        cairo_ctx.set_font_size(self.font_size)
        glyph_width = self.font_size * 3 / 5 # avarage glyph ratio
        for mark in self.scale.get_marks():
            mark_position = int(self.height * (1 - mark.scale))
            cairo_ctx.move_to(0, mark_position)
            cairo_ctx.line_to(self.width, mark_position)
            cairo_ctx.stroke()
            x_correction = self.width / 2 - glyph_width * len(mark.text) / 2
            cairo_ctx.move_to(x_correction, mark_position - 2)
            cairo_ctx.show_text(mark.text)

    def draw_value(self, cairo_ctx, value, x, width):
        #return
        cairo_ctx.set_source_color(self.color_value)
        cairo_ctx.rectangle(x, self.height * (1 - value), width, self.height * value)
        cairo_ctx.fill()

    def set_scale(self, scale):
        self.scale = scale
        self.invalidate_all()

class mono(meter):
    def __init__(self, scale):
        meter.__init__(self, scale)
        self.value = 0.0

    def draw(self, cairo_ctx):
        self.draw_background(cairo_ctx)
        self.draw_value(cairo_ctx, self.value, self.width/4.0, self.width/2.0)

    def set_value(self, value):
        if value != self.value:
            self.value = self.scale.db_to_scale(value)
            self.invalidate_all()

class stereo(meter):
    def __init__(self, scale):
        meter.__init__(self, scale)
        self.left = 0.0
        self.right = 0.0

    def draw(self, cairo_ctx):
        self.draw_background(cairo_ctx)
        self.draw_value(cairo_ctx, self.left, self.width/5.0, self.width/5.0)
        self.draw_value(cairo_ctx, self.right, self.width/5.0 * 3.0, self.width/5.0)

    def set_values(self, left, right):
        if left != self.left or right != self.right:
            self.left = self.scale.db_to_scale(left)
            self.right = self.scale.db_to_scale(right)
            self.invalidate_all()