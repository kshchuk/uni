package org.example.service.impl;

import org.example.entity.Request;
import org.example.repository.RequestRepository;
import org.example.service.RequestService;

import java.util.List;
import java.util.UUID;

public class RequestServiceImpl implements RequestService {
    private final RequestRepository requestRepository;

    public RequestServiceImpl(RequestRepository requestRepository) {
        this.requestRepository = requestRepository;
    }

    @Override
    public void create(Request request) {
        requestRepository.create(request);
    }

    @Override
    public Request get(UUID uuid) {
        return requestRepository.read(uuid);
    }

    @Override
    public void update(Request request) {
        requestRepository.update(request);
    }

    @Override
    public boolean delete(UUID uuid) {
         requestRepository.delete(uuid);
         return true;
    }

    @Override
    public List<Request> getAll() {
        return requestRepository.findAll();
    }
}
