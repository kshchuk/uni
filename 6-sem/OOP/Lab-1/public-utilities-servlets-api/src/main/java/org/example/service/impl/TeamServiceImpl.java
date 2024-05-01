package org.example.service.impl;

import org.example.entity.Team;
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
        return teamRepository.read(uuid);
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
        return teamRepository.findAll();
    }
}
