package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.SpecialistDto;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/specialist/")
public class SpecialistController {
    @GetMapping("/all")
    public List<SpecialistDto> getAllSpecialists() {
        /// TODO: Implement this method
        return null;
    }
}
