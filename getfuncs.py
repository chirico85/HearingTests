# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 14:40:00 2020

@author: galindo

"""

import os
import sounddevice as sd
import soundfile as sf
import time
import socket
import numpy as np
import json
import datetime

def initparameters():
    count = 1               # Iterator
    #Liste = 10   # Liste
    Sprachpegel = 65        # Startpegel
    Noisepegel = 65
    answers = [0] * 5       # Antworten pro Satz
    answers_time = [0] * 5  # Antworten pro Satz    
    Pegel = []              # Liste zur Speicherung aller genutzen Pegel
    Pegel.append(Sprachpegel)
    training = 0    
    return count,Sprachpegel,Noisepegel,answers,Pegel,training,answers_time        

def startserver(ip,port):
    print('Bitte Tablet verbinden mit TCP_IP: ',ip,'   TCP_PORT: ',port)          
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(1)
    conn, addr = s.accept()
    print('Connection address:', addr)    
    return conn

def startparameters_prot(Liste, serverpath):
    if int(Liste) <= 20:
        cdpath = os.path.join(serverpath,"olsa","CD 1")
    else:
        cdpath = os.path.join(serverpath,"olsa","CD 2")
    
    soundpath = os.path.join(cdpath, 'Liste'+str(Liste))
    soundfiles_path = [os.path.abspath(os.path.join(soundpath, x)) for x in os.listdir(soundpath)]
    soundfiles_path.sort()
    soundfiles_path = soundfiles_path[0:20]
    with open(serverpath + '/olsa/Liste20er/Liste'+str(Liste)+'.json', 'r') as fp:
        sentences = json.load(fp)        
    return sentences,soundfiles_path

def playolsa(serverpath,pegel,nr,Listengroesse):
    if security(pegel):
        tf = serverpath + '\olsa\CD 1\Liste1\CD1T1S'+str(nr)+'.wav'
        signal, fs = sf.read(tf, dtype='float32')  
        sd.play(signal,fs)  
        start_pause = time.time()
    return start_pause

def security(value):
    if value >= 80:
        print('Security Check Failed: {} dB Stimuli is > = 80 dB. \n Test-Stimuli not played!'.format(value))
        return False
    if value < 80:
        print('Security Check Succeeded: {} dB Stimuli is < 80 dB. \nPlayback Test-Stimuli...'.format(value))
        return True   

def savepath(serverpath,patientID):
    now = datetime.datetime.now()
    today = str(now.year)+'_'+str(now.month)+'_'+str(now.day)
    res_folder = os.path.join(serverpath,'ergebnisse',patientID,today)
    if not os.path.exists(res_folder):
        os.makedirs(res_folder)
    return res_folder    

def saveolsa(res_folder, pegel, finished, Liste, Listengroesse,Noisepegel):    
    file_pegel = open(res_folder+'/Liste_'+str(Liste)+'_Pegel_antwort.txt', 'w')
    for item in pegel:
        file_pegel.write("%.2f\n" % item)
    file_pegel.close()
    if finished == 1:
        AvrPegel = sum(pegel[12-1:]) / (Listengroesse-10)
        PatientSRT = round((AvrPegel - Noisepegel) * 100) / 100
        filename = res_folder+'/Liste_'+str(Liste)+'_srt.txt'
        file_srt = open(filename, 'w')         
        file_srt.write("%.2f\n" % PatientSRT)
        file_srt.close()
        print('SRT: ',PatientSRT)
        print('Files saved in: ', res_folder+'/Liste_'+str(Liste)+'_srt.txt')
        print('Olsa finished..Quit app, then me. ')
        

def count_rewind(scenepath,fs,Listengroesse,noiselen):
    wavinf = sf.info(scenepath)
    count_max = np.floor(wavinf.frames/(fs*noiselen))
    count_n = np.ceil(Listengroesse/count_max)
    arr_start = np.arange(0,count_max)                        
    arr_stop = np.arange(1,count_max+1)
    count_start = np.repeat(arr_start[None,:], count_n, axis=0)
    count_stop = np.repeat(arr_stop[None,:], count_n, axis=0)
    count_stop_array = count_stop.flatten()
    count_start_array = count_start.flatten() 
    return count_start_array,count_stop_array