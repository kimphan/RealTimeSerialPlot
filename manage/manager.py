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
from helper.fileManager import FileManager


class PlotManager(QObject):
    path = '..\\SerialPlot\\data'
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

        # Log
        self.directory = FileManager()
        self.csvfile = None
        self.mywriter = None
        self.fieldnames = []
        self.filename = ''
        self.data = dict()
        self.logenable= False
        self.writeheader = False

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
            self.data.clear()
            for f in self.plotfunc.keys():
                self.plotfunc[f].plotItem.clear()
                if f == 'Raw Data':
                    for c in self.clist:
                        self.graph(self.plotfunc[f], self.worker.getxbuffer(),self.worker.getybuffer(c),c)
                        self.data[c, f] = self.worker.getybuffer(c)

                elif f == 'Autocorrelation':
                    for c in self.clist:
                        x,y = self.computation.autocorrelation_plot(self.worker.getybuffer(c))
                        self.graph(self.plotfunc[f],x,y,c)
                        self.data[c, f] = y

            if self.logenable:
                # Header for log file
                if self.writeheader:
                    self.mywriter.writerow(self.fieldnames)
                    self.writeheader = False
                # Data
                processed_data = []
                result = []

                # for k in self.data.keys():
                #     field = 1
                #     while(field <= 2):
                #         for i in self.data[k]:
                #             if i != 0.0:
                #                 processed_data.clear()
                #                 processed_data.append(k[0])
                #                 processed_data.append(i)
                #                 self.mywriter.writerow(processed_data)

                for c in self.clist:
                    field = 1
                    for d in self.data[c,self.fieldnames[field]]:
                        while field < len(self.fieldnames):
                            if d != 0.0:
                                processed_data.clear()
                                processed_data.append(c)
                                processed_data.append(d)
                            field += 1
                        if len(processed_data) != 0:
                            self.mywriter.writerow(processed_data)


        else:
            self.stop()
            print('Manager fail to open port')

    def is_running(self):
        return self.worker.is_running()

    def update_plotDict(self,pf):
        self.plotfunc = pf
        self.fieldnames.clear()
        self.fieldnames.append('Channel')
        for header in pf.keys():
            self.fieldnames.append(header)
        self.writeheader = True


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
        if fileready:
            self.csvfile = self.directory.create_file(self.path,fname)
            self.mywriter = csv.writer(self.csvfile,delimiter=',')
        else:
            if self.directory.check_path(os.path.join(self.path,fname+'.csv')):
                self.csvfile.close()

    def count_channel(self):
        return self.worker.get_channel_num()

    def graph(self,plot_widget,x,y,i):
        pen = pg.mkPen(self.color_dict[i], width=1, style=None)
        plot_widget.plotItem.plot(x,y, pen=pen)







