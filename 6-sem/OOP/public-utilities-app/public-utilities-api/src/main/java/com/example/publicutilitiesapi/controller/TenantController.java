package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.TenantDto;
import com.example.publicutilitiesapi.entity.Tenant;
import com.example.publicutilitiesapi.mapper.TenantMapper;
import com.example.publicutilitiesapi.service.TenantService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("api/tenant/")
public class TenantController {

    private final TenantService tenantService;
    private final TenantMapper tenantMapper;

    @Autowired
    public TenantController(TenantService tenantService, TenantMapper tenantMapper) {
        this.tenantService = tenantService;
        this.tenantMapper = tenantMapper;
    }

    @GetMapping("/{id}")
    public TenantDto getTenantById(@PathVariable UUID id) {
        return tenantMapper.toDto(tenantService.findById(id).orElseThrow());
    }

    @PostMapping("/create")
    public TenantDto createTenant(@RequestBody TenantDto tenantDto) {
        Tenant tenant = tenantMapper.toEntity(tenantDto);
        return tenantMapper.toDto(tenantService.save(tenant));
    }

    @PutMapping("/update")
    public TenantDto updateTenant(@RequestBody TenantDto tenantDto) {
        Tenant tenant = tenantMapper.toEntity(tenantDto);
        return tenantMapper.toDto(tenantService.save(tenant));
    }

    @DeleteMapping("/{id}")
    public void deleteTenant(@PathVariable UUID id) {
        tenantService.deleteById(id);
    }

    @GetMapping("/all")
    public List<TenantDto> getAllTenants() {
        return tenantService.findAll().stream().map(tenantMapper::toDto).collect(Collectors.toList());
    }
}
// Path: public-utilities-api/src/main/java/com/example/publicutilitiesapi/controller/WorkPlanController.java