import win32gui
import wx
import DB_Class


########################################################################
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


########################################################################
class CameraPanel(wx.Panel):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_PAINT, self.OnPaint)


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




########################################################################
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

        # Asking the user to login
        dlg = LoginDialog()
        dlg.ShowModal()
        authenticated = dlg.logged_in
        if not authenticated:
            self.Close()

        self.Show()
        self.Centre()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
