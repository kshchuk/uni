package com.example.parser;

import com.example.model.Devices;
import org.xml.sax.SAXException;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParserFactory;
import java.io.File;
import java.io.IOException;

public class SAXParser {

    public static Devices apply(String xmlPath) throws SAXException, IOException, ParserConfigurationException {
        var xml = new File(xmlPath);
        var saxParserFactory = SAXParserFactory.newInstance();
        var saxParser = saxParserFactory.newSAXParser();
        var handler = new Handler();
        saxParser.parse(xml, handler);
        return new Devices(handler.getDevicesList());
    }
}