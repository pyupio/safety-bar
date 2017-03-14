#!/bin/env python3
# -*- coding: utf-8 -*-

import objc
from Cocoa import NSObject
from Foundation import NSDictionary


class Directory(NSObject):
    def initWithDict_(self, dictionary):
        self = objc.super(Directory, self).init()
        if self is not None:
            self.path = dictionary.objectForKey_("path")
            self.enable = dictionary.objectForKey_("enable")
            self.depth = dictionary.objectForKey_("depth").integerValue()
        return self

    def copyWithZone_(self, zone):
        newCopy = Directory.alloc().init()
        newCopy.path = self.path
        newCopy.enable = self.enable
        newCopy.depth = self.depth
        return newCopy

    def initWithCoder_(self, aDecoder):
        self = objc.super(Directory, self).init()
        if self is not None:
            self.path = aDecoder.decodeObjectForKey_("path")
            self.enable = aDecoder.decodeBoolForKey_("enable")
            self.depth = aDecoder.decodeIntegerForKey_("depth")
        return self

    def encodeWithCoder_(self, aCoder):
        aCoder.encodeObject_forKey_(self.path, "path")
        aCoder.encodeBool_forKey_(self.enable, "enable")
        aCoder.encodeInteger_forKey_(self.depth, "depth")

    def directoryToDict(self):
        return NSDictionary.dictionaryWithObjectsAndKeys_(
            self.path, "path",
            self.enable, "enable",
            self.depth, "depth", None)
