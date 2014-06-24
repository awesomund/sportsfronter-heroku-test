Readme Android app
==================

Acronyms
 * GCM - Google Cloud Messaging

This is a thin, Cordova-based wrapper around the html/js webapp.
Its main responsability is to handle push messages and to load the webapp as a native app.

The main classes are `com.iterate.sportsfronter` that is a Cordova app that essentially only
loads the webapp (from Internet) and `com.iterate.GCMIntentService` that reacts to
push message related events - namely registration (happens always upon start) and
pushed messages - and handles them.

We use a Cordova GCM plugin (the non-iterate packages) for most of the GCM stuff.

Set up Android application
----------------------------

The description assumes usage of the IntelliJ-based Android Studio. Latest version can be downloaded from http://developer.android.com/sdk/installing/studio.html#download

We use Gradle as a build tool, and this is integrated well with Android Studio. So you should be able to import the project as a Gradle project and just build it for your device.

The project may be built, deployed, and debugged as a standard Android project, even though it uses Cordova.



Handling of push notifications
-------------------------
The process of push notification can be explained as:
1. When the app loads the frontpage (index_cordova.html), we call the native code from the JS to get the device ID.
2. DeviceId is stored in the localStorage and saved in the database on login.
3. Whenever we create event, or edit event and send out notification we send a push notification to the devices related to the users who have logged in.

### Registration

Whenever the app starts, it registers itself with GCM - this happens via the native code here
and `init_gcm.js` and related code, which is included in the `index_cordova.html` page.

### Messages

Push messages are sent by the backend using Google GCM service.

When a push message is received, we do two things:

1. Create an Android notification to show up in the Android's status bar / notification place (whatever you call it).
   It contains basic info about the event and, when clicked, launches our app.
2. If Sportsfronter is currently running, we send it javascript with the message so that it can show the new event - see `GCMIntentService`.



Realeasing to Google Play Store
-------------------------------

Prerequesites: Access to google play developer account and certificates and password for signing apk.
First you need access to the account, https://play.google.com/.
Access can be given by ops@iterate.no, as well as getting the correct certificates.

Then you will need to package and sign the apk and upload it.
The certificate to be used for signing.

You will need to:

Create a sportsfronter.properties file at ~/.signing with such contents:
keystore=[path to]\[keystore.jks]
keystore.password=*********
keyAlias=***********
keyPassword=********

Create a sportsfronter.properties in the root folder and add a line pointing to the sportsfronter.properties.


To create the signed APK, the easiest way is to use Android Studio -> Build -> Create Signed APK and then fill out needed information. (Keystore, keypass, use existing alias named "sportsfronter").

This can then be uploaded and released either as a beta release or regular production release.

