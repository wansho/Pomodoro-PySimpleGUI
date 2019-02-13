# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 11:14:29 2019

@author: wansho
"""
import threading
from win10toast import ToastNotifier

import PySimpleGUI as sg

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
        toaster = ToastNotifier()
        toaster.show_toast(self.application_name,
                           "Pomodoro task: " + task + " over.",
                           icon_path=None,
                           duration=8,
                           threaded=True)

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
        # Event Loop
        while True:
            event, values = window.Read(1000)
            current_left_seconds -= 1 * (is_clock_running is True)
            if current_left_seconds == 0 and is_clock_running: # Pomodoro over
                task = str(values["_TASK2_"])
                # show toast in thread
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
            # print(current_left_seconds, "debug")
            window.FindElement('_COUNT_DOWN_').Update(
                '{:02d}:{:02d}:{:02d}'.format(current_left_seconds // 3600, current_left_seconds // 60,
                                              current_left_seconds % 60))


if __name__ == "__main__":
    # toaster = ToastNotifier()
    # toaster.show_toast("Example two", "This notification is in it's own thread!", icon_path=None, duration=5)

    gui = TomatoClock()
    gui.run()

