import re
import wx

import Alarm
import DB_Class
import sys
import wx.adv
import wx.lib.scrolledpanel


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
            # self.display_message("Login Successful")
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

        self.parent.parent.settings_screens_open.append(self.settings_frame)

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
        # self.parent.parent.sound_object.play_now = True

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
        self.parent.show_all_cameras_panel()

    def alert_call(self, e):
        print("Called alert")
        # self.parent.sound_object.play_now = True

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

    def list_screen(self, e):
        if not self.list.IsShown():
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


class ListFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super(ListFrame, self).__init__(*args, **kw)

        self.InitUI()

    def InitUI(self):

        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.listbox = wx.ListBox(panel)
        hbox.Add(self.listbox, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)

        self.myDB = DB_Class.DB("myDB")

        cameras_list = self.myDB.get_cameras()

        for camera in cameras_list:
            self.listbox.Append(str(camera[4]))

        btnPanel = wx.Panel(panel)
        vbox = wx.BoxSizer(wx.VERTICAL)
        # newBtn = wx.Button(btnPanel, wx.ID_ANY, 'New', size=(90, 30))
        ediBtn = wx.Button(btnPanel, wx.ID_ANY, 'Edit', size=(90, 30))
        delBtn = wx.Button(btnPanel, wx.ID_ANY, 'Delete', size=(90, 30))
        # clrBtn = wx.Button(btnPanel, wx.ID_ANY, 'Clear', size=(90, 30))

        self.open_settings_windows = []

        # self.Bind(wx.EVT_BUTTON, self.NewItem, id=newBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnEdit, id=ediBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDelete, id=delBtn.GetId())
        # self.Bind(wx.EVT_BUTTON, self.OnClear, id=clrBtn.GetId())
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnEdit)

        vbox.Add((-1, 20))
        # vbox.Add(newBtn)
        vbox.Add(ediBtn)
        vbox.Add(delBtn, 0, wx.TOP, 5)
        # vbox.Add(clrBtn, 0, wx.TOP, 5)

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)

        # When event closed send to function OnClose
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.SetTitle('wx.ListBox')
        self.Centre()

        self.Show()

    # def NewItem(self, event):
    #
    #     text = wx.GetTextFromUser('Enter a new item', 'Insert dialog')
    #     if text != '':
    #         self.listbox.Append(text)

    def OnClose(self, event):

        self.Destroy()

    def OnEdit(self, event):

        sel = self.listbox.GetSelection()
        text = self.listbox.GetString(sel)

        self.current_settings_frame = SettingsFrame(text)
        self.current_settings_frame.Show()

        # sel = self.listbox.GetSelection()
        # text = self.listbox.GetString(sel)
        # renamed = wx.GetTextFromUser('Rename item', 'Rename dialog', text)
        #
        # if renamed != '':
        #     self.listbox.Delete(sel)
        #     item_id = self.listbox.Insert(renamed, sel)
        #     self.listbox.SetSelection(item_id)

    def OnDelete(self, event):

        sel = self.listbox.GetSelection()
        if sel != -1:
            self.listbox.Delete(sel)

    # def OnClear(self, event):
    #     self.listbox.Clear()


class AllCamerasPanel(wx.Panel):

    def __init__(self, parent):

        wx.Panel.__init__(self, parent, size=(1900, 1000))

        self.parent = parent
        self.myDB = DB_Class.DB("myDB")

        self.last_selected = None

        cameras_list = self.myDB.get_cameras()

        # Setting the background to white
        self.SetBackgroundColour("white")

        # Log out button
        self.logout_button = wx.Button(self, label='Log out', pos=(1770, 50))
        self.logout_button.SetBackgroundColour((245, 66, 66, 255))
        self.logout_button.Bind(wx.EVT_BUTTON, self.logout_button_pressed)

        # Back button
        self.back_button = wx.Button(self, label='Back', pos=(25, 50))
        # self.back_button.SetBackgroundColour((245, 66, 66, 255))
        self.back_button.Bind(wx.EVT_BUTTON, self.back_button_pressed)
        
        # scrolled panel
        self.scrollP = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(426, 400), pos=(740, 400), style=wx.SIMPLE_BORDER)
        self.scrollP.SetAutoLayout(1)
        self.scrollP.SetupScrolling()
        self.scrollP.SetBackgroundColour('#FFFFFF')

        cameras_id_and_names = []

        for camera in cameras_list:
            cameras_id_and_names.append((str(camera[4]) + " - " + camera[2]))

        self.spSizer = wx.BoxSizer(wx.VERTICAL)
        for word in cameras_id_and_names:
            text = wx.TextCtrl(self.scrollP, value=word)
            text.Bind(wx.EVT_CHILD_FOCUS, self.file_selected)
            self.spSizer.Add(text)
        self.scrollP.SetSizer(self.spSizer)

    def file_selected(self, event):

        self.last_selected = event.GetWindow().GetValue()

        id = self.last_selected.split(" - ")[0]

        self.current_settings_frame = SettingsFrame(id)
        self.current_settings_frame.Show()

        print(event.GetWindow().GetValue())

    def logout_button_pressed(self, e):

        self.parent.main_panel.logout_button_pressed(e)

    def back_button_pressed(self, e):
        self.parent.hide_all_cameras_panel()


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

        # Info button
        self.info_button = wx.Button(self, label='Info', pos=(25, 910))
        self.info_button.Bind(wx.EVT_BUTTON, self.onAbout)


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
        self.parent.show_all_cameras_panel()

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

    def onAbout(self, e):
        info = wx.adv.AboutDialogInfo()
        info.SetName('Noam Camera')
        info.SetVersion('0.22B')
        info.SetDescription('A program for controlling the Noam Camera system')
        info.SetCopyright('(C) 2020 Noam')
        info.AddDeveloper("Noam Tirosh")

        wx.adv.AboutBox(info)


class MainFrame(wx.Frame):

    # ----------------------------------------------------------------------
    def __init__(self, start_x, start_y):
        """Constructor"""

        super().__init__(None, size=(1900, 1000), title="Main Screen")

        self.start_x = start_x
        self.start_y = start_y

        self.myDB = DB_Class.DB("myDB")

        self.settings_screens_open = []

        # self.sound_object = Alarm.AlarmSound()

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

    def hide_all_settings(self):
        for settings in self.settings_screens_open:
            settings.Hide()

    def create_main_panel(self):
        self.main_panel = MainPanel(self, self.start_x, self.start_y, self.username)

    def show_all_cameras_panel(self):
        # self.main_panel.Hide()
        # # Hiding the zoom panel if it's visible
        # try:
        #     self.zoom_panel.Hide()
        # except Exception:
        #     pass
        try:
            if self.all_cameras_panel.IsShown():
                self.all_cameras_panel.Destroy()
        except Exception:
            self.all_cameras_panel = ListFrame(self)

    def hide_all_cameras_panel(self):
        self.all_cameras_panel.Hide()
        self.main_panel.Show()
        self.SetLabel("Main Screen")

    def show_zoom_panel(self, position_number):
        self.hide_all_settings()
        self.main_panel.Hide()
        self.zoom_panel = ZoomPanel(self, position_number)
        self.SetLabel("Zoom Screen")

    def hide_zoom_panel(self):
        self.hide_all_settings()
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

                                mac_address = mac_address.higher()

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
