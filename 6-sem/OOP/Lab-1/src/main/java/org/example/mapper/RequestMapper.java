package org.example.mapper;

import org.example.dto.RequestDTO;
import org.example.entity.Request;
import org.example.entity.Tenant;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.mapstruct.factory.Mappers;

import java.util.UUID;

@Mapper
public interface RequestMapper {
    RequestMapper INSTANCE = Mappers.getMapper(RequestMapper.class);

    @Mapping(source = "tenant", target = "tenantId", qualifiedByName = "mapTenantId")
    RequestDTO toDto(Request request);

    @Mapping(source = "tenantId", target = "tenant", qualifiedByName = "mapTenant")
    Request toEntity(RequestDTO requestDTO);

    @Named("mapTenantId")
    default UUID mapTenantId(Tenant tenant) {
        if (tenant == null) {
            return null;
        }

        return tenant.getId();
    }

    @Named("mapTenant")
    default Tenant mapTenant(UUID tenantId) {
        if (tenantId == null) {
            return null;
        }

        Tenant tenant = new Tenant();
        tenant.setId(tenantId);
        return tenant;
    }
}
