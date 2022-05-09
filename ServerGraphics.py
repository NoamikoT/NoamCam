import os
import re
import cv2
import wx
import DB_Class
import sys
import wx.adv
import wx.grid
import wx.lib.scrolledpanel
from pubsub import pub
import ServerComms
import Setting


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

        # self.Bind(wx.EVT_CLOSE, self.handle_exit)

        self.SetSizer(main_sizer)

    def handle_exit(self, event):
        os._exit(0)

    # ----------------------------------------------------------------------
    def on_login(self, event):
        """
        Checks the credentials and login
        """

        self.myDB = DB_Class.DB("myDB")

        username = self.user.GetValue()
        user_password = self.password.GetValue()
        if self.myDB.do_passwords_match(username, user_password):
            # self.display_message("Login Successful")
            self.logged_in = True
            self.username = username
            # self.myDB.update_active(username, "IN")
            self.Close()
        else:
            self.display_message("Incorrect username or password")

        self.myDB.close()

    def display_message(self, message):
        dlg = wx.MessageDialog(None, message, "Message", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


class CameraPanel(wx.Panel):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, frame, parent, start_x, start_y, position_number, port, mac, place):
        wx.Panel.__init__(self, parent, size=(600, 330))

        self.frame = frame
        self.parent = parent
        self.start_x = start_x
        self.start_y = start_y
        self.position_number = position_number

        self.mac = mac
        self.place = place
        self.siren = False

        self.imgSizer = (600, 300)
        self.image = wx.Image(self.imgSizer[0], self.imgSizer[1])
        self.imageBit = wx.Bitmap(self.image)
        self.staticBit = wx.StaticBitmap(self, wx.ID_ANY, self.imageBit)

        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.alert = wx.Button(self, label='Alert', pos=(133, 302))
        self.alert.Bind(wx.EVT_BUTTON, self.alert_call)

        self.face = wx.ToggleButton(self, label='Face', pos=(258, 302))
        self.face.Bind(wx.EVT_TOGGLEBUTTON, self.toggle_face_detection)

        self.zoom = wx.Button(self, label='Zoom', pos=(383, 302))
        self.zoom.Bind(wx.EVT_BUTTON, self.call_zoom_screen)

        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD)
        lbl = wx.StaticText(self, style=wx.ALIGN_CENTER, pos=(2, 306))
        lbl.SetFont(font)
        lbl.SetLabel(self.place)
        lbl.SetBackgroundColour("gray")

        self.width = 600
        self.height = 300

        self.port = port

        pub.subscribe(self.update_frame, f"update frame-{self.port}")

        self.Layout()
        self.Show()

    def redraw(self, e):
        ret, self.data = self.capture.read()
        if ret:
            self.data = cv2.resize(self.data, (600, 300), interpolation=cv2.INTER_AREA)
            self.data = cv2.cvtColor(self.data, cv2.COLOR_BGR2RGB)
            self.bmp.CopyFromBuffer(self.data)
            self.staticBit.SetBitmap(self.bmp)
        # self.Refresh()

    def update_frame(self, video_frame):
        self.bmp = wx.Bitmap.FromBuffer(self.width, self.height, video_frame)

        data = cv2.resize(video_frame, (600, 300), interpolation=cv2.INTER_AREA)
        data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
        self.bmp.CopyFromBuffer(data)
        self.staticBit.SetBitmap(self.bmp)

        self.Refresh()

    def alert_call(self, e):
        if not self.siren:
            self.frame.graphics_comms.put(("ALERT ON", self.mac))
            print("Called alert")
            self.alert.SetLabel("Stop Alert")
            self.siren = True
        else:
            self.frame.graphics_comms.put(("ALERT OFF", self.mac))
            print("Stopped alert")
            self.alert.SetLabel("Alert")
            self.siren = False

    def toggle_face_detection(self, e):
        print(self.mac)
        is_pressed = self.face.GetValue()
        if is_pressed:
            self.frame.graphics_comms.put(("start face detection", self.mac))
        else:
            self.frame.graphics_comms.put(("stop face detection", self.mac))

    def call_zoom_screen(self, e):
        print(self.frame.current_zoom)
        if not self.frame.current_zoom:
            self.frame.graphics_comms.put(("Zoom", self.mac))
            self.frame.current_zoom = self.mac
            self.parent.Hide()
            self.frame.show_zoom_panel(self.mac)
            self.frame.zoom_panel.set_details(self.mac, self.port, self.place)

    def OnPaint(self, event):
        """set up the device context (DC) for painting"""
        dc = wx.PaintDC(self)

        # Black filled rectangle
        dc.SetPen(wx.Pen("black"))
        dc.SetBrush(wx.Brush("black"))
        dc.DrawRectangle(0, 0, 600, 300)

        # Red filled rectangle
        dc.SetPen(wx.Pen("gray"))
        dc.SetBrush(wx.Brush("gray"))
        dc.DrawRectangle(0, 300, 600, 30)


class ZoomPanel(wx.Panel):

    def __init__(self, parent, port=None, mac=None, place=None):

        wx.Panel.__init__(self, parent, size=(1900, 1000))

        self.parent = parent

        # Setting the background to white
        self.SetBackgroundColour("white")

        # self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.port = port
        self.mac = mac
        self.place = place
        self.width = 1600
        self.height = 900

        self.imgSizer = (1600, 900)
        self.image = wx.Image(self.imgSizer[0], self.imgSizer[1])
        self.imageBit = wx.Bitmap(self.image)
        self.staticBit = wx.StaticBitmap(self, wx.ID_ANY, self.imageBit)

        self.alert = wx.Button(self, label='Alert', pos=(1770, 600))
        self.alert.Bind(wx.EVT_BUTTON, self.alert_call)

        self.face = wx.ToggleButton(self, label='Face', pos=(1770, 650))
        self.face.Bind(wx.EVT_TOGGLEBUTTON, self.toggle_face_detection)

        self.zoom = wx.Button(self, label='unZoom', pos=(1770, 700))
        self.zoom.Bind(wx.EVT_BUTTON, self.call_unzoom_screen)

    def set_details(self, mac, port, place):
        self.mac = mac
        self.parent.SetLabel(f'Zoom Screen - {mac} - {place}')
        self.port = port
        self.place = place
        pub.subscribe(self.update_zoom_frame, f"update frame-{self.port}")

    def update_zoom_frame(self, video_frame):
        self.bmp = wx.Bitmap.FromBuffer(self.width, self.height, video_frame)

        data = cv2.resize(video_frame, (self.width, self.height), interpolation=cv2.INTER_AREA)
        data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
        self.bmp.CopyFromBuffer(data)
        self.staticBit.SetBitmap(self.bmp)

        self.Refresh()

    def settings_button_pressed(self, e):
        print("Settings button pressed")
        self.parent.show_all_cameras_panel()

    def alert_call(self, e):
        print("Called alert")

    def toggle_face_detection(self, e):
        is_pressed = self.face.GetValue()
        if is_pressed:
            print("Face detection is on")
        else:
            print("Face detection is off")

    def call_unzoom_screen(self, e):
        # try:
        #     self.settings_frame.Destroy()
        # except Exception:
        #     pass
        self.parent.graphics_comms.put(("Unzoom", self.mac))
        self.parent.current_zoom = None
        self.parent.hide_zoom_panel()

    def OnPaint(self, event):
        """set up the device context (DC) for painting"""
        dc = wx.PaintDC(self)

        # Black filled rectangle
        dc.SetPen(wx.Pen("black"))
        dc.SetBrush(wx.Brush("black"))
        dc.DrawRectangle(150, 50, 1600, 900)


class MainPanel(wx.Panel):

    def __init__(self, parent, start_x, start_y, username):

        wx.Panel.__init__(self, parent, size=(1900, 1000), pos=(0, 0))

        self.frame = parent

        self.camera_panels = []

        ports = [[xx[1], xx[3], xx[0], xx[2]] for xx in self.frame.camera_details]
        port_for_position = {}

        for pos, port, mac, place in ports:
            port_for_position[pos] = [port, mac, place]

        # First row
        self.camera_panels.append(CameraPanel(self.frame, self, start_x, start_y, 1, port_for_position[1][0], port_for_position[1][1], port_for_position[1][2]))
        self.camera_panels.append(CameraPanel(self.frame, self, start_x + 540, start_y, 2, port_for_position[2][0], port_for_position[2][1], port_for_position[2][2]))
        self.camera_panels.append(CameraPanel(self.frame, self, start_x + 1070, start_y, 3, port_for_position[3][0], port_for_position[3][1], port_for_position[3][2]))

        # Second row
        self.camera_panels.append(CameraPanel(self.frame, self, start_x, start_y + 330, 4, port_for_position[4][0], port_for_position[4][1], port_for_position[4][2]))
        self.camera_panels.append(CameraPanel(self.frame, self, start_x + 540, start_y + 330, 5, port_for_position[5][0], port_for_position[5][1], port_for_position[5][2]))
        self.camera_panels.append(CameraPanel(self.frame, self, start_x + 1070, start_y + 330, 6, port_for_position[6][0], port_for_position[6][1], port_for_position[6][2]))

        # Third row
        self.camera_panels.append(CameraPanel(self.frame, self, start_x, start_y + 660, 7, port_for_position[7][0], port_for_position[7][1], port_for_position[7][2]))
        self.camera_panels.append(CameraPanel(self.frame, self, start_x + 540, start_y + 660, 8, port_for_position[8][0], port_for_position[8][1], port_for_position[8][2]))
        self.camera_panels.append(CameraPanel(self.frame, self, start_x + 1070, start_y + 660, 9, port_for_position[9][0], port_for_position[9][1], port_for_position[9][2]))

        self.sizer_contain_sizer = wx.BoxSizer()
        self.sizer_contain_sizer.SetDimension(0, 0, 1590, 990)

        self.main_sizer = wx.GridSizer(3, 3, 0, 0)
        self.main_sizer.SetHGap(20)
        self.main_sizer.AddMany(self.camera_panels)

        self.sizer_contain_sizer.Add(self.main_sizer, 0)

        self.SetSizer(self.sizer_contain_sizer)
        self.Layout()

    def onAbout(self, e):
        info = wx.adv.AboutDialogInfo()
        info.SetName('Noam Cam')
        info.SetVersion('0.22B')
        info.SetDescription('A program for controlling the Noam Camera system')
        info.SetCopyright('(C) 2020 Noam')
        info.AddDeveloper("Noam Tirosh")

        wx.adv.AboutBox(info)


class MainFrame(wx.Frame):

    # ----------------------------------------------------------------------
    def __init__(self, server, graphics_comms):
        """Constructor"""

        super().__init__(None, size=(1900, 1029), title="Main Screen", style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER)

        self.SetSize(1900, 1029)

        self.server = server

        self.current_zoom = None

        self.graphics_comms = graphics_comms
        self.start_x = 10
        self.start_y = 0

        myDB = DB_Class.DB("myDB")
        self.camera_details = myDB.get_cameras()
        myDB.close()

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

        self.create_main_settings_panel()

        self.create_main_panel()

        # Setting the icon of the frame
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("NoamCamLens.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        self.Bind(wx.EVT_CLOSE, self.handle_exit)

        # Showing and centring the frame in the screen
        self.Show()
        self.Centre()

    def handle_exit(self, event):
        self.Hide()
        self.DestroyChildren()
        self.Destroy()
        os._exit(0)

    def create_main_panel(self):
        self.main_panel = MainPanel(self, self.start_x, self.start_y, self.username)
        self.main_panel.Hide()

    def create_main_settings_panel(self):
        self.SetLabel("Main Settings Screen")
        self.main_settings_panel = MainSettingsPanel(self)

    def show_zoom_panel(self, position_number):
        self.main_panel.Hide()
        self.zoom_panel = ZoomPanel(self)

    def hide_zoom_panel(self):
        self.zoom_panel.Hide()
        self.main_panel.Show()
        self.SetLabel("Main Screen")

    def camera_settings_pressed(self, event):
        self.main_settings_panel.Hide()
        self.SetLabel("Camera Settings Panel")
        self.camera_settings_panel = CameraSettingsPanel(self)
        self.camera_settings_panel.Show()

    def admin_settings_pressed(self, event):
        self.main_settings_panel.Hide()
        self.SetLabel("Admin Settings Panel")
        self.admin_settings_panel = AdminSettingsPanel(self)
        self.admin_settings_panel.Show()


class MainSettingsPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, size=(1900, 1000), pos=(0, 0))

        self.parent = parent

        # TODO: Add logo
        # open image from disk
        # bmp = wx.Bitmap("NoamCamLogo.png", wx.BITMAP_TYPE_ANY)
        # # create image button using BitMapButton constructor
        # button = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp, size=(bmp.GetWidth() + 10, bmp.GetHeight() + 10))

        # button.Bind(wx.EVT_BUTTON, self.camera_settings_pressed)
        # button.SetPosition((10, 10))

        font = wx.Font(35, wx.MODERN, wx.NORMAL, wx.BOLD)

        self.camera_settings_button = wx.Button(self, label='Camera Settings', pos=(470, 302), size=(430, 70))
        self.camera_settings_button.Bind(wx.EVT_BUTTON, self.camera_settings_pressed)

        self.admin_settings_button = wx.Button(self, label='Admins Settings', pos=(1000, 302), size=(430, 70))
        self.admin_settings_button.Bind(wx.EVT_BUTTON, self.admin_settings_pressed)

        self.start_main_button = wx.Button(self, label='Start Main Program', pos=(692, 600), size=(515, 70))
        self.start_main_button.Bind(wx.EVT_BUTTON, self.start_main)

        # SET FONT FOR LABEL
        self.camera_settings_button.SetFont(font)
        self.admin_settings_button.SetFont(font)
        self.start_main_button.SetFont(font)
        self.Centre()

    def test_logo_button(self, event):
        print("test")

    def camera_settings_pressed(self, event):
        self.parent.camera_settings_pressed(event)

    def admin_settings_pressed(self, event):
        self.parent.admin_settings_pressed(event)

    def start_main(self, event):
        self.parent.SetLabel("Main Screen")
        self.parent.main_panel.Show()
        self.Destroy()


class CameraSettingsPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, size=(1900, 1000), pos=(0, 0))

        self.parent = parent

        myDB = DB_Class.DB("myDB")
        self.camera_details = myDB.get_cameras()
        myDB.close()

        # Create a wxGrid object
        self.camera_grid = wx.grid.Grid(self, -1, size=(583, 393), pos=(658, 303))

        # Then we call CreateGrid to set the dimensions of the grid
        # (100 rows and 10 columns in this example)
        self.camera_grid.CreateGrid(9, 2)

        # Placing the grid cells with the camera details
        for camera in self.camera_details:
            self.camera_grid.SetCellValue(camera[1]-1, 0, camera[0])
            self.camera_grid.SetCellValue(camera[1]-1, 1, camera[2])

        self.camera_grid.SetColLabelValue(0, "MAC")
        self.camera_grid.SetColLabelValue(1, "Place")

        for row in range(9):
            for column in range(2):
                self.camera_grid.SetCellFont(row, column, wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL))

        for row in range(9):
            self.camera_grid.SetRowSize(row, 40)

        # Setting all of the column sizes to 220
        for column in range(2):
            self.camera_grid.SetColSize(column, 250)

        self.back_button = wx.Button(self, label='Back', pos=(1300, 470))
        self.back_button.Bind(wx.EVT_BUTTON, self.back_button_pressed)

        self.submit_button = wx.Button(self, label='Submit', pos=(1300, 520))
        self.submit_button.Bind(wx.EVT_BUTTON, self.submit_button_pressed)

        self.Centre()

    def back_button_pressed(self, event=None):
        self.Hide()
        self.parent.SetLabel("Main Settings Screen")
        self.parent.main_settings_panel.Show()

    def submit_button_pressed(self, event):
        valid = True
        for row in range(9):
            if not valid:
                break
            for column in range(2):
                if not valid:
                    break
                # print(row, column)
                current_cell = self.camera_grid.GetCellValue(row, column)
                if column == 0:        # MAC column
                    if self.check_mac_validity(current_cell):
                        pass
                    else:
                        self.display_message(f"MAC Address on row {row+1} is invalid!")
                        valid = False
                        break
                else:               # Place column
                    if self.check_place_validity(current_cell):
                        pass
                    else:
                        self.display_message(f"Place on row {row+1} is invalid!")
                        valid = False
                        break

        if valid:
            self.back_button_pressed()

    def display_message(self, message):
        dlg = wx.MessageDialog(None, message, "Message", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def check_mac_validity(self, mac):
        """
        Checking if the MAC Address is valid
        :param mac:
        :return:
        """
        if type(mac) == str:
            return (re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()) or mac == "")
        else:
            return False

    def check_place_validity(self, place):
        """
        Checking if the place is a string and only English characters, spaces and numbers
        :param place:
        :return:
        """
        if type(place) == str:
            res = all(chr.isalnum() or chr == "" or chr.isspace() for chr in place)
            return res
        else:
            return False


class AdminSettingsPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, size=(1900, 1000), pos=(0, 0))

        self.parent = parent

        myDB = DB_Class.DB("myDB")
        self.admin_details = myDB.get_admins()
        myDB.close()

        # Create a wxGrid object
        self.camera_grid = wx.grid.Grid(self, -1, size=(833, 393), pos=(533, 303))

        # Then we call CreateGrid to set the dimensions of the grid
        # (100 rows and 10 columns in this example)
        # TODO: Change row count according to the amount of admins in the database
        self.camera_grid.CreateGrid(len(self.admin_details), 3)

        self.camera_grid.SetColLabelValue(0, "Username")
        self.camera_grid.SetColLabelValue(1, "Full Name")
        self.camera_grid.SetColLabelValue(2, "Email")

        for admin in range(len(self.admin_details)):
            self.camera_grid.SetCellValue(admin, 0, self.admin_details[admin][0])
            self.camera_grid.SetCellValue(admin, 1, self.admin_details[admin][1])
            self.camera_grid.SetCellValue(admin, 2, self.admin_details[admin][2])

        for row in range(len(self.admin_details)):
            for column in range(3):
                self.camera_grid.SetCellFont(row, column, wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL))

        for row in range(len(self.admin_details)):
            self.camera_grid.SetRowSize(row, 40)

        # Setting all of the column sizes to 220
        for column in range(2):
            self.camera_grid.SetColSize(column, 200)

        self.camera_grid.SetColSize(2, 350)

        self.back_button = wx.Button(self, label='Back', pos=(1400, 470))
        self.back_button.Bind(wx.EVT_BUTTON, self.back_button_pressed)

        self.submit_button = wx.Button(self, label='Submit', pos=(1400, 520))
        self.submit_button.Bind(wx.EVT_BUTTON, self.submit_button_pressed)

        self.Centre()

    def back_button_pressed(self, event=None):
        self.Hide()
        self.parent.SetLabel("Main Settings Screen")
        self.parent.main_settings_panel.Show()

    def submit_button_pressed(self, event):
        valid = True
        for row in range(len(self.admin_details)):
            if not valid:
                break
            for column in range(3):
                if not valid:
                    break

                current_cell = self.camera_grid.GetCellValue(row, column)

                if column == 0:        # Username column
                    # if self.check_username_validity(current_cell):
                    pass
                    # else:
                    #     self.display_message(f"MAC Address on row {row+1} is invalid!")
                    #     valid = False
                    #     break

                elif column == 1:               # Full name column
                    # if self.check_full_name_validity(current_cell):
                    pass
                    # else:
                    #     self.display_message(f"Place on row {row+1} is invalid!")
                    #     valid = False
                    #     break

                elif column == 2:               # Email column
                    if self.check_email_validity(current_cell):
                        pass
                    else:
                        self.display_message(f"Email on row {row+1} is invalid!")
                        valid = False
                        break

        if valid:
            self.back_button_pressed()


    def check_email_validity(self, email):
        print(re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email))
        return re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)

    def display_message(self, message):
        dlg = wx.MessageDialog(None, message, "Message", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


if __name__ == "__main__":
    server = ServerComms.ServerComms(Setting.VIDEO_PORT)
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
