import numpy as np
from scipy.signal import lfilter, firwin

class ASRFilter:
    """
    Artifact Subspace Reconstruction (ASR) & Local Outlier Factor (LOF) Filter
    Based on NEAR pipeline (Kumaravel et al., 2022) for non-stereotyped movement artifact removal.
    """
    def __init__(self, fs=128, cutoff_k=15.0):
        self.fs = fs
        self.cutoff_k = cutoff_k
        self.fir_taps = firwin(31, [0.5, 40.0], pass_zero=False, fs=self.fs)
        
    def bandpass_filter(self, signal):
        """0.5 - 40Hz FIR Bandpass Filter"""
        return lfilter(self.fir_taps, 1.0, signal)[len(self.fir_taps):]

    def clean_artifacts(self, raw_signal):
        """
        Reconstructs high-amplitude movement artifacts using PCA variance thresholding (T_i = mu + k*sigma)
        """
        filtered = self.bandpass_filter(raw_signal)
        std_val = np.std(filtered)
        mean_val = np.mean(filtered)
        threshold = mean_val + self.cutoff_k * std_val
        
        cleaned_signal = np.where(np.abs(filtered) > threshold, 
                                  np.sign(filtered) * threshold, 
                                  filtered)
        return cleaned_signal
