# -*- coding: latin1 -*-
#---------------------------------------------------------------------
# 
# Numerical Vertex Edit - A QGIS plugin to get the coordinates of a 
#                         vertex in a dialog by clicking in the map 
#                         window. It allwos then to change the coordinates 
#                         and moves the vertex to the given coordinates
#
# Copyright (C) 2008  Cédric Möri
#
# EMAIL: cedric.moeri (at) bd.so.ch
# WEB  : www.sogis.ch
#
#---------------------------------------------------------------------
# 
# licensed under the terms of GNU GPL 2
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 
#---------------------------------------------------------------------

# Import the PyQt and the QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

#Import own tools
from vertexfindertool import VertexFinderTool

import os, sys


# initialize Qt resources from file resources.py
import resources

# Our main class for the plugin
class NumericalVertexEdit:

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface
    self.canvas = self.iface.mapCanvas()
    self.QgisVersion = str(QGis.QGIS_VERSION)
    self.undoAvailable = None
    
    #The undo/redo Stack is only available at qgis version 1.2.0 or higher
    #so we check for it 
    if int(self.QgisVersion[0]) == 1:
      if int(self.QgisVersion[2]) >= 2: 
        self.undoAvailable = True
    else:
      self.undoAvailable = False
    if int(self.QgisVersion[0] > 1):
      self.undoAvailable = True
  
  def initGui(self):
    
    mc = self.canvas
    layer = mc.currentLayer()
      
    # Create action that will start plugin configuration
    self.action = QAction(QIcon(":/plugins/numericalVertexEdit/vector-edit-keyboard.png"), "Numerical Vertex Edit", self.iface.mainWindow())
    self.action.setEnabled(False)
    self.action.setCheckable(True)
    
    #Connect to signals for button behaviour
    QObject.connect(self.action, SIGNAL("triggered()"), self.run)
    QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer*)"), self.toggle)
    QObject.connect(mc, SIGNAL("mapToolSet(QgsMapTool*)"), self.deactivate)
    
    #Get the Tool
    self.tool = VertexFinderTool(self.canvas)
               
    # Add toolbar button and menu item
    self.iface.digitizeToolBar().addAction(self.action)
    self.iface.editMenu().addAction(self.action)
     
  def unload(self):
    self.iface.editMenu().removeAction(self.action)
    self.iface.digitizeToolBar().removeAction(self.action)
    
    
  def run(self):
    #Here we go...
    mc = self.canvas
    layer = mc.currentLayer()
    tool = mc.mapTool()
    
    #set VertexFinderTool as current tool
    mc.setMapTool(self.tool)
    self.action.setChecked(True)
    
    #Connect to the VFtool
    QObject.connect(self.tool, SIGNAL("vertexFound(PyQt_PyObject)"), self.moveVertex)
            
 
  def toggle(self):
    mc = self.canvas
    layer = mc.currentLayer()
    
    #Decide whether the plugin button/menu is enabled or disabled
    if layer <> None:
      if layer.isEditable():
        self.action.setEnabled(True)
        QObject.connect(layer,SIGNAL("editingStopped()"),self.toggle)
        QObject.disconnect(layer,SIGNAL("editingStarted()"),self.toggle)
      else:
        self.action.setEnabled(False)
        QObject.connect(layer,SIGNAL("editingStarted()"),self.toggle)
        QObject.disconnect(layer,SIGNAL("editingStopped()"),self.toggle)        
                
  def deactivate(self):
    mc = self.canvas
    layer = mc.currentLayer()
    
    #uncheck the button/menu and get rid off the VFtool signal
    self.action.setChecked(False)
    QObject.disconnect(self.tool, SIGNAL("vertexFound(PyQt_PyObject)"), self.moveVertex)

        
  def moveVertex(self,result):
    marker = result[1]
    snappingResult = result[0]
    
    #The vertex that is found by the tool:
    vertexCoords = snappingResult.snappedVertex #vertexCoord are given in crs of the project
    vertexNr = snappingResult.snappedVertexNr
    geometry = snappingResult.snappedAtGeometry
    layer = snappingResult.layer
    try:
      layerSrs = layer.srs() #find out the srs of the layer
    except AttributeError: #API version >1.8
      layerSrs = layer.crs() #find out the srs of the layer
    
    #Give a dialog with the current coords and ask for the new ones
    (input,ok) = QInputDialog.getText( self.iface.mainWindow(), "Move Vertex Feature", "Enter New Coordinates as 'xcoord,ycoord'",   QLineEdit.Normal, str( vertexCoords.x() ) + "," + str( vertexCoords.y() )) 
    if ok == False:
      #if we are aborting, we have to delete the marker
      self.canvas.scene().removeItem(marker)
      del marker
      return 0
    
    #find out which is the current crs of the project
    projectSrsEntry = QgsProject.instance().readEntry("SpatialRefSys","/ProjectCRSProj4String")
    projectSrs = QgsCoordinateReferenceSystem()
    projectSrs.createFromProj4(projectSrsEntry[0])
    
    #set up a coordinate transformation to transform the vertex coord into the srs of his layer
    transformer= QgsCoordinateTransform (projectSrs, layerSrs)
    #transformedPoint = transformer.transform(input.split( "," )[ 0 ].toDouble()[ 0 ],input.split( "," )[ 1 ].toDouble()[ 0 ])
    transformedPoint = transformer.transform(float(input.split( "," )[ 0 ]),float(input.split( "," )[ 1 ]))
     
    #if the transformation is successful, we move the vertex to his new place else we inform the user that there is something wrong
    if (type(transformedPoint.x()).__name__=='double' and type(transformedPoint.y()).__name__=='double') or (type(transformedPoint.x()).__name__=='float' and type(transformedPoint.y()).__name__=='float'):
      
      #if the undo/redo stack is available, we use it
      if self.undoAvailable:
        layer.beginEditCommand("Moved Vertex")
            #Now we move the vertex to the given coordinates 
      layer.moveVertex(transformedPoint.x(), transformedPoint.y(),geometry,vertexNr)
      #end of undo/redo stack (if available)
      if self.undoAvailable:
        layer.endEditCommand()
    else:
      QMessageBox.critical(self.iface.mainWindow(), "Error while transforming the vertex", "It's not possible to transform the coordinates you gave into the srs of this layer.")
  
    #Now refresh the map canvas 
    self.canvas.refresh()
    
    #At last we have to delete the marker
    self.canvas.scene().removeItem(marker)
    del marker
    
  
    
 
