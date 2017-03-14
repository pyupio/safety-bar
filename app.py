# -*- coding: utf-8 -*-
import os
import objc
import rumps
import subprocess
import threading
import sys

from Cocoa import NSObject
from rumps import MenuItem
from Foundation import NSLog, NSMakeRect
from AppKit import (
    NSWindow,
    NSBackingStoreBuffered,
    NSTitledWindowMask,
    NSClosableWindowMask,
)

from safety.safety import check
from safety.util import (
    read_requirements,
    Package as SafetyPackage,
    RequirementFile as SafetyRequirementFile
)
from preference import PreferenceController, PreferenceSetting

__version__ = "0.1"

# icons come bundled with the binary
try:
    ROOT = sys._MEIPASS
except AttributeError:
    ROOT = os.path.dirname(os.path.realpath(__file__))

DEBUG = True

if DEBUG:
    def log(message):
        NSLog(message)
else:
    def log(_):
        pass


class UIHelper(NSObject):
    '''
    A helper to interact with UI, eg UI update
    '''
    def initWithApp_(self, app):
        '''
        Init Helper with rumps app instance
        interpret as Objc selector: initWithApp:
        '''
        self = objc.super(UIHelper, self).init()
        if self is None:
            return None
        self._app = app
        self.add = 0
        return self

    def updateMenuItem_(self, menu_item):
        '''
        Update the menu item
        :param menu_item  The menu item to be added to menu
        '''
        separator_key = 'separator_1'
        if separator_key not in self._app.menu.keys():
            # Add separator
            self._app.menu.insert_before('Preferences', rumps.separator)

        if menu_item.key not in self._app.menu.keys():
            # Add directory
            self._app.menu.insert_before(separator_key, menu_item)
        else:
            self._app.menu.update(menu_item)


class ICONS:
    GRAY = os.path.join(ROOT, 'icons/gray.png')
    GREEN = os.path.join(ROOT, 'icons/green.png')
    RED = os.path.join(ROOT, 'icons/red.png')


class RequirementFile(object):

    def __init__(self, project, path, requirements):
        self.project = project
        self.path = path

        self.menu_item = MenuItem(
            self.path,
            key=path,
            callback=self.clicked,
            icon=ICONS.GRAY,
        )

        self.requirements = requirements

    def clicked(self, sender):
        subprocess.call(['open', self.path])

    def check(self):
        vulns = check(self.requirements)
        if vulns:
            self.menu_item.icon = ICONS.RED
        else:
            self.menu_item.icon = ICONS.GREEN
        return vulns


class Project(object):

    def __init__(self, app, path):
        self.app = app
        self.path = path
        self.name = path.split("/")[-1]
        self.insecure = None

        self.menu_item = MenuItem(
            self.path,
            callback=self.clicked,
            key=self.path,
            icon=ICONS.GRAY,
        )

        self.requirement_files = None
        self.ui_helper = UIHelper.alloc().initWithApp_(app)

    @property
    def is_valid(self):
        return self.requirement_files is not None and self.requirement_files

    @property
    def needs_check(self):
        return self.insecure is None

    def find_requirement_files(self):
        def is_likely_a_requirement(path):
            if "req" in path:
                if path.endswith(".txt") or path.endswith(".pip"):
                    return True
            return False

        def parse(file_name):
            reqs = []
            try:
                with open(file_name) as fh:
                    for item in read_requirements(fh):
                        if isinstance(item, SafetyPackage):
                            reqs.append(item)
                        elif isinstance(item, SafetyRequirementFile):
                            for other_file in parse(item.path):
                                yield other_file
                    if reqs:
                        yield RequirementFile(
                            project=self,
                            requirements=reqs,
                            path=file_name
                        )
            except:
                pass

        for item in os.listdir(self.path):
            full_path = os.path.join(self.path, item)
            if os.path.isdir(full_path):
                for item_deep in os.listdir(full_path):
                    full_path_deep = os.path.join(full_path, item_deep)
                    if os.path.isfile(full_path_deep) and is_likely_a_requirement(full_path_deep):
                        for req_file in parse(full_path_deep):
                            yield req_file
            elif os.path.isfile(full_path) and is_likely_a_requirement(full_path):
                for req_file in parse(full_path):
                    yield req_file

    def check(self):
        if self.requirement_files is None:
            self.requirement_files = list(self.find_requirement_files())

        insecure = False
        for req in self.requirement_files:
            vulns = req.check()
            if vulns:
                insecure = True
        self.insecure = insecure
        if insecure:
            self.menu_item.icon = ICONS.RED
        else:
            self.menu_item.icon = ICONS.GREEN

    def add(self):
        self.menu_item.update(
            [r.menu_item for r in self.requirement_files]
        )

        # self.app.menu.update(self.menu_item)
        self.ui_helper.pyobjc_performSelectorOnMainThread_withObject_('updateMenuItem:', self.menu_item)

    def clicked(self, sender):
        subprocess.call(['open', self.path])

    def __eq__(self, other):
        if isinstance(other, Project):
            return self.path == other.path
        return super(Project, self).__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)


class PyupStatusBarApp(rumps.App):
    def __init__(self):
        super(PyupStatusBarApp, self).__init__(
            name="pyup",
        )

        self.projects = []

        # Load the settings from file
        self.reloadSettings()

    @rumps.clicked('Preferences')
    def preferences(self, _):
        if 'prefController' not in self.__dict__:
            # Initialize preference window
            rect = NSMakeRect(0, 0, 500, 500)
            window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                rect,
                NSTitledWindowMask | NSClosableWindowMask,
                NSBackingStoreBuffered,
                False)
            window.center()
            self.prefController = PreferenceController.alloc().initWithWindow_(window)
            self.prefController.setSettingChangedCallback_withArgs_(self.reloadSettings, [])
        self.prefController.showWindow_(self)

    def sync(self):
        log('Sync Thread {} is about to run...'.format(threading.current_thread().name))
        if self.icon is None:
            self.icon = ICONS.GRAY
        try:
            insecure = False
            for path in self.settings['paths']:
                for item in os.listdir(path):
                    full_path = os.path.join(path, item)
                    if os.path.isdir(full_path):
                        project = Project(self, full_path)
                        log("have {}".format(full_path))
                        if project not in self.projects:
                            self.projects.append(project)
                            if project.needs_check:
                                project.check()
                                if project.is_valid:
                                    project.add()
                                    if project.insecure:
                                        insecure = True
            if insecure:
                self.icon = ICONS.RED
            else:
                self.icon = ICONS.GREEN

            log('Sync Thread {} run finished.'.format(threading.current_thread().name))
        except:
            import traceback
            traceback.print_exc()

    @rumps.timer(60 * 60)  # run every hour
    def refresh(self, _):
        t = threading.Thread(target=self.sync, name='SyncThread')
        t.start()

    def reloadSettings(self, *args):
        self.settings = {
            'paths': PreferenceSetting.loadPathSettings(),
            'depth': 1,
            'key': ''
        }
        log('Setting is reloaed')


if __name__ == "__main__":
    PyupStatusBarApp().run(
        debug=True
    )
