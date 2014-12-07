#Boa:Frame:wxFrame1

from wxPython.wx import *
from wxPython.grid import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1BUTTON2, 
 wxID_WXFRAME1BUTTON3, wxID_WXFRAME1BUTTON4, wxID_WXFRAME1BUTTON5, 
 wxID_WXFRAME1BUTTON6, wxID_WXFRAME1GRID1, 
] = map(lambda _init_ctrls: wxNewId(), range(8))

class wxFrame1(wxFrame):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wxPoint(350, 272), size=wxSize(370, 310),
              style=wxDEFAULT_FRAME_STYLE, title='TN5250PY - Verbindingen')
        self._init_utils()
        self.SetClientSize(wxSize(362, 276))

        self.grid1 = wxGrid(id=wxID_WXFRAME1GRID1, name='grid1', parent=self,
              pos=wxPoint(0, 0), size=wxSize(370, 200), style=0)
        self.grid1.SetDefaultRowSize(15)

        self.button1 = wxButton(id=wxID_WXFRAME1BUTTON1, label='Toevoegen',
              name='button1', parent=self, pos=wxPoint(25, 210), size=wxSize(90,
              23), style=0)

        self.button2 = wxButton(id=wxID_WXFRAME1BUTTON2, label='Verwijderen',
              name='button2', parent=self, pos=wxPoint(140, 210),
              size=wxSize(90, 23), style=0)

        self.button3 = wxButton(id=wxID_WXFRAME1BUTTON3, label='Eigenschappen',
              name='button3', parent=self, pos=wxPoint(255, 210),
              size=wxSize(90, 23), style=0)

        self.button4 = wxButton(id=wxID_WXFRAME1BUTTON4, label='Verbinden',
              name='button4', parent=self, pos=wxPoint(25, 245), size=wxSize(90,
              23), style=0)

        self.button5 = wxButton(id=wxID_WXFRAME1BUTTON5, label='Opslaan',
              name='button5', parent=self, pos=wxPoint(140, 245),
              size=wxSize(90, 23), style=0)

        self.button6 = wxButton(id=wxID_WXFRAME1BUTTON6, label='Annuleren',
              name='button6', parent=self, pos=wxPoint(255, 245),
              size=wxSize(90, 23), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)
