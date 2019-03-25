import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from threading import Thread
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import tomograph
from skimage.io import imread
from skimage.transform import rescale


class Interface(QMainWindow):

    def __init__(self):
        super().__init__()
        self.margin_left = self.margin_top = 0
        self.window_width = 1250
        self.window_height = 700
        self.first_row_top_margin_label = 5
        self.first_row_top_margin_input = 30
        self.theta_input = None
        self.detectors_quantity_input = None
        self.span_input = None
        self.interactive_mode_checkbox = None
        self.image_select = None
        self.filter_select = None
        self.run_button = None
        self.slider = None
        self.plot = None
        self.scanner = None
        self.is_interactive = True
        self.result_table = None
        self.image_file_name = None
        self.current_row = 0
        self.is_working = False

        self.setWindowTitle('Tomograph simulator')
        self.setGeometry(self.margin_left, self.margin_top, self.window_width, self.window_height)

        # plots_area init
        self.plot = PlotCanvas(self)

        self.init_result_table()

        self.init_interaction()

    def init_result_table(self):
        self.result_table = QTableWidget(self)
        self.result_table.move(30, 82)
        self.result_table.setRowCount(1)
        self.result_table.setColumnCount(6)
        self.result_table.setHorizontalHeaderLabels(["File", "Theta", "Detectors", "Span", "Filter", "MSE"])
        self.result_table.setColumnWidth(0, 120)
        self.result_table.setColumnWidth(1, 50)
        self.result_table.setColumnWidth(2, 60)
        self.result_table.setColumnWidth(3, 50)
        self.result_table.setColumnWidth(4, 100)
        self.result_table.setColumnWidth(5, 80)
        self.result_table.setFixedWidth(492)
        self.result_table.setFixedHeight(275)

    def init_interaction(self):
        self.add_theta_input()
        self.add_detectors_quantity_input()
        self.add_span_input()
        self.add_filter_select()
        self.add_interactive_mode_checkbox()
        self.add_image_select()
        self.add_run_button()
        self.add_slider()
        self.add_labels()

    def add_theta_input(self):
        x = Interface.get_x_window_position(0)
        theta_label = QLabel('Theta value [deg]:', self)
        theta_label.move(x, self.first_row_top_margin_label)
        self.theta_input = QDoubleSpinBox(self)
        self.theta_input.setSingleStep(0.05)
        self.theta_input.setRange(0.05, 360)
        self.theta_input.setSingleStep(0.05)
        self.theta_input.setValue(0.5)
        self.theta_input.move(x, self.first_row_top_margin_input)

    def add_detectors_quantity_input(self):
        x = Interface.get_x_window_position(1)
        detectors_quantity_label = QLabel("Detectors number:", self)
        detectors_quantity_label.move(x, self.first_row_top_margin_label)
        self.detectors_quantity_input = QSpinBox(self)
        self.detectors_quantity_input.setRange(1, 3000)
        self.detectors_quantity_input.setValue(100)
        self.detectors_quantity_input.move(x, self.first_row_top_margin_input)

    def add_span_input(self):
        x = Interface.get_x_window_position(2)
        span_label = QLabel("Detectors span [deg]:", self)
        span_label.move(x, self.first_row_top_margin_label)
        self.span_input = QSpinBox(self)
        self.span_input.setRange(1, 360)
        self.span_input.setValue(180)
        self.span_input.move(x, self.first_row_top_margin_input)

    def add_filter_select(self):
        x = Interface.get_x_window_position(3)
        filter_label = QLabel("Select filter:", self)
        filter_label.move(x, self.first_row_top_margin_label)
        self.filter_select = QComboBox(self)
        self.filter_select.addItems(['None', 'Ramp', 'Shepp-Logan', 'Cosine', 'Hamming', 'Han'])
        self.filter_select.move(x, self.first_row_top_margin_input)

    def add_interactive_mode_checkbox(self):
        x = Interface.get_x_window_position(4)
        self.interactive_mode_checkbox = QCheckBox('Interactive\nmode', self)
        self.interactive_mode_checkbox.setChecked(self.is_interactive)
        self.interactive_mode_checkbox.move(x, self.first_row_top_margin_input)

    def add_image_select(self):
        x = Interface.get_x_window_position(5)
        self.image_select = QPushButton('Select image', self)
        self.image_select.clicked.connect(self.on_image_select_clicked)
        self.image_select.move(x, self.first_row_top_margin_input)

    def add_run_button(self):
        x = Interface.get_x_window_position(6)
        self.run_button = QPushButton('Run', self)
        self.run_button.setDisabled(True)
        self.run_button.clicked.connect(self.run_task)
        self.run_button.move(x, self.first_row_top_margin_input)

    def add_slider(self):
        self.slider = QSlider(Qt.Vertical, self)
        self.slider.move(924, 82)
        self.slider.setTickInterval(180)
        self.slider.setSingleStep(1)
        self.slider.setFixedHeight(580)
        self.slider.setFixedWidth(30)
        self.slider.setDisabled(True)
        self.slider.setTickPosition(QSlider.NoTicks)
        self.slider.valueChanged.connect(self.on_slider_value_change)

    def add_labels(self):
        result_table_label = QLabel('Results:', self)
        result_table_label.setFixedWidth(200)
        result_table_label.move(30, 58)
        image_label = QLabel('Original image:', self)
        image_label.setFixedWidth(200)
        image_label.move(617, 58)
        image_reconstructed_label = QLabel('Reconstructed image:', self)
        image_reconstructed_label.setFixedWidth(200)
        image_reconstructed_label.move(617, 360)
        sinogram_label = QLabel('Sinogram:', self)
        sinogram_label.setFixedWidth(200)
        sinogram_label.move(1078, 58)

    def on_image_select_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select image', '', "Images (*.png *.jpeg *.jpg *.bmp)")
        if file_path:
            image = imread(file_path, as_gray=True)
            #image = rescale(image, scale=0.4)
            self.plot.image = make_image_square(image)
            self.plot.ax1.imshow(self.plot.image, cmap="gray")
            self.plot.draw()
            self.image_file_name = file_path.split("/")[-1]
            self.run_button.setDisabled(False)

    def on_slider_value_change(self):
        value = self.slider.value()
        self.scanner.get_snapshot(value)

    def add_row_to_table(self, file, theta, detectors, span, filter_type, mse):
        for i, cell_value in enumerate([file, theta, detectors, span, filter_type, mse]):
            self.result_table.setItem(self.current_row, i, QTableWidgetItem(str(cell_value)))
        self.current_row += 1
        self.result_table.setRowCount(self.current_row + 1)

    def run_task(self):
        self.slider.setDisabled(True)
        self.run_button.setDisabled(True)
        self.image_select.setDisabled(True)
        self.plot.update_mse(0)
        self.is_interactive = self.interactive_mode_checkbox.isChecked()
        tomograph.params.set_parameters(self.plot.image, self.theta_input.value(),
                                        self.detectors_quantity_input.value(),
                                        self.span_input.value(), self.filter_select.currentText())
        self.scanner = tomograph.Tomograph(tomograph.params, self.plot, self.is_interactive)
        self.plot.initialize_scan(self.scanner, self.is_interactive)
        if self.is_interactive:
            Thread(target=lambda: self.scanner.image_reconstruction(self.on_finish_task)).start()
        else:
            self.scanner.image_reconstruction(self.on_finish_task)

    def on_finish_task(self):
        self.run_button.setDisabled(False)
        self.image_select.setDisabled(False)
        if self.is_interactive:
            self.slider.setDisabled(False)
        else:
            self.plot.ax2.imshow(self.scanner.sinogram, cmap="gray", animated=True)
            self.plot.ax2.invert_yaxis()
            self.plot.ax3.imshow(self.scanner.image_reconstructed, cmap="gray", animated=True)
            self.plot.ax_err.plot(self.scanner.mse_data, 'b')
            self.plot.draw()
            self.plot.update_mse(self.scanner.mse_error)
        self.add_row_to_table(self.image_file_name, tomograph.params.theta_deg, tomograph.params.detector_quantity,
                              tomograph.params.span_deg, tomograph.params.filter_type,
                              round(self.scanner.mse_error, 10))

    @staticmethod
    def get_x_window_position(index):
        return index * 120 + 30


class PlotCanvas(FigureCanvas):
    def __init__(self, interface):
        self.fig, _ = plt.subplots(2, 5, figsize=(14, 8))
        plt.tight_layout(pad=7, h_pad=0, w_pad=-3.3)
        plt.subplot2grid((2, 5), (0, 0), colspan=2, rowspan=1).set_axis_off()
        self.ax1 = plt.subplot2grid((2, 5), (0, 2), rowspan=1, colspan=2)  # image
        self.ax2 = plt.subplot2grid((2, 5), (0, 4), rowspan=2, colspan=1)  # sinogram
        self.ax3 = plt.subplot2grid((2, 5), (1, 2), rowspan=1, colspan=2)  # image_reconstructed
        self.ax_err = plt.subplot2grid((2, 5), (1, 0), colspan=2, rowspan=1)
        self.im2 = self.im3 = self.im_err = None
        self.ani2 = self.ani3 = self.ani_err = None
        self.scanner = None
        self.image = None
        self.mse_label = None
        self.mse_ylim = 0.41
        FigureCanvas.__init__(self, self.fig)
        self.setParent(interface)
        self.add_mse_label(interface)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.move(-70, -20)
        self.ax1.set_axis_off()
        self.ax2.set_axis_off()
        self.ax3.set_axis_off()
        zeros = np.zeros((400, 400))
        self.ax1.imshow(zeros, cmap="gray")
        self.im2 = self.ax2.imshow(zeros, cmap="gray", animated=True)
        self.im3 = self.ax3.imshow(zeros, cmap="gray", animated=True)

    def add_mse_label(self, interface):
        self.mse_label = QLabel('Mean Squared Error: 0', interface)
        self.mse_label.move(57, 358)
        self.mse_label.setFixedWidth(200)

    def initialize_scan(self, scanner, is_interactive):
        self.scanner = scanner
        zeros = np.zeros((400, 400))
        self.im2 = self.ax2.imshow(zeros, cmap="gray", animated=True)
        self.im3 = self.ax3.imshow(zeros, cmap="gray", animated=True)
        self.ax_err.clear()
        self.ax_err.set_ylim([0, self.mse_ylim])
        self.ax_err.set_yticks(np.arange(0, self.mse_ylim, 0.05))
        sinogram_iterations_num = len(tomograph.params.emitter_angles)
        self.ax_err.set_xlim([0, sinogram_iterations_num])
        self.ax_err.set_xticks(np.arange(0, sinogram_iterations_num + 1, sinogram_iterations_num // 5))
        self.im_err = self.ax_err
        self.draw()
        self.update_mse(0)
        if self.ani2 is not None:
            self.ani2.event_source.stop()
        if self.ani3 is not None:
            self.ani3.event_source.stop()
        if self.ani_err is not None:
            self.ani_err.event_source.stop()
        self.ani3 = self.ani2 = self.ani_err = None
        if is_interactive:
            self.ani2 = animation.FuncAnimation(self.fig, self.animation_sinogram_update, interval=25,
                                                blit=True)  # sinogram animation
            self.ani3 = animation.FuncAnimation(self.fig, self.animation_image_reconstructed_update, interval=25,
                                                blit=True)  # image_reconstructed animation
            self.ani_err = animation.FuncAnimation(self.fig, self.animation_error_update, interval=25,
                                                   blit=True)  # mse animation

    def put_sinogram_in_animation_buf(self, sinogram):
        self.im2 = self.ax2.imshow(sinogram, cmap="gray", animated=True)
        self.ax2.invert_yaxis()

    def put_image_reconstructed_in_animation_buf(self, image_reconstructed):
        self.im3 = self.ax3.imshow(image_reconstructed, cmap="gray", animated=True)

    def animation_sinogram_update(self, _):
        if self.scanner.refresh_sinogram:
            self.scanner.refresh_sinogram = False
            self.animation_update_element(self.im2, self.scanner.sinogram)
        return self.im2,

    def animation_image_reconstructed_update(self, _):
        if self.scanner.refresh_image_reconstructed:
            self.scanner.refresh_image_reconstructed = False
            self.animation_update_element(self.im3, self.scanner.image_reconstructed)
            self.update_mse(self.scanner.mse_error)
        return self.im3,

    def animation_error_update(self, _):
        [self.im_err] = self.ax_err.plot(self.scanner.mse_data, 'b')
        return self.im_err,

    @staticmethod
    def animation_update_element(im, data):
        im.set_data(data)
        im.norm.autoscale(data)

    def update_mse(self, value):
        self.mse_label.setText("Mean Squared Error: %f" % value)


def make_image_square(image_original):
    diagonal = np.sqrt(2) * max(image_original.shape)
    pad = [int(np.ceil(diagonal - s)) for s in image_original.shape]
    new_center = [(s + p) // 2 for s, p in zip(image_original.shape, pad)]
    old_center = [s // 2 for s in image_original.shape]
    pad_before = [nc - oc for oc, nc in zip(old_center, new_center)]
    pad_width = [(pb, p - pb) for pb, p in zip(pad_before, pad)]
    return np.pad(image_original, pad_width, mode='constant', constant_values=0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    interface = Interface()
    interface.show()
    sys.exit(app.exec_())
