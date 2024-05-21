package org.example.mapper;

import org.example.config.MapperConfig;
import org.example.dto.TenantDTO;
import org.example.entity.Request;
import org.example.entity.Tenant;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.mapstruct.factory.Mappers;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Mapper(config = MapperConfig.class, uses = {RequestMapper.class})
public interface TenantMapper extends MapperBase<Tenant, TenantDTO>{
    TenantMapper INSTANCE = Mappers.getMapper(TenantMapper.class);

    @Mapping(source = "requests", target = "requestIds", qualifiedByName = "mapRequestIds")
    TenantDTO toDto(Tenant tenant);

    @Mapping(source = "requestIds", target = "requests", qualifiedByName = "mapRequests")
    Tenant toEntity(TenantDTO tenantDTO);

    @Named("mapRequestIds")
    default List<String> mapRequestIds(List<Request> requests) {
        if (requests == null) {
            return null;
        }

        return requests.stream()
                .map(Request::getRequestId)
                .map(UUID::toString)
                .collect(Collectors.toList());
    }

    @Named("mapRequests")
    default List<Request> mapRequests(List<String> requestIds) {
        if (requestIds == null) {
            return null;
        }

        return requestIds.stream()
                .map(requestId -> {
                    Request request = new Request();
                    request.setRequestId(UUID.fromString(requestId));
                    return request;
                })
                .collect(Collectors.toList());
    }
}
