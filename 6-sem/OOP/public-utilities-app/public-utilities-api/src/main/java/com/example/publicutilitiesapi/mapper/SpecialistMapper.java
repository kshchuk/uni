package com.example.publicutilitiesapi.mapper;

import com.example.publicutilitiesapi.dto.SpecialistDto;
import com.example.publicutilitiesapi.entity.Specialist;
import org.mapstruct.*;

@Mapper(unmappedTargetPolicy = ReportingPolicy.IGNORE, componentModel = MappingConstants.ComponentModel.SPRING)
public interface SpecialistMapper extends MapperBase<SpecialistDto, Specialist> {
    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    Specialist partialUpdate(SpecialistDto specialistDto, @MappingTarget Specialist specialist);
}