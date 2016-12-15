/* 
    A MAIN ACTIVITY FOR OBJECT, TEXT, and FACIAL EXPRESSION RECOGNITIONS
*/

package com.example.android.bluep_eye;

import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Message;
import android.speech.tts.TextToSpeech;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import android.os.Handler;

import android.app.AlertDialog;

import java.util.Locale;

public class MainActivity extends AppCompatActivity {

    // Intent request codes
    private static final int REQUEST_CONNECT_DEVICE = 1;
    private static final int REQUEST_ENABLE_BT = 2;

    // Name of the connected device
    private String mConnectedDeviceName = null;

    /**
     * Set to true to add debugging code and logging.
     */
    public static final boolean DEBUG = true;

    /**
     * The tag we use when logging, so that our messages can be distinguished
     * from other messages in the log. Public because it's used by several
     * classes.
     */
    public static final String LOG_TAG = "P-eye";

    // Message types sent from the BluetoothReadService Handler
    public static final int MESSAGE_STATE_CHANGE = 1;
    public static final int MESSAGE_READ = 2;
    public static final int MESSAGE_WRITE = 3;
    public static final int MESSAGE_DEVICE_NAME = 4;
    public static final int MESSAGE_TOAST = 5;

    // Key names received from the BluetoothChatService Handler
    public static final String DEVICE_NAME = "device_name";
    public static final String TOAST = "toast";

    private BluetoothAdapter mBluetoothAdapter = null;
    private boolean mEnablingBT;
    /**
     * Our main view. Displays the emulated terminal screen.
     */
    private TextView mEmulatorView;

    private static BluetoothSerialService mSerialService = null;

    private TextView myLabel;
    private TextToSpeech tts;
    private Button imageRecognition;
    private Button textRecogntion;
    private Button faceRecogntion;
    private boolean isConnected = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // initialize a textview, buttons, text to speech, and bluetooth objects
        mEmulatorView = (TextView) findViewById(R.id.mEmulatorView);
        imageRecognition = (Button) findViewById(R.id.imageRecognition);
        textRecogntion = (Button) findViewById(R.id.textRecogntion);
        faceRecogntion = (Button) findViewById(R.id.faceRecogntion);
        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        tts=new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                if(status != TextToSpeech.ERROR) {
                    tts.setLanguage(Locale.UK);  // UK: English accent, US: American accent
                }
            }
        });

        // initialize a bluetooth object that takes care of all the bluetooth stuff
        mSerialService = new BluetoothSerialService(this, mEmulatorView, tts, mHandlerBT);

        // start an intent to pair bluetooth devices
        Intent serverIntent = new Intent(this, DeviceListActivity.class);
        startActivityForResult(serverIntent, REQUEST_CONNECT_DEVICE);

        // 0x69 : object  0x74 : text  0x66 : facial expression
        imageRecognition.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                if(isConnected == true) {
                    String toSpeak = "Image recognition";
                    tts.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, null, new String(this.hashCode() + ""));
                    byte[] buffer = new byte[1];
                    buffer[0] = 0x69; // ASKII code hex 'i'
                    mSerialService.write(buffer);
                }
                // if it hasn't been connected yet, keep starting the intent until it gets connected
                else{
                    Intent serverIntent = new Intent(MainActivity.this, DeviceListActivity.class);
                    startActivityForResult(serverIntent, REQUEST_CONNECT_DEVICE);
                }

            }
        });

        textRecogntion.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                if(isConnected == true) {
                    String toSpeak = "Text recognition";
                    tts.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, null, new String(this.hashCode() + ""));
                    byte[] buffer = new byte[1];
                    buffer[0] = 0x74; // ASKII code hex 't'
                    mSerialService.write(buffer);
                }
                // if it hasn't been connected yet, keep starting the intent until it gets connected
                else{
                    Intent serverIntent = new Intent(MainActivity.this, DeviceListActivity.class);
                    startActivityForResult(serverIntent, REQUEST_CONNECT_DEVICE);
                }
            }
        });

        faceRecogntion.setOnClickListener(new View.OnClickListener() {

            public void onClick(View v) {
                if(isConnected == true) {
                    String toSpeak = "Facial expression recognition";
                    tts.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, null, new String(this.hashCode() + ""));
                    byte[] buffer = new byte[1];
                    buffer[0] = 0x66;  //ASKII code hex 'f'
                    mSerialService.write(buffer);
                }
                // if it hasn't been connected yet, keep starting the intent until it gets connected
                else{
                    Intent serverIntent = new Intent(MainActivity.this, DeviceListActivity.class);
                    startActivityForResult(serverIntent, REQUEST_CONNECT_DEVICE);
                }
            }
        });

        if (DEBUG)
            Log.e(LOG_TAG, "+++ DONE IN ON CREATE +++");
    } // end of onCreate



    @Override
    public void onStart() {
        super.onStart();
        if (DEBUG)
            Log.e(LOG_TAG, "++ ON START ++");

        mEnablingBT = false;
    } // end of onStart

    @Override
    public synchronized void onResume() {
        super.onResume();

        if (DEBUG) {
            Log.e(LOG_TAG, "+ ON RESUME +");
        }

        if (!mEnablingBT) { // If we are turning on the BT we cannot check if it's enable
            if ( (mBluetoothAdapter != null)  && (!mBluetoothAdapter.isEnabled()) ) {

                AlertDialog.Builder builder = new AlertDialog.Builder(this);
                builder.setMessage(R.string.alert_dialog_turn_on_bt)
                        .setIcon(android.R.drawable.ic_dialog_alert)
                        .setTitle(R.string.alert_dialog_warning_title)
                        .setCancelable( false )
                        .setPositiveButton(R.string.alert_dialog_yes, new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int id) {
                                mEnablingBT = true;
                                Intent enableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
                                startActivityForResult(enableIntent, REQUEST_ENABLE_BT);
                            }
                        })
                        .setNegativeButton(R.string.alert_dialog_no, new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int id) {
                                finishDialogNoBluetooth();
                            }
                        });
                AlertDialog alert = builder.create();
                alert.show();
            }

            if (mSerialService != null) {
                // Only if the state is STATE_NONE, do we know that we haven't started already
                if (mSerialService.getState() == BluetoothSerialService.STATE_NONE) {
                    // Start the Bluetooth services
                    mSerialService.start();
                }
            }

            if (mBluetoothAdapter != null) {
                //readPrefs();
                //updatePrefs();
            }
        }
    } // end of onResume

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (DEBUG)
            Log.e(LOG_TAG, "--- ON DESTROY ---");

        if (mSerialService != null)
            mSerialService.stop();

    } // end of onDestroy

    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        if(DEBUG) Log.d(LOG_TAG, "onActivityResult " + resultCode);
        switch (requestCode) {
            // after DeviceListActivity intent called...
            case REQUEST_CONNECT_DEVICE:

                // When DeviceListActivity returns with a device to connect
                if (resultCode == Activity.RESULT_OK) {
                    // Get the device MAC address
                    String address = data.getExtras()
                            .getString(DeviceListActivity.EXTRA_DEVICE_ADDRESS);  // 00:15:83:D1:E6:76 is the external module
                    // Get the BLuetoothDevice object
                    BluetoothDevice device = mBluetoothAdapter.getRemoteDevice(address);
                    // Attempt to connect to the device
                    mSerialService.connect(device);
                }
                break;

            case REQUEST_ENABLE_BT:
                // When the request to enable Bluetooth returns
                if (resultCode != Activity.RESULT_OK) {
                    Log.d(LOG_TAG, "BT not enabled");
                    finishDialogNoBluetooth();
                }
        }
    } // end of onActivityResult()

    // The Handler that gets information back from the BluetoothService
    private final Handler mHandlerBT = new Handler() {

        @Override
        public void handleMessage(Message msg) {
            switch (msg.what) {
                // takes care of all kinds of toast notifications
                case MESSAGE_DEVICE_NAME:
                    // save the connected device's name
                    mConnectedDeviceName = msg.getData().getString(DEVICE_NAME);
                    Toast.makeText(getApplicationContext(), getString(R.string.toast_connected_to) + " "
                            + mConnectedDeviceName, Toast.LENGTH_SHORT).show();

                    // this is when you know it establishes the connection
                    if (mConnectedDeviceName.equals("raspberrypi")) {
                        isConnected = true;
                    }

                    break;
                case MESSAGE_TOAST:
                    Toast.makeText(getApplicationContext(), msg.getData().getString(TOAST), Toast.LENGTH_SHORT).show();
                    // this is when you know the connection is required
                    if (msg.getData().getString(TOAST).equals(R.string.toast_unable_to_connect)) {
                        isConnected = false;
                    }

                    break;
            }
        }
    };

    public void finishDialogNoBluetooth() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setMessage(R.string.alert_dialog_no_bt)
                .setIcon(android.R.drawable.ic_dialog_info)
                .setTitle(R.string.app_name)
                .setCancelable( false )
                .setPositiveButton(R.string.alert_dialog_ok, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                        finish();
                    }
                });
        AlertDialog alert = builder.create();
        alert.show();
    }
}
// please contact me if you would like to see the whole project 
// nackyu711@gmail.com
