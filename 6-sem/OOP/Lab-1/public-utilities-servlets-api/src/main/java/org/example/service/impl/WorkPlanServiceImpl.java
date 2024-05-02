package org.example.service.impl;

import org.example.entity.WorkPlan;
import org.example.repository.WorkPlanRepository;
import org.example.service.WorkPlanService;

import java.util.List;
import java.util.UUID;

public class WorkPlanServiceImpl implements WorkPlanService {
    private final WorkPlanRepository workPlanRepository;

    public WorkPlanServiceImpl(WorkPlanRepository workPlanRepository) {
        this.workPlanRepository = workPlanRepository;
    }

    @Override
    public void create(WorkPlan workPlan) {
        workPlanRepository.create(workPlan);
    }

    @Override
    public WorkPlan get(UUID uuid) {
        WorkPlan workPlan = workPlanRepository.read(uuid);
        workPlan = workPlanRepository.readWithTeam(workPlan);
        return workPlan;
    }

    @Override
    public void update(WorkPlan workPlan) {
        workPlanRepository.update(workPlan);
    }

    @Override
    public boolean delete(UUID uuid) {
        workPlanRepository.delete(uuid);
        return true;
    }

    @Override
    public List<WorkPlan> getAll() {
        List<WorkPlan> workPlans = workPlanRepository.findAll();
        for (WorkPlan workPlan : workPlans) {
            workPlan = workPlanRepository.readWithTeam(workPlan);
        }
        return workPlans;
    }
}
