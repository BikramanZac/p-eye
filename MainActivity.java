package com.example.android.p_eye;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Build;
import android.speech.tts.TextToSpeech;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.google.gson.Gson;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {

    private final byte delimiter = 33;
    private BluetoothSocket mmSocket;
    private BluetoothDevice mmDevice = null;
    private int readBufferPosition = 0;
    private final int REQUEST_ENABLE_BT = 1;
    private BluetoothAdapter mBluetoothAdapter;
    private static final String TAG = MainActivity.class.getSimpleName();
    private TextView myLabel;
    private TextToSpeech tts;
    private Button imageRecognition;
    private Button textRecogntion;
    private Button faceRecogntion;
    private Button volumeUp;
    private int count = 0;
    private String sendingString = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        myLabel = (TextView) findViewById(R.id.btResult);
        imageRecognition = (Button) findViewById(R.id.imageRecognition);
        textRecogntion = (Button) findViewById(R.id.textRecogntion);
        faceRecogntion = (Button) findViewById(R.id.faceRecogntion);

        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        tts=new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                if(status != TextToSpeech.ERROR) {
                    tts.setLanguage(Locale.UK);
                }
            }
        });


        if (!mBluetoothAdapter.isEnabled()) {
            Intent enableBluetooth = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBluetooth, REQUEST_ENABLE_BT);
        }

        Set<BluetoothDevice> pairedDevices = mBluetoothAdapter.getBondedDevices();
        if (pairedDevices.size() > 0) {
            for (BluetoothDevice device : pairedDevices) {
                //System.out.println(device.getName() + " is available from onCreate");
                if (device.getName().equals("raspberrypi") || device.getName().equals("p-eye")) //Note, you will need to change this to match the name of your device
                {
                    Log.e("Hello P-eye from onCre", device.getName());
                    mmDevice = device;
                    //break;
                }

            }
        }

        // 0 : object  1 : text  2 : facial expression
        imageRecognition.setOnClickListener(new View.OnClickListener() {

            public void onClick(View v) {
                String toSpeak = "Image recognition";
                tts.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, null, new String(this.hashCode() + ""));

                (new Thread(new workerThread("imageRecognition", 0))).start();
            }
        });

        textRecogntion.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                String toSpeak = "Text recognition";
                tts.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, null, new String(this.hashCode() + ""));

                (new Thread(new workerThread("textRecognition", 1))).start();
            }
        });

        faceRecogntion.setOnClickListener(new View.OnClickListener() {

            public void onClick(View v) {
                String toSpeak = "Facial expression recognition";
                tts.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, null, new String(this.hashCode() + ""));

                (new Thread(new workerThread("faceRecognition", 2))).start();
            }
        });

    } // end of onCreate()

    @Override
    public void onStop() {
        if (tts != null) {
            tts.stop();
        }
        super.onStop();
    }

    @Override
    public void onDestroy() {
        if (tts != null) {
            tts.shutdown();
        }
        super.onDestroy();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        // Check which request we're responding to and Make sure the request was successful
        if (requestCode == REQUEST_ENABLE_BT && resultCode == RESULT_OK) {
            Set<BluetoothDevice> pairedDevices = mBluetoothAdapter.getBondedDevices();
            if (pairedDevices.size() > 0) {
                for (BluetoothDevice device : pairedDevices) {
                    //System.out.println(device.getName() + " is available from onActivityResult");
                    if (device.getName().equals("raspberrypi") || device.getName().equals("p-eye")) //Note, you will need to change this to match the name of your device
                    {
                        Log.e("Hello P-eye from AcRes", device.getName());
                        mmDevice = device;
                        //break;
                    }

                }
            }
        }
    } // end of onActivityResult()

    final class workerThread implements Runnable {

        private String btMsg;
        private int recognitionDecider;

        public workerThread(String msg, int type) {
            btMsg = msg;
            recognitionDecider = type;
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
                        //System.out.println(bytesAvailable);
                        count++;
                        byte[] packetBytes = new byte[bytesAvailable];
                        //Log.e("Hello P-eye!", "bytes available it has called " + count + " times");
                        byte[] readBuffer = new byte[bytesAvailable];
                        mmInputStream.read(packetBytes);

                        /*
                         * turned out mmInputStream.read() can only receive 990 characters at a time
                         * when the number of characters we are trying to read from Pi is greater than 990,
                         * it iterates until it receives the whole string. so I had to have a global string that keep adding up these 990 characters of string
                         * so that it can keep track of all the strings that I have received
                         * and then send this whole string to AWS server!
                         */
                        sendingString = sendingString + new String(packetBytes, "US-ASCII");
                        // when it reaches the last chuck of the string the length of the string should be less then 990 
                        if(bytesAvailable < 990) {
                            for (int i = 0; i < bytesAvailable; i++) {
                                byte b = packetBytes[i];
                                // when the letter is "!" ( which means the string that it receives always have to end with "!")
                                if (b == delimiter) {
                                    System.out.println(sendingString.length());
                                    callAWSVision(sendingString, recognitionDecider);

                                    workDone = true;
                                    break;

                                } else {
                                    readBuffer[readBufferPosition++] = b;
                                }
                            }
                        }
                        if (workDone == true) {
                            mmSocket.close();
                            // reset global variables for next calls
                            readBufferPosition = 0;                            
                            count = 0;
                            sendingString = "";
                            break;
                        }
                    }

                } catch (IOException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }

            }
        }
    } // end of workerThread class

    private void callAWSVision(final String encoded, final int decider) {

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
                    // 0 : object  1 : text  2 : facial expression
                    if (decider == 0) urlString = urlString + "/label";
                    else if(decider == 1) urlString = urlString + "/text";
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
                        // Since it's JSON, adding a newline isn't necessary (it won't affect parsing)
                        // But it does make debugging a *lot* easier if you print out the completed
                        // buffer for debugging.
                        //buffer.append(line +"\n");
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
                    tts.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, null, new String(this.hashCode() + ""));

                    return toSpeak;


                } catch (IOException e) {
                    Log.d(TAG, "failed to make API request because of other IOException " +
                            e.getMessage());
                }

                return "something went wrong!!!! from android";
            }
            protected void onPostExecute(String result){
                myLabel.setText(result);
            }

        }.execute();
    } // end of callAWSVIsion()

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

    } // end of sendBtMsg()

}


