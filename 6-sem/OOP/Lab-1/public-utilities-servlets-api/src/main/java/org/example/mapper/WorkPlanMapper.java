package org.example.mapper;

import org.example.config.MapperConfig;
import org.example.dto.WorkPlanDTO;
import org.example.entity.Team;
import org.example.entity.WorkPlan;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.mapstruct.factory.Mappers;

import java.util.UUID;

@Mapper(config = MapperConfig.class, uses = {TeamMapper.class})
public interface WorkPlanMapper {
    WorkPlanMapper INSTANCE = Mappers.getMapper(WorkPlanMapper.class);

    @Mapping(source = "team", target = "teamId", qualifiedByName = "mapTeamId")
    WorkPlanDTO toDto(WorkPlan workPlan);

    @Mapping(source = "teamId", target = "team", qualifiedByName = "mapTeam")
    WorkPlan toEntity(WorkPlanDTO workPlanDTO);

    @Named("mapTeamId")
    default String mapTeamId(Team team) {
        if (team == null) {
            return null;
        }

        return team.getTeamId().toString();
    }

    @Named("mapTeam")
    default Team mapTeam(String teamId) {
        if (teamId == null) {
            return null;
        }

        Team team = new Team();
        team.setTeamId(UUID.fromString(teamId));
        return team;
    }
}
