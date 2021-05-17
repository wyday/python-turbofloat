# -*- coding: utf-8 -*-
#
# Copyright 2021 wyDay, LLC (https://wyday.com/)
#
# Current Author / maintainer:
#
#   Author: wyDay, LLC <support@wyday.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from ctypes import pointer, c_uint32, c_ushort

from turbofloat.c_wrapper import *

import os
import sys

#
# Object oriented interface
#


class TurboFloat(object):

    def __init__(self, guid, callback, dat_file_loc = "", library_folder = ""):

        # load the executing file's location
        if getattr(sys, 'frozen', False):
            # running in a bundle
            execFileLoc = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # running live
            execFileLoc = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))

        if not library_folder:
            library_folder = execFileLoc

        # form the full, absolute path to the TurboActivate.dat file
        if not dat_file_loc:
            dat_file_loc = os.path.join(execFileLoc, "TurboActivate.dat")

        self._lib = load_library(library_folder)
        self._set_restype()

        try:
            self._lib.TF_PDetsFromPath(wstr(dat_file_loc))
        except TurboFloatFailError:
            # The dat file is already loaded
            pass

        self._handle = self._lib.TF_GetHandle(wstr(guid))

        # if the handle is still unset then immediately throw an exception
        # telling the user that they need to actually load the correct
        # TurboActivate.dat and/or use the correct GUID for the TurboActivate.dat
        if self._handle == 0:
            raise TurboFloatDatFileError()

        # "cast" the native python function to LeaseCallback type
        # save it locally so that it acutally works when it's called
        # back
        self._callback = LeaseCallback(callback)

        self._lib.TF_SetLeaseCallback(self._handle, self._callback)

    #
    # Public
    #

    # Server

    def save_server(self, host_address, port, flags):
        """
        Saves the TurboFloat server location on the disk. You must call this function at
        least once before requesting a lease from the server. A good place to call this function
        is from your installer (so an IT admin could set the server location once).

        Using the "port" value of 443 is equivalent to passing in the "TF_REQUEST_OVER_HTTPS"
        flag. If you want to contact a TFS instance over HTTPS and not use port 443
        then you *must* pass in the "TF_REQUEST_OVER_HTTPS" flag. You cannot use "raw"
        (non-HTTPS) communication on port 443.


        Note: If you pass in the TF_SYSTEM flag and you don't have "admin" or "elevated"
        permission then the call will fail.

        If you call this function once in the past with the flag TF_SYSTEM and the calling
        process was an admin process then subsequent calls with the TF_SYSTEM flag will
        succeed even if the calling process is *not* admin/elevated.

        If you want to take advantage of this behavior from an admin process
        (e.g. an installer) but the user hasn't entered a product key then you can
        call this function with a null string:

                    TF_SaveServer(YourHandle, 0, 0, TF_SYSTEM);

        This will set everything up so that subsequent calls with the TF_SYSTEM flag will
        succeed even if from non-admin processes.
        """
        self._lib.TF_SaveServer(self._handle, wstr(host_address), c_ushort(port), flags)

    def get_server(self):
        """
        Gets the stored TurboFloat Server location.
        """

        buf_size = self._lib.TF_GetServer(self._handle, 0, 0, 0)
        buf = wbuf(buf_size)
        port = c_ushort(0)

        self._lib.TF_GetServer(self._handle, buf, buf_size, pointer(port))

        return buf.value, port.value


    # Leases

    def request_lease(self):
        """
        Requests a floating license lease from the TurboFloat Server. You should run
        this at the top of your app after calling TF_SetLeaseCallback().
        """

        self._lib.TF_RequestLease(self._handle)


    def drop_lease(self):
        """
        Drops the active lease from the TurboFloat Server. This frees up the lease
        so it can be used by another instance of your app.

        We recommend calling this before your application exits.

        Note: This function does *not* call the lease callback function. If you want that
                behavior then you can do it like this:


                if (TF_DropLease(tfHandle) == TF_OK)
                {
                    YourLeaseCallbackFunction(TF_CB_EXPIRED);
                }
        """

        self._lib.TF_DropLease(self._handle)


    def has_lease(self):
        """
        Lets you know whether there's an active lease for the handle specified. This function
        isn't necessary if you're tracking the responses from TF_RequestLease(), TF_DropLease(),
        and the callback function that you set in TF_SetLeaseCallback().
        """

        ret = self._lib.TF_HasLease(self._handle)

        if ret == TF_OK:
            return True
        elif ret == TF_FAIL:
            return False

        # raise an error on all other return codes
        validate_result(ret)

    # License fields

    def has_feature(self, name):
        return len(self.get_feature_value(name)) > 0

    def get_feature_value(self, name):
        """Gets the value of a feature."""
        buf_size = self._lib.TF_GetFeatureValue(self._handle, wstr(name), 0, 0)
        buf = wbuf(buf_size)

        self._lib.TF_GetFeatureValue(self._handle, wstr(name), buf, buf_size)

        return buf.value

    # Utils

    def is_date_valid(self, date):
        """
        Check if the date is valid
        """

        try:
            self._lib.TF_IsDateValid(self._handle, wstr(date), TF_HAS_NOT_EXPIRED)

            return True
        except TurboFloatFlagsError as e:
            raise e
        except TurboFloatError:
            return False

    def set_custom_proxy(self, address):
        """
        Sets the custom proxy to be used when "https" protocol is enabled (when the
        TF_REQUEST_OVER_HTTPS flag is given to the TF_SaveServer() function).

        Proxy address in the form: http://username:password@host:port/

        Example 1 (just a host): http://127.0.0.1/
        Example 2 (host and port): http://127.0.0.1:8080/
        Example 3 (all 3): http://user:pass@127.0.0.1:8080/

        If the port is not specified, TurboFloat will default to using port 1080 for proxies.
        """
        self._lib.TF_SetCustomProxy(wstr(address))

    def cleanup(self):
        """
        You should call this before your application exits. This frees up any
        allocated memory for all open handles. If you have an active license
        lease then you should call tf.DropLease() before you call TurboFloat.Cleanup().
        """
        self._lib.TF_Cleanup()

    def get_version(self):
        """
        Gets the version number of the currently used TurboFloat library.
        This is a useful alternative for platforms which don't support file meta-data
        (like Linux, FreeBSD, and other unix variants).

        The version format is:  Major.Minor.Build.Revision
        """
        major = c_uint32(0)
        minor = c_uint32(0)
        build = c_uint32(0)
        rev = c_uint32(0)

        self._lib.TF_GetVersion(pointer(major), pointer(minor), pointer(build), pointer(rev))

        return major.value, minor.value, build.value, rev.value

    def _set_restype(self):
        self._lib.TF_PDetsFromPath.restype = validate_result
        self._lib.TF_SetLeaseCallback.restype = validate_result
        self._lib.TF_SaveServer.restype = validate_result
        self._lib.TF_RequestLease.restype = validate_result
        self._lib.TF_DropLease.restype = validate_result
        self._lib.TF_IsDateValid.restype = validate_result
        self._lib.TF_SetCustomProxy.restype = validate_result
        self._lib.TF_Cleanup.restype = validate_result
