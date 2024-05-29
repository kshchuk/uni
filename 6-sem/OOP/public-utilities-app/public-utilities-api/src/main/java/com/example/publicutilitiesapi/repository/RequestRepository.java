package com.example.publicutilitiesapi.repository;

import com.example.publicutilitiesapi.entity.Request;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface RequestRepository extends JpaRepository<Request, UUID> {
    List<Request> findRequestsByTenantId(UUID tenantId);
    Long countRequestsByTenantId(UUID tenantId);
}