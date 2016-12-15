/**
 * This class does all the work for setting up and managing Bluetooth
 * connections with other devices. It has a thread that listens for
 * incoming connections, a thread for connecting with a device, and a
 * thread for performing data transmissions when connected.
 */

package com.example.android.bluep_eye;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.lang.reflect.Method;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Arrays;
import java.util.UUID;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.speech.tts.TextToSpeech;
import android.util.Log;
import android.widget.TextView;

import com.google.gson.Gson;


public class BluetoothSerialService {
    // Debugging
    private static final String TAG = "BluetoothReadService";
    private static final boolean D = true;


	private static final UUID SerialPortServiceClass_UUID = UUID.fromString("94f39d29-7d6d-437d-973b-fba39e49d4ee");

    // Member fields
    private final BluetoothAdapter mAdapter;
    private final Handler mHandler;
    private ConnectThread mConnectThread;
    private ConnectedThread mConnectedThread;
    private int mState;
    
    private boolean mAllowInsecureConnections;

    private TextToSpeech mtts;
    private TextView mEmulatorView;
    private Context mContext;

    private int count = 0;
    private int readBufferPosition = 0;
    private final byte delimiter = 33;

    // Constants that indicate the current connection state
    public static final int STATE_NONE = 0;       // we're doing nothing
    public static final int STATE_LISTEN = 1;     // now listening for incoming connections
    public static final int STATE_CONNECTING = 2; // now initiating an outgoing connection
    public static final int STATE_CONNECTED = 3;  // now connected to a remote device

    /**
     * Constructor. Prepares a new BluetoothChat session.
     * @param context  The UI Activity Context
     */

    public BluetoothSerialService(Context context, TextView emulatorView, TextToSpeech tts, Handler handler) {
        mAdapter = BluetoothAdapter.getDefaultAdapter();
        mState = STATE_NONE;
        mEmulatorView = emulatorView;
        mContext = context;
        mHandler = handler;
        mAllowInsecureConnections = true;
        mtts = tts;
    }

    /**
     * Set the current state of the chat connection
     * @param state  An integer defining the current connection state
     */
    private synchronized void setState(int state) {
        if (D) Log.d(TAG, "setState() " + mState + " -> " + state);
        mState = state;
    }

    /**
     * Return the current connection state. */
    public synchronized int getState() {
        return mState;
    }

    /**
     * Start the chat service. Specifically start AcceptThread to begin a
     * session in listening (server) mode. Called by the Activity onResume() */
    public synchronized void start() {
        if (D) Log.d(TAG, "start");

        // Cancel any thread attempting to make a connection
        if (mConnectThread != null) {
        	mConnectThread.cancel(); 
        	mConnectThread = null;
        }

        // Cancel any thread currently running a connection
        if (mConnectedThread != null) {
        	mConnectedThread.cancel(); 
        	mConnectedThread = null;
        }

        setState(STATE_NONE);
    }

    /**
     * Start the ConnectThread to initiate a connection to a remote device.
     * @param device  The BluetoothDevice to connect
     */
    public synchronized void connect(BluetoothDevice device) {
        if (D) Log.d(TAG, "connect to: " + device);

        // Cancel any thread attempting to make a connection
        if (mState == STATE_CONNECTING) {
            if (mConnectThread != null) {mConnectThread.cancel(); mConnectThread = null;}
        }

        // Cancel any thread currently running a connection
        if (mConnectedThread != null) {mConnectedThread.cancel(); mConnectedThread = null;}

        // Start the thread to connect with the given device
        mConnectThread = new ConnectThread(device);
        mConnectThread.start();
        setState(STATE_CONNECTING);
    }

    /**
     * Start the ConnectedThread to begin managing a Bluetooth connection
     * @param socket  The BluetoothSocket on which the connection was made
     * @param device  The BluetoothDevice that has been connected
     */
    public synchronized void connected(BluetoothSocket socket, BluetoothDevice device) {
        if (D) Log.d(TAG, "connected");

        // Cancel the thread that completed the connection
        if (mConnectThread != null) {
        	mConnectThread.cancel(); 
        	mConnectThread = null;
        }

        // Cancel any thread currently running a connection
        if (mConnectedThread != null) {
        	mConnectedThread.cancel(); 
        	mConnectedThread = null;
        }

        // Start the thread to manage the connection and perform transmissions
        mConnectedThread = new ConnectedThread(socket);
        mConnectedThread.start();

        // Send the name of the connected device back to the UI Activity
        Message msg = mHandler.obtainMessage(MainActivity.MESSAGE_DEVICE_NAME);
        Bundle bundle = new Bundle();
        bundle.putString(MainActivity.DEVICE_NAME, device.getName());
        msg.setData(bundle);
        mHandler.sendMessage(msg);

        setState(STATE_CONNECTED);
    }

    /**
     * Stop all threads
     */
    public synchronized void stop() {
        if (D) Log.d(TAG, "stop");


        if (mConnectThread != null) {
        	mConnectThread.cancel(); 
        	mConnectThread = null;
        }

        if (mConnectedThread != null) {
        	mConnectedThread.cancel(); 
        	mConnectedThread = null;
        }

        setState(STATE_NONE);
    }

    /**
     * Write to the ConnectedThread in an unsynchronized manner
     * @param out The bytes to write
     * @see ConnectedThread#write(byte[])
     */
    public void write(byte[] out) {
        // Create temporary object
        ConnectedThread r;
        // Synchronize a copy of the ConnectedThread
        synchronized (this) {
            if (mState != STATE_CONNECTED) return;
            r = mConnectedThread;
        }
        // Perform the write unsynchronized
        r.write(out);
    }
    
    /**
     * Indicate that the connection attempt failed and notify the UI Activity.
     */
    private void connectionFailed() {
        setState(STATE_NONE);
        // Send a failure message back to the Activity
        Message msg = mHandler.obtainMessage(MainActivity.MESSAGE_TOAST);
        Bundle bundle = new Bundle();
        bundle.putString(MainActivity.TOAST, mContext.getString(R.string.toast_unable_to_connect) );
        msg.setData(bundle);
        mHandler.sendMessage(msg);


    }

    /**
     * Indicate that the connection was lost and notify the UI Activity.
     */
    private void connectionLost() {
        setState(STATE_NONE);
        // Send a failure message back to the Activity
        Message msg = mHandler.obtainMessage(MainActivity.MESSAGE_TOAST);
        Bundle bundle = new Bundle();
        bundle.putString(MainActivity.TOAST, mContext.getString(R.string.toast_connection_lost) );
        msg.setData(bundle);
        mHandler.sendMessage(msg);

    }

    /**
     * This thread runs while attempting to make an outgoing connection
     * with a device. It runs straight through; the connection either
     * succeeds or fails.
     */
    private class ConnectThread extends Thread {
        private final BluetoothSocket mmSocket;
        private final BluetoothDevice mmDevice;

        public ConnectThread(BluetoothDevice device) {
            mmDevice = device;
            BluetoothSocket tmp = null;

            // Get a BluetoothSocket for a connection with the
            // given BluetoothDevice
            try {
            	if ( mAllowInsecureConnections ) {
            		Method method;
            		
            		method = device.getClass().getMethod("createRfcommSocket", new Class[] { int.class } );
                    tmp = (BluetoothSocket) method.invoke(device, 1);  
            	}
            	else {
            		tmp = device.createRfcommSocketToServiceRecord( SerialPortServiceClass_UUID );
            	}
            } catch (Exception e) {
                Log.e(TAG, "create() failed", e);
            }
            mmSocket = tmp;
        }

        public void run() {
            Log.i(TAG, "BEGIN mConnectThread");
            setName("ConnectThread");

            // Always cancel discovery because it will slow down a connection
            mAdapter.cancelDiscovery();

            // Make a connection to the BluetoothSocket
            try {
                // This is a blocking call and will only return on a
                // successful connection or an exception
                mmSocket.connect();
            } catch (IOException e) {
                connectionFailed();
                // Close the socket
                try {
                    mmSocket.close();
                } catch (IOException e2) {
                    Log.e(TAG, "unable to close() socket during connection failure", e2);
                }
                // Start the service over to restart listening mode
                //BluetoothSerialService.this.start();
                return;
            }

            // Reset the ConnectThread because we're done
            synchronized (BluetoothSerialService.this) {
                mConnectThread = null;
            }

            // Start the connected thread
            connected(mmSocket, mmDevice);
        }

        public void cancel() {
            try {
                mmSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "close() of connect socket failed", e);
            }
        }
    }

    /**
     * This thread runs during a connection with a remote device.
     * It handles all incoming and outgoing transmissions.
     */
    private class ConnectedThread extends Thread {
        private final BluetoothSocket mmSocket;
        private final InputStream mmInStream;
        private final OutputStream mmOutStream;
        String sendingString = "";
        int bytesAvailable;
        public ConnectedThread(BluetoothSocket socket) {
            Log.d(TAG, "create ConnectedThread");
            mmSocket = socket;
            InputStream tmpIn = null;
            OutputStream tmpOut = null;

            // Get the BluetoothSocket input and output streams
            try {
                tmpIn = socket.getInputStream();
                tmpOut = socket.getOutputStream();
            } catch (IOException e) {
                Log.e(TAG, "temp sockets not created", e);
            }

            mmInStream = tmpIn;
            mmOutStream = tmpOut;
        }

        public void run() {
            Log.i(TAG, "BEGIN mConnectedThread");
            byte[] buffer = new byte[990];
            int bytes;

            // Keep listening to the InputStream while connected
            while (true) {
                try {
                    // Read from the InputStream. bytes = the number of characters that it receives
                    bytes = mmInStream.read(buffer);

                    count ++; // needs to know how many iteration happens during one handshake

                    // builds the whole string that P-eye has sent
                    sendingString = sendingString + new String(buffer, "US-ASCII");

                    // when it reaches the last set of string (it should be less than 990 long)
                    if (bytes > 0 && bytes < 990) {
                        byte[] readBuffer = new byte[bytes];
                        // go over each characters to find '!'
                        for (int i = 0; i < bytes; i++) {
                            byte b = buffer[i];
                            // when the letter is "!" ( which means the string that it receives always have to end with "!")
                            if (b == delimiter) {
                                // remove the an extra 990 characters long string in the end of sendingString because it is redundant
                                sendingString = sendingString.substring(0, 990*(count-1));
                                /*
                                 the encoded string will end with i! or f! or t! which indicates the type of recognition
                                 i : object f : face t: text recognition and these are only for callAWSvision method
                                 so they have to be removed in sendingString
                                */
                                byte [] subReadBuffer = Arrays.copyOfRange(readBuffer, 0, bytes-2); // i! is sliced
                                sendingString = sendingString + new String(subReadBuffer, "US-ASCII");
                                Log.i(TAG, Integer.toString(count) + " times iteration "+
                                        Integer.toString(sendingString.length()) + " long string" );

                                // send sendingString to AWS server and aurally relay the response to users
                                callAWSVision(sendingString, readBuffer[bytes-2]);

                                // set variables to default for next calls
                                readBufferPosition = 0;
                                sendingString = "";
                                count = 0;
                            } else {
                                readBuffer[readBufferPosition++] = b;
                            }
                        }
                    }

                    // Send the obtained bytes to the UI Activity
                    //mHandler.obtainMessage(MainActivity.MESSAGE_READ, bytes, -1, buffer).sendToTarget();
                } catch (IOException e) {
                    Log.e(TAG, "disconnected", e);
                    connectionLost();
                    break;
                }
            }
        }

        /**
         * Write to the connected OutStream.
         * @param buffer  The bytes to write
         */
        public void write(byte[] buffer) {
            try {
                mmOutStream.write(buffer);


            } catch (IOException e) {
                Log.e(TAG, "Exception during write", e);
            }
        }

        public void cancel() {
            try {
                mmSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "close() of connect socket failed", e);
            }
        }
    }

    /*
     * takes care of HTTP POST protocol between the app and AWS server
     * it gets an encoded string of the image as a parameter and send this to the server.
     * once it gets the response back, it aurally relays to users using Text To Speech
     */

    private void callAWSVision(final String encoded, final byte decider) {

        // Do the real work in an async task, because we need to use the network anyway
        new AsyncTask<Object, Void, String>(){
            class Foo{
                private String encode = "";
                Foo(String encoded){
                    encode = encoded;
                }
            }
            @Override
            protected String doInBackground(Object... params){
                try{
                    final String encode = encoded;
                    String urlString = "http://ec2-52-88-62-32.us-west-2.compute.amazonaws.com/todo/api/v1.0/images";
                    // 0x69 : object  0x74 : text  0x66 : facial expression
                    if (decider == 0x69) urlString = urlString + "/label";
                    else if(decider == 0x74) urlString = urlString + "/text";
                    else urlString = urlString + "/face";

                    URL url = new URL(urlString);

                    // Create the request and open the connection
                    HttpURLConnection con = (HttpURLConnection) url.openConnection();

                    //add request header
                    con.setRequestMethod("POST");
                    con.setRequestProperty("Content-Type", "application/json");

                    // json constructor the type of the parameter should be json format
                    Gson gson = new Gson();
                    String json = gson.toJson(new Foo(encode));
                    String urlParameters = json;


                    // Send post request
                    con.setDoOutput(true);
                    DataOutputStream wr = new DataOutputStream(con.getOutputStream());
                    wr.writeBytes(urlParameters);
                    wr.flush();
                    wr.close();

                    int responseCode = con.getResponseCode();
                    System.out.println("\nSending 'POST' request to URL : " + url);
                    //System.out.println("Post parameters : " + urlParameters);
                    System.out.println("Response Code : " + responseCode);


                    // Read the input stream into a String
                    InputStream inputStream = con.getInputStream();
                    StringBuffer buffer = new StringBuffer();
                    if (inputStream == null) {
                        // nothing to do.
                        return null;
                    }
                    BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));

                    String line;
                    while((line = reader.readLine())!= null){
                        buffer.append(line);
                    }
                    reader.close();
                    if (buffer.length() == 0) {
                        // Stream was empty.  No point in parsing.
                        return null;
                    }

                    String toSpeak = buffer.toString();
                    toSpeak = toSpeak.replaceAll("\n", " ");
                    System.out.println(toSpeak);
                    mtts.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, null, new String(this.hashCode() + ""));

                    return toSpeak;


                } catch (IOException e) {
                    Log.d(TAG, "failed to make API request because of other IOException " +
                            e.getMessage());
                }

                return "something went wrong!!!! from android";
            }
            protected void onPostExecute(String result){
                //mEmulatorView.setText(result);
            }

        }.execute();
    } // end of callAWSVIsion()

    public void setAllowInsecureConnections( boolean allowInsecureConnections ) {
        mAllowInsecureConnections = allowInsecureConnections;
    }

    public boolean getAllowInsecureConnections() {
        return mAllowInsecureConnections;
    }
}
