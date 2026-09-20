import numpy as np
from scipy.signal import welch
from scipy.stats import skew, kurtosis

class FeatureExtractor:
    """
    Multi-domain EEG Feature Extractor
    Extracts Hjorth parameters, PSD band powers (TBR, Alpha Power), and time-domain statistics.
    """
    def __init__(self, fs=128, window_size=128):
        self.fs = fs
        self.window_size = window_size

    def hjorth_parameters(self, signal):
        """Computes Hjorth Activity, Mobility, and Complexity."""
        d1 = np.diff(signal)
        d2 = np.diff(d1)
        var_zero = np.var(signal) + 1e-10
        var_d1 = np.var(d1) + 1e-10
        var_d2 = np.var(d2) + 1e-10

        activity = var_zero
        mobility = np.sqrt(var_d1 / var_zero)
        complexity = np.sqrt(var_d2 / var_d1) / (mobility + 1e-10)
        return activity, mobility, complexity

    def extract_all(self, signal):
        """Extracts complete feature vector from cleaned EEG window."""
        kurt_val = float(kurtosis(signal))
        skew_val = float(skew(signal))
        line_len = float(np.sum(np.abs(np.diff(signal))))
        activity, mobility, complexity = self.hjorth_parameters(signal)

        freqs, psd = welch(signal, fs=self.fs, nperseg=min(len(signal), self.window_size))
        
        theta_p = np.mean(psd[(freqs >= 4) & (freqs <= 8)]) + 1e-6
        alpha_p = np.mean(psd[(freqs >= 8) & (freqs <= 12)]) + 1e-6
        beta_p  = np.mean(psd[(freqs >= 13) & (freqs <= 30)]) + 1e-6

        tbr = theta_p / beta_p
        risk_score = (tbr * 0.35) + ((1.0 / alpha_p) * 0.25) + (kurt_val * 0.2) + (mobility * 0.2)
        is_overload = risk_score > 2.8 or alpha_p < 0.30 or tbr > 3.6

        return {
            "tbr": float(np.round(tbr, 3)),
            "alphaPower": float(np.round(alpha_p, 3)),
            "mobility": float(np.round(mobility, 3)),
            "kurtosis": float(np.round(kurt_val, 3)),
            "riskScore": float(np.round(risk_score, 3)),
            "isOverload": bool(is_overload)
        }
