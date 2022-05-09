import wx
import DB_Class

class CameraPanel(wx.Panel):
    """The panel for the camera"""

    def __init__(self, parent, start_pos):
        wx.Panel.__init__(self, parent, pos = start_pos, size = (347, 267))
        self.SetBackgroundColour("blue")


class MainFrame(wx.Frame):
    """The main frame of the application"""

    def __init__(self):
        """Constructor"""

        # Initiating the frame
        super().__init__(None, size=(1900, 1000), title="Main Screen")

        # Locking the size of the frame
        self.SetMaxSize(wx.Size(1900, 1000))
        self.SetMinSize(wx.Size(1900, 1000))

        # Changing the Icon of the frame
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("NoamCamLens.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        first_panel = CameraPanel(self, (0, 0))
        # second_panel = CameraPanel(self)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(first_panel, 1, wx.EXPAND | wx.ALL, 5)
        # sizer.Add(second_panel, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)

        # first_panel = CameraPanel(self)
        # my_sizer = wx.BoxSizer(wx.VERTICAL)
        # self.text_ctrl = wx.TextCtrl(first_panel)
        # my_sizer.Add(self.text_ctrl, 0, wx.ALL | wx.EXPAND, 5)
        # my_btn = wx.Button(first_panel, label='Press Me')
        # my_btn.Bind(wx.EVT_BUTTON, self.on_press)
        # my_sizer.Add(my_btn, 0, wx.ALL | wx.CENTER, 5)
        # first_panel.SetSizer(my_sizer)

        # Showing the frame
        self.Show()
        # Centering the frame
        self.Centre()

    def on_press(self, event):
        value = self.text_ctrl.GetValue()
        if not value:
            print("You didn't enter anything!")
        else:
            print(f'You typed: "{value}"')



if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
