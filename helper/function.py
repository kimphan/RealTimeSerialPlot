from scipy.signal import savgol_filter, correlate
import numpy as np


class Function:
    def __init__(self):
        super(Function,self).__init__()

    # Get raw data from sensors and compute
    # Computation: filter raw data using Saviztky-Golay method
    #              detect the randomness in data with autocorrelation coefficient function
    #  Note: Lag value is an integer denoting how many time steps separate one value form another.
    #        Testing for randomness, need only one value of autocorrelation coefficient using lag k = 0
    def autocorrelation_plot(self,data):
        n=len(data)
        sgf = savgol_filter(data,polyorder=3,window_length=37) # Filter the raw data
        sig_mean = np.mean(sgf)
        sig_norm = sgf - sig_mean        # Normalize data
        variance = np.sum(sig_norm**2)    # Variance function
        if variance == 0:
            variance = 1
        acorr = correlate(sig_norm,sig_norm,'same')/variance
        lags = np.arange(int(n/2),n, 1)
        return lags,acorr[int(n/2):]

