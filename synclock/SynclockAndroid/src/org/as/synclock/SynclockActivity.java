package org.as.synclock;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Set;

import android.app.Activity;
import android.app.DialogFragment;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.ToggleButton;

public class SynclockActivity extends Activity {
    /** Called when the activity is first created. */
    
    private BluetoothAdapter mBluetoothAdapter;
    private BluetoothSocket mmSocket = null ;
    private Handler initGraphic = new Handler();
    
    private ToggleButton toggleAlarm;
    private Button sendTime;
    
    private EditText hours;
    private EditText minutes;

    
    private int h, m, available;
    
    private void connectDevice(BluetoothDevice device) {
        mBluetoothAdapter.cancelDiscovery();
        (new ConnectThread(device)).start();
    }
    
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

         
    }
    
    public void onStart() {
        super.onStart();
        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (mBluetoothAdapter == null) {
            // Device does not support Bluetooth
        }
        
        if (!mBluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBtIntent, 1);
        }
        
        Set<BluetoothDevice> pairedDevices = mBluetoothAdapter.getBondedDevices();

        if (pairedDevices.size() > 0) {
            for (BluetoothDevice device : pairedDevices) {
                Log.i("DEVICE", "" + device.getName());
                if(device.getName().contains("raspberry"))
                    connectDevice(device);
            }
        }
    }
    
    public void onPause() {
        super.onPause();
        try {
            if(mmSocket != null)
                mmSocket.close();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }
    
    private void initGraphic() {
        
        toggleAlarm = (ToggleButton) findViewById(R.id.togglebutton);
        
        sendTime = (Button) findViewById(R.id.sendbutton);
        
        hours = (EditText)findViewById(R.id.hour);
        minutes = (EditText)findViewById(R.id.minutes);
        
        hours.setText("" + h);
        minutes.setText("" + m);
        
        
        if(available == 1)
            toggleAlarm.setChecked(true);
        else
            toggleAlarm.setChecked(false);
        
        sendTime.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v) {
                byte[] data = new byte[3];
                data[0] = Byte.parseByte(((EditText)findViewById(R.id.hour)).getText().toString());
                data[1] = Byte.parseByte(((EditText)findViewById(R.id.minutes)).getText().toString());
                
                if(toggleAlarm.isChecked())
                    data[2] = 1;
                else
                    data[2] = 0;
                try {
                    mmSocket.getOutputStream().write(data);
                } catch (IOException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }
            
        });

    }
    
    class ConnectThread extends Thread {
     
        public ConnectThread(BluetoothDevice device) {

            BluetoothSocket tmp = null;
     
            try {
                tmp = device.createRfcommSocketToServiceRecord(Constants.MY_UUID);
            } catch (IOException e) { 
                Log.e(Constants.TAG, "CONNERR: " + e.getMessage());
            }
            
            mmSocket = tmp;
            
        }
        
        public BluetoothSocket getSocket() {
            return mmSocket;
        }
     
        public void run() {
     
            try {
                mmSocket.connect();
            } catch (IOException connectException) {
                Log.e(Constants.TAG, "" + "CONNERR: " + connectException.getMessage());
                try {
                    mmSocket.close();
                } catch (IOException closeException) { }
                return;
            }
     
            OutputStream tmpOut = null;
            InputStream tmpIn = null;
            byte[] buffer = new byte[10];
            
            try {
                tmpIn = mmSocket.getInputStream();
                int br = tmpIn.read(buffer);
                String[] time = new String(new String(buffer).substring(0, br)).split(":");
                h = Integer.parseInt(time[0]);
                m = Integer.parseInt(time[1]);
                available = Integer.parseInt(time[2]);
                initGraphic.post(new Runnable()
                {

                    @Override
                    public void run() {
                        initGraphic();
                    }
                    
                });
            } catch (IOException e) { }
    
        }
     
        public void cancel() {
            try {
                mmSocket.close();
            } catch (IOException e) { }
        }
        
    }
}