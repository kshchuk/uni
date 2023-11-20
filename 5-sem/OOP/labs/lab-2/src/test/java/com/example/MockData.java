package com.example;

import com.example.model.Type;
import com.example.model.Device;

public class MockData {
    static Device device = new Device(
    0, "Device 1", "USA", 1000, new Type(true, 500, true, "io_devices", "USB"), false
    );
}
