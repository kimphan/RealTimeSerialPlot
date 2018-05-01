"""
PlotManager:
    Role: manage data to plot
    References:
        https://github.com/ssepulveda/RTGraph
        Autocorelation:
            https://www.itl.nist.gov/div898/handbook/eda/section3/autocopl.htm
            https://stackoverflow.com/questions/20110590/how-to-calculate-auto-covariance-in-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
"""
import pyqtgraph as pg
from PyQt5.QtCore import QTimer,pyqtSlot,QObject
from manage.worker import Worker
import numpy as np
from scipy.signal import correlate,savgol_filter
from helper.ringBuffer import RingBuffer


class PlotManager(QObject):

    def __init__(self, g_id=0, samples=500, rate=0.02, port=None, plot_widget=None):
        super(PlotManager,self).__init__()
        # mp.Process.__init__(self)
        self.worker = Worker()
        self.graph_id = g_id
        self.samples = int(samples)
        self.rate = float(rate)
        self.port = port
        self.plot = []
        self.plot.append(plot_widget)

        self.configure_timers()
        self.color_dict = ({0:'#6c6d70',1:'#EB340D',2:'#0D46EB', 3:'#d01bd3', 4:'#ed9615', 5: '#298909'})


    def start(self):
        self.worker = Worker(samples=self.samples,rate=self.rate,port=self.port)
        if self.worker.start():
            self.timer_plot.start(20)


    def stop(self):
        self.timer_plot.stop()
        self.worker.stop()

    def configure_timers(self):
        """
        Configures specific elements of the QTimers.
        :return:
        """
        self.timer_plot = QTimer()
        self.timer_plot.timeout.connect(self.update_plot)

    def update_plot(self):
        if self.worker.is_running():
            self.worker.get_plot_value()
            widget_num = len(self.plot)
            count = self.worker.get_channel_num()
            c = 1
            # Clear all data before plot
            for p in self.plot:
                p.plotItem.clear()
            # Plot data
            # Plot all channel in 1 graph
            for i in range(count):
                x,y = self.autocorrelation_plot(data=self.worker.getybuffer(i))

                pen = pg.mkPen(self.color_dict[i], width=1, style=None)
                self.plot[0].plotItem.plot(x,y, pen=pen)
            # Individual plot
            while c <= widget_num-1:
                pen = pg.mkPen(self.color_dict[c-1], width=1, style=None)
                self.plot[c].plotItem.plot(self.worker.getxbuffer(), self.worker.getybuffer(c-1), pen=pen)
                c += 1
        else:
            self.stop()
            print('Manager fail to open port')

    def is_running(self):
        return self.worker.is_running()

    def update_parameter(self,s,r):
        self.samples = int(s)
        self.rate = float(r)
        print('Manager update')

    # Get raw data from sensors and compute
    # Computation: filter raw data using Saviztky-Golay method
    #              detect the randomness in data with autocorrelation coefficient function
    #  Note: Lag value is an integer denoting how many time steps separate one value form another.
    #        Testing for randomness, need only one value of autocorrelation coefficient using lag k = 0
    def autocorrelation_plot(self,data):
        sgf = savgol_filter(data,polyorder=3,window_length=37) # Filter the raw data
        sig_mean = np.mean(sgf)
        sig_norm = sgf - sig_mean        # Normalize data
        variance = np.sum(sig_norm**2)    # Variance function
        lags = np.arange(0, len(sig_norm), 1)
        acorr = RingBuffer(len(sig_norm))
        for l in lags:
            t = self.autocovariance(sig_norm, l)/variance
            acorr.append(t)
        return lags,acorr.get_all()

    # Credit for:
    #    https://stackoverflow.com/questions/20110590/how-to-calculate-auto-covariance-in-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    @staticmethod
    def autocovariance(y,lag):
        n = len(y)
        acov = 0
        for i in range(n-lag):
            acov += (y[i]*y[i+lag])
        return acov





