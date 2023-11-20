package com.example.parser;

import org.xml.sax.SAXException;

import javax.xml.XMLConstants;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;
import java.io.File;
import java.io.IOException;

public class XSDChecker {
    public static boolean apply(String xmlPath, String xsdPath) {
        try {
            validateThrows(xsdPath, xmlPath);
        } catch (IOException | SAXException e) {
            throw new IllegalStateException("Unvalid XML", e);
        }
        return true;
    }

    private static void validateThrows(String xsdPath, String xmlPath) throws SAXException, IOException {
        var factory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
        var schema = factory.newSchema(new File(xsdPath));
        Validator validator = schema.newValidator();
        validator.validate(new StreamSource(new File(xmlPath)));
    }
}
