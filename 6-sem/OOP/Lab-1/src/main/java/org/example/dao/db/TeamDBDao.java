package org.example.dao.db;

import org.example.dao.TeamDao;
import org.example.entity.Team;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class TeamDBDao extends DBDao<Team, UUID> implements TeamDao {
    protected TeamDBDao(Connection con, String tableName) throws SQLException {
        super(con, tableName);
    }

    @Override
    protected void createTableIfNotExists() throws SQLException {
        var statement = con.prepareStatement("CREATE TABLE IF NOT EXISTS team (" +
                "team_id UUID PRIMARY KEY," +
                "dispatcher_id UUID NOT NULL, " +
                "work_plan_id UUID NOT NULL," +
                "FOREIGN KEY (dispatcher_id) REFERENCES specialist(specialist_id)," +
                "FOREIGN KEY (work_plan_id) REFERENCES work_plan(work_plan_id)" +
                ");");

        statement.executeUpdate();

        // statement = con.prepareStatement("ALTER TABLE team ADD CONSTRAINT fk_team_dispatcher_id " +
        //         "FOREIGN KEY (dispatcher_id) REFERENCES specialist(specialist_id);");

        // statement.executeUpdate();
    }

    @Override
    public Team create(Team entity) throws Exception {
        var statement = con.prepareStatement("INSERT INTO team (team_id, dispatcher_id, work_plan_id) " +
                                                 "VALUES (?, ?, ?);");

        statement.setObject(1, entity.getTeamId());
        statement.setObject(2, entity.getDispatcher().getSpecialistId());
        statement.setObject(3, entity.getWorkPlan().getWorkPlanId());

        statement.executeUpdate();
        return entity;
    }

    @Override
    public Team read(UUID uuid) throws Exception {
        var statement = con.prepareStatement("SELECT team_id, dispatcher_id, " +
                                                 "work_plan_id FROM team WHERE team_id = ?;");
        statement.setObject(1, uuid);

        var resultSet = statement.executeQuery();
        if (resultSet.next()) {
            var team = new Team();
            team.setTeamId((UUID) resultSet.getObject(1));
            team.getDispatcher().setSpecialistId((UUID) resultSet.getObject(2));
            team.getWorkPlan().setWorkPlanId((UUID) resultSet.getObject(3));

            return team;
        }
        return null;
    }

    @Override
    public void update(Team entity) throws Exception {
        var statement = con.prepareStatement("UPDATE team SET dispatcher_id = ?, " +
                                                 "work_plan_id = ? WHERE team_id = ?;");
        statement.setObject(1, entity.getDispatcher().getSpecialistId());
        statement.setObject(2, entity.getWorkPlan().getWorkPlanId());
        statement.setObject(3, entity.getTeamId());

        statement.executeUpdate();
    }

    @Override
    public void delete(UUID uuid) throws Exception {
        var statement = con.prepareStatement("DELETE FROM team WHERE team_id = ?;");
        statement.setObject(1, uuid);

        statement.executeUpdate();
    }

    @Override
    public List<Team> findAll() throws Exception {
        var statement = con.prepareStatement("SELECT team_id, dispatcher_id, " +
                                                 "work_plan_id FROM team;");

        var resultSet = statement.executeQuery();
        var teams = new ArrayList<Team>();
        while (resultSet.next()) {
            var team = new Team();
            team.setTeamId((UUID) resultSet.getObject(1));
            team.getDispatcher().setSpecialistId((UUID) resultSet.getObject(2));
            team.getWorkPlan().setWorkPlanId((UUID) resultSet.getObject(3));

            teams.add(team);
        }
        return teams;
    }
}
