package org.example.service;

import org.example.entity.Specialist;
import org.example.entity.Team;
import org.example.entity.WorkPlan;

import java.util.List;
import java.util.UUID;

public interface TeamService extends Service<Team, UUID> {
    List<Specialist> getSpecialists(UUID teamId);
    List<WorkPlan> getWorkPlans(UUID teamId);
}
