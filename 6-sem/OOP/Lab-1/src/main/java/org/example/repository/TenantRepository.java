package org.example.repository;

import org.example.entity.Tenant;

import java.util.UUID;

public interface TenantRepository extends CrudRepository<Tenant, UUID> {
    Tenant readWithRequests(Tenant tenant);
}
