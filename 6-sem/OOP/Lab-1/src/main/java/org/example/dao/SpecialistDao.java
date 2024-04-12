package org.example.dao;

import org.example.entity.Specialist;

import java.sql.SQLException;
import java.util.List;
import java.util.UUID;

public interface SpecialistDao extends CrudDao<Specialist, UUID> {
    List<Specialist> findByTeamId(UUID teamId) throws SQLException;
}
