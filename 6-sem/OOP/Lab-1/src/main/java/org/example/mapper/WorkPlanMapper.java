package org.example.mapper;

import org.example.dto.WorkPlanDTO;
import org.example.entity.Team;
import org.example.entity.WorkPlan;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.mapstruct.factory.Mappers;

import java.util.UUID;

public interface WorkPlanMapper {
WorkPlanMapper INSTANCE = Mappers.getMapper(WorkPlanMapper.class);

    @Mapping(source = "team", target = "teamId", qualifiedByName = "mapTeamId")
    WorkPlanDTO toDto(WorkPlan workPlan);

    @Mapping(source = "teamId", target = "team", qualifiedByName = "mapTeam")
    WorkPlan toEntity(WorkPlanDTO workPlanDTO);

    @Named("mapTeamId")
    default UUID mapTeamId(Team team) {
        if (team == null) {
            return null;
        }

        return team.getId();
    }

    @Named("mapTeam")
    default Team mapTeam(UUID teamId) {
        if (teamId == null) {
            return null;
        }

        Team team = new Team();
        team.setId(teamId);
        return team;
    }
}
