import wx

########################################################################
class CameraPanel(wx.Panel):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.settings_frame = SettingsFrame()

        alert = wx.Button(self, label='Alert', pos=(100, 200))
        alert.Bind(wx.EVT_BUTTON, self.alert_call)

        face = wx.ToggleButton(self, label='Face', pos=(100, 230))
        face.Bind(wx.EVT_TOGGLEBUTTON, self.toggle_face_detection)

        zoom = wx.Button(self, label='zoom', pos=(200, 200))
        zoom.Bind(wx.EVT_BUTTON, self.toggle_face_detection)

        settings = wx.Button(self, label='Settings', pos=(200, 230))
        settings.Bind(wx.EVT_BUTTON, self.settings_screen)

    def alert_call(self, e):
        print("Called alert")

    def toggle_face_detection(self, e):
        obj = e.GetEventObject()
        is_pressed = obj.GetValue()
        if is_pressed:
            print("Face detection is on")
        else:
            print("Face detection is off")

    def call_zoom_screen(self, e):
        print("Called zoom")

    def settings_screen(self, e):
        if not self.settings_frame.IsShown():
            self.settings_frame.Show()

        else:
            self.settings_frame.Hide()



    def OnPaint(self, event):
        """set up the device context (DC) for painting"""
        dc = wx.PaintDC(self)

        # Black filled rectangle
        dc.SetPen(wx.Pen("black"))
        dc.SetBrush(wx.Brush("black"))
        dc.DrawRectangle(220, 10, 200, 200)


        # Red filled rectangle
        dc.SetPen(wx.Pen("red"))
        dc.SetBrush(wx.Brush("red"))
        dc.DrawRectangle(220, 210, 200, 100)

class MainFrame(wx.Frame):

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        camera_window_placement = [[]]

        wx.Frame.__init__(self, None, size=(1900, 1000), title="Main Screen")
        panel = CameraPanel(self, -1)

        # Locking the size of the frame
        self.SetMaxSize(wx.Size(1900, 1000))
        self.SetMinSize(wx.Size(1900, 1000))

        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("NoamCamLens.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)


        self.Show()
        self.Centre()

class SettingsFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, size=(500, 500), title="Settings")
        panel = wx.Panel(self, -1)

        # pass info
        mac_sizer = wx.BoxSizer(wx.HORIZONTAL)

        mac_label = wx.StaticText(self, label="Username:")
        mac_sizer.Add(mac_label, 0, wx.ALL | wx.CENTER, 5)
        self.user = wx.TextCtrl(self)
        mac_sizer.Add(self.user, 0, wx.ALL, 5)



if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()