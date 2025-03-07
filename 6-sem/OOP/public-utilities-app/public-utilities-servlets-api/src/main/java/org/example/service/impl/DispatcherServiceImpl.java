package org.example.service.impl;

import org.example.entity.Specialist;
import org.example.entity.Team;
import org.example.entity.WorkPlan;
import org.example.repository.SpecialistRepository;
import org.example.repository.TeamRepository;
import org.example.repository.WorkPlanRepository;
import org.example.service.DispatcherService;

import java.util.List;
import java.util.UUID;

public class DispatcherServiceImpl implements DispatcherService {
    private final SpecialistRepository specialistRepository;
    private final TeamRepository teamRepository;
    private final WorkPlanRepository workPlanRepository;

    public DispatcherServiceImpl(SpecialistRepository specialistRepository,
                                 TeamRepository teamRepository,
                                 WorkPlanRepository workPlanRepository) {

        this.specialistRepository = specialistRepository;
        this.teamRepository = teamRepository;
        this.workPlanRepository = workPlanRepository;
    }

    @Override
    public Team createTeam(UUID specialistId, Team team) {
        team.setDispatcher(specialistRepository.read(specialistId));
        teamRepository.create(team);
        return team;
    }

    @Override
    public List<Team> getTeams() {
        return teamRepository.findAll();
    }

    @Override
    public Team getTeam(UUID teamId) {
        return teamRepository.read(teamId);
    }

    @Override
    public void updateTeam(Team team) {
        teamRepository.update(team);
    }

    @Override
    public void removeTeam(UUID teamId) {
        teamRepository.delete(teamId);
    }

    @Override
    public void createWorkPlan(UUID teamId, WorkPlan workPlan) {
        var team = teamRepository.read(teamId);
        team = teamRepository.readWithWorkPlans(team);

        team.getWorkPlans().add(workPlan);
        teamRepository.update(team);
    }

    @Override
    public void removeWorkPlan(UUID teamId, UUID workPlanId) {
        var team = teamRepository.read(teamId);
        team = teamRepository.readWithWorkPlans(team);

        team.getWorkPlans().removeIf(workPlan -> workPlan.getWorkPlanId().equals(workPlanId));
        teamRepository.update(team);
    }

    @Override
    public void updateWorkPlan(UUID teamId, WorkPlan workPlan) {
        var team = teamRepository.read(teamId);
        team = teamRepository.readWithWorkPlans(team);

        team.getWorkPlans().removeIf(wp -> wp.getWorkPlanId().equals(workPlan.getWorkPlanId()));
        team.getWorkPlans().add(workPlan);
        teamRepository.update(team);
    }

    @Override
    public List<WorkPlan> getWorkPlans(UUID dispathcherid) {
        var dispatcher = specialistRepository.read(dispathcherid);
        dispatcher = specialistRepository.readWithWorkPlans(dispatcher);
        return dispatcher.getWorkPlans();
    }

    @Override
    public List<WorkPlan> getWorkPlans() {
        return workPlanRepository.findAll();
    }

    @Override
    public void create(Specialist specialist) {
        specialistRepository.create(specialist);
    }

    @Override
    public Specialist get(UUID uuid) {
        Specialist specialist = specialistRepository.read(uuid);
        specialist = specialistRepository.readWithTeam(specialist);
        specialist = specialistRepository.readWithWorkPlans(specialist);
        return specialist;
    }

    @Override
    public void update(Specialist specialist) {
        specialistRepository.update(specialist);
    }

    @Override
    public boolean delete(UUID uuid) {
        // TODO:
        specialistRepository.delete(uuid);
        return true;
    }

    @Override
    public List<Specialist> getAll() {
        List<Specialist> specialists = specialistRepository.findAll();
        for (Specialist specialist : specialists) {
            specialist = specialistRepository.readWithTeam(specialist);
            specialist = specialistRepository.readWithWorkPlans(specialist);
        }
        return specialists;
    }
}
