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

import sys
from os import path as ospath
from ctypes import (
    cdll,
    c_uint32,
    c_char_p,
    c_wchar_p,
    create_string_buffer,
    create_unicode_buffer,
    CFUNCTYPE
)

# Utilities

# python 2.7 string.encode('utf-8') returns an str class
# python 3.6 string.encode('utf-8') returns a bytes class

is_win = sys.platform == "win32"

wbuf = create_unicode_buffer if is_win else create_string_buffer

wstr_type = c_wchar_p if is_win else c_char_p


class wstr(wstr_type):
    def __init__(self, string):
        if sys.version_info > (3, 0) and isinstance(string, str):
            super(wstr, self).__init__(string.encode('utf-8') if not is_win else string)
        else:
            super(wstr, self).__init__(string)


# Wrapper

TF_OK = 0x00000000
TF_FAIL = 0x00000001
TF_E_SERVER = 0x00000002
TF_E_NO_CALLBACK = 0x00000003
TF_E_INET = 0x00000004
TF_E_NO_FREE_LEASES = 0x00000005
TF_E_LEASE_EXISTS = 0x00000006
TF_E_WRONG_TIME = 0x00000007
TF_E_PDETS = 0x00000008
TF_E_INVALID_HANDLE = 0x00000009
TF_E_NO_LEASE = 0x0000000A
TF_E_COM = 0x0000000B
TF_E_INSUFFICIENT_BUFFER = 0x0000000C
TF_E_PERMISSION = 0x0000000D
TF_E_INVALID_FLAGS = 0x0000000E
TF_E_WRONG_SERVER_PRODUCT = 0x0000000F
TF_E_INET_TIMEOUT = 0x00000010
TF_E_UPGRADE_LIBRARY = 0x00000011
TF_E_USERNAME_NOT_ALLOWED = 0x00000012
TF_E_BAD_HOST_ADDRESS = 0x00000013
TF_E_CLIENT_IPC = 0x00000014
TF_E_SERVER_UUID_MISMATCH = 0x0000001B
TF_E_ENABLE_NETWORK_ADAPTERS = 0x0000001C
TF_E_BROKEN_WMI = 0x00000022
TF_E_INET_TLS = 0x00000024

# Flags for the TF_SaveServer() function.

TF_SYSTEM = 0x00000001
TF_USER = 0x00000002
TF_REQUEST_OVER_HTTPS = 0x00000004


# Flags for the is_date_valid() Function

TF_HAS_NOT_EXPIRED = 0x00000001


# Possible callback statuses from LeaseCallbackType and LeaseCallbackTypeEx functions:

'''
Called when the lease has expired and couldn't be renewed. You
should disable your app immediately when this return code is called.
Of course give your user a way to save the current state of their
data and/or request a lease renewal from the server.

In other words, don't make the user mad. Make sure you test this
extensively with real end-users so you get the best behavior.
'''
TF_CB_EXPIRED = 0x00000000

'''
Called when the lease has expired and couldn't be renewed due to
failure to connect to the TurboFloat Server.
'''
TF_CB_EXPIRED_INET = 0x00000001

'''
Called when the lease was renewed and some or all of the custom
license fields have since changed. If you use the TF_GetFeatureValue()
function then it behooves you to get the latest changed feature
values upon this callback status.
'''
TF_CB_FEATURES_CHANGED = 0x00000002

'''
Called when the lease has been dropped by the TurboFloat Server. You
should disable your app immediately when this return code is called.
Of course give your user a way to save the current state of their
data and/or request a lease renewal from the server.

In other words, don't make the user mad. Make sure you test this
extensively with real end-users so you get the best behavior.
'''
TF_CB_LEASE_DROPPED = 0x00000003

'''
Called when the lease has been dropped because the system has entered
sleep or hibernation mode. You should disable your app immediately when
this return code is called. Of course give your user a way to save the
current state of their data and/or request a lease renewal from the server.

In other words, don't make the user mad. Make sure you test this
extensively with real end-users so you get the best behavior.

When / if the system is resumed, TurboFloat will automatically attempt
to request the lease again. If it's successful the LeaseCallback
will be TF_CB_LEASE_REGAINED.
'''
TF_CB_LEASE_DROPPED_SLEEP = 0x00000004

'''
Called when the lease has been regained after having been
dropped from TF_CB_LEASE_DROPPED_SLEEP.

If the lease request is attempted and fails, this will
never be called.

The best real-world usage of this is when the lease
callback function drops the lease (or the lease expires)
show a user-prompt for the customer (whether via a dialog
box or other interactive method) and if this "TF_CB_LEASE_REGAINED"
is called, then hide that re-attempt dialog and re-enable your
'''
TF_CB_LEASE_REGAINED = 0x00000005


LeaseCallback = CFUNCTYPE(None, c_uint32)

def load_library(path):

    if sys.platform == 'win32' or sys.platform == 'cygwin':
        return cdll.LoadLibrary(ospath.join(path, 'TurboFloat.dll'))
    elif sys.platform == 'darwin':
        return cdll.LoadLibrary(ospath.join(path, 'libTurboFloat.dylib'))

    # else: linux, bsd, etc.
    return cdll.LoadLibrary(ospath.join(path, 'libTurboFloat.so'))


def validate_result(return_code):
    # All ok, no need to perform error handling.
    if return_code == TF_OK:
        return

    # Raise an exception type appropriate for the kind of error
    if return_code == TF_FAIL:
        raise TurboFloatFailError()
    elif return_code == TF_E_SERVER:
        raise TurboFloatServerError()
    elif return_code == TF_E_NO_CALLBACK:
        raise TurboFloatNoCallbackError()
    elif return_code == TF_E_NO_FREE_LEASES:
        raise TurboFloatNoFreeLeasesError()
    elif return_code == TF_E_LEASE_EXISTS:
        raise TurboFloatLeaseExistsError()
    elif return_code == TF_E_WRONG_TIME:
        raise TurboFloatWrongTimeError()
    elif return_code == TF_E_NO_LEASE:
        raise TurboFloatNoLeaseError()
    elif return_code == TF_E_PDETS:
        raise TurboFloatDatFileError()
    elif return_code == TF_E_INVALID_FLAGS:
        raise TurboFloatFlagsError()
    elif return_code == TF_E_WRONG_SERVER_PRODUCT:
        raise TurboFloatWrongServerProductError()
    elif return_code == TF_E_UPGRADE_LIBRARY:
        raise TurboFloatUpgradeLibraryError()
    elif return_code == TF_E_USERNAME_NOT_ALLOWED:
        raise TurboFloatUsernameNotAllowedError()
    elif return_code == TF_E_BAD_HOST_ADDRESS:
        raise TurboFloatBadHostAddressError()
    elif return_code == TF_E_CLIENT_IPC:
        raise TurboFloatClientIPCError()
    elif return_code == TF_E_SERVER_UUID_MISMATCH:
        raise TurboFloatServerUUIDMismatchError()
    elif return_code == TF_E_COM:
        raise TurboFloatComError()
    elif return_code == TF_E_INET:
        raise TurboFloatInetError()
    elif return_code == TF_E_PERMISSION:
        raise TurboFloatPermissionError()
    elif return_code == TF_E_INVALID_HANDLE:
        raise TurboFloatInvalidHandleError()
    elif return_code == TF_E_ENABLE_NETWORK_ADAPTERS:
        raise TurboFloatEnableNetworkAdaptersError()
    elif return_code == TF_E_BROKEN_WMI:
        raise TurboFloatBrokenWMIError()
    elif return_code == TF_E_INET_TIMEOUT:
        raise TurboFloatInetTimeoutError()
    elif return_code == TF_E_INET_TLS:
        raise TurboFloatInetTLSError()

    # Otherwise bail out and raise a generic exception
    raise TurboFloatError(return_code)


#
# Exception types
#

class TurboFloatError(Exception):

    """Generic TurboFloat error"""
    pass


class TurboFloatFailError(TurboFloatError):

    """Fail error"""
    pass


class TurboFloatInetError(TurboFloatError):

    """Connection to the server failed."""
    pass


class TurboFloatInetTimeoutError(TurboFloatInetError):

    """The connection to the server timed out because a long period of time
    elapsed since the last data was sent or received."""
    pass

class TurboFloatInetTLSError(TurboFloatInetError):

    """The secure connection to the activation servers failed due to a TLS or
    certificate error. More information here: https://wyday.com/limelm/help/faq/#internet-error"""
    pass

class TurboFloatServerError(TurboFloatError):

    """
    There's no server specified. You must call tf.save_server() at least once to save the server.
    """
    pass

class TurboFloatNoCallbackError(TurboFloatError):

    """
    You didn't specify a callback. Do so using the TF_SetLeaseCallback() or TF_SetLeaseCallbackEx() function.
    """
    pass

class TurboFloatNoFreeLeasesError(TurboFloatError):

    """
    There are no more free leases available from the TurboFloat server. Either
    increase the number of allowed floating licenses for the TurboFloat server
    or wait for one of the other leases to expire.
    """
    pass

class TurboFloatLeaseExistsError(TurboFloatError):

    """
    The lease has already been acquired. TurboFloat automatically renews the lease
    when it needs to based on the information the TurboFloat Server provides.
    """
    pass

class TurboFloatWrongTimeError(TurboFloatError):

    """
    This computer's system time is more than 5 minutes (before/after)
    different from the TurboFloat Server's system time. Make sure
    the server's Date, Time, and Timezone are set correctly and make
    sure this computer's Date, Time, and Timezone are set correctly.

    Note: That TurboFloat and TurboFloat Server work even if the timezones
        of the computer/server are different. In other words, your
        TurboFloat Server could be hosted in France and have a "client"
        computer running in New York (a 6 hour time difference) and
        everything will work fine provided both server and "client"
        have their date, time, and timezones correctly configured.
    """
    pass

class TurboFloatComError(TurboFloatError):

    """
    The hardware id couldn't be generated due to an error in the COM setup.
    Re-enable Windows Management Instrumentation (WMI) in your group policy
    editor or reset the local group policy to the default values. Contact
    your system admin for more information.

    This error is Windows only.

    This error can also be caused by the user (or another program) disabling
    the "Windows Management Instrumentation" service. Make sure the "Startup type"
    is set to Automatic and then start the service.


    To further debug WMI problems open the "Computer Management" (compmgmt.msc),
    expand the "Services and Applications", right click "WMI Control" click
    "Properties" and view the status of the WMI.
    """
    pass

class TurboFloatPermissionError(TurboFloatError):

    """
    Insufficient system permission. Either start your process as an
    admin / elevated user or call the function again with the
    TF_USER flag instead of the TF_SYSTEM flag.
    """
    pass

class TurboFloatDatFileError(TurboFloatError):

    """The product details file "TurboActivate.dat" failed to load."""
    pass

class TurboFloatFlagsError(TurboFloatError):

    """
    The flags you passed to is_date_valid(...) or save_server were invalid (or missing).
    """
    pass

class TurboFloatInvalidHandleError(TurboFloatError):
    """
    The handle is not valid. To get a handle use TF_GetHandle().
    """
    pass

class TurboFloatNoLeaseError(TurboFloatError):

    """
    There's no lease. Your must first have a lease before you can
    drop it or get information on it.
    """
    pass

class TurboFloatWrongServerProductError(TurboFloatError):

    """
    The TurboFloat Server you're trying to contact can't give license
    leases for this product version.
    """
    pass

class TurboFloatUpgradeLibraryError(TurboFloatError):

    """
    The TurboFloat Library you're currently using cannot be used
    to communicate with the TurboFloat Server instance. Release a new
    version of your app with the latest version of the TurboFloat Library.

    Get it here: https://wyday.com/limelm/api/#turbofloat
    """
    pass

class TurboFloatUsernameNotAllowedError(TurboFloatError):

    """
    The current user cannot request a license lease from the server because
    their username has not been added to the whitelist of approved usernames.

    More information about per-seat licensing: https://wyday.com/limelm/help/licensing-types/#named-user
    """
    pass

class TurboFloatBadHostAddressError(TurboFloatError):

    """
    The host_address value you passed to SaveServer(...) was invalid.
    The value should not contain a leading protocol prefix (i.e., "http://")
    or a trailing port number (i.e., ":443").
    """
    pass

class TurboFloatClientIPCError(TurboFloatError):

    """
    An error occurred while the TurboFloat client library was trying
    use interprocess communication facilities. These are needed to
    coordinate between multiple client-program instances running in
    the same operating-system session.
    """
    pass

class TurboFloatServerUUIDMismatchError(TurboFloatError):

    """
    The host_address value passed to SaveServer(...) contained an invalid
    'server' parameter. (The 'server' parameter is used with the hosted
    version of the TurboFloatServer.)
    """
    pass

class TurboFloatEnableNetworkAdaptersError(TurboFloatError):
    """
    There are network adapters on the system that are disabled and
    TurboFloat couldn't read their hardware properties (even after trying
    and failing to enable the adapters automatically). Enable the network adapters,
    re-run the function, and TurboFloat will be able to "remember" the adapters
    even if the adapters are disabled in the future.

    Note:   The network adapters do not need an active Internet connections. They just
            need to not be disabled. Whether they are or are not connected to the
            internet/intranet is not important and does not affect this error code at all.


    On Linux you'll get this error if you don't have any real network adapters attached.
    For example if you have no "eth[x]", "wlan[x]", "en[x]", "wl[x]", "ww[x]", or "sl[x]"
    network interface devices.

    See: https://wyday.com/limelm/help/faq/#disabled-adapters
    """
    pass

class TurboFloatBrokenWMIError(TurboFloatError):
    """
    The WMI repository on the computer is broken. To fix the WMI repository
    see the instructions here:

    https://wyday.com/limelm/help/faq/#fix-broken-wmi
    """
    pass
