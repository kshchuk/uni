package com.example;

import com.example.model.Type;
import com.example.model.Device;

public class MockData {
    static Device device = new Device(
    1, "Device", "Korea", 100, new Type(true, 200, false, "multimedia", "USB"), true
    );
}
