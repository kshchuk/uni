package com.example.publicutilitiesapi.service;

import com.example.publicutilitiesapi.entity.WorkPlan;
import com.example.publicutilitiesapi.repository.WorkPlanRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class WorkPlanService extends CrudService<WorkPlan, UUID> {

    private final WorkPlanRepository workPlanRepository;

    @Autowired
    public WorkPlanService(WorkPlanRepository workPlanRepository) {
        this.workPlanRepository = workPlanRepository;
    }

    @Override
    protected JpaRepository<WorkPlan, UUID> getRepository() {
        return workPlanRepository;
    }
}
