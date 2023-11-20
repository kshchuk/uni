package com.example.parser;

import com.example.model.Devices;
import org.w3c.dom.Element;
import org.w3c.dom.Node;

import javax.xml.parsers.DocumentBuilderFactory;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

public class DOMParser {
    public static Devices apply(String xmlPath) {
        var xml = new File(xmlPath);
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        try {
            var documentBuilder = factory.newDocumentBuilder();
            var document = documentBuilder.parse(xml);
            document.getDocumentElement().normalize();
            var rootNode = document.getDocumentElement();
            var deviceHandler = new Handler();
            var devicesNodesList = rootNode.getElementsByTagName(deviceHandler.getName());
            for (int deviceNode = 0; deviceNode < devicesNodesList.getLength(); deviceNode++) {
                Element tariffElement = (Element) devicesNodesList.item(deviceNode);
                traverseNodes(tariffElement, deviceHandler);
            }
            return new Devices(deviceHandler.getDevicesList());
        } catch (Exception e) {
            e.getStackTrace();
        }
        return null;
    }
    private static void traverseNodes(Node node, Handler deviceHandler) {
        if(node.getNodeType() == Node.ELEMENT_NODE) {
            Map<String, String> attributes = new HashMap<>();
            if(node.getAttributes() != null) {
                for (int i = 0; i < node.getAttributes().getLength(); i++) {
                    attributes.put(node.getAttributes().item(i).getNodeName(),
                        node.getAttributes().item(i).getTextContent());
                }
            }
            deviceHandler.setField(node.getNodeName(), node.getTextContent(), attributes);
            for (int i = 0; i < node.getChildNodes().getLength(); i++) {
                traverseNodes(node.getChildNodes().item(i), deviceHandler);
            }
        }
    }
}
