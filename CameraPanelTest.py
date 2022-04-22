import re
import wx
import DB_Class
import sys


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
            self.username = username
            self.myDB.update_active(username, "IN")
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
    def __init__(self, parent, start_x, start_y, position_number):
        wx.Panel.__init__(self, parent, pos=(start_x, start_y), size=(347, 267))

        self.parent = parent
        self.start_x = start_x
        self.start_y = start_y
        self.position_number = position_number

        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.settings_frame = SettingsFrame(self.position_number)

        self.alert = wx.Button(self, label='Alert', pos=(50, 205))
        self.alert.Bind(wx.EVT_BUTTON, self.alert_call)

        self.face = wx.ToggleButton(self, label='Face', pos=(50, 235))
        self.face.Bind(wx.EVT_TOGGLEBUTTON, self.toggle_face_detection)

        self.zoom = wx.Button(self, label='Zoom', pos=(200, 205))
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
        self.parent.Hide()
        self.parent.parent.show_zoom_panel(self.position_number)

    def settings_screen(self, e):
        if not self.settings_frame.IsShown():
            self.settings_frame.Show()

        else:
            self.settings_frame.Hide()

    def close_settings_frame(self):
        try:
            self.settings_frame.Destroy()
        except Exception:
            pass

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


class ZoomPanel(wx.Panel):

    def __init__(self, parent, position_number):

        wx.Panel.__init__(self, parent, size=(1900, 1000))

        self.parent = parent
        self.myDB = DB_Class.DB("myDB")

        # Setting the background to white
        self.SetBackgroundColour("white")

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.position_number = position_number

        self.settings_frame = SettingsFrame(self.position_number)

        self.alert = wx.Button(self, label='Alert', pos=(1770, 600))
        self.alert.Bind(wx.EVT_BUTTON, self.alert_call)

        self.face = wx.ToggleButton(self, label='Face', pos=(1770, 650))
        self.face.Bind(wx.EVT_TOGGLEBUTTON, self.toggle_face_detection)

        self.zoom = wx.Button(self, label='unZoom', pos=(1770, 700))
        self.zoom.Bind(wx.EVT_BUTTON, self.call_zoom_screen)

        settings = wx.Button(self, label='Settings', pos=(1770, 750))
        settings.Bind(wx.EVT_BUTTON, self.settings_screen)

        # Log out button
        self.logout_button = wx.Button(self, label='Log out', pos=(1770, 50))
        self.logout_button.SetBackgroundColour((245, 66, 66, 255))
        self.logout_button.Bind(wx.EVT_BUTTON, self.logout_button_pressed)

        # Settings button panel
        settings_panel_button = wx.Panel(self, pos=(1778, 468), size=(72, 72))
        pic = wx.Bitmap("Settings.bmp", wx.BITMAP_TYPE_ANY)
        self.settings_button = wx.BitmapButton(settings_panel_button, -1, pic)
        self.Bind(wx.EVT_BUTTON, self.settings_button_pressed, self.settings_button)

    def settings_button_pressed(self, e):
        print("Settings button pressed")

    def alert_call(self, e):
        print("Called alert")

    def toggle_face_detection(self, e):
        is_pressed = self.face.GetValue()
        if is_pressed:
            print("Face detection is on")
        else:
            print("Face detection is off")

    def call_zoom_screen(self, e):
        try:
            self.settings_frame.Destroy()
        except Exception:
            pass
        self.parent.hide_zoom_panel()

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
        dc.DrawRectangle(150, 50, 1600, 900)

    def logout_button_pressed(self, e):

        try:
            self.settings_frame.Destroy()
        except Exception:
            pass

        self.parent.main_panel.logout_button_pressed(e)


class MainPanel(wx.Panel):

    def __init__(self, parent, start_x, start_y, username):

        wx.Panel.__init__(self, parent, size=(1900, 1000), pos=(0, 0))

        self.parent = parent
        self.myDB = DB_Class.DB("myDB")

        self.camera_panels = []

        # First row
        self.camera_panels.append(CameraPanel(self, start_x, start_y, 1))
        self.camera_panels.append(CameraPanel(self, start_x + 349, start_y, 2))
        self.camera_panels.append(CameraPanel(self, start_x + 698, start_y, 3))

        # Second row
        self.camera_panels.append(CameraPanel(self, start_x, start_y + 269, 4))
        self.camera_panels.append(CameraPanel(self, start_x + 349, start_y + 269, 5))
        self.camera_panels.append(CameraPanel(self, start_x + 698, start_y + 269, 6))

        # Third row
        self.camera_panels.append(CameraPanel(self, start_x, start_y + 538, 7))
        self.camera_panels.append(CameraPanel(self, start_x + 349, start_y + 538, 8))
        self.camera_panels.append(CameraPanel(self, start_x + 698, start_y + 538, 9))

        # Log out button
        self.logout_button = wx.Button(self, label='Log out', pos=(1770, 50))
        self.logout_button.SetBackgroundColour((245, 66, 66, 255))
        self.logout_button.Bind(wx.EVT_BUTTON, self.logout_button_pressed)

        # Settings button panel
        settings_panel_button = wx.Panel(self, pos=(1778, 468), size=(72, 72))
        pic = wx.Bitmap("Settings.bmp", wx.BITMAP_TYPE_ANY)
        self.settings_button = wx.BitmapButton(settings_panel_button, -1, pic)
        self.Bind(wx.EVT_BUTTON, self.settings_button_pressed, self.settings_button)

        # Presenting the name of the user to the screen
        # text_panel = wx.Panel(self, pos=(0, 0), size=(1900, 1000))
        text_hello_box = wx.BoxSizer(wx.HORIZONTAL)

        font = wx.Font(25, wx.MODERN, wx.NORMAL, wx.BOLD)
        lbl = wx.StaticText(self, style=wx.ALIGN_CENTER)
        lbl.SetFont(font)
        lbl.SetLabel(f'Hello {username}!')

        text_hello_box.Add(lbl, 0, wx.ALIGN_CENTER)

    def settings_button_pressed(self, e):
        print("Settings button pressed")

    def logout_button_pressed(self, e):
        print("Log out button pressed")
        self.myDB.update_active(self.parent.username, "OUT")

        for panel in self.camera_panels:
            panel.close_settings_frame()

        self.Destroy()
        self.parent.Destroy()


        # Asking the user to login again

        frame = MainFrame(426, 98)
        app.MainLoop()


class MainFrame(wx.Frame):

    # ----------------------------------------------------------------------
    def __init__(self, start_x, start_y):
        """Constructor"""

        super().__init__(None, size=(1900, 1000), title="Main Screen")

        self.start_x = start_x
        self.start_y = start_y

        self.myDB = DB_Class.DB("myDB")


        # Setting the background to white
        self.SetBackgroundColour(wx.WHITE)

        # Asking the user to login
        dlg = LoginDialog()
        dlg.ShowModal()
        authenticated = dlg.logged_in

        # If the user closed the login window without logging in
        if not dlg.logged_in:
            sys.exit()

        # Saving the username
        self.username = dlg.username

        self.create_main_panel()

        # Locking the size of the frame
        self.SetMaxSize(wx.Size(1900, 1000))
        self.SetMinSize(wx.Size(1900, 1000))

        # Setting the icon of the frame
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("NoamCamLens.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        self.Bind(wx.EVT_CLOSE, sys.exit)

        # Showing and centring the frame in the screen
        self.Show()
        self.Centre()

    def create_main_panel(self):
        self.main_panel = MainPanel(self, self.start_x, self.start_y, self.username)

    def show_zoom_panel(self, position_number):
        self.main_panel.Hide()
        self.zoom_panel = ZoomPanel(self, position_number)
        self.SetLabel("Zoom Screen")

    def hide_zoom_panel(self):
        self.zoom_panel.Hide()
        self.main_panel.Show()
        self.SetLabel("Main Screen")


class SettingsFrame(wx.Frame):

    def __init__(self, position_number):

        self.position_number = position_number

        super().__init__(None, size=(500, 500), title="Panel " + str(position_number) + " Settings")
        wx.Dialog.__init__(self, None, title="Panel " + str(position_number) + " Settings")
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

        # position info
        position_sizer = wx.BoxSizer(wx.HORIZONTAL)

        position_lbl = wx.StaticText(self, label="Camera position:")
        position_sizer.Add(position_lbl, 0, wx.ALIGN_LEFT, 5)
        position_sizer.AddStretchSpacer(1)
        self.position = wx.TextCtrl(self)
        self.position.SetValue(str(position_number))
        position_sizer.Add(self.position, 0, wx.ALIGN_LEFT, 5)
        position_sizer.AddSpacer(133)

        # place info
        place_sizer = wx.BoxSizer(wx.HORIZONTAL)

        place_lbl = wx.StaticText(self, label="Place:")
        place_sizer.Add(place_lbl, 0, wx.ALIGN_LEFT, 5)
        place_sizer.AddStretchSpacer(1)
        self.place = wx.TextCtrl(self)
        place_sizer.Add(self.place, 0,  wx.ALIGN_LEFT, 5)
        place_sizer.AddSpacer(133)

        # status info
        status_sizer = wx.BoxSizer(wx.HORIZONTAL)

        status_lbl = wx.StaticText(self, label="Status (ON\OFF):")
        status_sizer.Add(status_lbl, 0, wx.ALIGN_LEFT, 5)
        status_sizer.AddStretchSpacer(1)
        self.status = wx.TextCtrl(self)
        status_sizer.Add(self.status, 0, wx.ALIGN_LEFT, 5)
        status_sizer.AddSpacer(133)

        # ID info
        id_sizer = wx.BoxSizer(wx.HORIZONTAL)

        id_lbl = wx.StaticText(self, label="id: ")
        id_sizer.Add(id_lbl, 0, wx.ALIGN_LEFT, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(mac_sizer, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(position_sizer, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(place_sizer, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(status_sizer, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(id_sizer, 1, wx.ALL | wx.EXPAND, 5)

        btn = wx.Button(self, label="Save")
        btn.Bind(wx.EVT_BUTTON, self.save_settings)
        main_sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_CLOSE, self._when_closed)

    def _when_closed(self, event):
        self.Hide()

    def save_settings(self, event):
        mac_address = self.mac.GetValue()
        position = self.position.GetValue()
        place = self.place.GetValue()
        status = self.status.GetValue()

        # Checking if the mac address is valid
        if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_address.lower()):

            if not self.myDB.position_taken(position):
                try:
                    position = int(position)
                except Exception as e:
                    print("Position must be a number")

                else:
                    if 1 <= position <= 9:

                        if place.isalpha():

                            if status.lower() == "on" or status.lower() == "off":

                                # self.myDB.update_mac(self.id)
                                self.myDB.update_position(mac_address, position)
                                self.myDB.update_place(mac_address, place)
                                self.myDB.update_status(mac_address, status)

                                self.display_message("Settings saved successfully")

                                self.Hide()

                            else:
                                self.display_message("Status must be ON or OFF")

                        else:
                            self.display_message("Place must be English letters")

                    else:
                        self.display_message("Position must be between 1 and 9")

            else:
                self.display_message("Position taken")

        else:
            self.display_message("Invalid MAC address")


        print("The new saved settings are:" + mac_address + " " + str(position) + " " + place + " " + status)

    def display_message(self, message):
        dlg = wx.MessageDialog(None, message, "Message", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame(426, 98)
    app.MainLoop()
