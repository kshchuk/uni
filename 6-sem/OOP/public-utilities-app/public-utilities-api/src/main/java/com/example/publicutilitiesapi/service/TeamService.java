package com.example.publicutilitiesapi.service;

import com.example.publicutilitiesapi.entity.Team;
import com.example.publicutilitiesapi.repository.TeamRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class TeamService extends CrudService<Team, UUID> {

    private final TeamRepository teamRepository;

    @Autowired
    public TeamService(TeamRepository teamRepository) {
        this.teamRepository = teamRepository;
    }

    @Override
    protected JpaRepository<Team, UUID> getRepository() {
        return teamRepository;
    }
}
