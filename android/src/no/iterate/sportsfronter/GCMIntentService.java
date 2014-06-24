package no.iterate.sportsfronter;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.app.Notification;
import android.app.PendingIntent;
import android.app.NotificationManager;

import com.google.android.gcm.GCMBaseIntentService;
import no.plugin.GCM.GCMPlugin;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * Our code to handle push messages and registration with the GCM backend,
 * being invoked by the Cordova GCM plugin.
 */
public class GCMIntentService extends GCMBaseIntentService {

  public static final String ME="GCMReceiver";

  public GCMIntentService() {
    super("GCMIntentService");
  }
  private static final String TAG = "GCMIntentService";

  @Override
  public void onRegistered(Context context, String regId) {

    Log.v(ME + ":onRegistered", "Registration ID arrived!");
    Log.v(ME + ":onRegistered", regId);

    JSONObject json;

    try
    {
      json = new JSONObject().put("event", "registered");
      json.put("regid", regId);

      Log.v(ME + ":onRegisterd", json.toString());

      // Send this JSON data to the JavaScript application above EVENT should be set to the msg type
      // In this case this is the registration ID
      GCMPlugin.sendJavascript(json);

    }
    catch( JSONException e)
    {
      // No message to the user is sent, JSON failed
      Log.e(ME + ":onRegisterd", "JSON exception");
    }
  }

  @Override
  public void onUnregistered(Context context, String regId) {
    Log.d(TAG, "onUnregistered - regId: " + regId);
  }


  @Override
  protected void onMessage(Context context, Intent intent) {
    Log.d(TAG, "onMessage - context: " + context);

    // Extract the payload from the message
    Bundle extras = intent.getExtras();
    if (extras != null) {
      try
      {
        String message = extras.getString("message");
        String title = extras.getString("title");
        String event_id = extras.getString("event_id");
        Log.v(ME + ":onMessage extras ",message);

        displayAndroidNotification(context, title, message);
        sendEventToRunningApp(message, title, event_id);
      }
      catch( JSONException e)
      {
        Log.e(ME + ":onMessage", "JSON exception");
      }         
    }
  }

    /**
     * Display the native Android notification with a summary of the event.
     * When clicked, it will start the Sportsfronter app.
     */
    private void displayAndroidNotification(Context context, String title, String message) {
        Notification notif = new Notification(R.drawable.ic_launcher, message, System.currentTimeMillis() );

        notif.flags = Notification.FLAG_AUTO_CANCEL;
        notif.defaults |= Notification.DEFAULT_SOUND;
        notif.defaults |= Notification.DEFAULT_VIBRATE;

        Intent notificationIntent = new Intent(context, Sportsfronter.class);
        notificationIntent.putExtra("message", message);
        notificationIntent.putExtra("title", title);
        notificationIntent.addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent contentIntent = PendingIntent.getActivity(context, 0, notificationIntent, 0);

        notif.setLatestEventInfo(context, title, message, contentIntent);
        String ns = Context.NOTIFICATION_SERVICE;
        NotificationManager mNotificationManager = (NotificationManager) context.getSystemService(ns);
        mNotificationManager.notify(1, notif);
    }

    /**
     * Send the event to a running Sportsfronter app (if running at all) as a javascript so
     * that it can show it etc. Does nothing if the app is currently not running.
     */
    private void sendEventToRunningApp(String message, String title, String event_id) throws JSONException {
        final JSONObject json = new JSONObject().put("event", "message");
        json.put("title", title);
        json.put("message", message);
        json.put("event_id", event_id);
        GCMPlugin.sendJavascript(json);
    }

    @Override
  public void onError(Context context, String errorId) {
    Log.e(TAG, "onError - errorId: " + errorId);
  }
}
