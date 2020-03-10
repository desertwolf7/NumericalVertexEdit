# -*- coding: latin1 -*-
#
# Copyright (C) Cédric Möri
# EMAIL: cmoe (at) geoing (dot) ch
# WEB  : www.geoing.ch
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
from numericalvertexedit import NumericalVertexEdit
def name():
  return "Numerical Vertex Edit"
def description():
  return "Allows to edit a vertex in a numeric way by clicking on it."
def version():
  return "Version 0.2.1"
def classFactory(iface):
  return NumericalVertexEdit(iface)
def qgisMinimumVersion():
  return "2.0"  
def author():
  return "Cédric Möri"
def email():
  return "cmoe@geoing.ch"
def icon():
  return "vector-edit-keyboard.png"
 
  
    
