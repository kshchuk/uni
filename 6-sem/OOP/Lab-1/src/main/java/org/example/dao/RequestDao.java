package org.example.dao;

import org.example.entity.Request;

import java.sql.SQLException;
import java.util.List;
import java.util.UUID;

public interface RequestDao extends CrudDao<Request, UUID> {
    List<Request> findByTenantId(UUID tenantId) throws SQLException;
    List<Request> findByDispatcherId(UUID dispatcherId) throws SQLException;
}
