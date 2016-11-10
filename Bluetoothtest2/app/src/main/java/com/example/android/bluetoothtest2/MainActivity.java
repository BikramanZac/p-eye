package com.example.android.bluetoothtest2;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Set;
import java.util.UUID;

import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import com.google.gson.Gson;


public class MainActivity extends Activity {

    private final byte delimiter = 33;
    private BluetoothSocket mmSocket;
    private BluetoothDevice mmDevice = null;
    private int readBufferPosition = 0;
    private final int REQUEST_ENABLE_BT = 1;
    private BluetoothAdapter mBluetoothAdapter;
    private static final String TAG = MainActivity.class.getSimpleName();
    private TextView myLabel;

    int count = 0;
    String sendingString = "";

    public void sendBtMsg(String msg2send) {
        UUID uuid = UUID.fromString("94f39d29-7d6d-437d-973b-fba39e49d4ee"); //Standard SerialPortService ID

        try {
            //Create an RFCOMM BluetoothSocket ready to start
            //a secure outgoing connection to this remote device using SDP lookup of uuid.
            mmSocket = mmDevice.createRfcommSocketToServiceRecord(uuid);
            if (!mmSocket.isConnected()) {
                mmSocket.connect();
            }
            String msg = msg2send;
            //msg += "\n";
            OutputStream mmOutputStream = mmSocket.getOutputStream();
            mmOutputStream.write(msg.getBytes());

        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();

            /*  read failed, socket might closed or timeout, read ret: -1
            *   http://stackoverflow.com/questions/18657427/ioexception-read-failed-socket-might-closed-bluetooth-on-android-4-3
            *   NOW you don't have to worry about turning off and on but still don't push it to fast :)
            */
            try {
                Log.e("","trying fallback...");

                mmSocket =(BluetoothSocket) mmDevice.getClass().getMethod("createRfcommSocket",
                        new Class[] {int.class}).invoke(mmDevice,1);
                mmSocket.connect();

                Log.e("","Connected");
            }
            catch (Exception e2) {
                Log.e("", "Couldn't establish Bluetooth connection!");
            }

        }

    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        final Handler handler = new Handler();
        myLabel = (TextView) findViewById(R.id.btResult);
        //Button tempButton = (Button) findViewById(R.id.tempButton);
        final Button lightOnButton = (Button) findViewById(R.id.lightOn);
        final Button lightOffButton = (Button) findViewById(R.id.lightOff);



        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        final class workerThread implements Runnable {

            private String btMsg;

            public workerThread(String msg) {
                btMsg = msg;
            }

            public void run() {
                sendBtMsg(btMsg);
                while (!Thread.currentThread().isInterrupted()) {
                    int bytesAvailable;
                    boolean workDone = false;

                    try {

                        final InputStream mmInputStream;
                        mmInputStream = mmSocket.getInputStream();
                        bytesAvailable = mmInputStream.available();

                        if (bytesAvailable > 0) {

                            count++;
                            byte[] packetBytes = new byte[bytesAvailable];
                            Log.e("Hello P-eye!", "bytes available it has called " +count+ " times");
                            byte[] readBuffer = new byte[bytesAvailable*20];
                            mmInputStream.read(packetBytes);

                            /*
                             * turned out mmInputStream.read() can only parse 990 characters once at a time
                             * when the number of characters we are trying to read from Pi is greater than 990,
                             * it loops until it finds "!"(because I set it). so I had to have a global string that keep adding up these 990 characters of string
                             * so that it can keep track of all the strings that I have received
                             * and then send this whole string to AWS server!
                             */
                            sendingString = sendingString + new String(packetBytes, "US-ASCII");

                            for (int i = 0; i < bytesAvailable; i++) {
                                byte b = packetBytes[i];
                                // when the letter is "!" ( which means the string that I receive always have to end with "!")
                                if (b == delimiter) {

                                    callAWSVision(sendingString);

                                    workDone = true;
                                    break;


                                } else {
                                    readBuffer[readBufferPosition++] = b;
                                }
                            }

                            if (workDone == true) {
                                mmSocket.close();
                                readBufferPosition = 0;
                                count = 0;
                                break;
                            }

                        }
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }

                }
            }
        }
        ;

        if (!mBluetoothAdapter.isEnabled()) {
            Intent enableBluetooth = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBluetooth, REQUEST_ENABLE_BT);
        }

        Set<BluetoothDevice> pairedDevices = mBluetoothAdapter.getBondedDevices();
        if (pairedDevices.size() > 0) {
            for (BluetoothDevice device : pairedDevices) {
                System.out.println(device.getName() + " is available");
                if (device.getName().equals("raspberrypi")) //Note, you will need to change this to match the name of your device
                {
                    Log.e("Hello P-eye", device.getName());
                    mmDevice = device;
                    break;
                }

            }
        }

        /*
        // start temp button handler

        tempButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                // Perform action on temp button click

                (new Thread(new workerThread("temp"))).start();

            }
        });
        */

        //end temp button handler

        //start light on button handler
        lightOnButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                // Perform action on temp button click
                (new Thread(new workerThread("takePicture"))).start();
            }
        });
        //end light on button handler

        //start light off button handler

        lightOffButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                // Perform action on temp button click
                (new Thread(new workerThread("volumeUp"))).start();
            }
        });

        // end light off button handler

    }// end of onCreate()


    // prevents the device from crushing after turning bluetooth on
    // if you don't write onActivityResult(), the mmDevice will get a null object resulting in fetal exception
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        // Check which request we're responding to
        if (requestCode == REQUEST_ENABLE_BT && resultCode == RESULT_OK) {
            // Make sure the request was successful
            Set<BluetoothDevice> pairedDevices = mBluetoothAdapter.getBondedDevices();
            if (pairedDevices.size() > 0) {
                for (BluetoothDevice device : pairedDevices) {
                    System.out.println(device.getName() + " is available");
                    if (device.getName().equals("raspberrypi")) //Note, you will need to change this to match the name of your device
                    {
                        Log.e("Hello P-eye", device.getName());
                        mmDevice = device;
                        break;
                    }

                }
            }
        }
    } // onActivityResult


    private void callAWSVision(final String encoded) {

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
                    URL url = new URL("http://ec2-52-88-62-32.us-west-2.compute.amazonaws.com/todo/api/v1.0/images");

                    HttpURLConnection con = (HttpURLConnection) url.openConnection();

                    //add reuqest header
                    con.setRequestMethod("POST");
                    con.setRequestProperty( "Content-Type", "application/json");

                    // json constructor the type of the parameter should be json format
                    Gson gson = new Gson();
                    String json = gson.toJson(new Foo(encode));
                    String urlParameters = json;
                    //String urlParameters = "encode="+ encode;

                    // Send post request
                    con.setDoOutput(true);
                    DataOutputStream wr = new DataOutputStream(con.getOutputStream());
                    wr.writeBytes(urlParameters);
                    wr.flush();
                    wr.close();

                    int responseCode = con.getResponseCode();
                    System.out.println("\nSending 'POST' request to URL : " + url);
                    System.out.println("Post parameters : " + urlParameters);
                    System.out.println("Response Code : " + responseCode);

                    BufferedReader in = new BufferedReader(
                            new InputStreamReader(con.getInputStream()));
                    String inputLine;
                    StringBuffer response = new StringBuffer();

                    while ((inputLine = in.readLine()) != null) {
                        response.append(inputLine);
                    }
                    in.close();

                    //print result
                    System.out.println(response.toString());
                    return response.toString();


                } catch (IOException e) {
                    Log.d(TAG, "failed to make API request because of other IOException " +
                            e.getMessage());
                }

                return "something went wrong!!!! DAMN";
            }
            protected void onPostExecute(String result){
                myLabel.setText(result);
            }

        }.execute();
    }

}