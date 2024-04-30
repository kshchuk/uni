package org.example.service;

import org.example.entity.Request;
import org.example.entity.Tenant;
import org.example.repository.TenantRepository;

import java.util.List;
import java.util.UUID;

public class TenantServiceImpl implements TenantService {
    private final TenantRepository tenantRepository;

    public TenantServiceImpl(TenantRepository tenantRepository) {
        this.tenantRepository = tenantRepository;
    }

    @Override
    public List<Request> getTenantRequests(UUID tenantId) {
        var tenant = tenantRepository.read(tenantId);
        tenantRepository.readWithRequests(tenant);
        return tenant.getRequests();
    }

    @Override
    public void createRequest(UUID tenantId, Request request) {
        var tenant = tenantRepository.read(tenantId);
        tenantRepository.readWithRequests(tenant);
        request.setTenant(tenant);
        tenant.getRequests().add(request);
        tenantRepository.update(tenant);
    }

    @Override
    public void removeRequest(UUID tenantId, UUID requestId) {
        var tenant = tenantRepository.read(tenantId);
        tenantRepository.readWithRequests(tenant);
        tenant.getRequests().removeIf(request -> request.getRequestId().equals(requestId));
        tenantRepository.update(tenant);
    }

    @Override
    public void updateRequest(UUID tenantId, Request request) {
        var tenant = tenantRepository.read(tenantId);
        request.setTenant(tenant);
        tenantRepository.readWithRequests(tenant);
        var requests = tenant.getRequests();
        for (int i = 0; i < requests.size(); i++) {
            if (requests.get(i).getRequestId().equals(request.getRequestId())) {
                requests.set(i, request);
                break;
            }
        }
        tenantRepository.update(tenant);
    }

    @Override
    public void create(Tenant tenant) {
        tenantRepository.create(tenant);
    }

    @Override
    public Tenant get(UUID uuid) {
        return tenantRepository.read(uuid);
    }

    @Override
    public void update(Tenant tenant) {
        tenantRepository.update(tenant);
    }

    @Override
    public boolean delete(UUID uuid) {
        // TODO: add boolean return value
        tenantRepository.delete(uuid);
        return true;
    }

    @Override
    public List<Tenant> getAll() {
        return tenantRepository.findAll();
    }
}
