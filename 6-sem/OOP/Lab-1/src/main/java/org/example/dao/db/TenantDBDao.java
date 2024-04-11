package org.example.dao.db;

import org.example.dao.TenantDao;
import org.example.entity.Tenant;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

class TenantDBDao extends DBDao<Tenant, UUID> implements TenantDao {
    protected TenantDBDao(Connection con, String tableName) throws SQLException {
        super(con, tableName);
    }

    @Override
    protected void createTableIfNotExists() throws SQLException {
        var statement = con.prepareStatement("CREATE TABLE IF NOT EXISTS tenant (" +
                "tenant_id UUID PRIMARY KEY," +
                "name VARCHAR(255) NOT NULL," +
                "address VARCHAR(255) NOT NULL" +
                ");");
        statement.executeUpdate();
    }

    @Override
    public Tenant create(Tenant entity) throws Exception {
        var statement = con.prepareStatement("INSERT INTO tenant (tenant_id, name, address) VALUES (?, ?, ?);");
        statement.setObject(1, entity.getTenantId());
        statement.setString(2, entity.getName());
        statement.setString(3, entity.getAddress());

        statement.executeUpdate();
        return entity;
    }

    @Override
    public Tenant read(UUID uuid) throws Exception {
        var statement = con.prepareStatement("SELECT tenant_id, name, address FROM tenant " +
                                                 "WHERE tenant_id = ?;");
        statement.setObject(1, uuid);

        var resultSet = statement.executeQuery();
        if (resultSet.next()) {
            var tenant = new Tenant();
            tenant.setTenantId((UUID) resultSet.getObject(1));
            tenant.setName(resultSet.getString(2));
            tenant.setAddress(resultSet.getString(3));

            return tenant;
        }
        return null;
    }

    @Override
    public void update(Tenant entity) throws Exception {
        var statement = con.prepareStatement("UPDATE tenant SET name = ?, address = ? WHERE tenant_id = ?;");
        statement.setString(1, entity.getName());
        statement.setString(2, entity.getAddress());
        statement.setObject(3, entity.getTenantId());

        statement.executeUpdate();
    }

    @Override
    public void delete(UUID uuid) throws Exception {
        var statement = con.prepareStatement("DELETE FROM tenant WHERE tenant_id = ?;");
        statement.setObject(1, uuid);

        statement.executeUpdate();
    }

    @Override
    public List<Tenant> findAll() throws Exception {
        var statement = con.prepareStatement("SELECT tenant_id, name, address FROM tenant;");

        var resultSet = statement.executeQuery();
        var tenants = new ArrayList<Tenant>();
        while (resultSet.next()) {
            var tenant = new Tenant();
            tenant.setTenantId((UUID) resultSet.getObject(1));
            tenant.setName(resultSet.getString(2));
            tenant.setAddress(resultSet.getString(3));

            tenants.add(tenant);
        }

        return tenants;
    }
}