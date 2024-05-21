package com.example.publicutilitiesapi.mapper;

import com.example.publicutilitiesapi.dto.WorkPlanDto;
import com.example.publicutilitiesapi.entity.WorkPlan;
import org.example.mapper.MapperBase;
import org.mapstruct.*;

@Mapper(unmappedTargetPolicy = ReportingPolicy.IGNORE, componentModel = MappingConstants.ComponentModel.SPRING)
public interface WorkPlanMapper extends MapperBase<WorkPlanDto, WorkPlan> {
    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    WorkPlan partialUpdate(WorkPlanDto workPlanDto, @MappingTarget WorkPlan workPlan);
}