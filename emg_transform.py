# emg_transform.py

"""
Helper functions for EMG calculations and transformations.
"""

import numpy as np

def rectify_emg(emg_array):
    """
    Rectify EMG data by taking the absolute value.
    """
    return np.abs(emg_array)

def calculate_average_amplitude(emg_data, start_ms, end_ms, scan_rate):
    """
    Calculate the average rectified EMG amplitude between start_ms and end_ms.
    """
    start_index = int(start_ms * scan_rate / 1000)
    end_index = int(end_ms * scan_rate / 1000)
    emg_window = emg_data[start_index:end_index]
    rectified_emg_window = rectify_emg(emg_window)
    return np.mean(rectified_emg_window)

def calculate_mean_std(recordings, stimulus_value, channel_index, m_start_ms, m_end_ms, h_start_ms, h_end_ms, bin_size, scan_rate):
    """
    Calculate the M-responses and H-reflexes over multiple sessions for a given stimulus voltage, binning the stimulus voltages.
    """
    m_wave_amplitudes = []
    h_response_amplitudes = []
    for recording in recordings:
        binned_stimulus_v = round(recording['stimulus_v'] / bin_size) * bin_size
        if binned_stimulus_v == stimulus_value:
            channel_data = recording['channel_data'][channel_index]
            m_wave_amplitude = calculate_average_amplitude(channel_data, m_start_ms, m_end_ms, scan_rate)
            h_response_amplitude = calculate_average_amplitude(channel_data, h_start_ms, h_end_ms, scan_rate)
            m_wave_amplitudes.append(m_wave_amplitude)
            h_response_amplitudes.append(h_response_amplitude)
    m_wave_mean = np.mean(m_wave_amplitudes)
    m_wave_std = np.std(m_wave_amplitudes)
    h_response_mean = np.mean(h_response_amplitudes)
    h_response_std = np.std(h_response_amplitudes)
    return m_wave_mean, m_wave_std, h_response_mean, h_response_std