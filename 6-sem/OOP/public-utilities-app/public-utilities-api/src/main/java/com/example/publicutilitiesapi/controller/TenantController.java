package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.TenantDto;
import com.example.publicutilitiesapi.mapper.TenantMapper;
import com.example.publicutilitiesapi.repository.TenantRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/tenant/")
public class TenantController {

    private final TenantRepository tenantRepository;
    private final TenantMapper tenantMapper;

    public TenantController(TenantRepository tenantRepository,
                            TenantMapper tenantMapper) {
        this.tenantRepository = tenantRepository;
        this.tenantMapper = tenantMapper;
    }

    @GetMapping("/all")
    public List<TenantDto> getAllTenants() {
        return tenantRepository.findAll().stream().map(tenantMapper::toEntity).collect(Collectors.toList());
    }
}
