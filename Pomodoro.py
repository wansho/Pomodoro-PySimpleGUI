# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 11:14:29 2019

@author: wansho
"""
import logging
from os import path
from time import sleep
import threading
from pkg_resources import Requirement
from pkg_resources import resource_filename

import PySimpleGUI as sg

from win32api import GetModuleHandle
from win32api import PostQuitMessage
from win32con import CW_USEDEFAULT
from win32con import IDI_APPLICATION
from win32con import IMAGE_ICON
from win32con import LR_DEFAULTSIZE
from win32con import LR_LOADFROMFILE
from win32con import WM_DESTROY
from win32con import WM_USER
from win32con import WS_OVERLAPPED
from win32con import WS_SYSMENU
from win32gui import CreateWindow
from win32gui import DestroyWindow
from win32gui import LoadIcon
from win32gui import LoadImage
from win32gui import NIF_ICON
from win32gui import NIF_INFO
from win32gui import NIF_MESSAGE
from win32gui import NIF_TIP
from win32gui import NIM_ADD
from win32gui import NIM_DELETE
from win32gui import NIM_MODIFY
from win32gui import RegisterClass
from win32gui import Shell_NotifyIcon
from win32gui import UpdateWindow
from win32gui import WNDCLASS


class ToastNotifier(object):
    """Create a Windows 10  toast notification.

    from: https://github.com/jithurjacob/Windows-10-Toast-Notifications
    """

    def __init__(self):
        """Initialize."""
        message_map = {WM_DESTROY: self.on_destroy, }

        # Register the window class.
        wc = WNDCLASS()
        self.hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = str("PythonTaskbar")  # must be a string
        wc.lpfnWndProc = message_map  # could also specify a wndproc.
        self.classAtom = RegisterClass(wc)

    def show_toast(self, title="Notification", msg="Here comes the message",
                    icon_path=None, duration=5):
        """Notification settings.

        :title: notification title
        :msg: notification message
        :icon_path: path to the .ico file to custom notification
        :duration: delay in seconds before notification self-destruction
        """
        style = WS_OVERLAPPED | WS_SYSMENU
        self.hwnd = CreateWindow(self.classAtom, "Taskbar", style,
                                 0, 0, CW_USEDEFAULT,
                                 CW_USEDEFAULT,
                                 0, 0, self.hinst, None)
        UpdateWindow(self.hwnd)

        # icon
        if icon_path is not None:
            icon_path = path.realpath(icon_path)
        else:
            icon_path =  resource_filename(Requirement.parse("win10toast"), "win10toast/data/python.ico")
        icon_flags = LR_LOADFROMFILE | LR_DEFAULTSIZE
        try:
            hicon = LoadImage(self.hinst, icon_path,
                              IMAGE_ICON, 0, 0, icon_flags)
        except Exception as e:
            logging.error("Some trouble with the icon ({}): {}"
                          .format(icon_path, e))
            hicon = LoadIcon(0, IDI_APPLICATION)

        # Taskbar icon
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, WM_USER + 20, hicon, "Tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, (self.hwnd, 0, NIF_INFO,
                                      WM_USER + 20,
                                      hicon, "Balloon Tooltip", msg, 200,
                                      title))
        # take a rest then destroy
        sleep(duration)
        DestroyWindow(self.hwnd)
        return None

    def on_destroy(self, hwnd, msg, wparam, lparam):
        """Clean after notification ended.

        :hwnd:
        :msg:
        :wparam:
        :lparam:
        """
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)
        return None


class TomatoClock(object):
    """Pomodoro"""
    def __init__(self):
        self.default_mins = 20
        self.font = "Courier"
        self.font_size = 12
        self.application_name = "Pomodoro"
        self.win10_toaster = ToastNotifier()
        pass

    def show_toast(self, task):
        """show win10 toast"""
        self.win10_toaster.show_toast(self.application_name, "Pomodoro task: " + task + " over.",
                                 icon_path=None, duration=5)

    def run(self):
        """run"""
        layout = [
                    [sg.Text('Task', size=(8, 1), font=(self.font, self.font_size), key="_TASK1_")],
                    [sg.InputText('To Learn One Linux CMD', do_not_clear=True, key='_TASK2_')],
                    [sg.Text('Cycle', size=(8, 1), font=(self.font, self.font_size), key="_CYCLE1_")],
                    [sg.Spin(values=[i for i in range(1, 121)],
                             initial_value=self.default_mins, size=(6, 1), key="_CYCLE2_")],
                    [sg.Text('00:00:00', size=(15, 1), font=(self.font, 28),
                             justification='center', key='_COUNT_DOWN_')],
                    [sg.Button('start', font=(self.font, self.font_size), focus=True),
                     sg.Button('stop/continue', font=(self.font, self.font_size), focus=False),
                     sg.Button('reset', focus=False, font=(self.font, self.font_size)),
                     sg.Quit(font=(self.font, self.font_size))]]

        window = sg.Window('Pomodoro').Layout(layout)

        is_clock_running = False
        current_left_seconds = 0
        should_exit = False
        # Event Loop
        while True:
            event, values = window.Read(1000)
            current_left_seconds -= 1 * (is_clock_running is True)
            if current_left_seconds == 0 and is_clock_running: # Pomodoro over
                task = str(values["_TASK2_"])
                sub_thread = threading.Thread(target=self.show_toast, args=(task,))
                sub_thread.start()
                is_clock_running = False
            if event == "start":
                is_clock_running = True
                clock_mins = int(values["_CYCLE2_"])
                current_left_seconds = clock_mins * 60
                # current_left_seconds = 3
                window.FindElement('_TASK1_').Update(visible=False)
                window.FindElement('_CYCLE1_').Update(visible=False)
                window.FindElement('_TASK2_').Update(visible=False)
                window.FindElement('_CYCLE2_').Update(visible=False)
            if event == "stop/continue":
                is_clock_running = not is_clock_running
            if event == "reset":
                window.FindElement('_CYCLE2_').Update(self.default_mins)
                current_left_seconds = self.default_mins * 60
                # current_left_seconds = 3
                is_clock_running = False
                window.FindElement('_TASK1_').Update(visible=True)
                window.FindElement('_CYCLE1_').Update(visible=True)
                window.FindElement('_TASK2_').Update(visible=True)
                window.FindElement('_CYCLE2_').Update(visible=True)
            if event is None or event == 'Quit':  # if user closed the window using X or clicked Quit button
                break
            print(current_left_seconds, "hehe")
            window.FindElement('_COUNT_DOWN_').Update(
                '{:02d}:{:02d}:{:02d}'.format(current_left_seconds // 3600, current_left_seconds // 60,
                                              current_left_seconds % 60))


if __name__ == "__main__":
    # toaster = ToastNotifier()
    # toaster.show_toast("Example two", "This notification is in it's own thread!", icon_path=None, duration=5)

    gui = TomatoClock()
    gui.run()
