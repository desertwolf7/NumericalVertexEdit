
#all: ui_pseudoDrawingAbout.py resources.py 
all: resources.py

clean:
	rm -f ui_*.py resources.py
	rm -f *.pyc

#ui_pseudoDrawingAbout.py: pseudoDrawingAbout.ui
#	pyuic4 -o ui_pseudoDrawingAbout.py pseudoDrawingAbout.ui
#	
#ui_nonSpatialTablesDialogCols.py: nonSpatialTablesDialogCols.ui
#	pyuic4 -o ui_nonSpatialTablesDialogCols.py nonSpatialTablesDialogCols.ui
#	
#ui_nonSpatialTablesRename.py: nonSpatialTablesRename.ui
#	pyuic4 -o ui_nonSpatialTablesRename.py nonSpatialTablesRename.ui
#
resources.py: resources.qrc
	pyrcc4 -o resources.py resources.qrc

