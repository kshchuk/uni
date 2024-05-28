package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.SpecialistDto;
import com.example.publicutilitiesapi.mapper.SpecialistMapper;
import com.example.publicutilitiesapi.repository.SpecialistRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/specialist/")
public class SpecialistController {

    private final SpecialistRepository specialistRepository;
    private final SpecialistMapper specialistMapper;

    public SpecialistController(SpecialistRepository specialistRepository,
                                SpecialistMapper specialistMapper) {
        this.specialistRepository = specialistRepository;
        this.specialistMapper = specialistMapper;
    }

    @GetMapping("/{id}")
    public SpecialistDto getSpecialistById(@PathVariable UUID id) {
        return specialistMapper.toDto(specialistRepository.findById(id).orElseThrow());
    }

    @PostMapping("/create")
    public SpecialistDto createSpecialist(@RequestBody SpecialistDto specialistDto) {
        return specialistMapper.toDto(specialistRepository.save(specialistMapper.toEntity(specialistDto)));
    }

    @PutMapping("/update")
    public SpecialistDto updateSpecialist(@RequestBody SpecialistDto specialistDto) {
        return specialistMapper.toDto(specialistRepository.save(specialistMapper.toEntity(specialistDto)));
    }

    @DeleteMapping("/{id}")
    public void deleteSpecialist(@PathVariable UUID id) {
        specialistRepository.deleteById(id);
    }

    @GetMapping("/all")
    public List<SpecialistDto> getAllSpecialists() {
        return specialistRepository.findAll().stream().map(specialistMapper::toDto).collect(Collectors.toList());
    }
}
