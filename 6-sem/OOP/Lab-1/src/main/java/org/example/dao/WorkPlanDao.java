package org.example.dao;

import org.example.entity.WorkPlan;

import java.sql.SQLException;
import java.util.List;
import java.util.UUID;

public interface WorkPlanDao extends CrudDao<WorkPlan, UUID> {
    List<WorkPlan> findByDispatcherId(UUID dispatcherId) throws SQLException;
    List<WorkPlan> findByTeamId(UUID teamId) throws SQLException;
}
