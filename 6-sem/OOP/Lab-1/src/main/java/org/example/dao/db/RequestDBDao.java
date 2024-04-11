package org.example.dao.db;

import org.example.dao.RequestDao;
import org.example.entity.Request;

import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Duration;
import java.util.List;
import java.util.UUID;

import static org.example.utils.TimeUtils.pgIntervaltoDuration;


public class RequestDBDao extends DBDao<Request, UUID> implements RequestDao {
    protected RequestDBDao(Connection con, String tableName) throws SQLException {
        super(con, tableName);
    }

    @Override
    protected void createTableIfNotExists() throws SQLException {
        var statement = con.prepareStatement("CREATE TABLE IF NOT EXISTS request (" +
                "request_id UUID PRIMARY KEY," +
                "tenant_id UUID NOT NULL," +
                "work_type VARCHAR(255) NOT NULL," +
                "scope_of_work VARCHAR(255) NOT NULL," +
                "desired_time INTERVAL NOT NULL," +
                "FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id)" +
                ");");
        statement.executeUpdate();
    }

    @Override
    public Request create(Request entity) throws Exception {
        var statement = con.prepareStatement("INSERT INTO request (request_id, tenant_id, work_type, scope_of_work, desired_time) " +
                                                 "VALUES (?, ?, ?, ?, CAST(? AS INTERVAL));");
        statement.setObject(1, entity.getRequestId());
        statement.setObject(2, entity.getTenantId());
        statement.setString(3, entity.getWorkType());
        statement.setString(4, entity.getScopeOfWork());
        statement.setString(5, entity.getDesiredTime().toString());

        statement.executeUpdate();
        return entity;
    }

    @Override
    public Request read(UUID uuid) throws Exception {
        var statement = con.prepareStatement("SELECT request_id, tenant_id, work_type, " +
                                                 "scope_of_work, desired_time FROM request WHERE request_id = ?;");
        statement.setObject(1, uuid);

        var resultSet = statement.executeQuery();
        if (resultSet.next()) {
            var request = new Request();
            request.setRequestId((UUID) resultSet.getObject(1));
            request.setTenantId((UUID) resultSet.getObject(2));
            request.setWorkType(resultSet.getString(3));
            request.setScopeOfWork(resultSet.getString(4));
            var pgInterval = (org.postgresql.util.PGInterval) resultSet.getObject(5);
            var duration = pgIntervaltoDuration(pgInterval);
            request.setDesiredTime(duration);

            return request;
        }
        return null;
    }

    @Override
    public void update(Request entity) throws Exception {
        var statement = con.prepareStatement("UPDATE request SET tenant_id = ?, work_type = ?, " +
                                                 "scope_of_work = ?, desired_time = ? WHERE request_id = ?;");
        statement.setObject(1, entity.getTenantId());
        statement.setString(2, entity.getWorkType());
        statement.setString(3, entity.getScopeOfWork());
        statement.setObject(4, entity.getDesiredTime());
        statement.setObject(5, entity.getRequestId());

        statement.executeUpdate();
    }

    @Override
    public void delete(UUID uuid) throws Exception {
        var statement = con.prepareStatement("DELETE FROM request WHERE request_id = ?;");
        statement.setObject(1, uuid);

        statement.executeUpdate();
    }

    @Override
    public List<Request> findAll() throws Exception {
        var statement = con.prepareStatement("SELECT request_id, tenant_id, work_type, " +
                                                 "scope_of_work, desired_time FROM request;");

        var resultSet = statement.executeQuery();
        var requests = new java.util.ArrayList<Request>();
        while (resultSet.next()) {
            var request = new Request();
            request.setRequestId((UUID) resultSet.getObject(1));
            request.setTenantId((UUID) resultSet.getObject(2));
            request.setWorkType(resultSet.getString(3));
            request.setScopeOfWork(resultSet.getString(4));
            var pgInterval = (org.postgresql.util.PGInterval) resultSet.getObject(5);
            var duration = pgIntervaltoDuration(pgInterval);
            request.setDesiredTime(duration);

            requests.add(request);
        }
        return requests;
    }
}
