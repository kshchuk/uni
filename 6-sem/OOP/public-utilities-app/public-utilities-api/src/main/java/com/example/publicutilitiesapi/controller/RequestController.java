package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.RequestDto;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/request/")
public class RequestController {
    @GetMapping("/all")
    public List<RequestDto> getAllRequests() {
        /// TODO: Implement this method
        return null;
    }
}
