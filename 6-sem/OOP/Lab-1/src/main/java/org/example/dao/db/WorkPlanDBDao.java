package org.example.dao.db;

import org.example.dao.WorkPlanDao;
import org.example.entity.WorkPlan;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import static org.example.utils.TimeUtils.pgIntervaltoDuration;

public class WorkPlanDBDao extends DBDao<WorkPlan, UUID> implements WorkPlanDao {
    protected WorkPlanDBDao(Connection con, String tableName) throws SQLException {
        super(con, tableName);
    }

    @Override
    protected void createTableIfNotExists() throws SQLException {
        var statement = con.prepareStatement("CREATE TABLE IF NOT EXISTS work_plan (" +
                "work_plan_id UUID PRIMARY KEY," +
                "description VARCHAR(255) NOT NULL," +
                "duration INTERVAL NOT NULL" +
                ");");
        statement.executeUpdate();
    }

    @Override
    public WorkPlan create(WorkPlan entity) throws Exception {
        var statement = con.prepareStatement("INSERT INTO work_plan (work_plan_id, description, duration) " +
                                                 "VALUES (?, ?, CAST(? AS INTERVAL));");

        statement.setObject(1, entity.getWorkPlanId());
        statement.setString(2, entity.getDescription());
        statement.setString(3, entity.getDuration().toString());

        statement.executeUpdate();
        return entity;
    }

    @Override
    public WorkPlan read(UUID uuid) throws Exception {
        var statement = con.prepareStatement("SELECT work_plan_id, description, duration FROM work_plan " +
                                                 "WHERE work_plan_id = ?;");
        statement.setObject(1, uuid);

        var resultSet = statement.executeQuery();
        if (resultSet.next()) {
            var workPlan = new WorkPlan();
            workPlan.setWorkPlanId((UUID) resultSet.getObject(1));
            workPlan.setDescription(resultSet.getString(2));
            var pgInterval = (org.postgresql.util.PGInterval) resultSet.getObject(3);
            var duration = pgIntervaltoDuration(pgInterval);
            workPlan.setDuration(duration);

            return workPlan;
        }
        return null;
    }

    @Override
    public void update(WorkPlan entity) throws Exception {
        var statement = con.prepareStatement("UPDATE work_plan SET description = ?, duration = CAST(? AS INTERVAL) " +
                                                 "WHERE work_plan_id = ?;");
        statement.setString(1, entity.getDescription());
        statement.setString(2, entity.getDuration().toString());
        statement.setObject(3, entity.getWorkPlanId());

        statement.executeUpdate();
    }

    @Override
    public void delete(UUID uuid) throws Exception {
        var statement = con.prepareStatement("DELETE FROM work_plan WHERE work_plan_id = ?;");
        statement.setObject(1, uuid);

        statement.executeUpdate();
    }

    @Override
    public List<WorkPlan> findAll() throws Exception {
        var statement = con.prepareStatement("SELECT work_plan_id, description, duration FROM work_plan;");

        var resultSet = statement.executeQuery();
        var entities = new ArrayList<WorkPlan>();
        while (resultSet.next()) {
            var workPlan = new WorkPlan();
            workPlan.setWorkPlanId((UUID) resultSet.getObject(1));
            workPlan.setDescription(resultSet.getString(2));
            var pgInterval = (org.postgresql.util.PGInterval) resultSet.getObject(3);
            var duration = pgIntervaltoDuration(pgInterval);
            workPlan.setDuration(duration);

            entities.add(workPlan);
        }

        return entities;
    }
}
