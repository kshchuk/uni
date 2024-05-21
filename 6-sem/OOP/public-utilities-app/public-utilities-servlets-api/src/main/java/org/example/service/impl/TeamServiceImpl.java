package org.example.service.impl;

import org.example.entity.Specialist;
import org.example.entity.Team;
import org.example.entity.WorkPlan;
import org.example.repository.TeamRepository;
import org.example.service.TeamService;

import java.util.List;
import java.util.UUID;

public class TeamServiceImpl implements TeamService {
    private final TeamRepository teamRepository;

    public TeamServiceImpl(TeamRepository teamRepository) {
        this.teamRepository = teamRepository;
    }

    @Override
    public void create(Team team) {
        teamRepository.create(team);
    }

    @Override
    public Team get(UUID uuid) {
        Team team = teamRepository.read(uuid);
        team = teamRepository.readWithDispatcher(team);
        team = teamRepository.readWithSpecialists(team);
        team = teamRepository.readWithWorkPlans(team);
        return team;
    }

    @Override
    public void update(Team team) {
        teamRepository.update(team);
    }

    @Override
    public boolean delete(UUID uuid) {
        teamRepository.delete(uuid);
        return true;
    }

    @Override
    public List<Team> getAll() {
        List<Team> teams = teamRepository.findAll();
        for (Team team : teams) {
            team = teamRepository.readWithDispatcher(team);
            team = teamRepository.readWithSpecialists(team);
            team = teamRepository.readWithWorkPlans(team);
        }
        return teams;
    }

    @Override
    public List<Specialist> getSpecialists(UUID teamId) {
        Team team = teamRepository.read(teamId);
        team = teamRepository.readWithSpecialists(team);
        return team.getSpecialists();
    }

    @Override
    public List<WorkPlan> getWorkPlans(UUID teamId) {
        Team team = teamRepository.read(teamId);
        team = teamRepository.readWithWorkPlans(team);
        return team.getWorkPlans();
    }
}
