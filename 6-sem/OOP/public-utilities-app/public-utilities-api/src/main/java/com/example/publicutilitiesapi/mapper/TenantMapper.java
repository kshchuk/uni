package com.example.publicutilitiesapi.mapper;

import com.example.publicutilitiesapi.dto.TenantDto;
import com.example.publicutilitiesapi.entity.Tenant;
import org.mapstruct.*;

@Mapper(unmappedTargetPolicy = ReportingPolicy.IGNORE, componentModel = MappingConstants.ComponentModel.SPRING)
public interface TenantMapper extends MapperBase<TenantDto, Tenant> {
    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    Tenant partialUpdate(TenantDto tenantDto, @MappingTarget Tenant tenant);
}