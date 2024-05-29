package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.SpecialistDto;
import com.example.publicutilitiesapi.entity.Specialist;
import com.example.publicutilitiesapi.mapper.SpecialistMapper;
import com.example.publicutilitiesapi.service.SpecialistService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("api/specialist/")
public class SpecialistController {

    private final SpecialistService specialistService;
    private final SpecialistMapper specialistMapper;

    @Autowired
    public SpecialistController(SpecialistService specialistService, SpecialistMapper specialistMapper) {
        this.specialistService = specialistService;
        this.specialistMapper = specialistMapper;
    }

    @GetMapping("/{id}")
    public SpecialistDto getSpecialistById(@PathVariable UUID id) {
        return specialistMapper.toDto(specialistService.findById(id).orElseThrow());
    }

    @PostMapping("/create")
    public SpecialistDto createSpecialist(@RequestBody SpecialistDto specialistDto) {
        Specialist specialist = specialistMapper.toEntity(specialistDto);
        specialist.setId(UUID.randomUUID());
        return specialistMapper.toDto(specialistService.save(specialist));
    }

    @PutMapping("/update")
    public SpecialistDto updateSpecialist(@RequestBody SpecialistDto specialistDto) {
        Specialist specialist = specialistMapper.toEntity(specialistDto);
        return specialistMapper.toDto(specialistService.save(specialist));
    }

    @DeleteMapping("/{id}")
    public void deleteSpecialist(@PathVariable UUID id) {
        specialistService.deleteById(id);
    }

    @GetMapping("/all")
    public List<SpecialistDto> getAllSpecialists() {
        return specialistService.findAll().stream().map(specialistMapper::toDto).collect(Collectors.toList());
    }

    @GetMapping("/team/{teamId}")
    public List<SpecialistDto> getAllSpecialistsByTeamId(@PathVariable UUID teamId) {
        List<Specialist> specialists = specialistService.findAllByTeamId(teamId);
        return specialists.stream().map(specialistMapper::toDto).collect(Collectors.toList());
    }

    @GetMapping("/team/{teamId}/count")
    public Long countSpecialistsByTeamId(@PathVariable UUID teamId) {
        return specialistService.countSpecialistsByTeamId(teamId);
    }
}
