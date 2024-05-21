package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.TeamDto;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/team/")
public class TeamController {
    @GetMapping("/all")
    public List<TeamDto> getAllTeams() {
        /// TODO: Implement this method
        return null;
    }
}
