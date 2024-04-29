package org.example.mapper.impl;

import java.time.Duration;
import java.util.UUID;
import javax.annotation.processing.Generated;
import org.example.dto.RequestDTO;
import org.example.entity.Request;
import org.example.mapper.RequestMapper;

@Generated(
    value = "org.mapstruct.ap.MappingProcessor",
    date = "2024-04-29T15:01:54+0300",
    comments = "version: 1.5.5.Final, compiler: javac, environment: Java 21.0.2 (Oracle Corporation)"
)
public class RequestMapperImpl implements RequestMapper {

    @Override
    public RequestDTO toDto(Request request) {
        if ( request == null ) {
            return null;
        }

        RequestDTO requestDTO = new RequestDTO();

        if ( request.getTenant() != null ) {
            requestDTO.setTenantId( mapTenantId( request.getTenant() ) );
        }
        if ( request.getRequestId() != null ) {
            requestDTO.setRequestId( request.getRequestId().toString() );
        }
        if ( request.getWorkType() != null ) {
            requestDTO.setWorkType( request.getWorkType() );
        }
        if ( request.getScopeOfWork() != null ) {
            requestDTO.setScopeOfWork( request.getScopeOfWork() );
        }
        if ( request.getDesiredTime() != null ) {
            requestDTO.setDesiredTime( request.getDesiredTime().toString() );
        }

        return requestDTO;
    }

    @Override
    public Request toEntity(RequestDTO requestDTO) {
        if ( requestDTO == null ) {
            return null;
        }

        Request request = new Request();

        if ( requestDTO.getTenantId() != null ) {
            request.setTenant( mapTenant( requestDTO.getTenantId() ) );
        }
        if ( requestDTO.getRequestId() != null ) {
            request.setRequestId( UUID.fromString( requestDTO.getRequestId() ) );
        }
        if ( requestDTO.getWorkType() != null ) {
            request.setWorkType( requestDTO.getWorkType() );
        }
        if ( requestDTO.getScopeOfWork() != null ) {
            request.setScopeOfWork( requestDTO.getScopeOfWork() );
        }
        if ( requestDTO.getDesiredTime() != null ) {
            request.setDesiredTime( Duration.parse( requestDTO.getDesiredTime() ) );
        }

        return request;
    }
}
