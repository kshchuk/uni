package org.example.service;

import org.example.entity.Request;
import org.example.entity.Tenant;

import java.util.List;
import java.util.UUID;

public interface TenantService extends Service<Tenant, UUID> {
    List<Request> getTenantRequests(UUID tenantId);
    void createRequest(UUID tenantId, Request request);
    void removeRequest(UUID tenantId, UUID requestId);
    void updateRequest(UUID tenantId, Request request);
}
