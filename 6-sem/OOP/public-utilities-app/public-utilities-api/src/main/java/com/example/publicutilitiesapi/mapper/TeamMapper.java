package com.example.publicutilitiesapi.mapper;

import com.example.publicutilitiesapi.entity.Team;
import org.example.dto.TeamDTO;
import org.example.mapper.MapperBase;
import org.mapstruct.*;

@Mapper(unmappedTargetPolicy = ReportingPolicy.IGNORE, componentModel = MappingConstants.ComponentModel.SPRING)
public interface TeamMapper extends MapperBase<TeamDTO, Team> {
    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    Team partialUpdate(TeamDTO teamDTO, @MappingTarget Team team);
}