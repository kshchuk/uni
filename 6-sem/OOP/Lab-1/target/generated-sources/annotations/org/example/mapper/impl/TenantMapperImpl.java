package org.example.mapper.impl;

import java.util.List;
import java.util.UUID;
import javax.annotation.processing.Generated;
import org.example.dto.TenantDTO;
import org.example.entity.Request;
import org.example.entity.Tenant;
import org.example.mapper.TenantMapper;

@Generated(
    value = "org.mapstruct.ap.MappingProcessor",
    date = "2024-04-29T15:01:53+0300",
    comments = "version: 1.5.5.Final, compiler: javac, environment: Java 21.0.2 (Oracle Corporation)"
)
public class TenantMapperImpl implements TenantMapper {

    @Override
    public TenantDTO toDto(Tenant tenant) {
        if ( tenant == null ) {
            return null;
        }

        TenantDTO tenantDTO = new TenantDTO();

        List<String> list = mapRequestIds( tenant.getRequests() );
        if ( list != null ) {
            tenantDTO.setRequestIds( list );
        }
        if ( tenant.getTenantId() != null ) {
            tenantDTO.setTenantId( tenant.getTenantId().toString() );
        }
        if ( tenant.getName() != null ) {
            tenantDTO.setName( tenant.getName() );
        }
        if ( tenant.getAddress() != null ) {
            tenantDTO.setAddress( tenant.getAddress() );
        }

        return tenantDTO;
    }

    @Override
    public Tenant toEntity(TenantDTO tenantDTO) {
        if ( tenantDTO == null ) {
            return null;
        }

        Tenant tenant = new Tenant();

        List<Request> list = mapRequests( tenantDTO.getRequestIds() );
        if ( list != null ) {
            tenant.setRequests( list );
        }
        if ( tenantDTO.getTenantId() != null ) {
            tenant.setTenantId( UUID.fromString( tenantDTO.getTenantId() ) );
        }
        if ( tenantDTO.getName() != null ) {
            tenant.setName( tenantDTO.getName() );
        }
        if ( tenantDTO.getAddress() != null ) {
            tenant.setAddress( tenantDTO.getAddress() );
        }

        return tenant;
    }
}
