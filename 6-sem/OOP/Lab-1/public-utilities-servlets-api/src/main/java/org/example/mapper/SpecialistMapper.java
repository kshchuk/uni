package org.example.mapper;

import org.example.config.MapperConfig;
import org.example.dto.SpecialistDTO;
import org.example.entity.Specialist;
import org.example.entity.Team;
import org.example.entity.WorkPlan;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.mapstruct.factory.Mappers;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Mapper(config = MapperConfig.class, uses = {TeamMapper.class, WorkPlanMapper.class})
public interface SpecialistMapper {
    SpecialistMapper INSTANCE = Mappers.getMapper(SpecialistMapper.class);

    @Mapping(source = "team", target = "teamId", qualifiedByName = "mapTeamIdToString")
    @Mapping(source = "workPlans", target = "workPlanIds", qualifiedByName = "mapWorkPlanListToStringList")
    SpecialistDTO toDto(Specialist specialist);

    @Mapping(source = "teamId", target = "team", qualifiedByName = "mapStringToTeam")
    @Mapping(source = "workPlanIds", target = "workPlans", qualifiedByName = "mapStringListToWorkPlanList")
    Specialist toEntity(SpecialistDTO specialistDTO);

    @Named("mapTeamIdToString")
    default String mapTeamIdToString(Team team) {
        if (team == null) {
            return null;
        }
        return team.getTeamId().toString();
    }

    @Named("mapStringListToWorkPlanList")
    default List<WorkPlan> mapStringListToWorkPlanList(List<String> workPlanIds) {
        if (workPlanIds == null) {
            return null;
        }
        return workPlanIds.stream()
                .map(workPlanId -> {
                    WorkPlan workPlan = new WorkPlan();
                    workPlan.setWorkPlanId(UUID.fromString(workPlanId));
                    return workPlan;
                })
                .collect(Collectors.toList());
    }

    @Named("mapStringToTeam")
    default Team mapStringToTeam(String teamId) {
        if (teamId == null) {
            return null;
        }
        Team team = new Team();
        team.setTeamId(UUID.fromString(teamId));
        return team;
    }

    @Named("mapWorkPlanListToStringList")
    default List<String> mapWorkPlanListToStringList(List<WorkPlan> workPlans) {
        if (workPlans == null) {
            return null;
        }
        return workPlans.stream()
                .map(workPlan -> workPlan.getWorkPlanId().toString())
                .collect(Collectors.toList());
    }
}


