package org.example.mapper;

import org.example.config.MapperConfig;
import org.example.dto.TeamDTO;
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

@Mapper(config = MapperConfig.class, uses = {SpecialistMapper.class, WorkPlanMapper.class})
public interface TeamMapper extends MapperBase<Team, TeamDTO> {
    TeamMapper INSTANCE = Mappers.getMapper(TeamMapper.class);

    @Mapping(source = "specialists", target = "specialistIds", qualifiedByName = "mapTeamSpecialistListToStringList")
    @Mapping(source = "workPlans", target = "workPlanIds", qualifiedByName = "mapTeamWorkPlanListToStringList")
    @Mapping(source = "dispatcher", target = "dispatcherId", qualifiedByName = "mapTeamDispatcherToString")
    TeamDTO toDto(Team team);

    @Mapping(source = "specialistIds", target = "specialists", qualifiedByName = "mapTeamStringListToSpecialistList")
    @Mapping(source = "workPlanIds", target = "workPlans", qualifiedByName = "mapTeamStringListToWorkPlanList")
    @Mapping(source = "dispatcherId", target = "dispatcher", qualifiedByName = "mapTeamStringToDispatcher")
    Team toEntity(TeamDTO teamDTO);

    @Named("mapTeamSpecialistListToStringList")
    default List<String> mapTeamSpecialistListToStringList(List<Specialist> specialists) {
        if (specialists == null) {
            return null;
        }
        return specialists.stream()
                .map(Specialist::getSpecialistId)
                .map(UUID::toString)
                .collect(Collectors.toList());
    }

    @Named("mapTeamWorkPlanListToStringList")
    default List<String> mapTeamWorkPlanListToStringList(List<WorkPlan> workPlans) {
        if (workPlans == null) {
            return null;
        }
        return workPlans.stream()
                .map(WorkPlan::getWorkPlanId)
                .map(UUID::toString)
                .collect(Collectors.toList());
    }

    @Named("mapTeamDispatcherToString")
    default String mapTeamDispatcherToString(Specialist dispatcher) {
        if (dispatcher == null) {
            return null;
        }
        return dispatcher.getSpecialistId().toString();
    }

    @Named("mapTeamStringListToSpecialistList")
    default List<Specialist> mapTeamStringListToSpecialistList(List<String> specialistIds) {
        if (specialistIds == null) {
            return null;
        }
        return specialistIds.stream()
                .map(specialistId -> {
                    Specialist specialist = new Specialist();
                    specialist.setSpecialistId(UUID.fromString(specialistId));
                    return specialist;
                })
                .collect(Collectors.toList());
    }

    @Named("mapTeamStringListToWorkPlanList")
    default List<WorkPlan> mapTeamStringListToWorkPlanList(List<String> workPlanIds) {
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

    @Named("mapTeamStringToDispatcher")
    default Specialist mapTeamStringToDispatcher(String dispatcherId) {
        if (dispatcherId == null) {
            return null;
        }
        Specialist dispatcher = new Specialist();
        dispatcher.setSpecialistId(UUID.fromString(dispatcherId));
        return dispatcher;
    }
}
