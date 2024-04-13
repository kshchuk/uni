package org.example.mapper;

import org.mapstruct.Mapper;

import org.example.dto.SpecialistDTO;
import org.example.entity.Specialist;
import org.example.entity.Team;
import org.example.entity.WorkPlan;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.mapstruct.factory.Mappers;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Mapper
public interface TeamMapper {
    TeamMapper INSTANCE = Mappers.getMapper(TeamMapper.class);

    @Mapping(source = "dispatcherId", target = "dispatcher", qualifiedByName = "mapDispatcher")
    @Mapping(source = "specialistIds", target = "specialists", qualifiedByName = "mapSpecialists")
    @Mapping(source = "workPlanIds", target = "workPlans", qualifiedByName = "mapWorkPlans")
    SpecialistDTO toDto(Team team);

    @Mapping(source = "dispatcher", target = "dispatcherId", qualifiedByName = "mapDispatcherId")
    @Mapping(source = "specialists", target = "specialistIds", qualifiedByName = "mapSpecialistIds")
    @Mapping(source = "workPlans", target = "workPlanIds", qualifiedByName = "mapWorkPlanIds")
    Team toEntity(SpecialistDTO teamDTO);

    @Named("mapDispatcher")
    default Specialist mapDispatcher(UUID dispatcherId) {
        if (dispatcherId == null) {
            return null;
        }

        Specialist specialist = new Specialist();
        specialist.setId(dispatcherId);
        return specialist;
    }

    @Named("mapSpecialists")
    default List<Specialist> mapSpecialists(List<UUID> specialistIds) {
        if (specialistIds == null) {
            return null;
        }

        return specialistIds.stream()
                .map(specialistId -> {
                    Specialist specialist = new Specialist();
                    specialist.setId(specialistId);
                    return specialist;
                })
                .collect(Collectors.toList());
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

    @Named("mapDispatcherId")
    default UUID mapDispatcherId(Specialist dispatcher) {
        if (dispatcher == null) {
            return null;
        }

        return dispatcher.getId();
    }

    @Named("mapSpecialistIds")
    default List<UUID> mapSpecialistIds(List<Specialist> specialists) {
        if (specialists == null) {
            return null;
        }

        return specialists.stream()
                .map(Specialist::getId)
                .collect(Collectors.toList());
    }
}
