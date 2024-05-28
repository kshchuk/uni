package com.example.publicutilitiesapi.service;

import com.example.publicutilitiesapi.entity.Tenant;
import com.example.publicutilitiesapi.repository.TenantRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class TenantService extends CrudService<Tenant, UUID> {

    private final TenantRepository tenantRepository;

    @Autowired
    public TenantService(TenantRepository tenantRepository) {
        this.tenantRepository = tenantRepository;
    }

    @Override
    protected JpaRepository<Tenant, UUID> getRepository() {
        return tenantRepository;
    }
}
