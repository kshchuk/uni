package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.TeamDto;
import com.example.publicutilitiesapi.entity.Team;
import com.example.publicutilitiesapi.mapper.TeamMapper;
import com.example.publicutilitiesapi.service.TeamService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("api/team/")
public class TeamController {

    private final TeamService teamService;
    private final TeamMapper teamMapper;

    @Autowired
    public TeamController(TeamService teamService, TeamMapper teamMapper) {
        this.teamService = teamService;
        this.teamMapper = teamMapper;
    }

    @GetMapping("/{id}")
    public TeamDto getTeamById(@PathVariable UUID id) {
        return teamMapper.toDto(teamService.findById(id).orElseThrow());
    }

    @PostMapping("/create")
    public TeamDto createTeam(@RequestBody TeamDto teamDto) {
        Team team = teamMapper.toEntity(teamDto);
        return teamMapper.toDto(teamService.save(team));
    }

    @PutMapping("/update")
    public TeamDto updateTeam(@RequestBody TeamDto teamDto) {
        Team team = teamMapper.toEntity(teamDto);
        return teamMapper.toDto(teamService.save(team));
    }

    @DeleteMapping("/{id}")
    public void deleteTeam(@PathVariable UUID id) {
        teamService.deleteById(id);
    }

    @GetMapping("/all")
    public List<TeamDto> getAllTeams() {
        return teamService.findAll().stream().map(teamMapper::toDto).collect(Collectors.toList());
    }
}
