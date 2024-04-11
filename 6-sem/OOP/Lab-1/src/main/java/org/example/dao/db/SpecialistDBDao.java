package org.example.dao.db;

import org.example.dao.SpecialistDao;
import org.example.entity.Specialist;

import java.sql.Connection;
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
        statement.setString(3, entity.getSpecializtion());
        statement.setObject(4, entity.getTeamId());

        statement.executeUpdate();
        return entity;
    }

    @Override
    public Specialist read(UUID uuid) throws Exception {
        var statement = con.prepareStatement("SELECT specialist_id, name, specialization, team_id " +
                "FROM specialist WHERE specialist_id = ?;");
        statement.setObject(1, uuid);

        var resultSet = statement.executeQuery();
        if (resultSet.next()) {
            var specialist = new Specialist();
            specialist.setSpecialistId((UUID) resultSet.getObject(1));
            specialist.setName(resultSet.getString(2));
            specialist.setSpecializtion(resultSet.getString(3));
            specialist.setTeamId((UUID) resultSet.getObject(4));

            return specialist;
        }
        return null;
    }

    @Override
    public void update(Specialist entity) throws Exception {
        var statement = con.prepareStatement("UPDATE specialist SET name = ?, specializtion = ?, team_id = ? " +
                                                 "WHERE specialist_id = ?;");
        statement.setString(1, entity.getName());
        statement.setString(2, entity.getSpecializtion());
        statement.setObject(3, entity.getTeamId());
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

        var resultSet = statement.executeQuery();
        var specialists = new ArrayList<Specialist>();
        while (resultSet.next()) {
            var specialist = new Specialist();
            specialist.setSpecialistId((UUID) resultSet.getObject(1));
            specialist.setName(resultSet.getString(2));
            specialist.setSpecializtion(resultSet.getString(3));
            specialist.setTeamId((UUID) resultSet.getObject(4));

            specialists.add(specialist);
        }
        return specialists;
    }
}
