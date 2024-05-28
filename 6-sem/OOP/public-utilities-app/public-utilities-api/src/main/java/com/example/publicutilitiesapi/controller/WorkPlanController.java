package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.WorkPlanDto;
import com.example.publicutilitiesapi.mapper.WorkPlanMapper;
import com.example.publicutilitiesapi.repository.WorkPlanRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/work-plan/")
public class WorkPlanController {

    private final WorkPlanRepository workPlanRepository;
    private final WorkPlanMapper workPlanMapper;

    public WorkPlanController(WorkPlanRepository workPlanRepository,
                              WorkPlanMapper workPlanMapper) {
        this.workPlanRepository = workPlanRepository;
        this.workPlanMapper = workPlanMapper;
    }

    @GetMapping("/all")
    public List<WorkPlanDto> getAllWorkPlans() {
        return workPlanRepository.findAll().stream().map(workPlanMapper::toDto).collect(Collectors.toList());
    }
}
