
"""
Classes to analyze and plot EMG data from individual sessions or an entire dataset of sessions.
"""

import pickle
import numpy as np
import matplotlib.pyplot as plt
import emg_transform
import utils

config = utils.load_config('config.yaml')

class EMGSession:
    """
    Class for analyzing and plotting data from a single recording session of variable channel numbers for within-session analyses and plotting.

    This module provides functions for analyzing data stored in Pickle files from a single EMG recording session.
    It includes functions to extract session parameters, plot all EMG data, and plot EMG data from suspected H-reflex recordings.
    Class must be instatiated with the Pickled session data file.

    Attributes:
            time_window (float): Time window to plot in milliseconds. Defaults to first 10ms.
            m_start_ms (float): Start time of the M-response window in milliseconds. Defaults to 2.0 ms.
            m_end_ms (float): End time of the M-response window in milliseconds. Defaults to 4.0 ms.
            h_start_ms (float): Start time of the suspected H-reflex window in milliseconds. Defaults to 4.0 ms.
            h_end_ms (float): End time of the suspected H-reflex window in milliseconds. Defaults to 7.0 ms.
    """
    def __init__(self, pickled_session_data):
        """
        Initialize an EMGSession instance.

        Args:
            pickled_session_data (str): filepath of .pickle session data file for this session.
        """
        self.load_session_data(pickled_session_data)
        self.m_start = config['m_start']
        self.m_end = config['m_end']
        self.h_start = config['h_start']
        self.h_end = config['h_end']
        self.time_window_ms = config['time_window']

        self.m_color = 'blue'
        self.h_color = 'orange'
        self.flag_style = ':'
    
    def load_session_data(self, pickled_data):
        # Load the session data from the pickle file
        with open(pickled_data, 'rb') as pickle_file:
            session_data = pickle.load(pickle_file)

        # Access session-wide information
        session_info = session_data['session_info']
        self.session_name = session_info['session_name']
        self.num_channels = session_info['num_channels']
        self.scan_rate = session_info['scan_rate']
        self.num_samples = session_info['num_samples']
        self.stim_duration = session_info['stim_duration']
        self.stim_interval = session_info['stim_interval']
        self.emg_amp_gains = session_info['emg_amp_gains']
        self.recordings = sorted(session_data['recordings'], key=lambda x: x['stimulus_v'])

    def session_parameters (self):
        """
        Prints EMG recording session parameters from a Pickle file.
        """
        print(f"Session Name: {self.session_name}")
        print(f"# of Channels: {self.num_channels}")
        print(f"Scan rate (Hz): {self.scan_rate}")
        print(f"Samples/Channel: {self.num_samples}")
        print(f"Stimulus duration (ms): {self.stim_duration}")
        print(f"Stimulus interval (s): {self.stim_interval}")
        print(f"EMG amp gains: {self.emg_amp_gains}")

    def plot_emg (self, channel_names=[], m_flags = False, h_flags = False):
        """
        Plots EMG data from a Pickle file for a specified time window.

        Args:
            channel_names (string, optional): List of custom channels names to be plotted. Must be the exact same length as the number of recorded channels in the dataset.
        """

        # Handle custom channel names parameter if specified.
        customNames = False
        if len(channel_names) == 0:
            pass
        elif len(channel_names) != self.num_channels:
            print(f">! Error: list of custom channel names does not match the number of recorded channels. The entered list is {len(channel_names)} names long, but {self.num_channels} channels were recorded.")
        elif len(channel_names) == self.num_channels:
            customNames = True

        # Calculate time values based on the scan rate
        time_values_ms = np.arange(self.num_samples) * 1000 / self.scan_rate  # Time values in milliseconds

        # Determine the number of samples for the desired time window in ms
        num_samples_time_window = int(self.time_window_ms * self.scan_rate / 1000)  # Convert time window to number of samples

        # Slice the time array for the time window
        time_axis = time_values_ms[:num_samples_time_window]

        # Create a figure and axis
        if self.num_channels == 1:
            fig, ax = plt.subplots(figsize=(8, 4))
            axes = [ax]
        else:
            fig, axes = plt.subplots(nrows=1, ncols=self.num_channels, figsize=(12, 4), sharey=True)

        # Plot the EMG arrays for each channel, only for the first 10ms
        if customNames:
            for recording in self.recordings:
                for channel_index, channel_data in enumerate(recording['channel_data']):
                    if self.num_channels == 1:
                        ax.plot(time_axis, channel_data[:num_samples_time_window], label=f"Stimulus Voltage: {recording['stimulus_v']}")
                        ax.set_title(f'{channel_names[0]}')
                        ax.grid(True)
                        #ax.legend()
                        if m_flags:
                            ax.axvline(self.m_start, color=self.m_color, linestyle=self.flag_style)
                            ax.axvline(self.m_end, color=self.m_color, linestyle=self.flag_style)                         
                        if h_flags:
                            ax.axvline(self.h_start, color=self.h_color, linestyle=self.flag_style)
                            ax.axvline(self.h_end, color=self.h_color, linestyle=self.flag_style)                       
                    else:
                        axes[channel_index].plot(time_axis, channel_data[:num_samples_time_window], label=f"Stimulus Voltage: {recording['stimulus_v']}")
                        axes[channel_index].set_title(f'{channel_names[channel_index]}')
                        axes[channel_index].grid(True)
                        #axes[channel_index].legend()
                        if m_flags:
                            axes[channel_index].axvline(self.m_start, color=self.m_color, linestyle=self.flag_style)
                            axes[channel_index].axvline(self.m_end, color=self.m_color, linestyle=self.flag_style)
                        if h_flags:
                            axes[channel_index].axvline(self.h_start, color=self.h_color, linestyle=self.flag_style)
                            axes[channel_index].axvline(self.h_end, color=self.h_color, linestyle=self.flag_style)
        else:
            for recording in self.recordings:
                for channel_index, channel_data in enumerate(recording['channel_data']):
                    if self.num_channels == 1:
                        ax.plot(time_axis, channel_data[:num_samples_time_window], label=f"Stimulus Voltage: {recording['stimulus_v']}")
                        ax.set_title('Channel 0')
                        ax.grid(True)
                        #ax.legend()
                    else:
                        axes[channel_index].plot(time_axis, channel_data[:num_samples_time_window], label=f"Stimulus Voltage: {recording['stimulus_v']}")
                        axes[channel_index].set_title(f'Channel {channel_index}')
                        axes[channel_index].grid(True)
                        #axes[channel_index].legend()

        # Set labels and title
        if self.num_channels == 1:
            ax.set_xlabel('Time (ms)')
            ax.set_ylabel('EMG (mV)')
            fig.suptitle('EMG Overlay for Channel 0 (all recordings)', fontsize=16)
        else:
            fig.suptitle('EMG Overlay for All Channels (all recordings)', fontsize=16)
            fig.supxlabel('Time (ms)')
            fig.supylabel('EMG (mV)')

            # Adjust subplot spacing
            plt.subplots_adjust(wspace=0.1,left=0.1, right=0.9, top=0.85, bottom=0.15)

        # Show the plot
        plt.show()

    def plot_emg_rectified (self, channel_names=[], m_flags = False, h_flags = False):
        """
        Plots rectified EMG data from a Pickle file for a specified time window.

        Args:
            channel_names (string, optional): List of custom channels names to be plotted. Must be the exact same length as the number of recorded channels in the dataset.
        """

        # Handle custom channel names parameter if specified.
        customNames = False
        if len(channel_names) == 0:
            pass
        elif len(channel_names) != self.num_channels:
            print(f">! Error: list of custom channel names does not match the number of recorded channels. The entered list is {len(channel_names)} names long, but {self.num_channels} channels were recorded.")
        elif len(channel_names) == self.num_channels:
            customNames = True

        # Calculate time values based on the scan rate
        time_values_ms = np.arange(self.num_samples) * 1000 / self.scan_rate  # Time values in milliseconds

        # Determine the number of samples for the first 10ms
        num_samples_time_window = int(self.time_window_ms * self.scan_rate / 1000)  # Convert time window to number of samples

        # Slice the time array for the time window
        time_axis = time_values_ms[:num_samples_time_window]

        # Create a figure and axis
        if self.num_channels == 1:
            fig, ax = plt.subplots(figsize=(8, 4))
            axes = [ax]
        else:
            fig, axes = plt.subplots(nrows=1, ncols=self.num_channels, figsize=(12, 4), sharey=True)

        # Plot the rectified EMG arrays for each channel, only for the first 10ms
        if customNames:
            for recording in self.recordings:
                for channel_index, channel_data in enumerate(recording['channel_data']):
                    rectified_channel_data = emg_transform.rectify_emg(channel_data)
                    if self.num_channels == 1:
                        ax.plot(time_axis, rectified_channel_data[:num_samples_time_window], label=f"Stimulus Voltage: {recording['stimulus_v']}")
                        ax.set_title(f'{channel_names[0]} (Rectified)')
                        ax.grid(True)
                        #ax.legend()
                        if m_flags:
                            ax.axvline(self.m_start, color=self.m_color, linestyle=self.flag_style)
                            ax.axvline(self.m_end, color=self.m_color, linestyle=self.flag_style)
                        if h_flags:
                            ax.axvline(self.h_start, color=self.h_color, linestyle=self.flag_style)
                            ax.axvline(self.h_end, color=self.h_color, linestyle=self.flag_style)
                    else:
                        axes[channel_index].plot(time_axis, rectified_channel_data[:num_samples_time_window], label=f"Stimulus Voltage: {recording['stimulus_v']}")
                        axes[channel_index].set_title(f'{channel_names[channel_index]} (Rectified)')
                        axes[channel_index].grid(True)
                        #axes[channel_index].legend()
                        if m_flags:
                            axes[channel_index].axvline(self.m_start, color=self.m_color, linestyle=self.flag_style)
                            axes[channel_index].axvline(self.m_end, color=self.m_color, linestyle=self.flag_style)
                        if h_flags:
                            axes[channel_index].axvline(self.h_start, color=self.h_color, linestyle=self.flag_style)
                            axes[channel_index].axvline(self.h_end, color=self.h_color, linestyle=self.flag_style)
        else:
            for recording in self.recordings:
                for channel_index, channel_data in enumerate(recording['channel_data']):
                    rectified_channel_data = emg_transform.rectify_emg(channel_data)
                    if self.num_channels == 1:
                        ax.plot(time_axis, rectified_channel_data[:num_samples_time_window], label=f"Stimulus Voltage: {recording['stimulus_v']}")
                        ax.set_title('Channel 0 (Rectified)')
                        ax.grid(True)
                        #ax.legend()
                    else:
                        axes[channel_index].plot(time_axis, rectified_channel_data[:num_samples_time_window], label=f"Stimulus Voltage: {recording['stimulus_v']}")
                        axes[channel_index].set_title(f'Channel {channel_index} (Rectified)')
                        axes[channel_index].grid(True)
                        #axes[channel_index].legend()

        # Set labels and title
        if self.num_channels == 1:
            ax.set_xlabel('Time (ms)')
            ax.set_ylabel('Rectified EMG (mV)')
            fig.suptitle('Rectified EMG Overlay for Channel 0 (all recordings)', fontsize=16)
        else:
            fig.suptitle('Rectified EMG Overlay for All Channels (all recordings)', fontsize=16)
            fig.supxlabel('Time (ms)')
            fig.supylabel('Rectified EMG (mV)')

            # Adjust subplot spacing
            plt.subplots_adjust(wspace=0.1,left=0.1, right=0.9, top=0.85, bottom=0.15)
        # Show the plot
        plt.show()

    def plot_emg_suspectedH (self, channel_names=[], h_threshold=0.3, plot_legend=False):
        """
        Detects session recordings with potential H-reflexes and plots them.

        Args:
            channel_names (string, optional): List of custom channels names to be plotted. Must be the exact same length as the number of recorded channels in the dataset.
            h_threshold (float, optional): Detection threshold of the average rectified EMG response in millivolts in the H-relfex window. Defaults to 0.3mV.
            plot_legend (bool, optional): Whether to plot legends. Defaults to False.
        """

        # Handle custom channel names parameter if specified.
        customNames = False
        if len(channel_names) == 0:
            pass
        elif len(channel_names) != self.num_channels:
            print(f">! Error: list of custom channel names does not match the number of recorded channels. The entered list is {len(channel_names)} names long, but {self.num_channels} channels were recorded.")
        elif len(channel_names) == self.num_channels:
            customNames = True

        # Calculate time values based on the scan rate
        time_values_ms = np.arange(self.num_samples) * 1000 / self.scan_rate  # Time values in milliseconds

        # Determine the number of samples for the first 10ms
        num_samples_time_window = int(self.time_window_ms * self.scan_rate / 1000)  # Convert time window to number of samples

        # Slice the time array for the time window
        time_axis = time_values_ms[:num_samples_time_window]

        # Create a figure and axis
        if self.num_channels == 1:
            fig, ax = plt.subplots(figsize=(8, 4))
            axes = [ax]
        else:
            fig, axes = plt.subplots(nrows=1, ncols=self.num_channels, figsize=(12, 4), sharey=True)

        # Plot the EMG arrays for each channel, only for the first 10ms
        if customNames:
            for recording in self.recordings:
                for channel_index, channel_data in enumerate(recording['channel_data']):
                    h_window = recording['channel_data'][channel_index][int(self.h_start * self.scan_rate / 1000):int(self.h_end * self.scan_rate / 1000)]
                    if max(h_window) - min(h_window) > h_threshold:  # Check amplitude variation within 5-10ms window
                        if self.num_channels == 1:
                            ax.plot(time_axis, channel_data[:num_samples_time_window], label=f"Stimulus Voltage: {recording['stimulus_v']}")
                            ax.set_title(f'{channel_names[0]}')
                            ax.grid(True)
                            if plot_legend:
                                ax.legend()
                        else:
                            axes[channel_index].plot(time_axis, channel_data[:num_samples_time_window], label=f"Stimulus Voltage: {recording['stimulus_v']}")
                            axes[channel_index].set_title(f'{channel_names[channel_index]}')
                            axes[channel_index].grid(True)
                            if plot_legend:
                                axes[channel_index].legend()
        else:
            for recording in self.recordings:
                for channel_index, channel_data in enumerate(recording['channel_data']):
                    h_window = recording['channel_data'][channel_index][int(self.h_start * self.scan_rate / 1000):int(self.h_end * self.scan_rate / 1000)]
                    if max(h_window) - min(h_window) > h_threshold:  # Check amplitude variation within 5-10ms window
                        if self.num_channels == 1:
                            ax.plot(time_axis, channel_data[:num_samples_time_window], label=f"Stimulus Voltage: {recording['stimulus_v']}")
                            ax.set_title('Channel 0')
                            ax.grid(True)
                            if plot_legend:
                                ax.legend()
                        else:
                            axes[channel_index].plot(time_axis, channel_data[:num_samples_time_window], label=f"Stimulus Voltage: {recording['stimulus_v']}")
                            axes[channel_index].set_title(f'Channel {channel_index}')
                            axes[channel_index].grid(True)
                            if plot_legend:
                                axes[channel_index].legend()

        # Set labels and title
        if self.num_channels == 1:
            ax.set_xlabel('Time (ms)')
            ax.set_ylabel('EMG (mV)')
            fig.suptitle(f'EMG Overlay for Channel 0 (H-reflex Amplitude Variability > {h_threshold} mV)', fontsize=16)
        else:
            fig.suptitle(f'EMG Overlay for All Channels (H-reflex Amplitude Variability > {h_threshold} mV)', fontsize=16)
            fig.supxlabel('Time (ms)')
            fig.supylabel('EMG (mV)')

            # Adjust subplot spacing
            plt.subplots_adjust(wspace=0.1,left=0.1, right=0.9, top=0.85, bottom=0.15)

        # Show the plot
        plt.show()

    def plot_reflex_curves (self, channel_names=[]):
        """
        Plots overlayed M-response and H-reflex curves for each recorded channel.

        Args:
            channel_names (string, optional): List of custom channels names to be plotted. Must be the exact same length as the number of recorded channels in the dataset.
        """

        # Handle custom channel names parameter if specified.
        customNames = False
        if len(channel_names) == 0:
            pass
        elif len(channel_names) != self.num_channels:
            print(f">! Error: list of custom channel names does not match the number of recorded channels. The entered list is {len(channel_names)} names long, but {self.num_channels} channels were recorded.")
        elif len(channel_names) == self.num_channels:
            customNames = True

        # Create a figure and axis
        if self.num_channels == 1:
            fig, ax = plt.subplots(figsize=(8, 4))
            axes = [ax]
        else:
            fig, axes = plt.subplots(nrows=1, ncols=self.num_channels, figsize=(12, 4), sharey=True)

        # Plot the M-wave and H-response amplitudes for each channel
        for channel_index in range(self.num_channels):
            m_wave_amplitudes = []
            h_response_amplitudes = []
            stimulus_voltages = []

            for recording in self.recordings:
                channel_data = recording['channel_data'][channel_index]
                stimulus_v = recording['stimulus_v']

                m_wave_amplitude = emg_transform.calculate_average_amplitude(channel_data, self.m_start, self.m_end, self.scan_rate)
                h_response_amplitude = emg_transform.calculate_average_amplitude(channel_data, self.h_start, self.h_end, self.scan_rate)

                m_wave_amplitudes.append(m_wave_amplitude)
                h_response_amplitudes.append(h_response_amplitude)
                stimulus_voltages.append(stimulus_v)

            if self.num_channels == 1:
                ax.scatter(stimulus_voltages, m_wave_amplitudes, color='r', label='M-wave', marker='o')
                ax.scatter(stimulus_voltages, h_response_amplitudes, color='b', label='H-response', marker='o')
                ax.set_title('Channel 0')
                #ax.set_xlabel('Stimulus Voltage (V)')
                #ax.set_ylabel('Amplitude (mV)')
                ax.grid(True)
                ax.legend()
                if customNames:
                    ax.set_title(f'{channel_names[0]}')
            else:
                axes[channel_index].scatter(stimulus_voltages, m_wave_amplitudes, color='r', label='M-wave', marker='o')
                axes[channel_index].scatter(stimulus_voltages, h_response_amplitudes, color='b', label='H-response', marker='o')
                axes[channel_index].set_title(f'Channel {channel_index}')
                #axes[channel_index].set_xlabel('Stimulus Voltage (V)')
                #axes[0].set_ylabel('Amplitude (mV)')
                axes[channel_index].grid(True)
                axes[channel_index].legend()
                if customNames:
                    axes[channel_index].set_title(f'{channel_names[channel_index]}')
        
        # Set labels and title
        if self.num_channels == 1:
            ax.set_xlabel('Stimulus Voltage (V)')
            ax.set_ylabel('EMG Amplitude (mV)')
            fig.suptitle(f'M-response and H-reflex Curves', fontsize=16)
        else:
            fig.suptitle(f'M-response and H-reflex Curves', fontsize=16)
            fig.supxlabel('Stimulus Voltage (V)')
            fig.supylabel('EMG Amplitude (mV)')

            # Adjust subplot spacing
            plt.subplots_adjust(wspace=0.1,left=0.1, right=0.9, top=0.85, bottom=0.15)

        # Show the plot
        plt.show()

class EMGDataset:
    """
    Class for a dataset of EMGSession instances for multi-session analyses and plotting.

    This module provides functions for analyzing a full dataset of EMGSessions. This code assumes all session have the same recording parameters and number of channels.
    The class must be instatiated with a list of EMGSession instances.

    Attributes:
            m_start_ms (float, optional): Start time of the M-response window in milliseconds. Defaults to 2.0 ms.
            m_end_ms (float, optional): End time of the M-response window in milliseconds. Defaults to 4.0 ms.
            h_start_ms (float, optional): Start time of the suspected H-reflex window in milliseconds. Defaults to 4.0 ms.
            h_end_ms (float, optional): End time of the suspected H-reflex window in milliseconds. Defaults to 7.0 ms.
            bin_size (float, optional): Bin size for the x-axis (in V). Defaults to 0.05V.
    """
    def __init__(self, emg_sessions):
        """
        Initialize an EMGDataset instance from a list of EMGSession instances for multi-session analyses and plotting.

        Args:
            emg_sessions (list): a list of instances of the class EMGSession.
        """
        self.emg_sessions = emg_sessions
        self.scan_rate = emg_sessions[0].scan_rate
        self.num_channels = emg_sessions[0].num_channels

        self.m_start = config['m_start']
        self.m_end = config['m_end']
        self.h_start = config['h_start']
        self.h_end = config['h_end']
        self.bin_size = config['bin_size']

    def plot_reflex_curves(self, channel_names=[]):
        """
        Plots average M-response and H-reflex curves for a dataset of EMG sessions along with the standard deviation. 
        Because the stimulus voltages for subsequent trials/session vary slightly in their intensity, slight binning is required to plot a smooth curve.

        Args:
            channel_names (string, optional): List of custom channels names to be plotted. Must be the exact same length as the number of recorded channels in the dataset.
        """
        # Handle custom channel names parameter if specified.
        customNames = False
        if len(channel_names) == 0:
            pass
        elif len(channel_names) != self.num_channels:
            print(f">! Error: list of custom channel names does not match the number of recorded channels. The entered list is {len(channel_names)} names long, but {self.num_channels} channels were recorded.")
        elif len(channel_names) == self.num_channels:
            customNames = True
        
        # Unpack session recordings.
        recordings = []
        for session in self.emg_sessions:
            recordings.extend(session.recordings)
        sorted_recordings = sorted(recordings, key=lambda x: x['stimulus_v'])

        # Create a figure and axis
        if self.num_channels == 1:
            fig, ax = plt.subplots(figsize=(8, 4))
            axes = [ax]
        else:
            fig, axes = plt.subplots(nrows=1, ncols=self.num_channels, figsize=(12, 4), sharey=True)

        # Get unique binned stimulus voltages
        stimulus_voltages = sorted(list(set([round(recording['stimulus_v'] / self.bin_size) * self.bin_size for recording in sorted_recordings])))

        # Plot the M-wave and H-response amplitudes for each channel
        for channel_index in range(self.num_channels):
            m_wave_means = []
            m_wave_stds = []
            h_response_means = []
            h_response_stds = []
            for stimulus_v in stimulus_voltages:
                m_wave_mean, m_wave_std, h_response_mean, h_response_std = emg_transform.calculate_mean_std(sorted_recordings, stimulus_v, channel_index, self.m_start, self.m_end, self.h_start, self.h_end, self.bin_size, self.scan_rate)
                m_wave_means.append(m_wave_mean)
                m_wave_stds.append(m_wave_std)
                h_response_means.append(h_response_mean)
                h_response_stds.append(h_response_std)

            if self.num_channels == 1:
                ax.plot(stimulus_voltages, m_wave_means, color='r', label='M-wave')
                ax.fill_between(stimulus_voltages, np.array(m_wave_means) - np.array(m_wave_stds), np.array(m_wave_means) + np.array(m_wave_stds), color='r', alpha=0.2)
                ax.plot(stimulus_voltages, h_response_means, color='b', label='H-response')
                ax.fill_between(stimulus_voltages, np.array(h_response_means) - np.array(h_response_stds), np.array(h_response_means) + np.array(h_response_stds), color='b', alpha=0.2)
                ax.set_title('Channel 0')
                if customNames:
                    ax.set_title(f'{channel_names[0]}')
                ax.grid(True)
                ax.legend()
            else:
                axes[channel_index].plot(stimulus_voltages, m_wave_means, color='r', label='M-wave')
                axes[channel_index].fill_between(stimulus_voltages, np.array(m_wave_means) - np.array(m_wave_stds), np.array(m_wave_means) + np.array(m_wave_stds), color='r', alpha=0.2)
                axes[channel_index].plot(stimulus_voltages, h_response_means, color='b', label='H-response')
                axes[channel_index].fill_between(stimulus_voltages, np.array(h_response_means) - np.array(h_response_stds), np.array(h_response_means) + np.array(h_response_stds), color='b', alpha=0.2)
                axes[channel_index].set_title(f'Channel {channel_index}' if not channel_names else channel_names[channel_index])
                if customNames:
                    axes[channel_index].set_title(f'{channel_names[channel_index]}')
                axes[channel_index].grid(True)
                axes[channel_index].legend()

        # Set labels and title
        if self.num_channels == 1:
            ax.set_xlabel('Stimulus Voltage (V)')
            ax.set_ylabel('EMG Amplitude (mV)')
            fig.suptitle(f'M-response and H-reflex Curves', fontsize=16)
        else:
            fig.suptitle(f'M-response and H-reflex Curves', fontsize=16)
            fig.supxlabel('Stimulus Voltage (V)')
            fig.supylabel('EMG Amplitude (mV)')

            # Adjust subplot spacing
            plt.subplots_adjust(wspace=0.1,left=0.1, right=0.9, top=0.85, bottom=0.15)

        # Show the plot
        plt.show()