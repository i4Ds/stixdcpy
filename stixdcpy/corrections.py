from stixdcpy import instrument as inst

def live_time_correction(triggers, counts_arr, time_bins):
    """ Live time correction
    Args
        triggers: ndarray
            triggers in the spectrogram
        counts_arr:ndarray
            counts in the spectrogram
        time_bins: ndarray
            time_bins in the spectrogram
    Returns
    live_time_ratio: ndarray
        live time ratio of detectors
    count_rate:
        corrected count rate
    
    """
    trig_tau=3.96e6 #from idl
    #trig_rates=triggers/time_bins
    photons_in =   triggers/(time_bins-trig_tau*triggers)
    #this event rate= trig_rate/(1-trig_tau * trig_rate)
    live_time_ratio=np.zeros_like((time_bins.size, 32))
    counts_rate=counts_arr/time_bins
    
    for trig_i, g in enumerate(inst.get_trigger_detectors()):
        det1,det2=g
        group_counts=counts_arr[:,det1]+counts_arr[:,det2]
        live_time_ratio[:,det1] = group_counts/photons_in[trig_i]
        
        live_time_ratio[:,det2]=live_time_ratio[:,det1]
     
    return live_time_ratio, counts_rate/live_time_ratio

