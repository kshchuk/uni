package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.TeamDto;
import com.example.publicutilitiesapi.mapper.TeamMapper;
import com.example.publicutilitiesapi.repository.TeamRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/team/")
public class TeamController {

    private final TeamRepository teamRepository;
    private final TeamMapper teamMapper;

    public TeamController(TeamRepository teamRepository,
                          TeamMapper teamMapper) {
        this.teamRepository = teamRepository;
        this.teamMapper = teamMapper;
    }

    @GetMapping("/{id}")
    public TeamDto getTeamById(@PathVariable UUID id) {
        return teamMapper.toDto(teamRepository.findById(id).orElseThrow());
    }

    @PostMapping("/create")
    public TeamDto createTeam(@RequestBody TeamDto teamDto) {
        return teamMapper.toDto(teamRepository.save(teamMapper.toEntity(teamDto)));
    }

    @PutMapping("/update")
    public TeamDto updateTeam(@RequestBody TeamDto teamDto) {
        return teamMapper.toDto(teamRepository.save(teamMapper.toEntity(teamDto)));
    }

    @DeleteMapping("/{id}")
    public void deleteTeam(@PathVariable UUID id) {
        teamRepository.deleteById(id);
    }

    @GetMapping("/all")
    public List<TeamDto> getAllTeams() {
        return teamRepository.findAll().stream().map(teamMapper::toDto).collect(Collectors.toList());
    }
}
