'''
Showcase of Kivy Features
=========================

This showcases many features of Kivy. You should see a
menu bar across the top with a demonstration area below. The
first demonstration is the accordion layout. You can see, but not
edit, the kv language code for any screen by pressing the bug or
'show source' icon. Scroll through the demonstrations using the
left and right icons in the top right or selecting from the menu
bar.

The file showcase.kv describes the main container, while each demonstration
pane is described in a separate .kv file in the data/screens directory.
The image data/background.png provides the gradient background while the
icons in data/icon directory are used in the control bar. The file
data/faust_github.jpg is used in the Scatter pane. The icons are
from `http://www.gentleface.com/free_icon_set.html` and licensed as
Creative Commons - Attribution and Non-commercial Use Only; they
sell a commercial license.

The file android.txt is used to package the application for use with the
Kivy Launcher Android application. For Android devices, you can
copy/paste this directory into /sdcard/kivy/showcase on your Android device.

'''

from time import time
from kivy.app import App
from os.path import dirname, join
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty,\
    ListProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
import socket
import numpy as np
import os
import sys
import pickle

from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.checkbox import CheckBox
from functools import partial

Header = ['Name','Verb','Zahl','Adjektiv','Objekt']
Name = ['Britta','Doris','Kerstin','Nina','Peter','Stefan','Tanja','Thomas','Ulrich','Wolfgang']
Verb = ['bekommt','gewann', 'gibt', 'hat', 'kauft', 'malt', 'nahm', 'schenkt', 'sieht', 'verleiht']
Zahl = ['zwei','drei','vier','fuenf','sieben','acht','neun','elf','zwoelf','achtzehn']
Adjektiv = ['alte','grosse', 'gruene', 'kleine', 'nasse', 'rote', 'schoene', 'schwere', 'teure', 'weisse']
Objekt = ['Autos','Bilder', 'Blumen', 'Dosen', 'Messer', 'Ringe', 'Schuhe', 'Sessel', 'Steine', 'Tassen']

new_head = np.array([Name,Verb,Zahl,Adjektiv,Objekt])
new_head = np.rot90(new_head)
new_head = np.flipud(new_head)

ESCU = ['muehelos','==','sehr wenig anstrengend','==','wenig anstrengend','=='
        ,'mittelgradig anstrengend','==','deutlich anstrengend','=='
        ,'sehr anstrengend','==','extrem anstrengend','nur Stoergeraeusch']
ESCU.reverse()


class CB(CheckBox):

    def on_touch_down(self, *args):
        if self.active:
            print(self.active)
            return
        super(CB, self).on_touch_down(*args)


class ComboEdit(TextInput):

    options = ListProperty(('', ))
	
    def __init__(self, **kw):
        ddn = self.drop_down = DropDown()
        ddn.bind(on_select=self.on_select)
        super(ComboEdit, self).__init__(**kw)

    def on_options(self, instance, value):
        ddn = self.drop_down
        ddn.clear_widgets()
        for widg in value:
            widg.bind(on_release=lambda btn: ddn.select(btn.text))
            ddn.add_widget(widg)

    def on_select(self, *args):
        self.text = args[1]

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            self.drop_down.open(self)
        return super(ComboEdit, self).on_touch_up(touch)	
    
class ConnectionPopup(Popup):
    pass

class ShowcaseScreen(Screen):
    fullscreen = BooleanProperty(False)

    def add_widget(self, *args):
        if 'content' in self.ids:
            return self.ids.content.add_widget(*args)
        return super(ShowcaseScreen, self).add_widget(*args)
 
class ShowcaseApp(App):

    index = NumericProperty(-1)
    current_title = StringProperty()
    time = NumericProperty(0)
    show_sourcecode = BooleanProperty(False)
    sourcecode = StringProperty()
    screen_names = ListProperty([])
    hierarchy = ListProperty([])
    global_widgets = {}
    previous_ips = ListProperty([])
    
    def build(self):
        self.title = 'UKLapp Client'
        self.screens = {}
        self.available_screens = sorted([
            'OlSa','Acales'])
        self.screen_names = self.available_screens
        curdir = dirname(__file__)
        self.available_screens = [join(curdir, 'data', 'screens',
            '{}.kv'.format(fn).lower()) for fn in self.available_screens]
        self.connection_popup = ConnectionPopup()
        with open(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]))) + '/ips.txt', 'r') as g:
            lines = g.readlines()
            g.close()
        for i in range(0, len(lines)):
            self.previous_ips.append(Button(text = str(lines[i][:-1]),size_hint_y=None,height=100))
        Clock.schedule_once(self.open_connection_popup, 0.2)
            
######### Connection Popup #########
    def open_connection_popup(self, interval):
        self.connection_popup.open() 
    def hide(self,txtfield):
        if txtfield.text=='IP' or txtfield.text=='PORT' or txtfield.text=='Listennummer' or txtfield.text=='PatientenID':
            txtfield.text=''
    def unhide(self,txtfield,textname):
        if txtfield.text=='':
            txtfield.text=textname
    def connect(self,txt_ip,txt_port):
        try:
            self.BUFFER_SIZE = 4096      # Normally 1024, but we want fast response
            self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sckt.connect((txt_ip, int(txt_port))) 
            print("Connection succeeded to: " + txt_ip+ ':' + txt_port)
            self.connection_popup.ids['label1'].text = "Connection succeeded to: " + txt_ip+ ':' + txt_port
            testtype = self.sckt.recv(self.BUFFER_SIZE).decode('utf-8')
            idx = self.screen_names.index(testtype)
            print('idx of ',testtype,' is ' ,idx)
            self.next_screen = 'a'
            self.current_screen = 'b'
            self.go_screen(idx)    
            self.reset_answersolsa()
        except:
            print("Connection failed to: " + txt_ip+ ':' + txt_port)
            self.connection_popup.ids['label1'].text = "Connection failed to: " + txt_ip+ ':' + txt_port
    def disconnect(self):
        self.sckt.close()
        print('disconnected')
        self.get_running_app().stop()

####################################    
    def reset_answersolsa(self):
        self.answers_client = [0] * 5       # Antworten pro Satz
        self.instances_client = [0] * 5
        self.instances_old = [0] * 5     

    def get_msg(self,dt):
        self.sckt.recv(self.BUFFER_SIZE).decode('utf-8')           
            
    def instance_colorchange(self,dt):
        self.instance.background_color = (0,255,0,1)          

    def go_screen(self, idx):
        self.index = idx
        if self.next_screen != self.current_screen:
            self.root.ids.sm.switch_to(self.load_screen(idx), direction='left')
            self.root.ids.sm.disabled = True
            self.root.ids.actionstart.disabled = False
            print('back to go_screen 1')            
        else: 
            self.root.ids.sm.disabled = True
            self.root.ids.actionstart.disabled = False
            
            print('back to go_screen 2')
        
        print('Loaded screen: ',self.root.ids.spnr.text)

    def go_hierarchy_previous(self):
        ahr = self.hierarchy
        if len(ahr) == 1:
            return
        if ahr:
            ahr.pop()
        if ahr:
            idx = ahr.pop()
            self.go_screen(idx)

    def load_screen(self, index):
        #print(self.screens, index)
        
        if index in self.screens:
            print('i am in one: ',self.screens)
            print('i am in one: ', index, type(index),type(self.screens[index]))
            
            self.current_screen = self.screen_names[index]
            print(self.current_screen)
            print(self.screens[index])
            return self.screens[index]
        else:
            screen = Builder.load_file(self.available_screens[index])
            # print('i am in two: ',screen,self.screens[index])
            print('i am in two: ')
            self.screens[index] = screen
            print(self.screens[index])
            print(type(screen))
            
            self.current_screen = self.screen_names[index]
            #print('Current Screen: ', self.screen_names[index])
      
            return screen
    
    def Start(self):
        self.root.ids.actionstart.disabled = True
        self.root.ids.actionweiter.disabled = True
#        self.root.ids.sm.disabled = True
        self.root.ids.spnr.disabled = True
        
############## OlSa ######################
    def showcase_gridlayout(self, layout):
        
        if len(layout.children) > 0:
            layout.clear_widgets()
        layout.rows = 10
        layout.cols = 5
#        for item in Header:
#            for n in eval(item):
        for item in new_head:
            for n in item:
                layout.text = n
                layout.add_widget(Builder.load_string('''
Button:
    text:
        '{}'.format(self.parent.text)\
        if self.parent else ''
    on_press: app.action(self)
    id: self.parent.text
    font_size: '25sp'
'''))
        self.root.ids.sm.disabled = True
     
        print('!!! showcase_gridlayout failed !!!')
############## Acales ######################
    
    def register_widget(self, widget_object):
        ''' registers widget only if it has unique gid '''
        try:
            print('registering...')
            # if widget_object.gid not in self.global_widgets:
            self.global_widgets[widget_object.gid] = widget_object
            print(widget_object.gid)
        except: 
            print('!!! registering failed !!!')
    def showcase_gridlayout_acales(self, layout):
#       
        if len(layout.children) > 0:
            layout.clear_widgets()
        layout.cols = 1
#        layout.id = 14
        count = 14
        name = 'ESCU_'
        for item in ESCU:
                layout.text = item
                self.butname = name+str(count)
#                print(self.butname)
                layout.add_widget(Builder.load_string('''
Button:
    text:
        '{}'.format(self.parent.text)\
        if self.parent else ''
    on_press: app.action(self)
    on_pos: app.register_widget(self)
    gid: app.butname
    font_size: '25sp'
'''))
#                layout.id -= 1
                count -= 1
        self.root.ids.sm.disabled = True
        print('!!! showcase_gridlayout_acales failed !!!')
###########################################        
    def action(self,instance):
        self.instance = instance
        #print('The button <%s> is being pressed' % instance.text)
        self.change_color(self.instance,self.root.ids.spnr.text)
        #self.root.ids.actionweiter.disabled = False
        try:           
            if self.current_screen == 'OlSa':
                
                self.sckt.send(instance.text.encode('utf-8'))
                print('instance.id:', instance.id)
                print('sleepval before receiving')
                go2sleep = self.sckt.recv(self.BUFFER_SIZE).decode('utf-8')
                print(type(go2sleep), go2sleep)
                self.sckt.send('got it'.encode('utf-8'))
                go2sleep = float(go2sleep)
                sleepval=go2sleep
                server_msg = self.sckt.recv(self.BUFFER_SIZE).decode('utf-8')
                print('client received: ', server_msg)
                if server_msg == 'Weiter':
                    self.root.ids.actionweiter.disabled = True
                    for n in self.instances_client:
                        n.background_color = (1,1,1,1)   
                    self.root.ids.sm.disabled = True   

                    
                    Clock.schedule_once(self.my_callback, sleepval)
                if server_msg == 'Start':
                    self.Start()
               #     sleepval=self.vorl+3
                    Clock.schedule_once(self.my_callback,sleepval)
                if server_msg == 'enable_button':
                    self.root.ids.actionweiter.disabled = False
                    print('enabled..')  
                if server_msg == 'disable_button':
                    print('disabled..')                  
                if server_msg == 'Ende':
                    self.server_ende()
            if self.current_screen == 'Acales':
                self.root.ids.actionweiter.disabled = True # see line 255. acales needs weiter disabled
                try:
                    print(self.global_widgets.items())
                    print('instance: ', instance)
                    print('instance_text: ', instance.text)
                    
                    listOfKeys = [key  for (key, value) in self.global_widgets.items() if value == instance]
                    print('show: ',listOfKeys, 'type: ', type(listOfKeys[0]))
                    self.sckt.send(listOfKeys[0].encode('utf-8'))
                    print('client sends listofkeys: ',listOfKeys)
                    server_msg = self.sckt.recv(self.BUFFER_SIZE).decode('utf-8')
                    Clock.schedule_once(partial(self.my_callback_acalesresetcolor, instance), 1)
#                    print('show: ',instance)
#                    print(self.global_widgets.items())
                except: 
                    print('i am in except of first try')
                if server_msg == 'Start':
                    self.Start()
                    Clock.schedule_once(self.my_callback, 10)
                if server_msg == 'enable_button':
#                    print('I am in enable')
                    try:
                        self.root.ids.sm.disabled = True   
                    except: 
                        print('failed disabling sm')
                    Clock.schedule_once(self.my_callback, 11)
                    print(server_msg)      
                if server_msg == 'Ende':
                    self.server_ende()                   
        except:
            print('i am in except')
   
    def server_ende(self):        
        self.root.ids.sm.disabled = True 
        
    def change_color(self, instance, test):
        print('beginning first try of change color: testtype:',test)
        if test == 'OlSa':
            if instance.text == 'Start':
                print('in change color: ',instance.text)
            else:
                for item in Header:
                    # print(item, ' = ', instance.text)
                    if instance.text in eval(item):
                        
                        print(instance.text)
                        idx_header = Header.index(item)
                        # idx = eval(item).index(instance.text)
                        if self.answers_client[idx_header] != 0:
                            self.instances_old[idx_header].background_color = (1,1,1,1)
                        self.answers_client[idx_header] = instance.text
                        instance.background_color = (0,255,0,1)
                        self.instances_old[idx_header] = instance
                        self.instances_client[idx_header] = instance
                        print('inside first try of change color')
                # return self.answers_client
        if test == 'Acales':
            # instances_client = instance
            instance.background_color = (0,255,0,1)

            
    def my_callback(self, dt):
        self.root.ids.sm.disabled = False
        
    def my_callback_acalesresetcolor(self, instance, dt):
        instance.background_color = (1,1,1,1)      
          
if __name__ == '__main__':
    ShowcaseApp().run()
