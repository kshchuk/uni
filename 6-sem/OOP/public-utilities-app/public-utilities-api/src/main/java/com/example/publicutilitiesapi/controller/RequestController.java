package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.RequestDto;
import com.example.publicutilitiesapi.repository.RequestRepository;
import com.example.publicutilitiesapi.mapper.RequestMapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/request/")
public class RequestController {

    private final RequestRepository requestRepository;
    private final RequestMapper requestMapper;

    public RequestController(RequestRepository requestRepository,
                             RequestMapper requestMapper) {
        this.requestRepository = requestRepository;
        this.requestMapper = requestMapper;
    }

    @GetMapping("/{id}")
    public RequestDto getRequestById(@PathVariable UUID id) {
        return requestMapper.toEntity(requestRepository.findById(id).orElseThrow());
    }

    @PostMapping("/create")
    public RequestDto createRequest(@RequestBody RequestDto requestDto) {
        return requestMapper.toEntity(requestRepository.save(requestMapper.toDto(requestDto)));
    }

    @PutMapping("/update")
    public RequestDto updateRequest(@RequestBody RequestDto requestDto) {
        return requestMapper.toEntity(requestRepository.save(requestMapper.toDto(requestDto)));
    }

    @DeleteMapping("/{id}")
    public void deleteRequest(@PathVariable UUID id) {
        requestRepository.deleteById(id);
    }

    @GetMapping("/all")
    public List<RequestDto> getAllRequests() {
        return requestRepository.findAll().stream().map(requestMapper::toEntity).collect(Collectors.toList());
    }
}
