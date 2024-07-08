from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt5.QtCore import QPoint
import pyqtgraph as pg
import numpy as np

class PlotGraphWidget(pg.PlotWidget):
    def __init__(self):
        super().__init__()

        # Style definitions (if needed)
        self.legendTextColor = (255, 255, 255, 255)  # white
        self.getViewBox().setMouseMode(pg.ViewBox.RectMode)

        # Get plot item for modifications
        self.graph = self.getPlotItem()

        # Initialize context menu and legend
        self.initContextMenu()
        self.initLegend()

        # Enable grid
        self.showGrid(x=True, y=True)

        # Connect center action
        self.center_action.triggered.connect(self.centerPlotHandler)

    def initLegend(self):
        self.legend = self.addLegend(self.legendTextColor)
        self.legend.setVisible(True)
        self.legend.anchor(itemPos=(1, 0), parentPos=(1, 0), offset=(-15, 12))

    def initContextMenu(self):
        # Disable unwanted menu items
        self.graph.vb.menu.actions()[3].setVisible(False)  # Mouse-Mode
        self.graph.ctrlMenu.actions()[0].setVisible(False)  # Plot-Options/Transform
        self.graph.ctrlMenu.actions()[1].setVisible(False)  # Plot-Options/DownSample
        self.graph.ctrlMenu.actions()[2].setVisible(False)  # Plot-Options/Average
        self.graph.ctrlMenu.actions()[5].setVisible(False)  # Plot-Options/Points
        self.graph.vb.scene().contextMenu[0].setVisible(False)  # Export

        # Create center action
        self.center_action = self.graph.vb.menu.addAction("Center")
        self.graph.vb.menu.addAction(self.center_action)

    def centerPlotHandler(self):
        # Define scaling factors
        x_scale_factor = 0.3
        y_scale_factor = 1.0  # only scale in y-direction

        # Get absolute position of context menu
        geo = self.graph.vb.menu.geometry()
        point_abs = QPoint(geo.x(), geo.y())
        point_rel = self.mapFromGlobal(point_abs)
        coords_where_clicked = self.graph.vb.mapSceneToView(point_rel)

        # Scale viewbox around clicked coordinates
        self.graph.vb.scaleBy(s=[x_scale_factor, y_scale_factor], center=coords_where_clicked)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle('Interactive Sine Wave Plot')
        self.setGeometry(100, 100, 800, 600)

        # Create the custom plot widget
        self.plot_widget = PlotGraphWidget()
        self.setCentralWidget(self.plot_widget)

        # Generate data for sine wave
        x = np.linspace(0, 10, 1000)
        y = np.sin(x)

        # Plot the sine wave
        self.plot_widget.plot(x, y, pen='b')

if __name__ == '__main__':
    app = QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec()
