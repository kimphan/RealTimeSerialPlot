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
import os,csv
from PyQt5.QtCore import QTimer,QObject
from manage.worker import Worker
from helper.function import Function


class PlotManager(QObject):
    def __init__(self,samples=500, rate=0.02, port=None):
        super(PlotManager,self).__init__()
        # mp.Process.__init__(self)
        self.samples = int(samples)
        self.rate = int(rate)
        self.port = port
        self.plotfunc = dict()
        self.clist = []
        self.worker = Worker()
        self.computation = Function()
        self.configure_timers()
        self.color_dict = ({0:'#6c6d70',1:'#EB340D',2:'#0D46EB', 3:'#d01bd3', 4:'#ed9615', 5: '#298909'})
        self.line = 0
        self.fieldname = ['time']
        self.filename = ''
        self.y = dict()
        self.logenable= False

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
            for f in self.plotfunc.keys():
                self.plotfunc[f].plotItem.clear()
                if f == 'Raw Data':
                    for c in self.clist:
                        self.graph(self.plotfunc[f], self.worker.getxbuffer(),self.worker.getybuffer(c),c)
                elif f == 'Autocorrelation':
                    for c in self.clist:
                        x,y = self.computation.autocorrelation_plot(self.worker.getybuffer(c))
                        self.graph(self.plotfunc[f],x,y,c)
                if self.logenable:
                    self.create_file(self.filename)

        else:
            self.stop()
            print('Manager fail to open port')

    def is_running(self):
        return self.worker.is_running()

    def update_plotDict(self,pf):
        self.plotfunc = pf
        print('Manager update')

    def update_samples(self,s):
        self.samples = int(s)
        if self.is_running():
            self.stop()
        self.start()

    def add_channel(self,c):
        if c not in self.clist:
            self.clist.append(c)

    def remove_channel(self,c):
        for ch in self.clist:
            if ch == c:
                self.clist.remove(c)

    def setup_serial(self,sample,brate,port):
        self.samples = int(sample)
        self.rate = int(brate)
        self.port = port
        print('Setting up serial port!')

    def get_port(self):
        return self.worker.get_port()

    def csv_checked(self, fileready, fname):
        self.logenable = fileready
        self.filename = fname

    @staticmethod
    def create_file(filename):
        save_path = '..\\SerialPlot\\data'
        with open(os.path.join(save_path, filename+'.csv'),'a') as f:
            print(filename)
            writer = csv.writer(f)
            writer.writerow(['test','test23'])


    def count_channel(self):
        return self.worker.get_channel_num()

    def graph(self,plot_widget,x,y,i):
        pen = pg.mkPen(self.color_dict[i], width=1, style=None)
        plot_widget.plotItem.plot(x,y, pen=pen)







