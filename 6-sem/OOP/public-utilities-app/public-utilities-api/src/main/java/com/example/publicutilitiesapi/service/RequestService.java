package com.example.publicutilitiesapi.service;

import com.example.publicutilitiesapi.entity.Request;
import com.example.publicutilitiesapi.repository.RequestRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
public class RequestService extends CrudService<Request, UUID> {

    private final RequestRepository requestRepository;

    @Autowired
    public RequestService(RequestRepository requestRepository) {
        this.requestRepository = requestRepository;
    }

    @Override
    protected JpaRepository<Request, UUID> getRepository() {
        return requestRepository;
    }

    public List<Request> findRequestsByTenantId(UUID tenantId) {
        return requestRepository.findRequestsByTenantId(tenantId);
    }

    public Long countRequestsByTenantId(UUID tenantId) {
        return requestRepository.countRequestsByTenantId(tenantId);
    }
}
