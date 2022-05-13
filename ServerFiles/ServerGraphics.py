import os
import re
import cv2
import wx
import DB_Class
import wx.adv
import wx.grid
import locale
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

        # Loading and setting the icon
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("NoamCamLens.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        # Setting the size
        self.SetSize(400, 280)

        # user info
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)

        user_lbl = wx.StaticText(self, label="Username:")
        user_sizer.Add(user_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.user = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.user.Bind(wx.EVT_TEXT_ENTER, self.on_login)
        user_sizer.Add(self.user, 0, wx.ALL, 5)

        # pass info
        p_sizer = wx.BoxSizer(wx.HORIZONTAL)

        p_lbl = wx.StaticText(self, label="Password:")
        p_sizer.Add(p_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.password.Bind(wx.EVT_TEXT_ENTER, self.on_login)
        p_sizer.Add(self.password, 0, wx.ALL, 5)

        # The main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Creating and adding the logo
        png = wx.Image("NoamCamLogoRec.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.Bitmap(png)
        image = bitmap.ConvertToImage()
        image = image.Scale(300, 67, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        self.control = wx.StaticBitmap(self, -1, result)
        self.control.SetPosition((0, 0))

        # Adding everything to the main sizer
        main_sizer.Add(self.control, 0, wx.ALL | wx.CENTER, 5)

        main_sizer.Add(user_sizer, 0, wx.ALL, 5)
        main_sizer.Add(p_sizer, 0, wx.ALL, 5)

        # Creating and adding the login button
        btn = wx.Button(self, label="Login")
        btn.Bind(wx.EVT_BUTTON, self.on_login)
        main_sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)

        # Creating and adding the about button
        info_button = wx.Button(self, label="Info.")
        info_button.Bind(wx.EVT_BUTTON, self.onAbout)
        main_sizer.Add(info_button, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(main_sizer)

    def onAbout(self, event):
        info = wx.adv.AboutDialogInfo()
        info.SetName("Noam Cam")
        info.SetVersion("1.0")
        info.SetDescription("Camera Software")
        info.SetCopyright("(C) 2022 Noam Cam")
        info.AddDeveloper("Noam Tirosh")

        wx.adv.AboutBox(info)

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
        """
        Displays a message to the user
        :param message: The message to display
        :type message: String
        """

        dlg = wx.MessageDialog(None, message, "Message", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


class CameraPanel(wx.Panel):
    """A panel printing the frames and buttons for each camera"""

    # ----------------------------------------------------------------------
    def __init__(self, frame, parent, start_x, start_y, position_number, port, mac, place):
        wx.Panel.__init__(self, parent, size=(600, 330))

        # Setting all of the parameters
        self.frame = frame
        self.parent = parent
        self.start_x = start_x
        self.start_y = start_y
        self.position_number = position_number

        self.mac = mac
        self.place = place
        self.siren = False
        self.control = None
        self.camera_is_on = False

        # Setting the frame imgSizer
        self.imgSizer = (600, 300)
        self.image = wx.Image(self.imgSizer[0], self.imgSizer[1])
        self.imageBit = wx.Bitmap(self.image)
        self.staticBit = wx.StaticBitmap(self, wx.ID_ANY, self.imageBit)

        # Setting the background color and printing boxes
        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        # Setting all the buttons that control the camera
        self.alert = wx.Button(self, label='Alert', pos=(133, 302))
        self.alert.Bind(wx.EVT_BUTTON, self.alert_call)

        self.face = wx.ToggleButton(self, label='Face', pos=(258, 302))
        self.face.Bind(wx.EVT_TOGGLEBUTTON, self.toggle_face_detection)

        self.zoom = wx.Button(self, label='Zoom', pos=(383, 302))
        self.zoom.Bind(wx.EVT_BUTTON, self.call_zoom_screen)

        self.folder_button = wx.Button(self, label='Recordings', pos=(508, 302))
        self.folder_button.Bind(wx.EVT_BUTTON, self.folder_button_pressed)

        # Setting the font and printing the camera's place
        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD)
        lbl = wx.StaticText(self, style=wx.ALIGN_CENTER, pos=(2, 306))
        lbl.SetFont(font)
        lbl.SetLabel(self.place)
        lbl.SetForegroundColour("blue")
        lbl.SetBackgroundColour("gray")

        self.width = 600
        self.height = 300

        self.port = port

        # Subscribing to the camera's topic, update frame - when there's a new frame to display, disconnect - when the camera is disconnected
        pub.subscribe(self.update_frame, f"update frame-{self.port}")
        pub.subscribe(self.CallDrawBlank, f'disconnected1-{self.port}')

        self.Layout()
        self.Show()

    def CallDrawBlank(self):
        """
        Draws a blank frame when the camera is disconnected
        :return:
        """

        png = wx.Image("BlackPic.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.Bitmap(png)
        image = bitmap.ConvertToImage()
        image = image.Scale(600, 300, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        self.control = wx.StaticBitmap(self, -1, result)
        self.control.SetPosition((0, 0))
        self.Refresh()
        self.camera_is_on = False

    def update_frame(self, video_frame):
        """
        Updates the frame with the new frame from the camera
        :param video_frame:
        :return:
        """

        if not self.camera_is_on:
            if self.control:
                self.control.Hide()
            self.camera_is_on = True
        try:
            self.bmp = wx.Bitmap.FromBuffer(self.width, self.height, video_frame)
        except:
            pass
        else:

            data = cv2.resize(video_frame, (600, 300), interpolation=cv2.INTER_AREA)
            data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
            self.bmp.CopyFromBuffer(data)
            self.staticBit.SetBitmap(self.bmp)

        self.Refresh()

    def alert_call(self, e):
        """
        When the alert was pressed
        """

        if not self.siren:
            self.frame.graphics_comms.put(("ALERT ON", self.mac))
            self.alert.SetLabel("Stop Alert")
            self.siren = True
        else:
            self.frame.graphics_comms.put(("ALERT OFF", self.mac))
            self.alert.SetLabel("Alert")
            self.siren = False

    def toggle_face_detection(self, e):
        """
        When the face detection was pressed
        """

        is_pressed = self.face.GetValue()
        if is_pressed:
            self.frame.graphics_comms.put(("start face detection", self.mac))
        else:
            self.frame.graphics_comms.put(("stop face detection", self.mac))

    def call_zoom_screen(self, e):
        """
        When the zoom was pressed
        """

        if not self.frame.current_zoom:
            self.frame.graphics_comms.put(("Zoom", self.mac))
            self.frame.current_zoom = self.mac
            self.parent.Hide()
            self.frame.show_zoom_panel(self.mac)
            self.frame.zoom_panel.set_details(self.mac, self.port, self.place)

    def folder_button_pressed(self, event):
        """
        When the folder button was pressed
        """

        current_path = os.getcwd()
        folder_path = f"{current_path}\\Server"

        if self.mac != "":
            fixed_mac = self.mac.replace(":", "_")
            folder_path += f"\\Video\\{fixed_mac}"

            if not os.path.exists(folder_path):
                folder_path = f"{current_path}\\Server"

        path = os.path.realpath(folder_path)
        os.startfile(path)

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
    """A panel of a camera zoomed in"""

    def __init__(self, parent, port=None, mac=None, place=None):

        wx.Panel.__init__(self, parent, size=(1900, 1000))

        self.parent = parent

        # Setting the background to white
        self.SetBackgroundColour("white")

        # Setting the panel parameters
        self.port = port
        self.mac = mac
        self.place = place
        self.width = 1600
        self.height = 900

        # Setting the imgSizer of the camera
        self.imgSizer = (1600, 900)
        self.image = wx.Image(self.imgSizer[0], self.imgSizer[1])
        self.imageBit = wx.Bitmap(self.image)
        self.staticBit = wx.StaticBitmap(self, wx.ID_ANY, self.imageBit)

        # An unzoom button to go back to the main view (Main Panel)
        self.zoom = wx.Button(self, label='unZoom', pos=(1770, 700))
        self.zoom.Bind(wx.EVT_BUTTON, self.call_unzoom_screen)

        self.Layout()
        self.Show()


    def set_details(self, mac, port, place):
        """
        Sets the details of the camera
        :param mac: The mac address of the camera
        :type mac: String
        :param port: The port of the camera
        :type port: String
        :param place: The place of the camera
        :type place: String
        """

        self.mac = mac
        self.parent.SetLabel(f'Zoom Screen - {mac} - {place}')
        self.port = port
        self.place = place

        # Subscribing to the camera's notifications
        pub.subscribe(self.pub_unzoom, f"disconnected2-{self.port}")
        pub.subscribe(self.update_zoom_frame, f"update frame-{self.port}")

    def update_zoom_frame(self, video_frame):
        """
        Updates the zoom frame
        :param video_frame: The video frame to be displayed
        """
        try:
            self.bmp = wx.Bitmap.FromBuffer(self.width, self.height, video_frame)
        except:
            pass
        else:

            data = cv2.resize(video_frame, (self.width, self.height), interpolation=cv2.INTER_AREA)
            data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
            self.bmp.CopyFromBuffer(data)
            self.staticBit.SetBitmap(self.bmp)

        self.Refresh()

    def pub_unzoom(self):
        """
        Unzoms the camera
        """

        if self.IsShown():
            self.width = 600
            self.height = 300

            self.parent.current_zoom = None
            self.parent.hide_zoom_panel()

    def call_unzoom_screen(self, e=None):
        """
        Unzoms the camera
        :param e:
        :return:
        """

        self.parent.graphics_comms.put(("Unzoom", self.mac))
        self.width = 600
        self.height = 300

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
    """The main panel of the application, where you can see all of the camera panels"""
    def __init__(self, parent, start_x, start_y, username):

        wx.Panel.__init__(self, parent, size=(1900, 1000), pos=(0, 0))

        self.frame = parent

        self.camera_panels = []

        ports = [[xx[1], xx[3], xx[0], xx[2]] for xx in self.frame.camera_details]
        port_for_position = {}

        # Creating the camera panels details
        for pos, port, mac, place in ports:
            port_for_position[pos] = [port, mac, place]

        # Creating all of the camera panels and saving them in a list so that they can be easily accessed
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

        # Putting the camera panels in a sizer
        self.sizer_contain_sizer = wx.BoxSizer()
        self.sizer_contain_sizer.SetDimension(0, 0, 1590, 990)

        self.main_sizer = wx.GridSizer(3, 3, 0, 0)
        self.main_sizer.SetHGap(20)
        self.main_sizer.AddMany(self.camera_panels)

        self.sizer_contain_sizer.Add(self.main_sizer, 0)

        self.SetSizer(self.sizer_contain_sizer)
        self.Layout()


class MainFrame(wx.Frame):
    """The main frame of the application, where all of the panels are placed"""

    # ----------------------------------------------------------------------
    def __init__(self, server, graphics_comms):
        """Constructor"""

        super().__init__(None, size=(1900, 1029), title="Main Screen", style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER)

        self.SetSize(1900, 1029)

        # A status bar
        self.statusBar = self.CreateStatusBar(style=wx.BORDER_NONE)
        self.statusBar.SetStatusStyles([wx.SB_FLAT])

        self.statusBar.SetBackgroundColour('gray')
        self.statusBar.SetStatusText("NoamCam - Developed by Noam Tirosh V1.0 05.2022")
        self.server = server

        self.current_zoom = None
        # So that no ICC warning is created
        self.locale = locale.setlocale(locale.LC_ALL, 'C')

        self.graphics_comms = graphics_comms
        self.start_x = 10
        self.start_y = 0

        # Accessing the database and saving the camera details in a list
        myDB = DB_Class.DB("myDB")
        self.camera_details = myDB.get_cameras()
        myDB.close()

        # Setting the background to white
        self.SetBackgroundColour(wx.WHITE)

        # Asking the user to login with the login dialog
        dlg = LoginDialog()
        dlg.ShowModal()
        authenticated = dlg.logged_in

        # If the user closed the login window without logging in
        if not dlg.logged_in:
            os._exit(0)

        # Saving the username
        self.username = dlg.username

        self.titlePanel = TitlePanel(self)
        #self.titlePanel.Hide()

        # Starting the main settings panel
        self.create_main_settings_panel()

        # Setting the icon of the frame
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("NoamCamLens.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        self.Bind(wx.EVT_CLOSE, self.handle_exit)

        # Showing and centring the frame in the screen
        self.Show()
        self.Centre()

    def handle_exit(self, event):
        """
        Handles the exit event
        """

        self.Hide()
        self.DestroyChildren()
        self.Destroy()
        os._exit(0)

    def create_main_panel(self):
        """
        Creates the main panel
        """

        self.main_panel = MainPanel(self, self.start_x, self.start_y, self.username)
        self.main_panel.Hide()

    def create_main_settings_panel(self):
        """
        Creates the main settings panel
        """

        self.titlePanel.set_title("Main Settings Panel")
        self.SetLabel("Main Settings Screen")
        self.main_settings_panel = MainSettingsPanel(self)

    def show_zoom_panel(self, position_number):
        """
        Shows the zoom panel
        """

        self.main_panel.Hide()
        self.zoom_panel = ZoomPanel(self)

    def hide_zoom_panel(self):
        """
        Hides the zoom panel
        """

        self.zoom_panel.Hide()
        self.main_panel.Show()
        self.SetLabel("Main Screen")

    def camera_settings_pressed(self, event):
        """
        Handles the camera settings button
        """

        self.main_settings_panel.Hide()
        self.titlePanel.set_title("Camera Settings Panel")
        self.SetLabel("Camera Settings Panel")
        self.camera_settings_panel = CameraSettingsPanel(self)
        self.camera_settings_panel.Show()

    def admin_settings_pressed(self, event):
        """
        Handles the admin settings button
        """

        self.main_settings_panel.Hide()
        self.titlePanel.set_title("Admin Settings Panel")
        self.SetLabel("Admin Settings Panel")
        self.admin_settings_panel = AdminSettingsPanel(self)
        self.admin_settings_panel.Show()


class TitlePanel(wx.Panel):
    """The title panel, where it says the current panels name and shows the logo"""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(1900, 200), pos=(0, 0))

        # Setting the background to sea green
        self.SetBackgroundColour("sea green")

        # Creating the title label
        font = wx.Font(40, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.lbl = wx.StaticText(self, style=wx.ALIGN_CENTER_HORIZONTAL) #, pos=(2, 306))
        self.lbl.SetFont(font)

        # Creating the logo
        png = wx.Image("NoamCamLogoRec.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.Bitmap(png)
        image = bitmap.ConvertToImage()
        image = image.Scale(300, 67, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        self.control = wx.StaticBitmap(self, -1, result)
        self.control.SetPosition((10, 10))

    def set_title(self, title):
        """
        Sets the title
        :param title: The title to set
        """

        self.lbl.SetLabel(title)
        self.lbl.SetPosition((1900/2-(self.lbl.GetSize()[0])/2,20))
        self.Layout()


class MainSettingsPanel(wx.Panel):
    """The main settings panel, where it shows the camera settings and admin settings buttons, and starts the main program"""
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, size=(1900, 800), pos=(0, 200))

        self.parent = parent

        font = wx.Font(35, wx.MODERN, wx.NORMAL, wx.BOLD)

        # Sets the buttons
        self.camera_settings_button = wx.Button(self, label='Camera Settings', pos=(470, 302), size=(430, 70))
        self.camera_settings_button.Bind(wx.EVT_BUTTON, self.camera_settings_pressed)

        self.admin_settings_button = wx.Button(self, label='Admins Settings', pos=(1000, 302), size=(430, 70))
        self.admin_settings_button.Bind(wx.EVT_BUTTON, self.admin_settings_pressed)

        self.start_main_button = wx.Button(self, label='Start Main Program', pos=(692, 600), size=(515, 70))
        self.start_main_button.Bind(wx.EVT_BUTTON, self.start_main)

        # Showing the appropriate images for the buttons
        png = wx.Image("CameraClipart.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.Bitmap(png)
        image = bitmap.ConvertToImage()
        image = image.Scale(150, 150, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        self.control = wx.StaticBitmap(self, -1, result)
        self.control.SetPosition((595, 130))

        png = wx.Image("UserClipart.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.Bitmap(png)
        image = bitmap.ConvertToImage()
        image = image.Scale(200, 165, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        self.control = wx.StaticBitmap(self, -1, result)
        self.control.SetPosition((1125, 138))

        png = wx.Image("MainProgramPic.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.Bitmap(png)
        image = bitmap.ConvertToImage()
        image = image.Scale(260, 140, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        self.control = wx.StaticBitmap(self, -1, result)
        self.control.SetPosition((835, 675))

        # SET FONT FOR LABEL
        self.camera_settings_button.SetFont(font)
        self.admin_settings_button.SetFont(font)
        self.start_main_button.SetFont(font)
        self.Centre()

    def camera_settings_pressed(self, event):
        """
        Opens the camera settings panel
        """

        self.parent.camera_settings_pressed(event)

    def admin_settings_pressed(self, event):
        """
        Opens the admin settings panel
        """

        self.parent.admin_settings_pressed(event)

    def start_main(self, event):
        """
        Starts the main program (the main panel)
        """

        self.parent.SetLabel("Main Screen")
        myDB = DB_Class.DB("myDB")
        self.parent.camera_details = myDB.get_cameras()
        myDB.close()
        self.parent.create_main_panel()
        self.parent.statusBar.Hide()
        self.parent.titlePanel.Hide()
        self.parent.main_panel.Show()
        self.Destroy()


class CameraSettingsPanel(wx.Panel):
    """A panel for the camera settings"""
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, size=(1900, 800), pos=(0, 200))

        self.parent = parent

        # Accessing the database to get the camera details
        myDB = DB_Class.DB("myDB")
        self.camera_details = myDB.get_cameras()
        myDB.close()

        # Appropriate photo for the panel
        png = wx.Image("CameraClipart.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.Bitmap(png)
        image = bitmap.ConvertToImage()
        image = image.Scale(280, 280, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        self.control = wx.StaticBitmap(self, -1, result)
        self.control.SetPosition((800, 15))

        # Create a wxGrid object
        self.camera_grid = wx.grid.Grid(self, -1, size=(583, 393), pos=(658, 303))
        self.currentlySelectedCell = (0, 0)

        # Then we call CreateGrid to set the dimensions of the grid
        # (100 rows and 10 columns in this example)
        self.camera_grid.CreateGrid(9, 2)

        # Placing the grid cells with the camera details
        for camera in self.camera_details:
            self.camera_grid.SetCellValue(camera[1]-1, 0, camera[0])
            self.camera_grid.SetCellValue(camera[1]-1, 1, camera[2])

        # Setting the column labels
        self.camera_grid.SetColLabelValue(0, "MAC")
        self.camera_grid.SetColLabelValue(1, "Place")

        # Setting the font in each cell
        for row in range(9):
            for column in range(2):
                self.camera_grid.SetCellFont(row, column, wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL))

        # Setting the size of each row to 40
        for row in range(9):
            self.camera_grid.SetRowSize(row, 40)

        # Setting all the column sizes to 220
        for column in range(2):
            self.camera_grid.SetColSize(column, 250)

        # Creating the buttons
        self.back_button = wx.Button(self, label='Back', pos=(1300, 470))
        self.back_button.Bind(wx.EVT_BUTTON, self.back_button_pressed)

        self.submit_button = wx.Button(self, label='Submit', pos=(1300, 520))
        self.submit_button.Bind(wx.EVT_BUTTON, self.submit_button_pressed)

        self.clear_button = wx.Button(self, label='Clear', pos=(1300, 570))
        self.clear_button.Bind(wx.EVT_BUTTON, self.clear_button_pressed)

        self.Centre()

    def back_button_pressed(self, event=None):
        """
        Goes back to the main settings panel
        """

        self.Hide()
        self.parent.SetLabel("Main Settings Screen")
        self.parent.titlePanel.set_title("Main Settings Panel")
        self.parent.main_settings_panel.Show()

    def submit_button_pressed(self, event):
        """
        If the new data is valid, submits the camera details to the database and goes back to the main settings panel
        """

        valid = True
        for row in range(9):
            if not valid:
                break
            for column in range(2):
                if not valid:
                    break
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
            self.update_db()
            self.back_button_pressed()

    def clear_button_pressed(self, event):
        """
        Clears the grid selected cells
        """

        self.onGetSelection()

    def onGetSelection(self):
        """
        Get whatever cells are currently selected
        """
        cells = self.camera_grid.GetSelectedCells()
        if not cells:
            if self.camera_grid.GetSelectionBlockTopLeft():
                top_left = self.camera_grid.GetSelectionBlockTopLeft()[0]
                bottom_right = self.camera_grid.GetSelectionBlockBottomRight()[0]
                self.clearSelectedCells(top_left, bottom_right)
            else:
                print(self.currentlySelectedCell)
        else:
            print(cells)

    def clearSelectedCells(self, top_left, bottom_right):
        """
        Clears the selected cells, based on code from http://ginstrom.com/scribbles/2008/09/07/getting-the-selected-cells-from-a-wxpython-grid/
        """
        cells = []

        rows_start = top_left[0]
        rows_end = bottom_right[0]
        cols_start = top_left[1]
        cols_end = bottom_right[1]
        rows = range(rows_start, rows_end + 1)
        cols = range(cols_start, cols_end + 1)
        cells.extend([(row, col)
                      for row in rows
                      for col in cols])

        for cell in cells:
            row, col = cell
            self.camera_grid.SetCellValue(row, col, "")

    def update_db(self):
        """
        Updates the database with the new camera details
        """

        myDB = DB_Class.DB("myDB")

        for row in range(9):
            myDB.update_mac_by_position(row+1, self.camera_grid.GetCellValue(row, 0))
            myDB.update_place_by_position(row+1, self.camera_grid.GetCellValue(row, 1))

        myDB.close()

    def display_message(self, message):
        """
        Displays a message to the user
        """

        dlg = wx.MessageDialog(None, message, "Message", wx.OK | wx.ICON_ERROR)
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
    """A panel for the admin settings"""
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, size=(1900, 800), pos=(0, 200))

        self.parent = parent

        # Accessing the database to get the admins details
        myDB = DB_Class.DB("myDB")
        self.admin_details = myDB.get_admins()
        myDB.close()

        # Appropriate photo for the panel
        png = wx.Image("UserClipart.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.Bitmap(png)
        image = bitmap.ConvertToImage()
        image = image.Scale(380, 300, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        self.control = wx.StaticBitmap(self, -1, result)
        self.control.SetPosition((750, 10))

        # Create a wxGrid object
        self.admin_grid = wx.grid.Grid(self, -1, size=(833, 393), pos=(533, 303))

        # Then we call CreateGrid to set the dimensions of the grid
        # (100 rows and 10 columns in this example)
        # Changing row count according to the amount of admins in the database
        self.admin_grid.CreateGrid(len(self.admin_details), 3)

        # Setting the column labels
        self.admin_grid.SetColLabelValue(0, "Username")
        self.admin_grid.SetColLabelValue(1, "Full Name")
        self.admin_grid.SetColLabelValue(2, "Email")

        # Filling the cells with the admins details
        for admin in range(len(self.admin_details)):
            self.admin_grid.SetCellValue(admin, 0, self.admin_details[admin][0])
            # (Can't change username)
            self.admin_grid.SetReadOnly(admin, 0)
            self.admin_grid.SetCellValue(admin, 1, self.admin_details[admin][1])
            self.admin_grid.SetCellValue(admin, 2, self.admin_details[admin][2])

        for row in range(len(self.admin_details)):
            for column in range(3):
                self.admin_grid.SetCellFont(row, column, wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL))

        for row in range(len(self.admin_details)):
            self.admin_grid.SetRowSize(row, 40)

        # Setting all of the column sizes to 220
        for column in range(2):
            self.admin_grid.SetColSize(column, 200)

        self.admin_grid.SetColSize(2, 350)

        # Creating the buttons
        self.back_button = wx.Button(self, label='Back', pos=(1400, 470))
        self.back_button.Bind(wx.EVT_BUTTON, self.back_button_pressed)

        self.submit_button = wx.Button(self, label='Submit', pos=(1400, 520))
        self.submit_button.Bind(wx.EVT_BUTTON, self.submit_button_pressed)

        self.change_password_button = wx.Button(self, label='Change Password', pos=(1400, 570))
        self.change_password_button.Bind(wx.EVT_BUTTON, self.change_password_pressed)

        self.Centre()

    def back_button_pressed(self, event=None):
        """
        Goes back to the main settings panel
        """

        self.Hide()
        self.parent.SetLabel("Main Settings Screen")
        self.parent.titlePanel.set_title("Main Settings Panel")
        self.parent.main_settings_panel.Show()

    def submit_button_pressed(self, event):
        """
        If the new data is valid, submits the camera details to the database and goes back to the main settings panel
        """

        valid = True
        for row in range(len(self.admin_details)):
            if not valid:
                break
            for column in range(3):
                if not valid:
                    break

                current_cell = self.admin_grid.GetCellValue(row, column)

                # if column == 0:        # Username column
                #     result = self.check_username_validity(current_cell)
                #     if result == "Valid":
                #         pass
                #     else:
                #         self.display_message(f"Username on row {row+1}: {result}")
                #         valid = False
                #         break

                if column == 1:               # Full name column
                    if self.check_full_name_validity(current_cell):
                        pass
                    else:
                        self.display_message(f"Full name on row {row+1} is invalid!")
                        valid = False
                        break

                elif column == 2:               # Email column
                    if self.check_email_validity(current_cell):
                        pass
                    else:
                        self.display_message(f"Email on row {row+1} is invalid!")
                        valid = False
                        break

        if valid:
            self.update_db()
            self.back_button_pressed()

    def change_password_pressed(self, event):
        """
        Calls the change password dialog to change the password of the current user
        """

        dlg = ChangePasswordDialog(self)
        dlg.ShowModal()

    def update_db(self):
        """
        Updates the database with the new admins details
        """

        myDB = DB_Class.DB("myDB")

        for row in range(len(self.admin_details)):
            # myDB.update_username(row+1, self.admin_grid.GetCellValue(row, 0))
            myDB.update_full_name(self.admin_grid.GetCellValue(row, 0), self.admin_grid.GetCellValue(row, 1))
            myDB.update_email(self.admin_grid.GetCellValue(row, 0), self.admin_grid.GetCellValue(row, 2))

        myDB.close()

    def check_full_name_validity(self, full_name):
        """
        Checks if the full name is valid
        :param full_name: The full name to check
        :return: True if valid, False otherwise
        """

        if full_name != "":
            name_list = full_name.split(" ")
            if len(name_list) == 2:
                if name_list[0].isalpha() and name_list[1].isalpha():
                    return True

        return False

    def check_email_validity(self, email):
        """
        Checks if the email is valid
        :param email: The email to check
        :return: True if valid, False otherwise
        """

        return re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)

    def display_message(self, message):
        """
        Displays a message to the user
        """

        dlg = wx.MessageDialog(None, message, "Message", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()


class ChangePasswordDialog(wx.Dialog):
    """
    Class to define change password dialog
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Dialog.__init__(self, parent, title="Change Password Screen")

        self.parent = parent
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("NoamCamLens.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        # new password info
        new_password_sizer = wx.BoxSizer(wx.HORIZONTAL)

        new_password_lbl = wx.StaticText(self, label="Enter new password:")
        new_password_sizer.Add(new_password_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.new_password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.new_password.Bind(wx.EVT_TEXT_ENTER, self.check_password_validity)
        new_password_sizer.Add(self.new_password, 0, wx.ALL, 5)

        # confirm new password info
        confirm_new_password_sizer = wx.BoxSizer(wx.HORIZONTAL)

        confirm_new_password_lbl = wx.StaticText(self, label="Confirm new password:")
        confirm_new_password_sizer.Add(confirm_new_password_lbl, 0, wx.ALL | wx.CENTER, 5)
        self.confirm_new_password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.confirm_new_password.Bind(wx.EVT_TEXT_ENTER, self.check_password_validity)
        confirm_new_password_sizer.Add(self.confirm_new_password, 0, wx.ALL, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(new_password_sizer, 0, wx.ALL, 5)
        main_sizer.Add(confirm_new_password_sizer, 0, wx.ALL, 5)

        btn = wx.Button(self, label="Login")
        btn.Bind(wx.EVT_BUTTON, self.check_password_validity)
        main_sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)

        # self.Bind(wx.EVT_CLOSE, self.handle_exit)

        self.SetSizer(main_sizer)

    def handle_exit(self, event):
        self.Destroy()

    # ----------------------------------------------------------------------
    def check_password_validity(self, event):
        """
        Checks the validity of the passwords
        """

        new_password = self.new_password.GetValue()
        confirm_new_password = self.confirm_new_password.GetValue()

        if new_password == confirm_new_password:
            if len(new_password) >= 8:
                if len(new_password) <= 20:
                    if new_password.isalnum():
                        myDB = DB_Class.DB("myDB")
                        myDB.update_password(self.parent.parent.username, new_password)
                        myDB.close()
                        self.Destroy()
                    else:
                        self.display_message("The password can only contain English characters and Numeric characters (No spaces)")
                else:
                    self.display_message("The password max size is 20 characters")
            else:
                self.display_message("The password min size is 8 characters")
        else:
            self.display_message("Passwords do not match")

    def display_message(self, message):
        """
        Displays a message to the user
        """

        dlg = wx.MessageDialog(None, message, "Message", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
