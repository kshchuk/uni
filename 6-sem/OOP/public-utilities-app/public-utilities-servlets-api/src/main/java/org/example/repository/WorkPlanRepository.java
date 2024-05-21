package org.example.repository;

import org.example.entity.WorkPlan;

import java.util.UUID;

public interface WorkPlanRepository extends CrudRepository<WorkPlan, UUID> {
    WorkPlan readWithTeam(WorkPlan workPlan);
}
