package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.WorkPlanDto;
import com.example.publicutilitiesapi.entity.WorkPlan;
import com.example.publicutilitiesapi.mapper.WorkPlanMapper;
import com.example.publicutilitiesapi.service.WorkPlanService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("api/work-plan/")
public class WorkPlanController {

    private final WorkPlanService workPlanService;
    private final WorkPlanMapper workPlanMapper;

    @Autowired
    public WorkPlanController(WorkPlanService workPlanService, WorkPlanMapper workPlanMapper) {
        this.workPlanService = workPlanService;
        this.workPlanMapper = workPlanMapper;
    }

    @GetMapping("/{id}")
    public WorkPlanDto getWorkPlanById(@PathVariable UUID id) {
        return workPlanMapper.toDto(workPlanService.findById(id).orElseThrow());
    }

    @PostMapping("/create")
    public WorkPlanDto createWorkPlan(@RequestBody WorkPlanDto workPlanDto) {
        WorkPlan workPlan = workPlanMapper.toEntity(workPlanDto);
        return workPlanMapper.toDto(workPlanService.save(workPlan));
    }

    @PutMapping("/update")
    public WorkPlanDto updateWorkPlan(@RequestBody WorkPlanDto workPlanDto) {
        WorkPlan workPlan = workPlanMapper.toEntity(workPlanDto);
        return workPlanMapper.toDto(workPlanService.save(workPlan));
    }

    @DeleteMapping("/{id}")
    public void deleteWorkPlan(@PathVariable UUID id) {
        workPlanService.deleteById(id);
    }

    @GetMapping("/all")
    public List<WorkPlanDto> getAllWorkPlans() {
        List<WorkPlan> workPlans = workPlanService.findAll();
        return workPlans.stream().map(workPlanMapper::toDto).collect(Collectors.toList());
    }

    @GetMapping("/dispatcher/{dispatcherId}")
    public List<WorkPlanDto> getAllWorkPlansByDispatcherId(@PathVariable UUID dispatcherId) {
        List<WorkPlan> workPlans = workPlanService.findAllByDispatcherId(dispatcherId);
        return workPlans.stream().map(workPlanMapper::toDto).collect(Collectors.toList());
    }

    @GetMapping("/team/{teamId}")
    public List<WorkPlanDto> getAllWorkPlansByTeamId(@PathVariable UUID teamId) {
        List<WorkPlan> workPlans = workPlanService.findAllByTeamId(teamId);
        return workPlans.stream().map(workPlanMapper::toDto).collect(Collectors.toList());
    }

    @GetMapping("/team/{teamId}/count")
    public Long countWorkPlansByTeamId(@PathVariable UUID teamId) {
        return workPlanService.countWorkPlansByTeamId(teamId);
    }
}
