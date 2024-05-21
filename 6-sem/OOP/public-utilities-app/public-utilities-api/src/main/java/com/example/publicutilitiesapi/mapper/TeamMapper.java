package com.example.publicutilitiesapi.mapper;

import com.example.publicutilitiesapi.dto.TeamDto;
import com.example.publicutilitiesapi.entity.Team;
import org.example.mapper.MapperBase;
import org.mapstruct.*;

@Mapper(unmappedTargetPolicy = ReportingPolicy.IGNORE, componentModel = MappingConstants.ComponentModel.SPRING)
public interface TeamMapper extends MapperBase<TeamDto, Team> {
    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    Team partialUpdate(TeamDto teamDto, @MappingTarget Team team);
}