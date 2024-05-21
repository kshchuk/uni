package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.TenantDto;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/tenant/")
public class TenantController {
    @GetMapping("/all")
    public List<TenantDto> getAllTenants() {
        /// TODO: Implement this method
        return null;
    }
}
