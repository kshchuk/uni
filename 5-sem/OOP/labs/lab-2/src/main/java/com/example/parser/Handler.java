package com.example.parser;

import com.example.Strings;
import com.example.model.Device;
import com.example.model.Type;

import org.jetbrains.annotations.NotNull;
import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Handler extends DefaultHandler {
    private String value;
    private List<Device> devices = new ArrayList<>();

    @Override
    public void startElement(String url, String name, @NotNull String attributeName, Attributes attributes) {
        switch (attributeName) {
            case Strings.DEVICE -> {
                Device device = new Device();
                devices.add(device);
            }
            case Strings.TYPE -> {
                Type type = new Type();
                getLastDevice().setType(type);
            }
        }
    }

    @Override
    public void endElement(String uri, String name, @NotNull String attributeName) {
        switch (attributeName) {
            case Strings.ID -> getLastDevice().setId(Integer.parseInt(value));
            case Strings.NAME -> getLastDevice().setName(value);
            case Strings.ORIGIN -> getLastDevice().setOrigin(value);
            case Strings.PRICE -> getLastDevice().setPrice(Integer.parseInt(value));
            case Strings.CRITICAL -> getLastDevice().setCritical(Boolean.parseBoolean(value));
            case Strings.PERIPHERAL -> getLastDevice().getType().setPeripheral(Boolean.parseBoolean(value));
            case Strings.ENERGY_CONSUMPTION -> getLastDevice().getType().setEnergyConsumption(Integer.parseInt(value));
            case Strings.COOLER -> getLastDevice().getType().setCooler(Boolean.parseBoolean(value));
            case Strings.COMPONENT_GROUP -> getLastDevice().getType().setComponentGroup(value);
            case Strings.PORT -> getLastDevice().getType().setPort(value);    
        }
    }

    public void setField(@NotNull String attributeName, String value, Map<String, String> attributes) {
        this.value = value;
        switch (attributeName) {
            case Strings.DEVICE -> {
                Device device = new Device();
                devices.add(device);
            }
            case Strings.ID -> getLastDevice().setId(Integer.parseInt(value));
            case Strings.NAME -> getLastDevice().setName(value);
            case Strings.ORIGIN -> getLastDevice().setOrigin(value);
            case Strings.PRICE -> getLastDevice().setPrice(Integer.parseInt(value));
            case Strings.CRITICAL -> getLastDevice().setCritical(Boolean.parseBoolean(value));
            case Strings.TYPE -> {
                Type type = new Type();
                getLastDevice().setType(type);
            }
            case Strings.PERIPHERAL -> getLastDevice().getType().setPeripheral(Boolean.parseBoolean(value));
            case Strings.ENERGY_CONSUMPTION -> getLastDevice().getType().setEnergyConsumption(Integer.parseInt(value));
            case Strings.COOLER -> getLastDevice().getType().setCooler(Boolean.parseBoolean(value));
            case Strings.COMPONENT_GROUP -> getLastDevice().getType().setComponentGroup(value);
            case Strings.PORT -> getLastDevice().getType().setPort(value);
        }
    }

    public List<Device> getDevicesList() {
        return devices;
    }

    @Override
    public void startDocument() throws SAXException {
        devices = new ArrayList<>();
    }

    @Override
    public void characters(char[] ch, int start, int length) {
        value = new String(ch, start, length);
    }

    private Device getLastDevice() {
        return devices.get(devices.size() - 1);
    }

    public String getName() {
        return Strings.DEVICE;
    }
}