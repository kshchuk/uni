package org.example.mapper;

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

@Mapper
public interface SpecialistMapper {
    SpecialistMapper INSTANCE = Mappers.getMapper(SpecialistMapper.class);

    @Mapping(source = "teamId", target = "team", qualifiedByName = "mapTeam")
    @Mapping(source = "workPlanIds", target = "workPlans", qualifiedByName = "mapWorkPlans")
    SpecialistDTO toDto(Specialist specialist);

    @Mapping(source = "team", target = "teamId", qualifiedByName = "mapTeamId")
    @Mapping(source = "workPlans", target = "workPlanIds", qualifiedByName = "mapWorkPlanIds")
    Specialist toEntity(SpecialistDTO specialistDTO);

    @Named("mapTeam")
    default Team mapTeam(UUID teamId) {
        if (teamId == null) {
            return null;
        }

        Team team = new Team();
        team.setId(teamId);
        return team;
    }

    @Named("mapWorkPlans")
    default List<WorkPlan> mapWorkPlans(List<UUID> workPlanIds) {
        if (workPlanIds == null) {
            return null;
        }

        return workPlanIds.stream()
                .map(workPlanId -> {
                    WorkPlan workPlan = new WorkPlan();
                    workPlan.setId(workPlanId);
                    return workPlan;
                })
                .collect(Collectors.toList());
    }

    @Named("mapTeamId")
    default UUID mapTeamId(Team team) {
        if (team == null) {
            return null;
        }

        return team.getId();
    }

    @Named("mapWorkPlanIds")
    default List<UUID> mapWorkPlanIds(List<WorkPlan> workPlans) {
        if (workPlans == null) {
            return null;
        }

        return workPlans.stream()
                .map(WorkPlan::getId)
                .collect(Collectors.toList());
    }
}
