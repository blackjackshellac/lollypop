# Copyright (c) 2014-2016 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, GLib, Gio

from lollypop.objects import Track
from lollypop.define import Lp


class RatingWidget(Gtk.Bin):
    """
        Rate widget
    """

    def __init__(self, object):
        """
            Init widget
            @param object as Track/Album
            @param is album as bool
        """
        Gtk.Bin.__init__(self)
        self._object = object
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Lollypop/RatingWidget.ui')
        builder.connect_signals(self)

        self._stars = []
        self._stars.append(builder.get_object('star0'))
        self._stars.append(builder.get_object('star1'))
        self._stars.append(builder.get_object('star2'))
        self._stars.append(builder.get_object('star3'))
        self._stars.append(builder.get_object('star4'))
        self._on_leave_notify(None, None)
        self.add(builder.get_object('widget'))

#######################
# PROTECTED           #
#######################
    def _on_enter_notify(self, widget, event):
        """
            On enter notify, change star opacity
            @param widget as Gtk.EventBox
            @param event as Gdk.Event
        """
        event_star = widget.get_children()[0]
        # First star is hidden (used to clear score)
        if event_star.get_opacity() == 0.0:
            found = True
        else:
            found = False
        for star in self._stars:
            star.set_opacity(0.2 if found else 0.8)
            if star == event_star:
                found = True

    def _on_leave_notify(self, widget, event):
        """
            On leave notify, change star opacity
            @param widget as Gtk.EventBox (can be None)
            @param event as Gdk.Event (can be None)
        """
        stars = self._object.get_popularity()
        if stars < 1:
            for i in range(5):
                self._stars[i].set_opacity(0.2)
        else:
            if stars >= 1:
                self._stars[0].set_opacity(0.8)
            else:
                self._stars[0].set_opacity(0.2)
            if stars >= 2:
                self._stars[1].set_opacity(0.8)
            else:
                self._stars[1].set_opacity(0.2)
            if stars >= 3:
                self._stars[2].set_opacity(0.8)
            else:
                self._stars[2].set_opacity(0.2)
            if stars >= 4:
                self._stars[3].set_opacity(0.8)
            else:
                self._stars[3].set_opacity(0.2)
            if stars >= 4.75:
                self._stars[4].set_opacity(0.8)
            else:
                self._stars[4].set_opacity(0.2)

    def _on_button_press(self, widget, event):
        """
            On button press, set album popularity
            @param widget as Gtk.EventBox
            @param event as Gdk.Event
        """
        if Lp().scanner.is_locked():
            return
        event_star = widget.get_children()[0]
        if event_star in self._stars:
            position = self._stars.index(event_star)
        else:
            position = -1
        pop = position + 1
        self._object.set_popularity(pop)
        # Save to tags if needed
        if Lp().settings.get_value('save-to-tags') and\
                GLib.find_program_in_path("kid3-cli") is not None and\
                isinstance(self._object, Track) and\
                not self._object.is_web:
            if pop == 0:
                value = 0
            elif pop == 1:
                value = 1
            elif pop == 2:
                value = 64
            elif pop == 3:
                value = 128
            elif pop == 4:
                value = 196
            else:
                value = 255
            path = GLib.filename_from_uri(self._object.uri)[0]
            try:
                bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
                proxy = Gio.DBusProxy.new_sync(
                                        bus, Gio.DBusProxyFlags.NONE, None,
                                        'org.gnome.Lollypop.Portal',
                                        '/org/gnome/LollypopPortal',
                                        'org.gnome.Lollypop.Portal', None)
                proxy.call_sync('SetPopularity',
                                GLib.Variant(
                                 '(is)', (value,
                                          path)),
                                Gio.DBusCallFlags.NO_AUTO_START,
                                500, None)
            except Exception as e:
                print("RatingWidget::_on_button_press():", e)
        return True
