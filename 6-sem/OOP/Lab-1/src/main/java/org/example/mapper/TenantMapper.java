package org.example.mapper;

import org.example.dto.SpecialistDTO;
import org.example.entity.Request;
import org.example.entity.Specialist;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.mapstruct.factory.Mappers;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Mapper
public interface TenantMapper {
    TenantMapper INSTANCE = Mappers.getMapper(TenantMapper.class);

    @Mapping(source = "requests", target = "requestIds", qualifiedByName = "mapRequestIds")
    SpecialistDTO toDto(Specialist specialist);

    @Mapping(source = "requestIds", target = "requests", qualifiedByName = "mapRequests")
    Specialist toEntity(SpecialistDTO specialistDTO);

    @Named("mapRequestIds")
    default List<UUID> mapRequestIds(List<Request> requests) {
        if (requests == null) {
            return null;
        }

        return requests.stream()
                .map(Request::getId)
                .collect(Collectors.toList());
    }

    @Named("mapRequests")
    default List<Request> mapRequests(List<UUID> requestIds) {
        if (requestIds == null) {
            return null;
        }

        return requestIds.stream()
                .map(requestId -> {
                    Request request = new Request();
                    request.setId(requestId);
                    return request;
                })
                .collect(Collectors.toList());
    }
}
