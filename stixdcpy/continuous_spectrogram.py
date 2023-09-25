def fetch_spectrogram(start_utc, end_utc):
    url='https://datacenter.stix.i4ds.net/request/bsd/spectrograms'
    res=requests.post(url, data={'begin':start_utc, 'end':end_utc})
    data=res.json()
    spectrograms=[]
    begin, end = dtparser.parse(start_utc).timestamp(), dtparser.parse(end_utc).timestamp()
    last_unix=0
    timestamps=[]
    time_bins=[]
    E1, E2, Eunit, dmask, pmask=[[]]*5
    utcs=[]
    #utcs
    for req in data['data']:
        for gr in req['groups']:
            #print(gr)
            #break
            #if E0 is None:
            E1.append(gr['E1'])
            E2.append(gr['E2'])
            Eunit.append(gr['Eunit'])
            dmask.append(gr['detector_mask'])
            pmask.append(gr['pixel_mask'])
                                 
            for sb in gr['subgroups']:
                unix=sb[0]
                if unix<last_unix or unix<begin or unix>end:
                    continue
            
                spectrograms.append(sb[2])
                
                utcs.append(datetime.utcfromtimestamp(unix))
                time_bins.append(sb[3])
            
    #if np.unique(E1).size > 1 or np.unique(E2).size >1 or np.unique(dmask).size>1 or np.unique(pmask).size>1:
    #    raise ValueError('Failed to merge the spectrogram! STIX spectrogram configuration changed in the requested time frame! ')
    time_bins=np.array(time_bins)
    spectrograms=np.array(spectrograms).T/time_bins

    #print(spectrograms.shape)
    return {'datetime': utcs, 'time_bin': time_bins, 
            'spectrogram':spectrograms,
            'energy_bins': get_spectrogram_energy_bins(E1[0], E2[0],Eunit[0])  }
