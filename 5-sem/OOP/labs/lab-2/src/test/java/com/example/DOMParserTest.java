package com.example;

import com.example.parser.DOMParser;
import lombok.SneakyThrows;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class DOMParserTest {

    @Test
    @SneakyThrows
    public void parseTest() {
        var devices = DOMParser.apply(Main.XMLPath);
        assertEquals(devices.size(), 3);
        assertEquals(devices.get(0), MockData.device);
    }
}
