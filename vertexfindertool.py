# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------

 Vertex Finder - A QGIS tool to get a vertex and marking it
                 by clicking in the map window

 Copyright (C) 2008  Cédric Möri

 EMAIL: cedric.moeri (at) bd.so.ch
 WEB  : www.sogis.ch

---------------------------------------------------------------------

 licensed under the terms of GNU GPL 2

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

---------------------------------------------------------------------
"""

from qgis.PyQt.QtCore import QPoint, QSettings, pyqtSignal
from qgis.PyQt.QtGui import QCursor, QPixmap, QColor
from qgis.gui import QgsMapTool, QgsMessageViewer, QgsVertexMarker
from qgis.core import QgsSnappingUtils, QgsPointLocator


# Vertex Finder Tool class
class VertexFinderTool(QgsMapTool):

    vertexFound = pyqtSignal(list)

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.marker = None
        # Our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #FFFFFF",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.     .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.     .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):
        # Get the click
        x = event.pos().x()
        y = event.pos().y()

        layer = self.canvas.currentLayer()

        if layer is not None:
            # something to store the result
            snapResult = None

            # The clicked point is our starting point
            startingPoint = QPoint(x, y)

            # We need a snapper, so we use the MapCanvas snapper
            snapper = self.canvas.snappingUtils()

            # We snap to the current layer (we don't have exclude points and use the tolerances
            # from the qgis properties)
            result = snapper.snapToCurrentLayer(startingPoint, QgsPointLocator.Vertex)

            # So if we have found a vertex
            if result != []:
                snapResult = result[0]
            # else:
                # Fix/workaround for broken snapper (Bug in 2.8 see ticket #12631)
                # try:
                #    utils = self.canvas.snappingUtils()
                #    SegmentLocator = utils.snapToCurrentLayer(startingPoint, 1)

                #    if SegmentLocator.isValid():
                #        snapResult = QgsSnappingResult()

                # VertexCoord are given in crs of the project
                #        vertexCoords = snapResult.snappedVertex  = SegmentLocator.point()
                #        vertexNr = snapResult.snappedVertexNr = SegmentLocator.vertexIndex()
                #        geometry = snapResult.snappedAtGeometry = SegmentLocator.featureId()
                #        layer = snapResult.layer = SegmentLocator.layer()

                # except AttributeError:
                #    self.showSettingsWarning()
                #    return

            if snapResult is not None:
                # We like to mark the vertex that is choosen, so we build a vertex marker...
                self.marker = QgsVertexMarker(self.canvas)

                # We have to know about the standard vertex marker, so we may use an other one
                settings = QSettings()
                settingsLabel = "/Qgis/digitizing/marker_style"
                markerType = settings.value(settingsLabel)
                if markerType == "Cross":
                    self.marker.setIconType(3)
                    self.marker.setColor(QColor(255, 255, 0))
                else:
                    self.marker.setIconType(2)
                    self.marker.setColor(QColor(255, 0, 0))

                self.marker.setIconSize(10)
                self.marker.setPenWidth(2)

                # Mark the vertex
                self.marker.setCenter(snapResult.snappedVertex)

                # Tell the world about the vertex and the marker
                self.vertexFound.emit([snapResult, self.marker])

            else:
                # Warn about missing snapping tolerance if appropriate
                self.showSettingsWarning()

    def showSettingsWarning(self):
        # Get the setting for displaySnapWarning
        settings = QSettings()
        settingsLabel = "/UI/displaySnapWarning"
        displaySnapWarning = settings.value(settingsLabel)

        # Only show the warning if the setting is true
        if displaySnapWarning == 'true' or displaySnapWarning is None:
            m = QgsMessageViewer()
            m.setWindowTitle("Snap tolerance")
            m.setCheckBoxText("Don't show this message again")
            m.setCheckBoxVisible(True)
            m.setCheckBoxQSettingsLabel(settingsLabel)
            m.setMessageAsHtml( "<p>Could not snap vertex.</p><p>Have you set the tolerance in Settings > "
                                "Project Properties > General?</p>")
            m.showMessage()

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
