package org.example.service;

import org.example.entity.Specialist;
import org.example.entity.Team;
import org.example.entity.WorkPlan;

import java.util.List;
import java.util.UUID;

public interface DispatcherService extends Service<Specialist, UUID> {
    Team createTeam(UUID SpecialistId, Team team);
    List<Team> getTeams();
    Team getTeam(UUID teamId);
    void updateTeam(Team team);
    void removeTeam(UUID teamId);
    void createWorkPlan(UUID teamId, WorkPlan workPlan);
    void removeWorkPlan(UUID teamId, UUID workPlanId);
    void updateWorkPlan(UUID teamId, WorkPlan workPlan);

    List<WorkPlan> getWorkPlans(UUID teamId);
    List<WorkPlan> getWorkPlans();
}
