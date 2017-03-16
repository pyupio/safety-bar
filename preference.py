# -*- coding: utf-8 -*-
import os
import objc
from Cocoa import NSObject
from Foundation import (
    NSData,
    NSIndexSet,
    NSMakeRect,
    NSPredicate,
    NSFileManager,
    NSMutableArray,
    NSJSONSerialization,
    NSMutableDictionary,
)
from AppKit import (
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
        script_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(script_dir, ".pyupconfig")

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
        paths = settings['paths'].filteredArrayUsingPredicate_(pred).valueForKeyPath_("path")

        settings['paths'] = paths

        return settings

    @classmethod
    def load(cls):
        '''
        Load the all paths from setting file
        :return An array which contain all the directory model
        '''
        settingPath = cls.settingPath()
        fm = NSFileManager.defaultManager()
        paths = NSMutableArray.array()
        settings = NSMutableDictionary.dictionary()
        if fm.fileExistsAtPath_isDirectory_(settingPath, None)[0]:
            settingFile = NSData.dataWithContentsOfFile_(settingPath)
            jsonData = NSJSONSerialization.JSONObjectWithData_options_error_(settingFile, 0, None)[0]
            settings['startup'] = jsonData['startup']
            settings['api_key'] = jsonData['api_key']
            for item in jsonData['paths']:
                directory = Directory.alloc().initWithDict_(item)
                paths.addObject_(directory)
            settings['paths'] = paths
        else:
            settings['startup'] = True
            settings['api_key'] = ''
            settings['paths'] = paths
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
        self.data = NSMutableDictionary.dictionaryWithDictionary_(settings)

    def _setupContentView(self):
        # ------------------------------------------ #
        #                   Table View               #
        # ------------------------------------------ #
        rect = NSMakeRect(0, 0, self.WIDTH, self.HEIGHT)
        containerView = NSView.alloc().initWithFrame_(rect)

        # Startup btn
        height = 20
        margin = 20
        width = self.WIDTH - 2 * margin
        self.startupBtn = NSButton.buttonWithTitle_target_action_("Run safetyapp on startup", self, "startupDidChanged:")
        self.startupBtn.setButtonType_(NSButtonTypeSwitch)
        self.startupBtn.setFrame_(NSMakeRect(margin, self.HEIGHT - 2 * height, width, height))
        self.startupBtn.setState_(self.data["startup"])
        containerView.addSubview_(self.startupBtn)

        # API Key settings
        titleLabel = NSTextField.labelWithString_("API Key")
        titleLabel.setTextColor_(NSColor.blackColor())
        rect = NSMakeRect(self.startupBtn.frame().origin.x, self.startupBtn.frame().origin.y - self.startupBtn.frame().size.height - height, width, height)
        titleLabel.setFrame_(rect)
        titleLabel.setFont_(NSFont.boldSystemFontOfSize_(14))
        containerView.addSubview_(titleLabel)

        # API Key Sub-label
        titleSubLabel = NSTextField.labelWithString_("Lorem lpsum dolor sit amet")
        titleSubLabel.setTextColor_(NSColor.blackColor())
        rect = NSMakeRect(titleLabel.frame().origin.x, titleLabel.frame().origin.y - titleLabel.frame().size.height - height / 2, width, height)
        titleSubLabel.setFrame_(rect)
        titleSubLabel.setFont_(NSFont.systemFontOfSize_(14))
        containerView.addSubview_(titleSubLabel)

        # API Key text field
        self.apiTextField = NSTextField.textFieldWithString_("")
        rect = NSMakeRect(titleSubLabel.frame().origin.x, titleSubLabel.frame().origin.y - titleSubLabel.frame().size.height - height / 2, width, 1.2 * height)
        self.apiTextField.setFrame_(rect)
        self.apiTextField.setFocusRingType_(NSFocusRingTypeNone)
        self.apiTextField.setTitleWithMnemonic_(self.data["api_key"])
        self.apiTextField.setEditable_(True)
        containerView.addSubview_(self.apiTextField)
        self.window().makeFirstResponder_(self.apiTextField)

        # Table title
        tableTitleLabel = NSTextField.labelWithString_("Directories")
        tableTitleLabel.setTextColor_(NSColor.blackColor())
        rect = NSMakeRect(self.apiTextField.frame().origin.x, self.apiTextField.frame().origin.y - self.apiTextField.frame().size.height - height, width, height)
        tableTitleLabel.setFrame_(rect)
        tableTitleLabel.setFont_(NSFont.boldSystemFontOfSize_(14))
        containerView.addSubview_(tableTitleLabel)

        # Table sub-title
        tableSubTitleLabel = NSTextField.labelWithString_("Lorem lpsum dolor sit amet")
        tableSubTitleLabel.setTextColor_(NSColor.blackColor())
        rect = NSMakeRect(tableTitleLabel.frame().origin.x, tableTitleLabel.frame().origin.y - tableTitleLabel.frame().size.height - height / 2, width, height)
        tableSubTitleLabel.setFrame_(rect)
        tableSubTitleLabel.setFont_(NSFont.systemFontOfSize_(14))
        containerView.addSubview_(tableSubTitleLabel)

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

        rect = NSMakeRect(86, 21, self.WIDTH - 2 * margin - rect.size.width + 1, 21)
        toolbar = NSButton.alloc().initWithFrame_(rect)
        toolbar.setTitle_("")
        toolbar.setRefusesFirstResponder_(True)
        toolbar.setBezelStyle_(NSBezelStyleSmallSquare)
        containerView.addSubview_(toolbar)

        height = tableSubTitleLabel.frame().origin.y - segControl.frame().origin.y - margin - segControl.frame().size.height + 1 + tableSubTitleLabel.frame().size.height / 2
        rect = NSMakeRect(tableSubTitleLabel.frame().origin.x, tableSubTitleLabel.frame().origin.y - tableSubTitleLabel.frame().size.height / 2 - height, width, height)
        scrollView = NSScrollView.alloc().initWithFrame_(rect)
        scrollView.setBorderType_(NSBezelBorder)

        self.tableView = NSTableView.alloc().initWithFrame_(scrollView.bounds())
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
        jsonData = NSMutableDictionary.dictionaryWithDictionary_(self.data)
        paths = NSMutableArray.array()
        for directory in self.data['paths']:
            paths.addObject_(directory.directoryToDict())

        jsonData['paths'] = paths
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
            self.data['paths'].removeObjectAtIndex_(self.tableView.selectedRow())
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
                if self.data['paths'].filteredArrayUsingPredicate_(pred).count() > 0:
                    continue

                directory = Directory.alloc().init()
                directory.path = url.path()
                directory.enable = True
                directory.depth = 1

                self.tableView.beginUpdates()
                self.data['paths'].addObject_(directory)
                index = NSIndexSet.indexSetWithIndex_(self.data['paths'].count() - 1)
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
        return self.data['paths'].count()

    def tableView_objectValueForTableColumn_row_(self, tableView, tableColumn, row):
        directory = self.data['paths'].objectAtIndex_(row)
        if tableColumn.identifier() == self.PATH_COL_IDENTIFIER:
            return directory.path
        elif tableColumn.identifier() == self.ENALBE_COL_IDENTIFIER:
            return directory.enable
        return None

    def tableView_setObjectValue_forTableColumn_row_(self, tableView, obj, tableColumn, row):
        if tableColumn.identifier() == self.ENALBE_COL_IDENTIFIER:
            directory = self.data['paths'].objectAtIndex_(row)
            directory.enable = obj

            # Save to file
            self.saveSettings()

    # ------------------------------------------------- #
    #                   NSWindowDelegate                #
    # ------------------------------------------------- #

    def windowWillClose_(self, notification):
        # Save settings when window to be closed
        self.data["startup"] = False if self.startupBtn.state() == 0 else True
        self.data["api_key"] = self.apiTextField.stringValue()
        self.saveSettings()

        # Notify the app to reload settings
        self.callback(*self.args)

    # def canBecomeKeyWindow(self):
    #     return True
