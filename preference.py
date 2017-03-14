# -*- coding: utf-8 -*-

import objc
from Cocoa import NSObject
from Foundation import (
    NSData,
    NSIndexSet,
    NSMakeRect,
    NSPredicate,
    NSFileManager,
    NSMutableArray,
    NSHomeDirectory,
    NSJSONSerialization
)
from AppKit import (
    NSApp,
    NSView,
    NSFont,
    NSAlert,
    NSImage,
    NSButton,
    NSColor,
    NSTableView,
    NSOpenPanel,
    NSScrollView,
    NSTextField,
    NSButtonCell,
    NSBezelBorder,
    NSTableColumn,
    NSTextFieldCell,
    NSModalResponseOK,
    NSWindowController,
    NSButtonTypeSwitch,
    NSSegmentedControl,
    NSFocusRingTypeNone,
    NSImageNameAddTemplate,
    NSBezelStyleSmallSquare,
    NSSegmentStyleSmallSquare,
    NSImageNameRemoveTemplate,
    NSTableViewAnimationSlideUp,
    NSTableViewAnimationEffectFade,
)

from models import Directory


class PreferenceSetting(NSObject):
    '''
    PreferenceSetting is a helper function to load pyup settings
    from user home dir, filename: ~/.pyupconfig file.
    '''
    @classmethod
    def settingPath(cls):
        '''
        Get the setting file absolute path
        :return The path for the setting file
        '''
        return NSHomeDirectory().stringByAppendingPathComponent_(".pyupconfig")

    @classmethod
    def loadPathSettings(cls):
        '''
        Load the active paths from setting file
        :return An array which contain the active paths
        '''
        settings = cls.load()
        # Filter the directory when enable
        pred = NSPredicate.predicateWithFormat_("enable == 1")
        # Retrieve active path array
        paths = settings.filteredArrayUsingPredicate_(pred).valueForKeyPath_("path")
        return tuple(paths)

    @classmethod
    def load(cls):
        '''
        Load the all paths from setting file
        :return An array which contain all the directory model
        '''
        settingPath = cls.settingPath()
        fm = NSFileManager.defaultManager()
        settings = NSMutableArray.array()
        if fm.fileExistsAtPath_isDirectory_(settingPath, None)[0]:
            settingFile = NSData.dataWithContentsOfFile_(settingPath)
            jsonData = NSJSONSerialization.JSONObjectWithData_options_error_(settingFile, 0, None)
            for item in jsonData[0]:
                directory = Directory.alloc().initWithDict_(item)
                settings.addObject_(directory)
        return settings


class PreferenceController(NSWindowController):

    # Preference window width
    WIDTH = 500

    # Preference window height
    HEIGHT = 500

    # Preference table view path column identifier
    PATH_COL_IDENTIFIER = "pathColumn"

    # Preference table view is enable column identifier
    ENALBE_COL_IDENTIFIER = "enableColumn"

    def initWithWindow_(self, window):
        '''
        Initialize a PreferenceController with window
        :param  window A NSWindow instance
        :return A PreferenceController window controller instance
        '''
        self = objc.super(PreferenceController, self).initWithWindow_(window)

        # Get notified when window is closed
        window.setDelegate_(self)

        if self is None:
            return None
        self.setup()
        return self

    def _setupPaths(self):
        '''
        Read the path setting from ~/.pyupconfig
        '''
        self.settingPath = PreferenceSetting.settingPath()
        settings = PreferenceSetting.load()
        self.data = NSMutableArray.arrayWithArray_(settings)

    def _setupContentView(self):
        # ------------------------------------------ #
        #                   Table View               #
        # ------------------------------------------ #
        rect = NSMakeRect(0, 0, self.WIDTH, self.HEIGHT)
        containerView = NSView.alloc().initWithFrame_(rect)

        margin = 20
        rect = NSMakeRect(margin, 2 * margin, self.WIDTH - 2 * margin, self.HEIGHT - 6 * margin)
        scrollView = NSScrollView.alloc().initWithFrame_(rect)
        scrollView.setBorderType_(NSBezelBorder)

        rect = NSMakeRect(0, 0, self.WIDTH - 2 * margin, self.HEIGHT - 2 * margin)
        self.tableView = NSTableView.alloc().initWithFrame_(rect)
        self.tableView.setDataSource_(self)
        self.tableView.setDelegate_(self)
        self.tableView.setFocusRingType_(NSFocusRingTypeNone)

        # Path column
        pathCol = NSTableColumn.alloc().initWithIdentifier_(self.PATH_COL_IDENTIFIER)
        pathCol.setTitle_("Directory")  # <-- Table view directory column title
        pathCol.setWidth_(self.WIDTH * 0.8)
        textCell = NSTextFieldCell.alloc().init()
        textCell.setEditable_(True)
        textCell.setTarget_(self)
        pathCol.setDataCell_(textCell)

        # Enable column
        enableCol = NSTableColumn.alloc().initWithIdentifier_(self.ENALBE_COL_IDENTIFIER)
        enableCol.setTitle_("Enable?")  # <-- Enable column title
        enableCol.setWidth_(self.WIDTH * 0.2)
        cell = NSButtonCell.alloc().init()
        cell.setButtonType_(NSButtonTypeSwitch)
        cell.setTitle_("")
        cell.setTarget_(self)
        enableCol.setDataCell_(cell)

        self.tableView.addTableColumn_(pathCol)
        self.tableView.addTableColumn_(enableCol)

        # ------------------------------------------ #
        #               Title label                  #
        # ------------------------------------------ #

        titleLabel = NSTextField.labelWithString_("Preference")
        titleLabel.setTextColor_(NSColor.blackColor())
        titleLabel.setFrame_(NSMakeRect(margin, self.HEIGHT - 1.5 * margin, self.WIDTH - 2 * margin, margin))
        titleLabel.setFont_(NSFont.boldSystemFontOfSize_(14))
        containerView.addSubview_(titleLabel)

        label = NSTextField.labelWithString_("The following directories will be check dependencies every 1 hour")
        label.setTextColor_(NSColor.blackColor())
        label.setFrame_(NSMakeRect(margin, self.HEIGHT - 3 * margin, self.WIDTH - 2 * margin, margin))
        label.setFont_(NSFont.systemFontOfSize_(14))
        containerView.addSubview_(label)

        # ------------------------------------------ #
        #               Toolbar button               #
        # ------------------------------------------ #
        rect = NSMakeRect(20, 20, 67, 21)
        segControl = NSSegmentedControl.alloc().initWithFrame_(rect)
        segControl.setSegmentCount_(2)
        segControl.setSegmentStyle_(NSSegmentStyleSmallSquare)
        segControl.setWidth_forSegment_(32, 0)
        segControl.setWidth_forSegment_(32, 1)
        segControl.setImage_forSegment_(NSImage.imageNamed_(NSImageNameAddTemplate), 0)
        segControl.setImage_forSegment_(NSImage.imageNamed_(NSImageNameRemoveTemplate), 1)
        segControl.setTarget_(self)

        segControl.setAction_("segControlDidClicked:")

        containerView.addSubview_(segControl)

        width = self.WIDTH - 2 * margin - rect.size.width + 1
        rect = NSMakeRect(86, 21, width, 21)
        toolbar = NSButton.alloc().initWithFrame_(rect)
        toolbar.setTitle_("")
        toolbar.setRefusesFirstResponder_(True)
        toolbar.setBezelStyle_(NSBezelStyleSmallSquare)
        containerView.addSubview_(toolbar)

        scrollView.setDocumentView_(self.tableView)
        scrollView.setHasVerticalScroller_(True)
        containerView.addSubview_(scrollView)
        self.window().setContentView_(containerView)

    def setup(self):
        '''
        Setup UI
        '''
        self._setupPaths()

        self._setupContentView()

    def saveSettings(self):
        '''
        Save the path setting to setting file
        '''
        jsonData = NSMutableArray.arrayWithCapacity_(self.data.count())
        for directory in self.data:
            jsonData.addObject_(directory.directoryToDict())

        data = NSJSONSerialization.dataWithJSONObject_options_error_(jsonData, 0, None)
        if len(data) > 0 and not data[0].writeToFile_atomically_(self.settingPath, True):
            alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
                "Error",
                "Confirm",
                None,
                None,
                "Save setting failed."
            )
            alert.runModal()
        else:
            # Notify the app to reload settings
            self.callback(*self.args)

    def segControlDidClicked_(self, segment):
        '''
        IBAction for add/remove button is clicked
        '''
        if segment.selectedSegment() == 0:
            self._addDirectory()
        else:
            self._removeDirectory()

        segment.setSelectedSegment_(-1)

    def _removeDirectory(self):
        '''
        Remove directory from settings
        '''
        if self.tableView.selectedRow() == -1:
            alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
                "Error",
                "Confirm",
                None,
                None,
                "Please select a row first."
            )
            alert.runModal()
        else:
            self.tableView.beginUpdates()
            self.data.removeObjectAtIndex_(self.tableView.selectedRow())
            index = NSIndexSet.indexSetWithIndex_(self.tableView.selectedRow())
            self.tableView.removeRowsAtIndexes_withAnimation_(index, NSTableViewAnimationEffectFade)
            self.tableView.endUpdates()

            # Save to file
            self.saveSettings()

    def _addDirectory(self):
        '''
        Add directory to settings
        '''
        panel = NSOpenPanel.openPanel()
        panel.setCanChooseFiles_(False)
        panel.setCanChooseDirectories_(True)
        panel.setAllowsMultipleSelection_(True)
        if panel.runModal() == NSModalResponseOK:
            for url in panel.URLs():
                pred = NSPredicate.predicateWithFormat_("path == %@", url.path())
                if self.data.filteredArrayUsingPredicate_(pred).count() > 0:
                    continue

                directory = Directory.alloc().init()
                directory.path = url.path()
                directory.enable = True
                directory.depth = 1

                self.tableView.beginUpdates()
                self.data.addObject_(directory)
                index = NSIndexSet.indexSetWithIndex_(self.data.count() - 1)
                self.tableView.insertRowsAtIndexes_withAnimation_(index, NSTableViewAnimationSlideUp)
                self.tableView.endUpdates()

                # Save to file
                self.saveSettings()

    def setSettingChangedCallback_withArgs_(self, callback, args):
        '''
        Register settings change callback
        :param  callback  The callback for settings is changed
        :param  args      The arguments for the callback
        '''
        self.callback = callback
        self.args = args

    # ------------------------------------------------- #
    #       Table View data source / delegate           #
    # ------------------------------------------------- #

    def numberOfRowsInTableView_(self, tableView):
        return self.data.count()

    def tableView_objectValueForTableColumn_row_(self, tableView, tableColumn, row):
        directory = self.data.objectAtIndex_(row)
        if tableColumn.identifier() == self.PATH_COL_IDENTIFIER:
            return directory.path
        elif tableColumn.identifier() == self.ENALBE_COL_IDENTIFIER:
            return directory.enable
        return None

    def tableView_setObjectValue_forTableColumn_row_(self, tableView, obj, tableColumn, row):
        if tableColumn.identifier() == self.ENALBE_COL_IDENTIFIER:
            directory = self.data.objectAtIndex_(row)
            directory.enable = obj

            # Save to file
            self.saveSettings()

    # ------------------------------------------------- #
    #                   NSWindowDelegate                #
    # ------------------------------------------------- #

    def showWindow_(self, sender):
        # Bring the window to the front
        NSApp.activateIgnoringOtherApps_(True)
        objc.super(PreferenceController, self).showWindow_(sender)

    def windowWillClose_(self, notification):
        # Bring the window to the back
        NSApp.activateIgnoringOtherApps_(False)
