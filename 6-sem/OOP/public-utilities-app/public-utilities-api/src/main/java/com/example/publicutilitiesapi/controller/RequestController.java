package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.RequestDto;
import com.example.publicutilitiesapi.entity.Request;
import com.example.publicutilitiesapi.mapper.RequestMapper;
import com.example.publicutilitiesapi.service.RequestService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("api/request/")
public class RequestController {

    private final RequestService requestService;
    private final RequestMapper requestMapper;

    @Autowired
    public RequestController(RequestService requestService, RequestMapper requestMapper) {
        this.requestService = requestService;
        this.requestMapper = requestMapper;
    }

    @GetMapping("/{id}")
    public RequestDto getRequestById(@PathVariable UUID id) {
        return requestMapper.toDto(requestService.findById(id).orElseThrow());
    }

    @GetMapping("/tenant/{tenantId}")
    public List<RequestDto> getRequestsByTenantId(@PathVariable UUID tenantId) {
        return requestService.findRequestsByTenantId(tenantId).stream().map(requestMapper::toDto).collect(Collectors.toList());
    }

    @GetMapping("/tenant/{tenantId}/count")
    public Long getRequestsCountByTenantId(@PathVariable UUID tenantId) {
        Long count = requestService.countRequestsByTenantId(tenantId);
        return count;
    }

    @PostMapping("/create")
    public RequestDto createRequest(@RequestBody RequestDto requestDto) {
        Request request = requestMapper.toEntity(requestDto);
        return requestMapper.toDto(requestService.save(request));
    }

    @PutMapping("/update")
    public RequestDto updateRequest(@RequestBody RequestDto requestDto) {
        Request request = requestMapper.toEntity(requestDto);
        return requestMapper.toDto(requestService.save(request));
    }

    @DeleteMapping("/{id}")
    public void deleteRequest(@PathVariable UUID id) {
        requestService.deleteById(id);
    }

    @GetMapping("/all")
    public List<RequestDto> getAllRequests() {
        return requestService.findAll().stream().map(requestMapper::toDto).collect(Collectors.toList());
    }
}
