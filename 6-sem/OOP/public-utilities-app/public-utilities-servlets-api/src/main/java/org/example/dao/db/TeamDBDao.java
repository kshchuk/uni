package org.example.dao.db;

import org.example.dao.TeamDao;
import org.example.entity.Specialist;
import org.example.entity.Team;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
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
                "FOREIGN KEY (dispatcher_id) REFERENCES specialist(specialist_id)" +
                ");");

        statement.executeUpdate();

        // statement = con.prepareStatement("ALTER TABLE team ADD CONSTRAINT fk_team_dispatcher_id " +
        //         "FOREIGN KEY (dispatcher_id) REFERENCES specialist(specialist_id);");

        // statement.executeUpdate();
    }

    @Override
    public Team create(Team entity) throws Exception {
        var statement = con.prepareStatement("INSERT INTO team (team_id, dispatcher_id) " +
                                                 "VALUES (?, ?);");

        statement.setObject(1, entity.getTeamId());
        statement.setObject(2, entity.getDispatcher().getSpecialistId());

        statement.executeUpdate();
        return entity;
    }

    @Override
    public Team read(UUID uuid) throws Exception {
        var statement = con.prepareStatement("SELECT team_id, dispatcher_id " +
                                                 " FROM team WHERE team_id = ?;");
        statement.setObject(1, uuid);

        return getTeam(statement);
    }

    @Override
    public void update(Team entity) throws Exception {
        var statement = con.prepareStatement("UPDATE team SET dispatcher_id = ? " +
                                                 " WHERE team_id = ?;");
        statement.setObject(1, entity.getDispatcher().getSpecialistId());
        statement.setObject(2, entity.getTeamId());

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
        var statement = con.prepareStatement("SELECT team_id, dispatcher_id " +
                                                 " FROM team;");

        return getTeams(statement);
    }

    private Team getTeam(PreparedStatement statement) throws SQLException {
        var resultSet = statement.executeQuery();
        if (resultSet.next()) {
            return getTeam(resultSet);
        }
        return null;
    }

    private List<Team> getTeams(PreparedStatement statement) throws SQLException {
        var resultSet = statement.executeQuery();
        var entities = new ArrayList<Team>();
        while (resultSet.next()) {
            var team = getTeam(resultSet);

            entities.add(team);
        }
        return entities;
    }

    private Team getTeam(ResultSet resultSet) throws SQLException {
        var team = new Team();
        team.setTeamId((UUID) resultSet.getObject(1));
        var dispatcher = new Specialist();
        team.setDispatcher(dispatcher);
        team.getDispatcher().setSpecialistId((UUID) resultSet.getObject(2));

        return team;
    }
}
