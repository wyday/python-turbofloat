#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from turbofloat import (
    TurboFloat,
    TurboFloatError,
    TurboFloatServerError,
    TurboFloatInetError,
    TurboFloatWrongServerProductError,
    TurboFloatServerUUIDMismatchError,
    TurboFloatUsernameNotAllowedError,
    TF_USER,
    TF_SYSTEM,
    TF_REQUEST_OVER_HTTPS,
    TF_CB_FEATURES_CHANGED,
    TF_CB_LEASE_DROPPED_SLEEP,
    TF_CB_LEASE_REGAINED
)

import sys

def leasecallback(status):

    if status == TF_CB_FEATURES_CHANGED:
        print("TODO: reload any features using TF_GetFeatureValue()")

    elif status == TF_CB_LEASE_DROPPED_SLEEP:
        # TODO: prompt the user to re-connect -- hide this prompt upon receipt of TF_CB_LEASE_REGAINED
        print("The lease has been dropped due to computer sleeping.")
        
    elif status == TF_CB_LEASE_REGAINED:
        # TODO: hide a prompt to the user if shown during TF_CB_LEASE_DROPPED_SLEEP
        print("The lease has been successfully regained after a sleep.")
    else:
        # TODO: disable any features in your app.
        print("The lease expired or has been dropped: ", status)

        '''
        After disabling the user's access to your app, we recommend
        you do 3 things:

        1. Give the user the option to save their progress.

        2. Give the user the option to save their progress to a
           separate file (i.e. "Save as" in case the work they were
           doing was incomplete).

        3. Give the user the option to retry. For example a
           "Try again" button that calls TF_RequestLease(tfHandle).

        Don't just exit the app without warning or without giving the user ptions.
        For example, this behavior right here is a terrible example to be etting:
        '''
        sys.exit("The app is exiting. In your app you shouldn't just abruptly exit! That's bad. See the comments in the example app.")



if __name__ == "__main__":

    try:
        # TODO: go to the version page at LimeLM and
        # paste this GUID here
        tf = TurboFloat("18324776654b3946fc44a5f3.49025204", leasecallback)

        try:
            tf.request_lease()
        except TurboFloatServerError:
            '''
            We're just hardcoding the localhost for testing
            purposes in real life you'd want to let the user
            enter the host address / port you can either do
            this in your app, or in your installer.

            If your customer is using LicenseChest hosted TFS
            instances, you might want to make a simple prompt
            for the LicenseChest TFS UUID.

            More information: https://wyday.com/licensechest/help/create-tfs-instance/

            Then call tf.save_server(...) using
            "floating.wyday.com/?server=[UUID]" as the host address.

            For example:

            hr = tf.save_server("floating.wyday.com/?server=00000000-0000-0000-0000-000000000000", 443, TF_USER | TF_REQUEST_OVER_HTTPS);
            '''
            tf.save_server("127.0.0.1", 13, TF_USER)

            tf.request_lease()
        except (TurboFloatInetError, TurboFloatWrongServerProductError, TurboFloatServerUUIDMismatchError, TurboFloatUsernameNotAllowedError):
            sys.exit("TODO: Give user an option to try another server instead of just exiting here.")


    except TurboFloatError as e:
        sys.exit("Failed to get the floating license lease " + str(e))


    # The floating license lease requested successfully.
    # Here's where you let your user start using your app.

    # if this app is activated then you can get a feature value (completely optional)
    # See: https://wyday.com/limelm/help/license-features/
    #
    # feature_value = tf.get_feature_value("myFeature")
    # print("the value of myFeature is %s" % feature_value)

    print("Floating license lease was requested successfully.")
    
    
    print('You must reverify with the activation servers before you can use this app. ')
    print('Type R and then press enter to retry after you\'ve ensured that you\'re connected to the internet. ')
    print('Or to exit the app press X. ')

    while True:
        user_resp = sys.stdin.read(1)

        if user_resp == 'x' or user_resp == 'X':

            # Drop the floating license, wait for the response, then exit your app.
            if tf.has_lease():
                tf.drop_lease()

            sys.exit("Exiting now. Bye.")

        else:
            print('Invalid input. Press X to exit the app.')
