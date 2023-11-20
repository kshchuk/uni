package com.example;

import com.example.parser.StAXParser;
import lombok.SneakyThrows;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class StAXParserTest {
    @Test
    @SneakyThrows
    public void parseTest() {
        var papers = StAXParser.apply(Strings.DEVICES_PATH).getDevices();
        assertEquals(papers.size(), 3);
        assertEquals(papers.get(0), MockData.device);
    }
}
