package com.example.publicutilitiesapi.mapper;

import com.example.publicutilitiesapi.dto.RequestDto;
import com.example.publicutilitiesapi.entity.Request;
import org.mapstruct.*;

@Mapper(unmappedTargetPolicy = ReportingPolicy.IGNORE, componentModel = MappingConstants.ComponentModel.SPRING)
public interface RequestMapper extends MapperBase<RequestDto, Request> {
    Request toEntity(RequestDto requestDto);

    RequestDto toDto(Request request);

    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    Request partialUpdate(RequestDto requestDto, @MappingTarget Request request);
}