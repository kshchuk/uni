package org.example.dao.db;

import org.example.dao.SpecialistDao;
import org.example.entity.Specialist;
import org.example.entity.Team;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class SpecialistDBDao extends DBDao<Specialist, UUID> implements SpecialistDao {
    protected SpecialistDBDao(Connection con, String tableName) throws SQLException {
        super(con, tableName);
    }

    @Override
    protected void createTableIfNotExists() throws SQLException {
        var statement = con.prepareStatement("CREATE TABLE IF NOT EXISTS specialist (" +
                "specialist_id UUID PRIMARY KEY," +
                "name VARCHAR(50) NOT NULL," +
                "specialization VARCHAR(100) NOT NULL," +
                "team_id UUID " +
                ");");

        statement.executeUpdate();
    }

    @Override
    public Specialist create(Specialist entity) throws Exception {
        var statement = con.prepareStatement("INSERT INTO specialist (specialist_id, name, specialization, team_id) " +
                "VALUES (?, ?, ?, ?);");
        statement.setObject(1, entity.getSpecialistId());
        statement.setString(2, entity.getName());
        statement.setString(3, entity.getSpecialization());
        var team = entity.getTeam();
        if (team != null) {
            statement.setObject(4, team.getTeamId());
        } else {
            statement.setObject(4, null);
        }

        statement.executeUpdate();
        return entity;
    }

    @Override
    public Specialist read(UUID uuid) throws Exception {
        var statement = con.prepareStatement("SELECT specialist_id, name, specialization, team_id " +
                "FROM specialist WHERE specialist_id = ?;");
        statement.setObject(1, uuid);

        return getSpecialist(statement);
    }

    @Override
    public void update(Specialist entity) throws Exception {
        var statement = con.prepareStatement("UPDATE specialist SET name = ?, specializtion = ?, team_id = ? " +
                                                 "WHERE specialist_id = ?;");
        statement.setString(1, entity.getName());
        statement.setString(2, entity.getSpecialization());
        var team = entity.getTeam();
        if (team != null) {
            statement.setObject(3, team.getTeamId());
        } else {
            statement.setObject(3, null);
        }
        statement.setObject(4, entity.getSpecialistId());

        statement.executeUpdate();
    }

    @Override
    public void delete(UUID uuid) throws Exception {
        var statement = con.prepareStatement("DELETE FROM specialist WHERE specialist_id = ?;");
        statement.setObject(1, uuid);

        statement.executeUpdate();
    }

    @Override
    public List<Specialist> findAll() throws Exception {
        var statement = con.prepareStatement("SELECT specialist_id, name, specialization, team_id " +
                                                 "FROM specialist;");

        return getSpecialists(statement);
    }

    @Override
    public List<Specialist> findByTeamId(UUID teamId) throws SQLException {
        var statement = con.prepareStatement("SELECT specialist_id, name, specialization, team_id " +
                                                 "FROM specialist WHERE team_id = ?;");
        statement.setObject(1, teamId);

        return getSpecialists(statement);
    }

    private Specialist getSpecialist(PreparedStatement statement) throws SQLException {
        var resultSet = statement.executeQuery();
        if (resultSet.next()) {
            return getSpecialist(resultSet);
        }
        return null;
    }

    private List<Specialist> getSpecialists(PreparedStatement statement) throws SQLException {
        var resultSet = statement.executeQuery();
        var specialists = new ArrayList<Specialist>();
        while (resultSet.next()) {
            var specialist = getSpecialist(resultSet);

            specialists.add(specialist);
        }
        return specialists;
    }

    private Specialist getSpecialist(ResultSet resultSet) throws SQLException {
        var specialist = new Specialist();
        specialist.setSpecialistId((UUID) resultSet.getObject(1));
        specialist.setName(resultSet.getString(2));
        specialist.setSpecialization(resultSet.getString(3));
        var team = resultSet.getObject(4);
        if (team != null) {
            specialist.setTeam(new Team());
            specialist.getTeam().setTeamId((UUID) team);
        }

        return specialist;
    }
}
