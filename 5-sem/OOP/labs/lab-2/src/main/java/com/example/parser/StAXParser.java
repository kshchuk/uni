package com.example.parser;

import com.example.model.Devices;

import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamException;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.HashMap;

public class StAXParser {
    public static Devices apply(String xmlPath) throws XMLStreamException, FileNotFoundException {
        var xml = new File(xmlPath);
        var xmlInputFactory = XMLInputFactory.newInstance();
        var handler = new Handler();
        var reader = xmlInputFactory.createXMLEventReader(new FileInputStream(xml));

        while (reader.hasNext()) {
            var nextXMLEvent = reader.nextEvent();
            if (nextXMLEvent.isStartElement()) {
                var startElement = nextXMLEvent.asStartElement();
                nextXMLEvent = reader.nextEvent();
                String name = startElement.getName().getLocalPart();
                if (nextXMLEvent.isCharacters()) {
                    var iter = startElement.getAttributes();
                    var attributeMap = new HashMap<String, String>();
                    while (iter.hasNext()) {
                        var attribute = iter.next();
                        attributeMap.put(attribute.getName().getLocalPart(), attribute.getValue());
                    }
                    handler.setField(name, nextXMLEvent.asCharacters().getData(), attributeMap);
                }
            }
        }
        return new Devices(handler.getDevicesList());
    }
}
