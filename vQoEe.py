# videoqoe.py
#(C) Sami Souihi
# -*- coding: iso-8859-1 -*-

############## IMPORTS ##################
try:
    try:
        from tkinter import *
    except:
        from Tkinter import *
except:
    raise ImportError('Wrapper Tk non disponible')
import ttk
from Tkinter import *
import random
import os
import json
import MySQLdb
import numpy
import subprocess
import time
import Tkinter
import sys
import threading 
from threading import Thread
import multiprocessing






############### 0) CLASESSES ####################################

    


############## I) Variables globales##################
ident=0
data_user=[]
bwd="0"
rateT="0"
loss="0"
delay="0"
jitter="0"
root=""
pbar = ""
LabelProgress = ""   
nb1 = 0 	


## * * * ".config"
#- - - BDD - - -
ip_sql_server = "10.12.20.56"
user_sql = "root"
password_sql = "paris2015"

#- - -  - - -
inter_sortie = "eth0"
adressIPping = "10.12.20.131" # 192.168.43.1 (PA) // 10.12.20.56 (grand) // 10.12.20.131 (moy)
netw_type = "EATHERNET"
videoId = "1"

# --- Test Iperf
Tiperf = "iperf"

#--Fenetres
IuserProfilWindows = "1200x1400+350+50"
IprogressBarWindows = "1400"
IpricipalWindows = "1900x2200+50+30"
IfeedbackWindwos = "1800x1350+20+20"

############## Fin Variables globales ##################


########""""" II) Declaration des fonction et methodes"""""""""""""""""""""""""""

## (1) initialisation
def dbInit():
    db = MySQLdb.connect(ip_sql_server, user_sql, password_sql, "BDD_FIXE")
    cursor = db.cursor()
    print "Intialisation db -ok-"
    return db,cursor

## (2) Fermeture du connecteur db
def dbClose(db):
    db.close()


# (3) Fermeture application
def appExit(Mafenetre,db):
    dbClose(db)
    os.system("wondershaper clear "+inter_sortie+"")
   # os.system("tc qdisc del dev "+inter_sortie+" root handle 1:1 netem")
    Mafenetre.destroy()
    

# (4) Fin application
def saveandexit(s,a):
    s.destroy()
    audio=a
    print a


## (5) Sauvgarde ou/et mise a jour BDD ppur les facteurs colleectes 
def dbSaveCaracteristics(cursor,data,db):
   global ident
   db.commit()
   cursor.execute('UPDATE qod_metrics SET codec=%s, videoId=%s, bwd=%s,  bwdT=%s, loss=%s, delay=%s, jitter=%s, frame_rate=%s, frame_loss=%s, audio_rate=%s, audio_loss=%s, bitrate=%s, cpu_mhz_moy=%s ,cpu_mhz_avg=%s, cpu_nbr=%s, cpu_core_nbr=%s, stepping=%s, cpu_bigo_mips=%s,carte_class=%s, screen_resolotion=%s, screen_dimension=%s, screen_mhz=%s, screen_blug_type=%s, ram_clock_speed=%s, ram_size=%s,ram_used_moy=%s, ram_used_avg=%s   WHERE id=%s', (data["codec"],data["videoId"],data["bwd"], data["rateT"], data["loss"],data["delay"],data["jitter"], data["frame_rate"],data["frame_loss"],data["audio_rate"],data["audio_loss"],data["bitrate"], data["cpu_mhz_moy"],data["cpu_mhz_avg"],data["cpu_nbr"],data["cpu_core_nbr"], data["stepping"],data["cpu_bigo_mips"],data["carte_class"],data["screen_resolotion"],data["screen_dimension"],data["screen_mhz"],data["screen_blug_type"],data["ram_clock_speed"],data["ram_size"], data["ram_used_moy"], data["ram_used_avg"] , int(ident)) )

   db.commit()

## (6) Sauvgarde ou/et mise a jour BDD du retour utilisateur : QUESTIONS
def dbSaveFeedback(cursor,mydata,db):
   global ident
   db.commit()
   cursor.execute('UPDATE qod_metrics SET q21 ,q22 ,q23 ,q24 , mos,pb_blocage, pb_balckScreen, pb_audio, network_type   WHERE id=%s', (mydata["q21"] ,mydata["q22"] , mydata["q23"] ,mydata["q24"], mydata["mos"], mydata["pb_blocage"], mydata["pb_balckScreen"], mydata["pb_audio"], mydata["network_type"] , int(ident)) )

   db.commit()

## (7) Evaluation QoS: QUESTIONS
def QosEvaluation():
   global ident
   global bwd
   global rateT
   global loss
   global delay
   global jitter
   global nb1
   # (c0) ---------- RECUPERATION Bandwidth (BWD)  ---------------  
   #**** Genaration de la bande passante (BWD)
   json_params=open('params.json')
   data = json.load(json_params)
   


   #  nb2 = random.randint(1,2)
   #  if nb2 == 1 :
   #  rateT = "2048"
   #  else:
   #  rateT = "1024"
     

   
   if  nb1 == 0 : 
        #Change Rate Tehorique
        nb =random.randint(1,8)
        rateT= data[1].get("p"+str(nb))
        #Change QoS Param
        print "WONDERSHAPER ****  COMBINAISON "
        bwd_cmd = "wondershaper "+inter_sortie+" "+rateT+" "+rateT+"" 
        os.system(bwd_cmd)
        os.system("iperf -c "+adressIPping+" > Fiperf ")
        
        bwd = subprocess.Popen('cat Fiperf | grep sec | cut -c34-41',shell=True, stdout=subprocess.PIPE).communicate()[0]
        print "BANDE PASSANTE = " +  bwd      
        
       # (c1) ---------- RECUPERATION PING (loss-delay-gigue)  ---------------  
        os.system("rm Fping; ping  "+ adressIPping +" -c 15  > Fping")
        loss = subprocess.Popen('cat Fping | grep loss | cut -c37-40',shell=True, stdout=subprocess.PIPE).communicate()[0]

   
   print "1) LOSS = " +  loss 
    
   PingInfos = subprocess.Popen('cat Fping | grep rtt | cut -c24-64',shell=True, stdout=subprocess.PIPE).communicate()[0]
   pingTab = GetPartSentence(PingInfos) 
   delay = pingTab[1]
   print "2) DELAY = " +  delay
   jitter = pingTab[3]
   print "3) GIGUE = " +  jitter 


##############################---- FONCTION A RE-UTILISER--------

 # 1) Fonction  de la virgule (,) dans string a float 
 # ==> st : Number in form of string  with ','   -->  have just the decimal value
def Str_with_comma(st):
    viv = ''
    for ii in xrange(1, len(st)):
              if st[ii] is ',' :
                  break;
              else : 
                  viv = viv + st[ii]
    return viv


 # 2) Fonction qui nous donne les partie d'une phrase separee par "/"
 #  sent : Phrase a separer. 
def GetPartSentence(sent):
    tabSentence = []
    wd = ""
    j = 1
    for ii in xrange(1, len(sent)):
              if sent [ii] is not '/' :
                   wd = wd + sent [ii] 
                   if sent [ii] is ' ':
                         break;     
              else : 
                  tabSentence.insert(j,wd)
                  j = j+1 
                  wd = ""
                  
    tabSentence.insert(j,wd)
    return tabSentence


 # 3) Fonction to get NeTem combinition
def getNetemCombinaison(n):
    return {
             1 : "tc qdisc add  dev "+inter_sortie+" root handle 1:1 netem delay 100ms 10ms 25%  distribution normal loss  5% 25% corrupt 5 reorder 25% 50%", # 2
             2 : "tc qdisc add  dev "+inter_sortie+" root handle 1:1 netem delay 1ms 1ms 1%    distribution normal loss  1% 1% corrupt 20 reorder 1% 1%", # 7
             3 : "tc qdisc add  dev "+inter_sortie+" root handle 1:1 netem delay 100ms 10ms 25%  distribution normal loss  5% 25% corrupt 5 reorder 25% 50%",
             4 : "tc qdisc add  dev "+inter_sortie+" root handle 1:1 netem delay 500ms 1ms 1%     distribution normal loss  1% 1% corrupt 1 reorder 1% 1%",
             5 : "tc qdisc add  dev "+inter_sortie+" root handle 1:1 netem delay 100ms 10ms 1%       distribution normal loss  1% 1% corrupt 1 reorder 1% 1%",
             6 : "tc qdisc add  dev "+inter_sortie+" root handle 1:1 netem delay 500ms 100ms 2%  distribution normal loss  1% 1% corrupt 1 reorder 1% 1%",
            }[n]

 # 3) Fonction to get NeTem combinition
def getVideoURL(n):
    return {
             1 : "https://www.youtube.com/watch?v=FWinObVeBFg", # 1 film loup
             2 : "https://www.youtube.com/watch?v=MyV2ufbr670", # 2 dragon ball https://www.youtube.com/watch?v=MyV2ufbr670  
             3 : "https://www.youtube.com/watch?v=0Dti0Qt7a3k", # 3 film action
            }[n]



##########################################################################################################
####### ----- CLICKED BOUTONS ---------
##########################################################################################################

### (A) Recuperation des informations du testeur : Boutton Nouveau utilisateur ()
def userProfileWindow(cursor,d):
    global userProfileBtn
    # BoutonLancer.config(state='norm')
    newWindow=Toplevel()
    newWindow.geometry(IuserProfilWindows)
    newWindow.grab_set()
    newWindow.focus_set()
    newWindow.resizable(False,False)
    newWindow.title("Veuillez saisir votre profil")

    ##  ------------ Parametres Feedback  ------------------------------------------------------------
    ##  ----------------------------------------------------------------------------------------
    Labelaff = Label( newWindow, text="Profil participant aux  tests", fg="purple",font =("Helv etica", "48", "bold italic underline") )
    Labelaff.pack (anchor=CENTER)

    # Espace ---------- 0 ---------------
    label1=Label(newWindow, height = 7, width = 40)
    label1.pack()

    # (a) ---------- Age ---------------
    Labelage= Label(newWindow, text = "1) Votre age",font =("Helvetica", "25", "bold "), fg="red")
    Labelage.pack(anchor=CENTER)
    v_age = StringVar()
    v_age.set("0")
    age=Entry(newWindow, width=20, justify='right',  fg="red", textvariable=v_age, font =("Helvetica", "20", "bold ")) 
    age.pack(anchor=CENTER)

     # Espace ---------- 1 ---------------
    label1=Label(newWindow, height = 5, width = 40)
    label1.pack()

     # (b) ---------- Sexe ---------------
    Labelsex= Label(newWindow, text = "2) Votre sexe", fg="orange",font =("Helvetica", "25", "bold "))
    Labelsex.pack(anchor=CENTER)
    MODES1 = [
        ("Homme","homme"),
        ("Femme", "femme"),
    ]
    v1 = StringVar()
    v1.set("homme") # initialize
    for text, mode in MODES1:
        bs1 = Radiobutton(newWindow, text=text, variable=v1, fg="orange", value=mode, font =("Helvetica", "20"))
        bs1.pack(anchor=CENTER)
    

    # Espace ------------ 2 -------------
    label1=Label(newWindow, height = 5, width = 40)
    label1.pack()


    # (c) ---------- Niveau Etude ---------------
    Labelscol= Label(newWindow, text = "3) Votre niveau scolaire",  fg="green",font =("Helvetica", "25", "bold "))
    Labelscol.pack(anchor=CENTER)
    MODES2 = [
        ("Superieur","Superieur"),
        ("Lycee","Lycee"),
        ("College","College"),
        ("Primaire","Primaire"),
        ("Autre","Autre"),
    ]
    v2 = StringVar()
    v2.set("Superieur") # initialize
    for text, mode in MODES2:
        bs2 = Radiobutton(newWindow, text=text, variable=v2, value=mode, fg="green", font =("Helvetica", "20"))
        bs2.pack(anchor=CENTER)
    

    # Espace ------------ 3 -------------
    label1=Label(newWindow, height = 5, width = 40)
    label1.pack()

    # (d) ---------- Affinite Video ---------------
    Labelaff= Label(newWindow, text = "4) Votre Affinite avec les videos en ligne", fg="blue",font =("Helvetica", "25", "bold "))
    Labelaff.pack(anchor=CENTER)
  
    MODES = [
        ("Oui","oui"),
        ("Non", "non"),
    ]
    v3 = StringVar()
    v3.set("oui") # initialize
    for text, mode in MODES:
        bs3 = Radiobutton(newWindow, text=text, variable=v3, value=mode, fg="blue", font =("Helvetica", "20"))
        bs3.pack(anchor=CENTER)

    # Espace ------------ 4 -------------
    label1=Label(newWindow, height = 3, width = 30)
    label1.pack()


    # (-) ---------- BOUTTON CLICK () ---------------
    buttonPrint=Button(newWindow, text="Save and Exit", font =("Helvetica", "22", "bold ") , command = lambda: mQuestionsUser(v_age,v1,v2,v3,newWindow,cursor,d)) #, saveandexit(newWindow,4))
    buttonPrint.pack(anchor=CENTER)
    
     # (-) ---------- PROGRESS BAR AND LABEL ---------------
    global pbar
    global LabelProgress
    LabelProgress= Label(Mafenetre, text = "La connexion au serveur de test est en cours. Veuillez patientez. ",font =("Helvetica", "26", "bold "), fg="orange")
    LabelProgress.pack(anchor=CENTER)
    pbar = ttk.Progressbar(Mafenetre, orient ="horizontal",length = IprogressBarWindows, mode ="determinate" )
    pbar.pack()
    pbar.start(15)
    

## (A.1) *** FONCTION ** : Insertion du profil utilisateur (preparer aussi pour les autres videos)
def mQuestionsUser(v1,v2,v3,v4,w,cursor,db):
    global data_user
    global ident	
    global pbar
 

    ## Get the last "id" for the database
    cursor.execute("SELECT MAX(id) FROM qod_metrics")
    result_set = cursor.fetchall()
    for row in result_set:
       try:
          ident = row[0] 
       except: 
          ident=1
       pass 

     # * - - - * INCRIMENTER (ID)
    ident= int(ident) + 1        

    # (a) ---------- Former data et INSERTION  ---------------
    data_user = {"q11" : v1.get(), "q12" : v2.get(), "q13" : v3.get(), "q14" : v4.get()}
    cursor.execute('INSERT INTO qod_metrics (id, age, sexe , scolarschip, familiarity, videoId) VALUES ("%d","%s","%s","%s","%s","%s")' % (int(ident), data_user["q11"],data_user["q12"],data_user["q13"],data_user["q14"], videoId))
    db.commit()
    saveandexit(w,4)
  

    
   
   # (c0) ---------- RECUPERATION Bandwidth (BWD)  ---------------  
    QosEvaluation()



   # (d) ---------- MISE A JOUR BOUTTONS  ---------------
    userProfileBtn.config(state="disable")
    BoutonLancer.config(state='norm')
    
   # (d) ---------- CHANGEMENT Label et SUPPRESSION BAR PROGRESS  --------------- 
    pbar.destroy()
    LabelProgress.config(text="Connexion Etablie ..." ,font =("Helvetica", "32", "bold "), fg="green")
    LabelProgress.update_idletasks()
    LabelProgress.pack(anchor=CENTER)
    pbar = ttk.Progressbar(Mafenetre, orient ="horizontal",length = IprogressBarWindows, mode ="determinate" )



    

##########################################################################################################
##########################################################################################################
## (B) New Test : Button Lancer ()
def newTest(cursor):
    global bwd
    global loss
    global delay
    global jitter
    global nb1


    # Label Update
    LabelProgress.config(text="Chargement de la video et des questions. Veuillez patientez " ,font =("Helvetica", "32", "bold "), fg="red")
    LabelProgress.update_idletasks()

    ##  ------------ Parametres QoS  ------------------------------------------------------------
    ##  ----------------------------------------------------------------------------------------
    
    # (1) ---------- Recuperation URLs  ---------------
     
    nb1 = (nb1+1)%3
    videoId = ""
    

    # Recuperate the URL WITH AN INTEGER 1, 2 OR 3
    url= getVideoURL(nb1+1)
    
    print " ID **** VIDEO = "+ videoId
    videoId = str(nb1+1)
     # (2) ---------- CHOIX du CODEC ---------------
    json_params=open('params.json')
    data = json.load(json_params)
    nbb = random.randint(1,6)
    codec= data[0].get("p"+str(nbb))

    print "CODEC 55 === "+ str(codec)



    # (3) ---------- LANCEMENT PLAYER + Fichers stats + caracteristics RAM et CPU  ---------------

    proc = subprocess.Popen(['rm stats; rm stats2; rm RAMrate; rm CPUmhz; touch stats;touch stats2; touch RAMrate; touch CPUmhz; while true; do top -b -d1 -n1 | grep -i "Cpu(s)" | cut -c10-14 | sed -n 1p >> RAMrate; lscpu | grep CPU\ MHz |  cut -c23-32 >>  CPUmhz ; echo stats; sleep 3; done | vlc -vv --fullscreen  --file-logging --logfile=stats2 --preferred-resolution '+str(codec)+' --play-and-exit  -I rc  '+ url +' >> stats'], shell=True)
    time.sleep(41) # <-- There's no time.wait, but time.sleep.
    pid = proc.pid # <--- access `pid` attribute to get the pid of the child process
    proc.terminate()
  

     # (4) ---------- Recuperation CPU used ---------------
    cpu_MHz = subprocess.Popen('lscpu | grep CPU\ MHz |  cut -c24-32',shell=True, stdout=subprocess.PIPE).communicate()[0]   
    print "- cpu_MHz = " + str(cpu_MHz)

      # (5) ---------- Recuperation RAM rate ---------------
    ram_rate = subprocess.Popen('top -b -d1 -n3 | grep -i "Cpu(s)" | cut -c10-14 | sed -n 3p',shell=True, stdout=subprocess.PIPE).communicate()[0]  
    print "- RAM used  (%)= " + str(ram_rate) 


     # (6) ---------- Active "New measure" Button --------------------
    videoEvaluationWindow(cursor,db) ### A prevoir l'envoi de data
    


    ##  ----------------------------------------------------------------------------------------
    ##  ------------ Parametres QoA ------------------------------------------------------------
    ##  ----------------------------------------------------------------------------------------
    i=0

   # (a1) ----- Frame rate : it's the number of video frame decoded in 1 second  -------------------------------------------
    with open("stats") as fp:
        list_frame_rate =['0']
        old_FR = 0
        val_FR = 0
        list_FR = ['0']
        for line in iter(fp.readline, ''):
              if line.startswith("| video decoded"):
                 un, deux = line.split(":")
                 trois, quatre = deux.split('\n')
                 list_frame_rate.insert(i, int(trois))
                 # Recuperation des FR chaque periode
                 val = float(list_frame_rate[0])
                 val_FR =  val - float(old_FR)
                 val_frame_rate =  (val - old_FR)/3
                 print " Frame rate  = " + str(val_frame_rate)
		 list_FR.insert(i,val_frame_rate)
                 old_FR = val

    mean_frame_rate = numpy.mean(list_FR[3:8])
    print " 1) - Mean of the Frame rate is : " + str(mean_frame_rate)
   

   # (a2) ---- Frame loss : It's the average  video frame loss number in 1 second-----------------------------------------
    with open("stats") as fp:
         list_frame_loss =['']
         for line in iter(fp.readline, ''):
                if line.startswith("| frames lost"):
                   un, deux = line.split(":")
                   trois, quatre = deux.split('\n')
                   #print " Frame loss  == " +  trois
                   list_frame_loss.insert(i, int(trois))
                   #print " Frame loss == " + str(list_frame_rate[i])   

    mean_frame_loss = numpy.mean(list_frame_loss[3:8])
    print " 2) - Mean of the frame loss is : " + str(mean_frame_loss)
   


    # (a3) ---- Audio Bit rate -----------------------------------------
    with open("stats") as fp:
         list_audio_decoded =['0']
         old_AD = 0
         val_AD = 0
         list_AD  =['0']
         for line in iter(fp.readline, ''):
                if line.startswith("| audio decoded"):
                   un, deux = line.split(":")
                   trois, quatre = deux.split('\n')
                   # Recuperation des AD chaque periode
                   list_audio_decoded.insert(i, int(trois))
                   val = float(list_audio_decoded[0])
                   val_AD =  val - float(old_AD)
                   val_audio_decoded =  (val - old_AD)/3
                   print " Audio bitrate  = " + str(val_audio_decoded)
                   old_AD = val
                   list_AD.insert(i,val_audio_decoded)

    mean_audio_bitrate = numpy.mean(list_AD[3:8])
    print " 3) - Mean of the audio bitrate is : " + str(mean_audio_bitrate)
   

    # (a4) ---- Audio loss -----------------------------------------
    with open("stats") as fp:
         list_audio_loss =['']
         for line in iter(fp.readline, ''):
                if line.startswith("| buffers lost"):
                   un, deux = line.split(":")
                   trois, quatre = deux.split('\n')
                   #print " Audio loss  == " +  trois
                   list_audio_loss.insert(i, int(trois))
                   #print " Audio loss == " + str(list_frame_rate[i])   

    mean_audio_loss = numpy.mean(list_audio_loss[3:8])
    print " 4) - Mean of the audio loss is : " + str(mean_audio_loss)
   

   # (a5)---  Bitrate--------------------------------------------------------------------------
    with open("stats") as fp:
        list_birate =['']
        for line in iter(fp.readline, ''): 
            if line.startswith("| input bitrate"):
               un, deux = line.split(":")
               trois, quatre = deux.split("kb")
               #list_birate.append()
               list_birate.insert(i, int(trois))
               #print " bitrate == " + str(list_birate[i])     
        
    mean_bitrate = numpy.mean(list_birate[3:8])
    print " 5) - Mean bitrate is : " + str(mean_bitrate)
    
  # (d1)---  RAM rate --------------------------------------------------------------------------
    list_ram_rate = []
    for n in xrange(1, 11):
            val = subprocess.Popen('cat RAMrate | sed -n  '+str(n)+'p',shell=True, stdout=subprocess.PIPE).communicate()[0]
    	    print "VAL RAM rate = " + Str_with_comma(val) 
            list_ram_rate.append(float(Str_with_comma(val)))
               
    mean_ram_rate = numpy.mean(list_ram_rate[1:10])
    print " 6) - Mean of the RAM rate is : " + str(mean_ram_rate)
    std_ram_rate = numpy.std(list_ram_rate[1:10])
    print " 7) - Standard diviation of the RAM rate is : " + str(std_ram_rate)

  # (d2)---  CPU MHZ --------------------------------------------------------------------------
    list_cpu_mhz = []
    for n2 in xrange(1, 11):
            val = subprocess.Popen('cat CPUmhz | sed -n  '+str(n2)+'p',shell=True, stdout=subprocess.PIPE).communicate()[0]
    	    print "VAL cpu_mhz = " + Str_with_comma(val) 
            list_cpu_mhz.append(float(Str_with_comma(val)))
               
    mean_cpu_mhz = numpy.mean(list_cpu_mhz[1:10])
    print " 8) - Mean of the RAM rate is : " + str(mean_cpu_mhz)
    std_cpu_mhz = numpy.std(list_cpu_mhz[1:10])
    print " 9) - Standard diviation of the RAM rate is : " + str(std_cpu_mhz)


    ##  ----------------------------------------------------------------------------------------
    ##  ------------ Parametres QoD ------------------------------------------------------------
    ##  ----------------------------------------------------------------------------------------

    #  01) CPU parameters -  --   --  --   --   --   --   --   --  --   --   --   --   --   --  --   --   --   -- 
    os.system("echo '  * * *  DEVICE CARACTERISTICS  '")
    os.system("echo '  I) CPU '")
    cpu_number = subprocess.Popen('lscpu | grep CPU\(s\): |  cut -c24-32 | head -n1',shell=True, stdout=subprocess.PIPE).communicate()[0]   
    print "1) cpu_number = " + str(cpu_number)
    core_number = subprocess.Popen('lscpu | grep Core |  cut -c24-24',shell=True, stdout=subprocess.PIPE).communicate()[0]   
    print "2) core_number = " + str(core_number) 
    stepping = subprocess.Popen('lscpu | grep Stepping |  cut -c24-24',shell=True, stdout=subprocess.PIPE).communicate()[0]   
    print "3) Stepping = " + str(stepping)
    bogo_MIPS = subprocess.Popen('lscpu | grep Bogo |  cut -c24-32',shell=True, stdout=subprocess.PIPE).communicate()[0]   
    print "4) bogo_MIPS = " + str(bogo_MIPS)
   
     # 02) SCREEN parameters  -  --   --  --   --   --   --   --   --  --   --   --   --   --   --  --   --   --   -- 
     # Carte graphique Metrics 
    carte_type = subprocess.Popen('lspci -vm | grep VGA -A 12 | grep SDevice | head -n1 | cut -c10-24 ',shell=True, stdout=subprocess.PIPE).communicate()[0]   
    print "a) Carte graphique = " + str(carte_type)
  
    # SCREEN Metrics  - - - - - - - - - - - - - - - - - - - - - - - -- -- 
    current_screen = subprocess.Popen('xrandr -q | grep -w current | cut -c37-47',shell=True, stdout=subprocess.PIPE).communicate()[0]   
    print "b) Current Screen = " + str(current_screen)
    # type Fiche (LVDS, HDMI, VGA)
    blug_type = subprocess.Popen('xrandr -q | grep -w primary |cut -c1-6',shell=True, stdout=subprocess.PIPE).communicate()[0]   
    print "c) Blug_type = " + str(blug_type)
    screen_MHz = subprocess.Popen('xrandr --verbose | grep MH | grep current  | cut -c21-25',shell=True, stdout=subprocess.PIPE).communicate()[0]   
    print "d) screen_MHz = " + str(screen_MHz)
    
    screen_dimension = subprocess.Popen('xdpyinfo | grep dimension | cut -c36-42',shell=True, stdout=subprocess.PIPE).communicate()[0]   
    print "e) screen_dimension = " + str(screen_dimension)

     # 03) RAM parameters   -  --   --  --   --   --   --   --   --  --   --   --   --   --   --  --   --   --   -- 
    clock_speed = subprocess.Popen('dmidecode -t 17 | grep Clock | grep MH | cut -c25-30 | head -n1',shell=True, stdout=subprocess.PIPE).communicate()[0]   
    print "i) clock speed = " + str(clock_speed)
    
    ram_size = subprocess.Popen('dmidecode -t 17 | grep Size | sed -n 2p | cut -c8-12',shell=True, stdout=subprocess.PIPE).communicate()[0]   
    print "ii) RAM size = " + str(ram_size)


 
    ##  ------------ Formation de la DATA ------------------------------------------------------------
    ##  ----------------------------------------------------------------------------------------


    data = {"codec" : codec, "bwd" : bwd, "rateT" : rateT, "loss" : loss, "delay" : delay, "jitter" : jitter, "frame_rate" : mean_frame_rate,"frame_loss" : mean_frame_loss,"audio_rate" : mean_audio_bitrate, "audio_loss" : mean_audio_loss,"bitrate" : mean_bitrate,"cpu_mhz_moy" : mean_cpu_mhz, "cpu_mhz_avg"  : std_cpu_mhz, "cpu_nbr" : cpu_number, "cpu_core_nbr"  : core_number, "stepping" : stepping, "cpu_bigo_mips"  : bogo_MIPS, "carte_class" : carte_type, "screen_resolotion" :  current_screen, "screen_dimension" : screen_dimension, "screen_mhz" : screen_MHz, "screen_blug_type" : blug_type, "ram_clock_speed" : clock_speed, "ram_size"  : ram_size, "ram_used_moy" : mean_ram_rate, "ram_used_avg" : std_ram_rate, "videoId" : videoId }
    dbSaveCaracteristics(cursor,data,db)

    print " ** * *  UPDATE 2 -OK- "
    
   # try:
 #      os.system("tc qdisc del dev "+inter_sortie+" root handle 1:1 netem") 
 #   except IOError: 
  #     print "ERROR DELETING LINK "
    
    # -------------- Activer le boutton ------------------------
    videoEvalBtn.config(state='norm')
    
    
### (C) Feedback utilisateur (Juste apres la fin de la video) : Boutton Lancer () 
def videoEvaluationWindow(cur,d):  # 
    global loss
    global delay
    global jitter
    global bwd
    #global bwdT
    global ident

    # Label Update
    LabelProgress.config(text="Connexion au serveur de donnees. Veuillez patientez " , fg="blue")
    LabelProgress.update_idletasks()


     # Desactiver Boutton Lancement    
    BoutonLancer.config(state='disable')
    videoEvalBtn.config (state='disable')  


    qoeWindow=Toplevel()
    qoeWindow.geometry(IfeedbackWindwos)
    qoeWindow.title("Veuillez entrer votre valuation")
    # Creation d'un widget Scale
    

    Labelaff = Label( qoeWindow, text="Valuation de la video", fg="purple",font =("Helv etica", "48", "bold italic underline") )
    Labelaff.pack (anchor=CENTER)


    # - Temps de debut
    q21Val = StringVar()
    q21Val.set(3)
    q21 = Scale(qoeWindow,from_=1,to=5,resolution=1,orient=HORIZONTAL,\
    length=570,width=40,label="Rapidite de lancement de la video [(1): Tres lent // (5): Tres rapide] ",tickinterval=1,variable=q21Val, font =("Helvetica", "14", "bold") )
    q21.pack(padx=1,pady=1, anchor=CENTER)

    MODES11 = [
        ("Oui","oui"),
        ("Non","non"),
    ]
    # --- ECRAN NOIR
    v11 = StringVar()
    v11.set("non") # initialize
    Labelaff = Label( qoeWindow, text="Ecran noir", fg="blue",font =("Helvetica", "20", "bold italic underline") )
    Labelaff.pack (anchor=CENTER)
    for text, mode in MODES11:
        bs22 = Radiobutton(qoeWindow, text=text, variable=v11, value=mode,fg="blue", font =("Helvetica", "14", "bold"))
        bs22.pack(anchor=CENTER)


   # Espace ---------- 1 ---------------
    #label1=Label(qoeWindow, height = 1, width = 40)
    #label1.pack()
   

    # --- Decallage entre Son et image
    q22Val = StringVar()
    q22Val.set(3)
    q22 = Scale(qoeWindow,from_=1,to=5,resolution=1,orient=HORIZONTAL,\
    length=820,width=40,label="Decalage entre le son et la video ? [(1): Bcp de decalage // (5): Pas de decalage]",tickinterval=1,variable=q22Val,  font =("Helvetica", "13", "bold"))
    q22.pack(padx=1,pady=1, anchor=CENTER)

    # --- BEAUCOUP DE BLOCAGES	
    v22 = StringVar()
    v22.set("non") # initialize
    Labelaff2 = Label( qoeWindow, text="Beaucoup de blocages", fg="orange",font =("Helvetica", "20", "bold italic underline") )
    Labelaff2.pack (anchor=CENTER)
    for text, mode in MODES11:
        bs33 = Radiobutton(qoeWindow, text=text, variable=v22, value=mode,fg="orange", font =("Helvetica", "14", "bold"))
        bs33.pack(anchor=CENTER)


   # Espace ---------- 2 ---------------
    #label1=Label(qoeWindow, height = 1, width = 40)
    #label1.pack()
   
    # --- QUALITE IMAGE
    q24Val = StringVar()
    q24Val.set(3)
    q24 = Scale(qoeWindow,from_=1,to=5,resolution=1,orient=HORIZONTAL,\
    length=500,width=40,label="Qualite de l'image [(1): Tres mauvaise // (5): Tres bonne]", tickinterval=1,variable=q24Val, font =("Helvetica", "14", "bold"))
    q24.pack(padx=1,pady=1, anchor=CENTER)
    
    # --- QUALITE SON
    q25Val = StringVar()
    q25Val.set(3)
    q25 = Scale(qoeWindow,from_=1,to=5,resolution=1,orient=HORIZONTAL,\
    length=500,width=40,label="Qualite de la voix [(1): Tres mauvaise // (5): Tres bonne]",tickinterval=1,variable=q25Val, font =("Helvetica", "14", "bold"))
    q25.pack(padx=1,pady=1, anchor=CENTER)

  # --- BEAUCOUP DE BLOCAGES	
    v33 = StringVar()
    v33.set("non") # initialize
    Labelaff3 = Label( qoeWindow, text="Pas de son ", fg="red",font =("Helvetica", "20", "bold italic underline") )
    Labelaff3.pack (anchor=CENTER)
    for text, mode in MODES11:
        bs44 = Radiobutton(qoeWindow, text=text, variable=v33, value=mode, fg="red",font =("Helvetica", "14", "bold"))
        bs44.pack(anchor=CENTER)

    # Espace ---------- 3 ---------------
    #label1=Label(qoeWindow, height = 4, width = 40)
    #label1.pack()

    # --- QUALITE GLOBALE - MOS - 
    q23Val = StringVar()
    q23Val.set(3)
    q23 = Scale(qoeWindow,from_=1,to=5,resolution=1,orient=HORIZONTAL,\
    length=720,width=48,label="Qualite de la video (de facon globale) [(1): Tres mauvaise // (5): Tres bonne]",tickinterval=1,variable=q23Val,font =("Helvetica", "16", "bold"))
    q23.pack(padx=3,pady=3, anchor=CENTER)

    ## ENVOI ---->
    buttonPrint=Button(qoeWindow, text="Save and Exit",font =("Helvetica", "20", "bold"), command = lambda: mFeedbackUser(q21Val,q22Val,q24Val,q25Val,q23Val,qoeWindow,cur,d, v11,v22,v33)) 
    buttonPrint.pack()


## (6) Definition de la fonction de mise a jours de la BDD apres le feedback utilisateur
def mFeedbackUser(v1,v2,v3,v4,v5,w,cursor,db,v11,v22,v33):
    global ident
    print "q21 ==1=== " + str(v1.get())
    print "q22 ===== "+ str(v2.get())
    print "q23 ===== "+ str(v3.get())
    print "q24 ===== "+ str(v4.get())
    print "q25 ===== "+ str(v5.get())
    print "VVVVVV111 == "+ str(v11.get())
    print "VVVVVV222 == "+ str(v22.get())
    print "VVVVVV333 == "+ str(v33.get())
    data_feedback = {"q21" : v1.get(), "q22" : v2.get(), "q23" : v3.get(), "q24" : v4.get(), "blocage" : v11.get(), "black" : v22.get(), "audio" : v33.get(), "typeN" :  netw_type ,  "mos" : v5.get()  }
    cursor.execute('UPDATE qod_metrics SET q21=%s, q22=%s, q23=%s, q24=%s, pb_blocage=%s, pb_balckScreen=%s, pb_audio=%s, network_type=%s, mos=%s WHERE id=%s' , (data_feedback["q21"],data_feedback["q22"],data_feedback["q23"],data_feedback["q24"],data_feedback["blocage"],data_feedback["black"],data_feedback["audio"],data_feedback["typeN"],data_feedback["mos"],ident))
    db.commit()
    saveandexit(w,4)
    os.system('tc qdisc del dev '+inter_sortie+' root')


# 2222222222222222222222222222222222222222222222



#**** RECUPERATION de la bande passante (BWD)   
    QosEvaluation()

    print " ** * *  UPDATE ENVOYE APRES QUESTIONNAIRES - - -  -OK- "


#**** METTRE A JOUR LABEL - - - - -
    LabelProgress.config(text="Connexion Etablie.." ,font =("Helvetica", "32", "bold "), fg="green")
    LabelProgress.update_idletasks()


#### (D) Boutton insert existant utilisateur pour une nouvelle mesure : Nouvelle mesure boutton () 
def InsertExistantUser(cursor,d):
    global ident
    global loss
    global delay
    global jitter
    global bwd
    # global bwdT
    ident = ident+1
    cursor.execute('INSERT INTO qod_metrics (id, age, sexe , scolarschip, familiarity, videoId) VALUES ("%d","%s","%s","%s","%s","%s")' % (int(ident), data_user["q11"],data_user["q12"],data_user["q13"],data_user["q14"], videoId))
    db.commit()
    newTest(cursor)
   
    ### DESACTIVE  - New Test Button -
    videoEvalBtn.config (state='disable')


 

    
    # - - - - -  RECUPERATION PING (loss-delay-gigue)  -New Test- 
    QosEvaluation()

    ### ACTIVE  - New Test Button -
    videoEvalBtn.config (state='norm')     


#######################################################################################################
############# PROGRAMME PRINCIPAL #####################################################################
#######################################################################################################
# Creation de la fenetre principale (main window)
Mafenetre = Tk()

db,cursorDB=dbInit()

Mafenetre.title('*********** TEST STANDARD*************************')
Mafenetre.geometry(IpricipalWindows)


#Creation d'un Label UPEC 
#photo = PhotoImage(file="/home/lissi/app_fixe/ressources/UPEC.gif")
#w = Label(Mafenetre, image=photo)
#w.photo = photo
#w.pack()

# Espace 1
label1=Label(Mafenetre, height = 8, width = 40)
label1.pack()

# Creation d'un widget Button (saisie de profile)
userProfileBtn=Button(Mafenetre, text = "New User", command = lambda: userProfileWindow(cursorDB,db), height = 4, width = 40)
userProfileBtn.pack()

# Espace 2
label2=Label(Mafenetre, height = 6, width = 40)
label2.pack()

# Creation d'un widget Button (bouton Lancer)
BoutonLancer = Button(Mafenetre, text ='Launch video', command = lambda: newTest(cursorDB), height = 8, width = 20, state=DISABLED)

# Positionnement du widget avec la methode pack()
BoutonLancer.pack()

# Espace 3
label3=Label(Mafenetre, height = 4, width = 40)
label3.pack()

# Creation d'un widget Button (saisie de feedback)
videoEvalBtn=Button(Mafenetre, text = "New measure ", command = lambda: InsertExistantUser(cursorDB,db), height = 4, width = 40, state=DISABLED)
videoEvalBtn.pack(side = LEFT) 

#Creation d'un widget Button (bouton Quitter)
BoutonQuitter = Button(Mafenetre, text ='Close', command = lambda: appExit(Mafenetre,db),  height = 4, width = 20)
BoutonQuitter.pack(side = RIGHT, padx = 20, pady = 7)

# Espace 4
label4=Label(Mafenetre, height = 4, width = 40)
label4.pack()

# Lancement (main)
Mafenetre.mainloop()

#######################################################################################################
############# END END END END #####################################################################
#######################################################################################################
