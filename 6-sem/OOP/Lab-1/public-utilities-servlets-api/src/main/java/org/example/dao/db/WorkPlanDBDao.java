package org.example.dao.db;

import org.example.dao.WorkPlanDao;
import org.example.entity.Team;
import org.example.entity.WorkPlan;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
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
                "duration INTERVAL NOT NULL," +
                "team_id UUID NOT NULL" +
                //"FOREIGN KEY (team_id) REFERENCES team(team_id)" +
                ");");
        statement.executeUpdate();

        // statement = con.prepareStatement("ALTER TABLE work_plan ADD CONSTRAINT fk_work_plan_team_id " +
        //        "FOREIGN KEY (team_id) REFERENCES team(team_id);");

        // statement.executeUpdate();
    }

    @Override
    public WorkPlan create(WorkPlan entity) throws Exception {
        var statement = con.prepareStatement("INSERT INTO work_plan (work_plan_id, description, duration, team_id) " +
                                                 "VALUES (?, ?, CAST(? AS INTERVAL), ?);");

        statement.setObject(1, entity.getWorkPlanId());
        statement.setString(2, entity.getDescription());
        statement.setString(3, entity.getDuration().toString());
        var team = entity.getTeam();
        if (team != null) {
            statement.setObject(4, team.getTeamId());
        } else {
            throw new IllegalArgumentException("Team cannot be null");
        }

        statement.executeUpdate();
        return entity;
    }

    @Override
    public WorkPlan read(UUID uuid) throws Exception {
        var statement = con.prepareStatement("SELECT work_plan_id, description, duration, team_id FROM work_plan " +
                                                 "WHERE work_plan_id = ?;");
        statement.setObject(1, uuid);

        return getwWorkPlan(statement);
    }

    @Override
    public void update(WorkPlan entity) throws Exception {
        var statement = con.prepareStatement("UPDATE work_plan SET description = ?, duration = CAST(? AS INTERVAL), team_id = ? " +
                                                 "WHERE work_plan_id = ?;");
        statement.setString(1, entity.getDescription());
        statement.setString(2, entity.getDuration().toString());
        var team = entity.getTeam();
        if (team != null) {
            statement.setObject(3, team.getTeamId());
        } else {
            throw new IllegalArgumentException("Team cannot be null");
        }
        statement.setObject(4, entity.getWorkPlanId());

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
        var statement = con.prepareStatement("SELECT work_plan_id, description, duration, team_id FROM work_plan;");

        return getWorkPlans(statement);
    }

    @Override
    public List<WorkPlan> findByDispatcherId(UUID dispatcherId) throws SQLException {
        var statement = con.prepareStatement("SELECT work_plan.work_plan_id, work_plan.description, work_plan.duration, work_plan.team_id FROM work_plan " +
                                                 " INNER JOIN team on work_plan.team_id = team.team_id " +
                                                 " WHERE team.dispatcher_id = ?;");
        statement.setObject(1, dispatcherId);

        return getWorkPlans(statement);
    }

    @Override
    public List<WorkPlan> findByTeamId(UUID teamId) throws SQLException {
        var statement = con.prepareStatement("SELECT work_plan_id, description, duration, team_id FROM work_plan " +
                                                 " WHERE team_id = ?;");
        statement.setObject(1, teamId);

        return getWorkPlans(statement);
    }

    private List<WorkPlan> getWorkPlans(PreparedStatement statement) throws SQLException {
        var resultSet = statement.executeQuery();
        var entities = new ArrayList<WorkPlan>();
        while (resultSet.next()) {
            var workPlan = getWorkPlan(resultSet);

            entities.add(workPlan);
        }

        return entities;
    }

    private WorkPlan getwWorkPlan(PreparedStatement statement) throws SQLException {
        var resultSet = statement.executeQuery();
        if (resultSet.next()) {
            return getWorkPlan(resultSet);
        }
        return null;
    }

    private WorkPlan getWorkPlan(ResultSet resultSet) throws SQLException {
        var workPlan = new WorkPlan();
        workPlan.setWorkPlanId((UUID) resultSet.getObject(1));
        workPlan.setDescription(resultSet.getString(2));
        var pgInterval = (org.postgresql.util.PGInterval) resultSet.getObject(3);
        var duration = pgIntervaltoDuration(pgInterval);
        workPlan.setDuration(duration);
        var teamId = (UUID) resultSet.getObject(4);
        var team = new Team();
        team.setTeamId(teamId);
        workPlan.setTeam(team);

        return workPlan;
    }
}
