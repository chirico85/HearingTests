#!/usr/bin/env python
"""
Created on Wed Mar 11 2020
@author: galindo

This is a python implementation of the speech test "adaptive OlSa" according to: 
Oldenburger Satztest - Handbuch und Hintergrundwissen - version vom 25.07.2000
Oldenburg sentence test - Manual and background knowledge - version from 25.07.2000
by HörTech gGmbH
references:
Wagener, K., Kühnel, V., Kollmeier, B. (1999a) „Entwicklung und Evaluation eines Satztests in deutscher Sprache I: Design des Oldenburger Satztests“. Z Audiol 38 (1), 4-15 
Wagener, K., Brand,T., Kollmeier, B. (1999b) „Entwicklung und Evaluation eines Satztests in deutscher Sprache II: Optimierung des Oldenburger Satztests“. Z Audiol 38 (2), 44-56 
Wagener, K., Brand,T., Kollmeier, B. (1999c) „Entwicklung und Evaluation eines Satztests in deutscher Sprache III: Evaluation des Oldenburger Satztests“. Z Audiol 38 (3), 86-95

Please read the above listed references before using to garantee correct working.

"""
import numpy as np
import time
import os, sys
from getfuncs import initparameters,startserver,playolsa,savepath,saveolsa,startparameters_prot
import os.path

# -*- coding: iso-8859-1 -*- 

class MyPaths:
    serverpath = os.path.abspath(os.path.dirname(sys.argv[0]))
    tempwav = serverpath + "/Scenes/tmp/szene_temp.wav"
    rootfolder = os.path.split(serverpath)[0]
    projname = os.path.split(serverpath)[1]    
    datapath = os.path.join(rootfolder,projname+'_data')

class MyScenes:
    szene_dic = {"office":"nopath", 
                 "livr":os.path.join(MyPaths.datapath,'Scenes','livingroom.wav'), 
                 "rest":os.path.join(MyPaths.datapath,'Scenes','restaurant.wav')}
class MyOlSa:
    def SRT_fixedLC(Sprachpegel,count,Antwort):
        Schrittweite = np.linspace(1,3,3)
        if count < 6:
            if Antwort == 5:
                Sprachpegel = Sprachpegel- Schrittweite[3-1]
            if Antwort == 4:
                Sprachpegel = Sprachpegel- round(Schrittweite[2-1]*10)/10
            if Antwort == 3:
                Sprachpegel = Sprachpegel- Schrittweite[1-1]     
            if Antwort == 2:
                Sprachpegel = Sprachpegel+ Schrittweite[1-1]     
            if Antwort == 1:
                Sprachpegel = Sprachpegel+ round(Schrittweite[2-1]*10)/10
            if Antwort == 0:
               Sprachpegel = Sprachpegel+ Schrittweite[3-1]
        else:
            if Antwort == 5:
                Sprachpegel = Sprachpegel- round(Schrittweite[2-1]*10)/10   
            if Antwort == 4:
                Sprachpegel = Sprachpegel- Schrittweite[1-1]     
            if Antwort == 1:
                Sprachpegel = Sprachpegel+ Schrittweite[1-1] 
            if Antwort == 0:
                Sprachpegel = Sprachpegel+ round(Schrittweite[2-1]*10)/10
        return Sprachpegel    
    
class UklappServer:
    switch = True 
    Header = ['Name','Verb','Zahl','Adjektiv','Objekt']
    Name = ['Britta','Doris','Kerstin','Nina','Peter','Stefan','Tanja','Thomas','Ulrich','Wolfgang']
    Verb = ['bekommt','gewann', 'gibt', 'hat', 'kauft', 'malt', 'nahm', 'schenkt', 'sieht', 'verleiht']
    Zahl = ['acht','achtzehn', 'drei', 'elf', 'fuenf', 'neun', 'vier', 'sieben', 'zwei', 'zwoelf']
    Adjektiv = ['alte','grosse', 'gruene', 'kleine', 'nasse', 'rote', 'schoene', 'schwere', 'teure', 'weisse']
    Objekt = ['Autos','Bilder', 'Blumen', 'Dosen', 'Messer', 'Ringe', 'Schuhe', 'Sessel', 'Steine', 'Tassen']
    preproc_alg = ['std','zoom','beam','ff','NH','training']
    CI_side = ['left', 'right']
    
    def __init__(self,ip,port,betterear,patientID):
        self.ip = ip
        self.port = port
        self.conn = startserver(self.ip,self.port)
        
        Liste = 1
        testtype = 'OlSa'
        count,Sprachpegel,Noisepegel,answers,Pegel,training,answers_time = initparameters()
        sentences,soundfiles_path = startparameters_prot(Liste, MyPaths.datapath)

        self.conn.send(testtype.encode('utf-8')) 
        
        BUFFER_SIZE = 4096
        Listengroesse = 2      # 20 Saetze
        vorl = 1 # Vorlaufzeit
        pau = 7 # Pause
        olsa_length = 3 # Durchchnittlänge eines Olsa Satzes
        noise_len = vorl+olsa_length # Länge Gesamtes Störgeräusch 
        print(MyPaths.serverpath)
        print(testtype)
        
        while self.switch == True:
            if not testtype:
                break
            if testtype == 'OlSa':
                data = self.conn.recv(BUFFER_SIZE).decode('utf-8')
                print('received data: ', data)
                if data == 'Start':
                    #  load+play noise
                    go2sleep = 0 + noise_len
                    self.conn.send(str(go2sleep).encode('utf-8')) #go2sleep added 21.09.2020
                    self.conn.recv(BUFFER_SIZE).decode('utf-8') #got it
                    self.conn.send(data.encode('utf-8'))                           
                    time.sleep(vorl)
                    start_pause = playolsa(MyPaths.datapath,Sprachpegel,count,Listengroesse)
                if data == 'Weiter':
                    end_pause = time.time()
                    elapsed_pause = end_pause - (start_pause + olsa_length)           
                    n_correct = len(list(set(sentences['Satz'+str(count)]) & set(answers)))   # n richtige Woerter, Saetze starten mit Satz1 -> count+1
                    print(n_correct)
                    print('server:'+ str(sentences['Satz'+str(count)]))
                    print('Patient:'+str(answers))
                    count += 1
                    Sprachpegel = MyOlSa.SRT_fixedLC(Sprachpegel,count,n_correct)                  # Berechne Sprachpegel abh. von n_correct
                    Pegel.append(Sprachpegel)                                                      # Speichere Pegel in Liste
                    print(Pegel)
                    print(count,Listengroesse)
                    if count <= Listengroesse:
                        finished = 0
                        res_folder = savepath(MyPaths.datapath,patientID)
                        saveolsa(res_folder, Pegel, finished, Liste, Listengroesse,Noisepegel)                        

                        if elapsed_pause < pau:
                            go2sleep = round(pau - elapsed_pause,1) + vorl + olsa_length
                            print('sleeping: ',str(go2sleep - vorl - olsa_length), ' seconds')
                            
                            self.conn.send(str(go2sleep).encode('utf-8'))
                            self.conn.recv(BUFFER_SIZE).decode('utf-8') #got it
                            self.conn.send(data.encode('utf-8'))  # echo 
                            time.sleep(go2sleep - vorl - olsa_length)
    #                        print(tosleep)
                        else:
                            go2sleep = 0 + vorl + olsa_length
                            self.conn.send(str(go2sleep).encode('utf-8'))
                           # tosleep = self.conn.recv(BUFFER_SIZE).decode('utf-8')
                            self.conn.send(data.encode('utf-8'))  # echo 
                        time.sleep(vorl)                  
                       
                        start_pause = playolsa(MyPaths.datapath,Sprachpegel,count,Listengroesse)                        
                        if start_pause == False:
                            pass
                        answers = [0] * 5
                    if count == Listengroesse+1:                                                
                        data = 'Ende'
                        finished = 1      
                        saveolsa(res_folder, Pegel, finished, Liste, Listengroesse,Noisepegel)                        
                        count,Sprachpegel,Noisepegel,answers,Pegel,training,answers_time = initparameters()              
                        self.conn.send(str(0).encode('utf-8')) # sleep val #dummy go2sleep added 21.09.2020
                        self.server_ende(self.conn,data)                        

                else:
                    if data in self.Name:               
                        answers[0] = data
                        answers_time[0] = time.time()
                        self.check_answers(answers)
                    if data in self.Verb:      
                        answers[1] = data
                        answers_time[1] = time.time()
                        self.check_answers(answers)
                    if data in self.Zahl:
                        if data == 'fuenf':
                            data = 'fünf'
                            print(data)
                        elif data == 'zwoelf':
                            data = 'zwölf' 
                        print(data)
                        answers[2] = data
                        answers_time[2] = time.time()
                        self.check_answers(answers)
                    if data in self.Adjektiv:
                        if data == 'gruene':
                            data = 'grüne'
                        elif data == 'schoene':
                            data = 'schöne'  
                        print(data)
                        answers[3] = data
                        answers_time[3] = time.time()
                        self.check_answers(answers)
                    if data in self.Objekt:
                        answers[4] = data
                        answers_time[4] = time.time()
                        self.check_answers(answers)
                
    def check_answers(self,answers):
        self.conn.send(str(0).encode('utf-8')) #dummy go2sleep added 21.09.2020
        print('in check answers: ',answers)
        self.conn.recv(4096).decode('utf-8') #got it

        if 0 not in answers:
            MSG = 'enable_button'
            try:
                self.conn.send(MSG.encode('utf-8'))  # echo
                print(MSG, 'sent') 
            except: 
                print('did not sent')    
        else:
            MSG = 'disable_button'
            try:
                self.conn.send(MSG.encode('utf-8'))  # echo
                print(MSG, 'sent') 
            except: 
                print('did not sent') 
                
            
    def server_ende(self,conn,data):
        conn.send(data.encode('utf-8'))  # echo
        
        
UklappServer('127.0.0.1',5007,'left','P31')