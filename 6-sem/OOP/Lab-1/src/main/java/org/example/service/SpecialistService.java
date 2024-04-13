package org.example.service;

import org.example.entity.Specialist;
import org.example.entity.WorkPlan;

import java.util.List;
import java.util.UUID;

public interface SpecialistService extends Service<Specialist, UUID>{
    List<WorkPlan> getWorkPlans(UUID specialistId);
}
