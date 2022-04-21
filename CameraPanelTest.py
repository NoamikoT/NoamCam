import wx
import DB_Class


class LoginDialog(wx.Dialog):
    """
    Class to define login dialog
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Dialog.__init__(self, None, title="Login Screen")
        self.logged_in = False

        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("NoamCamLens.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        self.myDB = DB_Class.DB("myDB")

        # user info
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)

        user_lbl = wx.StaticText(self, label="Username:")
        user_sizer.Add(user_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.user = wx.TextCtrl(self)
        user_sizer.Add(self.user, 0, wx.ALL, 5)

        # pass info
        p_sizer = wx.BoxSizer(wx.HORIZONTAL)

        p_lbl = wx.StaticText(self, label="Password:")
        p_sizer.Add(p_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.password.Bind(wx.EVT_TEXT_ENTER, self.on_login)
        p_sizer.Add(self.password, 0, wx.ALL, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(user_sizer, 0, wx.ALL, 5)
        main_sizer.Add(p_sizer, 0, wx.ALL, 5)

        btn = wx.Button(self, label="Login")
        btn.Bind(wx.EVT_BUTTON, self.on_login)
        main_sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(main_sizer)

    # ----------------------------------------------------------------------
    def on_login(self, event):
        """
        Checks the credentials and login
        """

        username = self.user.GetValue()
        user_password = self.password.GetValue()
        if self.myDB.do_passwords_match(username, user_password):
            self.display_message("Login Successful")
            self.logged_in = True
            self.Close()
        else:
            self.display_message("Incorrect username or password")

    def display_message(self, message):
        dlg = wx.MessageDialog(None, message, "Message", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


class CameraPanel(wx.Panel):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, start_x, start_y, id_number):
        wx.Panel.__init__(self, parent, pos=(start_x, start_y), size=(347, 267))

        self.start_x = start_x
        self.start_y = start_y
        self.id_number = id_number

        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.settings_frame = SettingsFrame(self.id_number)

        self.alert = wx.Button(self, label='Alert', pos=(50, 205))
        self.alert.Bind(wx.EVT_BUTTON, self.alert_call)

        self.face = wx.ToggleButton(self, label='Face', pos=(50, 235))
        self.face.Bind(wx.EVT_TOGGLEBUTTON, self.toggle_face_detection)

        self.zoom = wx.Button(self, label='zoom', pos=(200, 205))
        self.zoom.Bind(wx.EVT_BUTTON, self.call_zoom_screen)

        settings = wx.Button(self, label='Settings', pos=(200, 235))
        settings.Bind(wx.EVT_BUTTON, self.settings_screen)

    def alert_call(self, e):
        print("Called alert")

    def toggle_face_detection(self, e):
        is_pressed = self.face.GetValue()
        if is_pressed:
            print("Face detection is on")
        else:
            print("Face detection is off")

    def call_zoom_screen(self, e):
        print("Called zoom on panel " + str(self.id_number))

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
        dc.DrawRectangle(0, 0, 347, 197)

        # Red filled rectangle
        dc.SetPen(wx.Pen("red"))
        dc.SetBrush(wx.Brush("red"))
        dc.DrawRectangle(0, 0 + 197, 347, 70)


class MainFrame(wx.Frame):

    # ----------------------------------------------------------------------
    def __init__(self, start_x, start_y):
        """Constructor"""

        super().__init__(None, size=(1900, 1000), title="Main Screen")

        # Setting the background to white
        self.SetBackgroundColour(wx.WHITE)

        # First row
        first_panel = CameraPanel(self, start_x, start_y, 1)
        second_panel = CameraPanel(self, start_x + 349, start_y, 2)
        third_panel = CameraPanel(self, start_x + 698, start_y, 3)

        # Second row
        forth_panel = CameraPanel(self, start_x, start_y + 269, 4)
        fifth_panel = CameraPanel(self, start_x + 349, start_y + 269, 5)
        sixth_panel = CameraPanel(self, start_x + 698, start_y + 269, 6)

        # Third row
        seventh_panel = CameraPanel(self, start_x, start_y + 538, 7)
        eighth_panel = CameraPanel(self, start_x + 349, start_y + 538, 8)
        ninth_panel = CameraPanel(self, start_x + 698, start_y + 538, 9)

        # Settings button panel
        settings_panel_button = wx.Panel(self, pos=(1800, 468), size=(72, 72))
        pic = wx.Bitmap("Settings.bmp", wx.BITMAP_TYPE_ANY)
        self.settings_button = wx.BitmapButton(settings_panel_button, -1, pic)
        self.Bind(wx.EVT_BUTTON, self.settings_button_pressed, self.settings_button)

        # Presenting the name of the user to the screen
        text_panel = wx.Panel(self, pos=(875, 20), size=(150, 30))
        lbl = wx.StaticText(text_panel, -1, style=wx.ALIGN_CENTER)
        box = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        lbl.SetFont(font)
        lbl.SetLabel('Hello {User}!')

        box.Add(lbl, 0, wx.ALIGN_CENTER)

        # Locking the size of the frame
        self.SetMaxSize(wx.Size(1900, 1000))
        self.SetMinSize(wx.Size(1900, 1000))

        # Setting the icon of the frame
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("NoamCamLens.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        # Asking the user to login
        dlg = LoginDialog()
        dlg.ShowModal()
        authenticated = dlg.logged_in
        if not authenticated:
            self.Close()

        # Showing and centring the frame in the screen
        self.Show()
        self.Centre()

    def settings_button_pressed(self, e):
        print("Settings button pressed")


class SettingsFrame(wx.Frame):

    def __init__(self, id_number):

        self.id_number = id_number

        super().__init__(None, size=(500, 500), title="Panel " + str(id_number) + " Settings")
        wx.Dialog.__init__(self, None, title="Panel " + str(id_number) + " Settings")
        panel = wx.Panel(self, -1)

        # Setting the background to white
        self.SetBackgroundColour(wx.LIGHT_GREY)

        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("NoamCamLens.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        self.myDB = DB_Class.DB("myDB")

        # mac info
        mac_sizer = wx.BoxSizer(wx.HORIZONTAL)

        mac_lbl = wx.StaticText(self, label="MAC Address:")
        mac_sizer.Add(mac_lbl, 0, wx.ALIGN_LEFT, 5)
        mac_sizer.AddStretchSpacer(1)
        self.mac = wx.TextCtrl(self)
        mac_sizer.Add(self.mac, 0, wx.ALIGN_LEFT, 5)
        mac_sizer.AddSpacer(133)

        # number info
        number_sizer = wx.BoxSizer(wx.HORIZONTAL)

        number_lbl = wx.StaticText(self, label="Camera number:")
        number_sizer.Add(number_lbl, 0, wx.ALIGN_LEFT, 5)
        number_sizer.AddStretchSpacer(1)
        self.number = wx.TextCtrl(self)
        number_sizer.Add(self.number, 0, wx.ALIGN_LEFT, 5)
        number_sizer.AddSpacer(133)

        # place info
        place_sizer = wx.BoxSizer(wx.HORIZONTAL)

        place_lbl = wx.StaticText(self, label="Place:")
        place_sizer.Add(place_lbl, 0, wx.ALIGN_LEFT, 5)
        place_sizer.AddStretchSpacer(1)
        self.place = wx.TextCtrl(self)
        place_sizer.Add(self.place, 0,  wx.ALIGN_LEFT, 5)
        place_sizer.AddSpacer(133)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(mac_sizer, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(number_sizer, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(place_sizer, 1, wx.ALL | wx.EXPAND, 5)

        btn = wx.Button(self, label="Save")
        btn.Bind(wx.EVT_BUTTON, self.save_settings)
        main_sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_CLOSE, self._when_closed)

    def _when_closed(self, event):
        self.Hide()



    def save_settings(self, event):
        mac_address = self.mac.GetValue()
        number = self.number.GetValue()
        place = self.place.GetValue()

        print("The new saved settings are:" + mac_address + " " + number + " " + place)


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame(426, 98)
    app.MainLoop()
