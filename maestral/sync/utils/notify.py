# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 16:23:13 2018

@author: samschott
"""
import os
from enum import Enum
from maestral.config.main import CONF
from maestral.sync.utils import is_macos_bundle

if is_macos_bundle:
    import Foundation
    import objc


class SupportedImplementation(Enum):
    notifySend = 'notify-send'
    osascript = 'osascript'


class Notipy(object):
    """Send native OS notifications to user.

    Relies on AppleScript on macOS and notify-send on linux, otherwise
    falls back to stdout."""

    def __init__(self):
        self.implementation = self.__get_available_implementation()

    def send(self, message, title="Maestral"):
        self.__send_message(message, title)

    def __send_message(self, message, title=""):
        if is_macos_bundle:
            notify_macOS_bundle(title, message)
        elif self.implementation == SupportedImplementation.osascript:
            os.system("osascript -e 'display notification \"{}\" with title \"{}\"'".format(message, title))
        elif self.implementation == SupportedImplementation.notifySend:
            os.system('notify-send "{}" "{}"'.format(title, message))
        else:
            print('{}: {}'.format(title, message))

    @staticmethod
    def __command_exists(command):
        return any(
            os.access(os.path.join(path, command), os.X_OK)
            for path in os.environ["PATH"].split(os.pathsep)
        )

    def __get_available_implementation(self):
        if self.__command_exists('osascript'):
            return SupportedImplementation.osascript
        elif self.__command_exists('notify-send'):
            return SupportedImplementation.notifySend
        return None


if is_macos_bundle:

    NSUserNotification = objc.lookUpClass('NSUserNotification')
    NSUserNotificationCenter = objc.lookUpClass('NSUserNotificationCenter')


    def notify_macOS_bundle(title, info_text, subtitle=None, delay=0, sound=False,
                            userInfo={}):
        notification = NSUserNotification.alloc().init()
        notification.setTitle_(title)
        if subtitle:
            notification.setSubtitle_(subtitle)
        notification.setInformativeText_(info_text)
        notification.setUserInfo_(userInfo)
        if sound:
            notification.setSoundName_("NSUserNotificationDefaultSoundName")
        notification.setDeliveryDate_(Foundation.NSDate.dateWithTimeInterval_sinceDate_(delay, Foundation.NSDate.date()))
        NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)